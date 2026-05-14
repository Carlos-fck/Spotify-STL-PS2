import urllib.parse
import xml.etree.ElementTree as ET
import re
from pathlib import Path
from uuid import uuid4

import requests
import trimesh
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from shapely.affinity import scale, translate
from shapely.geometry import LineString, MultiPolygon, Point, Polygon
from svgpathtools import parse_path

router = APIRouter()

SUPPORTED_SPOTIFY_TYPES = {"track", "album", "playlist", "artist"}
BASE_KEYCHAIN_PATH = Path("app/assets/keychain.stl")
GENERATED_DIR = Path("frontend/static/generated")
SVG_EXTRUDE_HEIGHT = 1.0


class SpotifyURLRequest(BaseModel):
    spotify_url: str


def parse_spotify_url(spotify_url: str) -> tuple[str, str, str]:
    parsed_url = urllib.parse.urlparse(spotify_url)
    if parsed_url.netloc not in {"open.spotify.com", "www.open.spotify.com"}:
        raise ValueError("Invalid Spotify URL")

    path_parts = parsed_url.path.strip("/").split("/")
    if len(path_parts) < 2 or path_parts[0] not in SUPPORTED_SPOTIFY_TYPES:
        raise ValueError("Invalid Spotify URL")

    item_type = path_parts[0]
    item_id = path_parts[1]
    spotify_uri = f"spotify:{item_type}:{item_id}"
    return item_type, item_id, spotify_uri


def generate_spotify_code_url(spotify_url: str) -> str:
    _, _, spotify_uri = parse_spotify_url(spotify_url)
    encoded_uri = urllib.parse.quote(f"svg/FFFFFF/black/640/{spotify_uri}", safe="")
    return f"https://www.spotifycodes.com/downloadCode.php?uri={encoded_uri}"


def generate_spotify_preview_url(spotify_url: str) -> str:
    _, _, spotify_uri = parse_spotify_url(spotify_url)
    encoded_uri = urllib.parse.quote(spotify_uri, safe="")
    return f"https://scannables.scdn.co/uri/plain/jpeg/ffffff/black/640/{encoded_uri}"


def fetch_spotify_code_svg(spotify_url: str) -> str:
    try:
        response = requests.get(generate_spotify_code_url(spotify_url), timeout=20)
        response.raise_for_status()
    except requests.RequestException as error:
        raise HTTPException(status_code=502, detail="Failed to download Spotify Code SVG") from error

    return response.text


def parse_translate(transform: str | None) -> tuple[float, float]:
    if not transform:
        return 0.0, 0.0

    match = re.search(r"translate\(([-0-9.]+)(?:[ ,]+([-0-9.]+))?\)", transform)
    if not match:
        return 0.0, 0.0

    x_offset = float(match.group(1))
    y_offset = float(match.group(2) or 0)
    return x_offset, y_offset


def rect_to_polygon(rect_elem, offset_x: float = 0.0, offset_y: float = 0.0) -> Polygon | None:
    try:
        x = float(rect_elem.get("x", 0)) + offset_x
        y = float(rect_elem.get("y", 0)) + offset_y
        width = float(rect_elem.get("width", 0))
        height = float(rect_elem.get("height", 0))
        radius_x = float(rect_elem.get("rx", 0) or 0)
        radius_y = float(rect_elem.get("ry", 0) or 0)
    except ValueError:
        return None

    if width <= 0 or height <= 0:
        return None

    radius = min(radius_x or radius_y, radius_y or radius_x, width / 2, height / 2)
    if radius > 0:
        if height >= width and radius >= width / 2 * 0.95:
            center_x = x + width / 2
            line = LineString([(center_x, -(y + radius)), (center_x, -(y + height - radius))])
            return line.buffer(width / 2, resolution=16, cap_style=1)

        if width > height and radius >= height / 2 * 0.95:
            center_y = -(y + height / 2)
            line = LineString([(x + radius, center_y), (x + width - radius, center_y)])
            return line.buffer(height / 2, resolution=16, cap_style=1)

    return Polygon([
        (x, -y),
        (x + width, -y),
        (x + width, -(y + height)),
        (x, -(y + height)),
    ])


