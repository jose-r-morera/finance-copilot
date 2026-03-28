"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Google AI
    GOOGLE_API_KEY: str = ""
    GOOGLE_PROJECT_ID: str = ""
    GOOGLE_REGION: str = "us-central1"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # App
    DEBUG: bool = False
    DEFAULT_TICKER: str = "AAPL"


settings = Settings()
