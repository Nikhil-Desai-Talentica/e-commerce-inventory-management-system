# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "E-commerce Inventory Management"
    API_V1_STR: str = "/api/v1"
    SQLALCHEMY_DATABASE_URI: str = "sqlite+aiosqlite:///./inventory.db"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()