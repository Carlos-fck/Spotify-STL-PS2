import trimesh
from svgpathtools import svg2paths
from shapely.geometry import Polygon, MultiPolygon, LineString, Point
from shapely.affinity import scale, translate
from shapely.ops import unary_union
import numpy as np
import xml.etree.ElementTree as ET

# === Settings ===
svg_path = "spotify.svg"
base_model_path = "keychain.stl"
output_path = "Spotify_Keychain.stl"

svg_extrude_height = 1.0
padding = 1.0
base_width = 80.0
base_height = 14.0
corner_radius = 2.0        # Raio para arredondar cantos (mm)
buffer_resolution = 16     # Resolução do buffer de arredondamento

# Circle settings
circle_radius = 5        # Raio do círculo (mm)
circle_offset = 4        # Offset do círculo das barras (mm)

def sample_path_to_polygon(path, num_points=900): 
    points = []
    for segment in path:
        segment_points = [segment.point(t) for t in np.linspace(0, 1, num_points)]
        points.extend([(pt.real, -pt.imag) for pt in segment_points])
    # Close polygon if ends aren't equal
    if points[0] != points[-1]:
        points.append(points[0])
    polygon = Polygon(points)
    return polygon if polygon.is_valid and polygon.is_simple else None

def rect_to_polygon(rect_elem):
    x = float(rect_elem.get('x', 0))
    y = float(rect_elem.get('y', 0))
    width = float(rect_elem.get('width', 0))
    height = float(rect_elem.get('height', 0))
    # SVG y axis is down, shapely y axis is up, so invert y
    points = [
        (x, -y),
        (x + width, -y),
        (x + width, -(y + height)),
        (x, -(y + height)),
        (x, -y)
    ]
    return Polygon(points)

def load_svg_polygons(svg_path):
    # Parse SVG XML
    tree = ET.parse(svg_path)
    root = tree.getroot()
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    # Try both with and without namespace
    rects = root.findall('.//svg:rect', ns)
    if not rects:
        rects = root.findall('.//rect')
    rect_polys = []
    rect_info = []
    print(f"Found {len(rects)} rect elements.")
    for rect in rects:
        poly = rect_to_polygon(rect)
        x = float(rect.get('x', 0))
        y = float(rect.get('y', 0))
        w = float(rect.get('width', 0))
        h = float(rect.get('height', 0))
        print(f"Rect: x={x}, y={y}, w={w}, h={h}, area={poly.area if poly else 0}, valid={poly.is_valid if poly else False}")
        if poly.is_valid and poly.is_simple:
            rect_polys.append(poly)
            rect_info.append({'poly': poly, 'x': x, 'y': y, 'w': w, 'h': h, 'area': poly.area})
    # Remove all rectangles that match the largest area (border)
    if len(rect_polys) > 1:
        max_area = max(r['area'] for r in rect_info)
        filtered = [r['poly'] for r in rect_info if r['area'] < max_area]
        print(f"Removed {len(rect_polys) - len(filtered)} border rectangles (area={max_area})")
        rect_polys = filtered
    if not rect_polys:
        raise ValueError("No valid polygons could be created from SVG.")
    print(f"Polygons to extrude: {len(rect_polys)}")
    return MultiPolygon(rect_polys)

def fit_and_center_polygon(polygon, width, height, padding=3.0, offset_x_correction=1.75, offset_y_correction=1.75):
    # Bounds do SVG
    minx, miny, maxx, maxy = polygon.bounds
    svg_width = maxx - minx
    svg_height = maxy - miny

    # Escala para caber com padding
    scale_x = (width - 2 * padding) / svg_width
    scale_y = (height - 2 * padding) / svg_height
    scale_factor = min(scale_x, scale_y)

    # Escalar em torno da origem
    scaled = scale(polygon, xfact=scale_factor, yfact=scale_factor, origin=(0, 0))

    # Recalcular bounds após o scale
    minx, miny, maxx, maxy = scaled.bounds
    new_width = maxx - minx
    new_height = maxy - miny

    # Centralizar ignorando a argola (deslocada 1.75mm da esquerda e de cima)
    offset_x = ((width - new_width) / 2 - minx) + offset_x_correction
    offset_y = ((height - new_height) / 2 - miny) + offset_y_correction

    return translate(scaled, xoff=offset_x, yoff=offset_y)

def fit_and_center_multipolygon(multipolygon, width, height, padding=2.0, offset_x_correction=2.0, offset_y_correction=1.75):
    minx, miny, maxx, maxy = multipolygon.bounds
    svg_width = maxx - minx
    svg_height = maxy - miny
    scale_x = (width - 2 * padding) / svg_width
    scale_y = (height - 2 * padding) / svg_height
    scale_factor = min(scale_x, scale_y)
    
    # Remove horizontal flip - back to normal orientation
    scaled = scale(multipolygon, xfact=scale_factor, yfact=scale_factor, origin=(0, 0))
    
    minx, miny, maxx, maxy = scaled.bounds
    new_width = maxx - minx
    new_height = maxy - miny
    offset_x = ((width - new_width) / 2 - minx) + offset_x_correction
    offset_y = ((height - new_height) / 2 - miny) + offset_y_correction
    return translate(scaled, xoff=offset_x, yoff=offset_y)