def sample_path_to_polygons(path_data: str, offset_x: float, offset_y: float) -> list[Polygon]:
    path = parse_path(path_data)
    shells = []
    holes = []

    for subpath in path.continuous_subpaths():
        points = []
        for segment in subpath:
            for step in range(32):
                point = segment.point(step / 31)
                points.append((point.real + offset_x, -(point.imag + offset_y)))

        if len(points) < 3:
            continue

        if points[0] != points[-1]:
            points.append(points[0])

        polygon = Polygon(points)
        if not polygon.is_valid or polygon.area <= 0:
            polygon = polygon.buffer(0)
        if not polygon.is_valid or polygon.area <= 0:
            continue

        signed_area = 0.0
        for current, next_point in zip(points, points[1:]):
            signed_area += current[0] * next_point[1] - next_point[0] * current[1]

        if signed_area >= 0:
            shells.append(polygon)
        else:
            holes.append(polygon)

    result = []
    for shell in shells:
        shell_holes = []
        remaining_holes = []
        for hole in holes:
            if shell.contains(hole.representative_point()):
                shell_holes.append(list(hole.exterior.coords))
            else:
                remaining_holes.append(hole)
        holes = remaining_holes

        polygon = Polygon(shell.exterior.coords, shell_holes)
        if polygon.is_valid and polygon.area > 0:
            result.append(polygon)

    result.extend(hole for hole in holes if hole.is_valid and hole.area > 0)
    return result


def path_to_circle(path_data: str, offset_x: float, offset_y: float) -> Polygon | None:
    path = parse_path(path_data)
    points = []
    for segment in path:
        for step in range(24):
            point = segment.point(step / 23)
            points.append((point.real + offset_x, -(point.imag + offset_y)))

    if not points:
        return None

    min_x = min(point[0] for point in points)
    max_x = max(point[0] for point in points)
    min_y = min(point[1] for point in points)
    max_y = max(point[1] for point in points)
    radius = min(max_x - min_x, max_y - min_y) / 2
    if radius <= 0:
        return None

    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    return Point(center_x, center_y).buffer(radius, resolution=32)


def collect_svg_polygons(elem, offset_x: float = 0.0, offset_y: float = 0.0) -> list[Polygon]:
    local_x, local_y = parse_translate(elem.get("transform"))
    current_x = offset_x + local_x
    current_y = offset_y + local_y
    tag_name = elem.tag.split("}")[-1]
    fill = (elem.get("fill") or elem.get("style") or "").lower()

    polygons = []
    if "#fff" not in fill and "white" not in fill:
        if tag_name == "rect":
            polygon = rect_to_polygon(elem, current_x, current_y)
            if polygon and polygon.is_valid and polygon.area > 0:
                polygons.append(polygon)
        elif tag_name == "path" and elem.get("d"):
            polygon = path_to_circle(elem.get("d"), current_x, current_y)
            if polygon and polygon.is_valid and polygon.area > 0:
                polygons.append(polygon)
        elif tag_name == "circle":
            try:
                cx = float(elem.get("cx", 0)) + current_x
                cy = float(elem.get("cy", 0)) + current_y
                radius = float(elem.get("r", 0))
            except ValueError:
                radius = 0
            if radius > 0:
                polygons.append(Point(cx, -cy).buffer(radius, resolution=32))

    for child in elem:
        polygons.extend(collect_svg_polygons(child, current_x, current_y))

    return polygons


def load_svg_polygons(svg_content: str) -> MultiPolygon:
    try:
        root = ET.fromstring(svg_content)
    except ET.ParseError as error:
        raise HTTPException(status_code=502, detail="Invalid Spotify Code SVG") from error

    polygons = collect_svg_polygons(root)

    if not polygons:
        raise HTTPException(status_code=502, detail="Spotify Code SVG has no extrudable geometry")

    return MultiPolygon(polygons)


