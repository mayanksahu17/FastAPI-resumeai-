from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Server"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
