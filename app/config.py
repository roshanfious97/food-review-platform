from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Food Review API"
    environment: str = "local"
    debug: bool = False
    secret_key: str = "change-me-in-local-env"
    access_token_expire_minutes: int = 60
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/food_review",
        validation_alias="DATABASE_URL",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