def extrude_polygon(polygon, height, corner_radius=0.0, buffer_resolution=16):
    """Extrude polygon with rounded end-caps or rounded corners"""
    original_polygon = polygon
    
    # Se for retângulo simples (4 arestas), criar cápsula usando linha central
    if corner_radius and corner_radius > 0:
        try:
            coords = list(polygon.exterior.coords)
            # Retângulo simples: 5 pontos (início/reinício)
            if len(coords) == 5:
                # Criar cápsula pelo maior eixo
                minx, miny, maxx, maxy = polygon.bounds
                w = maxx - minx
                h = maxy - miny
                cx = (minx + maxx) / 2
                cy = (miny + maxy) / 2
                if h >= w:
                    line = LineString([(cx, miny), (cx, maxy)])
                    polygon = line.buffer(w/2, resolution=buffer_resolution, cap_style=1)
                else:
                    line = LineString([(minx, cy), (maxx, cy)])
                    polygon = line.buffer(h/2, resolution=buffer_resolution, cap_style=1)
            else:
                # Arredonda todos os cantos via buffer e erosão
                polygon = polygon.buffer(corner_radius, resolution=buffer_resolution, join_style=1)
                polygon = polygon.buffer(-corner_radius, resolution=buffer_resolution, join_style=1)
        except Exception as e:
            print(f"⚠ Erro no buffer de arredondamento: {e}")
            polygon = original_polygon  # Use original if buffer fails

    # Ensure polygon is valid before extrusion
    if not polygon.is_valid:
        print(f"⚠ Invalid polygon detected, using original")
        polygon = original_polygon

    # Extrude to mesh
    try:
        if polygon.geom_type == 'Polygon':
            mesh = trimesh.creation.extrude_polygon(polygon, height)
        elif polygon.geom_type == 'MultiPolygon':
            mesh = trimesh.util.concatenate([
                trimesh.creation.extrude_polygon(p, height)
                for p in polygon.geoms if p.is_valid
            ])
        else:
            raise ValueError(f"Unsupported geometry type: {polygon.geom_type}")
        
        print(f"✅ Successfully extruded {polygon.geom_type} with {len(mesh.vertices)} vertices")
        return mesh
        
    except Exception as e:
        print(f"⚠ Error during extrusion: {e}")
        # Fallback: try with original polygon
        if polygon != original_polygon:
            print("Trying with original polygon...")
            mesh = trimesh.creation.extrude_polygon(original_polygon, height)
            return mesh
        else:
            raise e

def place_extrusion_on_base(base, extrusion):
    # Get bounds of the base
    base_min, base_max = base.bounds
    center_x = (base_min[0] + base_max[0]) / 2
    center_y = (base_min[1] + base_max[1]) / 2
    front_z = base_max[2]  # front face

    # Get bounds of the extrusion
    extr_min, extr_max = extrusion.bounds
    
    # Apply custom offset instead of perfect centering
    offset_x_custom = -4.0  # Deslocamento para a direita em mm
    
    shift_x = center_x - (extr_min[0] + extr_max[0]) / 2 + offset_x_custom
    shift_y = center_y - (extr_min[1] + extr_max[1]) / 2
    shift_z = front_z - extr_min[2]  # place exactly on front surface

    extrusion.apply_translation([shift_x, shift_y, shift_z])
    return trimesh.util.concatenate([base, extrusion])





# === Main Execution ===
print("Loading base model...")
base = trimesh.load(base_model_path)
if not isinstance(base, trimesh.Trimesh):
    base = base.dump(concatenate=True)

print("Processing SVG...")
svg_multipoly = load_svg_polygons(svg_path)
svg_fitted = fit_and_center_multipolygon(svg_multipoly, base_width, base_height, padding, offset_x_correction=2.0, offset_y_correction=3.5)

# Add a circle to the left of the bars
print("Adding circle to the left of bars...")
# Find the leftmost position of all polygons
min_x = min(poly.bounds[0] for poly in svg_fitted.geoms)
# Calculate center Y of all polygons
all_bounds = svg_fitted.bounds
center_y = (all_bounds[1] + all_bounds[3]) / 2
# Position circle to the left with offset
circle_center_x = min_x - circle_offset - circle_radius
# Create circle as a buffered point
circle = Point(circle_center_x, center_y).buffer(circle_radius, resolution=buffer_resolution)
# Add circle to the geometry collection
svg_fitted_with_circle = MultiPolygon(list(svg_fitted.geoms) + [circle])

# Extrude each polygon with individual corner radius (half of polygon height)
print("Extruding with per-polygon rounded corners...")
svg_extrusions = []
for i, poly in enumerate(svg_fitted_with_circle.geoms):
    minx, miny, maxx, maxy = poly.bounds
    # For the circle (last element), don't apply corner radius to avoid double-rounding
    if i == len(svg_fitted_with_circle.geoms) - 1:  # Last element is the circle
        print(f"Extruding circle (no corner radius)...")
        extr = extrude_polygon(poly, svg_extrude_height, corner_radius=0.0, buffer_resolution=buffer_resolution)
    else:
        # radius = half of polygon height for bars
        r = (maxy - miny) / 2
        print(f"Extruding bar {i} with corner radius {r:.2f}...")
        extr = extrude_polygon(poly, svg_extrude_height, corner_radius=r, buffer_resolution=buffer_resolution)
    svg_extrusions.append(extr)

print("Combining extrusions...")
all_extrusions = trimesh.util.concatenate(svg_extrusions)
final_model = place_extrusion_on_base(base, all_extrusions)

print("Exporting STL...")
final_model.export(output_path)
print(f"✅ Exported: {output_path}")