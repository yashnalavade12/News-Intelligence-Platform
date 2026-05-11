from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    FETCH_INTERVAL_MINUTES: int = 60
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DB_NAME: str = "newsdb"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