def fit_svg_to_keychain(svg_polygons: MultiPolygon, base_mesh: trimesh.Trimesh) -> MultiPolygon:
    base_min, base_max = base_mesh.bounds
    base_width = base_max[0] - base_min[0]
    base_height = base_max[1] - base_min[1]

    target_min_x = base_min[0] + base_width * 0.055
    target_max_x = base_max[0] - base_width * 0.13
    target_min_y = base_min[1] + base_height * 0.035
    target_max_y = base_max[1] - base_height * 0.035

    min_x, min_y, max_x, max_y = svg_polygons.bounds
    svg_width = max_x - min_x
    svg_height = max_y - min_y
    target_width = target_max_x - target_min_x
    target_height = target_max_y - target_min_y
    scale_factor = min(target_width / svg_width, target_height / svg_height)

    fitted = scale(svg_polygons, xfact=scale_factor, yfact=scale_factor, origin=(0, 0))
    min_x, min_y, max_x, max_y = fitted.bounds
    fitted_width = max_x - min_x
    fitted_height = max_y - min_y

    offset_x = target_min_x + (target_width - fitted_width) / 2 - min_x
    offset_y = target_min_y + (target_height - fitted_height) / 2 - min_y
    return translate(fitted, xoff=offset_x, yoff=offset_y)


def extrude_svg_polygons(svg_polygons: MultiPolygon) -> trimesh.Trimesh:
    meshes = []
    for polygon in svg_polygons.geoms:
        if polygon.is_valid and polygon.area > 0:
            meshes.append(trimesh.creation.extrude_polygon(polygon, SVG_EXTRUDE_HEIGHT))

    if not meshes:
        raise HTTPException(status_code=502, detail="Spotify Code SVG extrusion failed")

    return trimesh.util.concatenate(meshes)


def place_extrusion_on_base(base_mesh: trimesh.Trimesh, extrusion: trimesh.Trimesh) -> trimesh.Trimesh:
    front_z = base_mesh.bounds[1][2]
    extrusion.apply_translation([0, 0, front_z - extrusion.bounds[0][2]])
    return trimesh.util.concatenate([base_mesh, extrusion])


def create_keychain_stl(spotify_url: str) -> str:
    if not BASE_KEYCHAIN_PATH.exists():
        raise HTTPException(status_code=500, detail="Base keychain STL was not found")

    base_mesh = trimesh.load(BASE_KEYCHAIN_PATH)
    if not isinstance(base_mesh, trimesh.Trimesh):
        base_mesh = base_mesh.dump(concatenate=True)

    svg_content = fetch_spotify_code_svg(spotify_url)
    svg_polygons = load_svg_polygons(svg_content)
    fitted_polygons = fit_svg_to_keychain(svg_polygons, base_mesh)
    svg_extrusion = extrude_svg_polygons(fitted_polygons)
    final_model = place_extrusion_on_base(base_mesh, svg_extrusion)

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    file_name = f"soundchain-{uuid4().hex}.stl"
    output_path = GENERATED_DIR / file_name
    final_model.export(output_path)
    return f"/static/generated/{file_name}"


def build_generation_response(spotify_url: str):
    item_type, item_id, spotify_uri = parse_spotify_url(spotify_url)
    return {
        "type": item_type,
        "id": item_id,
        "spotify_uri": spotify_uri,
        "code_url": generate_spotify_code_url(spotify_url),
        "preview_url": generate_spotify_preview_url(spotify_url),
        "download_url": create_keychain_stl(spotify_url),
    }


@router.post("/")
def post_generate_spotify_code(request: SpotifyURLRequest):
    try:
        return build_generation_response(request.spotify_url)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/")
def get_generate_spotify_code(url: str):
    try:
        return JSONResponse(content=build_generation_response(url))
    except ValueError as error:
        return JSONResponse(status_code=400, content={"error": str(error)})
