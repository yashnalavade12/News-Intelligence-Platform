from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    FETCH_INTERVAL_MINUTES: int = 60
    DB_PATH: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "news.db"
    )

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
