from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    # --- Application ---
    APP_NAME: str = "finance-copilot"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # --- Database ---
    POSTGRES_HOST: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "finance_copilot"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    @model_validator(mode="after")
    def assemble_db_url(self) -> "Settings":
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return self

    # --- Redis ---
    REDIS_URL: str = "redis://redis:6379/0"

    # --- APIs ---
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    PRIMARY_LLM_PROVIDER: str = "openai"
    
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    FMP_API_KEY: Optional[str] = None
    SEC_EDGAR_USER_AGENT: str = "finance-copilot contact@example.com"

    # --- Observability ---
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

settings = Settings()
