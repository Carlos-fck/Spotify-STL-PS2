from fastapi import APIRouter
from app.api.v1.endpoints import generate_spotify_code, items, spotify, users

api_router = APIRouter()
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(spotify.router, prefix="/spotify", tags=["spotify"])
api_router.include_router(generate_spotify_code.router, prefix="/generate_spotify_code", tags=["generate_spotify_code"])