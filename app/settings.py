from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SoundChain"
    API_V1_STR: str = "/api"
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str

    class Config:
        env_file = ".env"

settings = Settings()