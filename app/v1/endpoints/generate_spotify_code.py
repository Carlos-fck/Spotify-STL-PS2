from fastapi import APIRouter, Depends
from app.api.v1.dependencies import get_token_header
from pydantic import BaseModel

router = APIRouter()

class SpotifyURLRequest(BaseModel):
    spotify_url: str

@router.post("/")
def post_generate_spotify_code(request: SpotifyURLRequest):
    print("Received request with Spotify URL:", request.spotify_url)
    spotify_url = request.spotify_url
    return {"message": spotify_url}

@router.get("/")
def get_generate_spotify_code():
    return {"message": "Generate Spotify Code Endpoint"}