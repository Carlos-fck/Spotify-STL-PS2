from fastapi import APIRouter, Depends
from app.api.v1.dependencies import get_token_header
from pydantic import BaseModel
import urllib.parse
from fastapi.responses import JSONResponse

router = APIRouter()

class SpotifyURLRequest(BaseModel):
    spotify_url: str

def generate_spotify_code_url(spotify_url: str):
    parsed_url = urllib.parse.urlparse(spotify_url)
    path_parts = parsed_url.path.strip('/').split('/')

    if len(path_parts) < 2:
        raise ValueError("Invalid Spotify URL")

    item_type = path_parts[0]
    item_id = path_parts[1]
    spotify_uri = f"spotify:{item_type}:{item_id}"
    encoded_uri = urllib.parse.quote(f"svg/FFFFFF/black/640/{spotify_uri}", safe='')

    final_url = f"https://www.spotifycodes.com/downloadCode.php?uri={encoded_uri}"
    print(f"Generated Spotify code URL: {final_url}")
    return final_url

@router.post("/")
def post_generate_spotify_code(request: SpotifyURLRequest):
    code_url = generate_spotify_code_url(request.spotify_url)
    preview_url = f"https://scannables.scdn.co/uri/plain/jpeg/ffffff/black/640/{urllib.parse.quote(request.spotify_url, safe='')}"
    print("Received request with Spotify URL:", code_url)
    print("Generated preview URL:", preview_url)
    
    return {"message": preview_url}

@router.get("/")
def get_generate_spotify_code(url : str):
    try:
        print("Received URL for Spotify code generation:", url)
        code_url = generate_spotify_code_url(url)
        return JSONResponse(content={"code_url": code_url})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})       