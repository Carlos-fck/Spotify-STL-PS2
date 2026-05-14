from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SoundChain"
    API_V1_STR: str = "/api/v1"
    SPOTIFY_CLIENT_ID: str = ""
    SPOTIFY_CLIENT_SECRET: str = ""

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()