from fastapi import APIRouter, HTTPException, Body
import requests
from urllib.parse import urlparse
from app.core.config import settings
from app.schemas.spotify_auth import get_spotify_access_token

router = APIRouter()

@router.post("/get-track-info")
def get_spotify_info(spotify_url: str = Body(..., embed=True)):
    parsed = urlparse(spotify_url)
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid Spotify URL")

    type_, spotify_id = path_parts
    if type_ not in ["track", "album", "playlist", "artist"]:
        raise HTTPException(status_code=400, detail="Unsupported Spotify type")

    token = get_spotify_access_token(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET)
    headers = {"Authorization": f"Bearer {token}"}

    url = f"https://api.spotify.com/v1/{type_}s/{spotify_id}"
    response = requests.get(url, headers=headers)

    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch from Spotify")

    data = response.json()

    if type_ == "track":
        return {
            "type": "track",
            "id": spotify_id,
            "data": {
                "title": data["name"],
                "artist": data["artists"][0]["name"],
                "album": data["album"]["name"],
                "image": data["album"]["images"][0]["url"],
                "duration": f"{int(data['duration_ms'] // 60000)}:{str(int(data['duration_ms'] % 60000 // 1000)).zfill(2)}",
                "release_date": data["album"]["release_date"]
            }
        }

    elif type_ == "album":
        return {
            "type": "album",
            "id": spotify_id,
            "data": {
                "title": data["name"],
                "artist": data["artists"][0]["name"],
                "image": data["images"][0]["url"],
                "tracks": data["total_tracks"],
                "release_date": data["release_date"]
            }
        }

    elif type_ == "playlist":
        return {
            "type": "playlist",
            "id": spotify_id,
            "data": {
                "title": data["name"],
                "creator": data["owner"]["display_name"],
                "image": data["images"][0]["url"],
                "tracks": data["tracks"]["total"],
                "followers": f"{data['followers']['total']:,}"
            }
        }

    elif type_ == "artist":
        return {
            "type": "artist",
            "id": spotify_id,
            "data": {
                "title": data["name"],
                "image": data["images"][0]["url"],
                "followers": f"{data['followers']['total']:,}",
                "monthly_listeners": "—"  # Spotify API doesn't expose monthly listeners directly
            }
        }