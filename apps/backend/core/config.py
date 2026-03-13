from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/xps_intelligence"
    )
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "change-me-in-production-never-hardcode"

    AUTONOMY_ENABLED: bool = False
    SCRAPER_AUTORUN_ENABLED: bool = False

    LLM_PROVIDER: str = "copilot"
    LLM_SECONDARY_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""

    SANDBOX_NETWORK_MODE: str = "restricted"

    OBJECT_STORAGE_ENDPOINT: str = "https://t3.storageapi.dev"
    OBJECT_STORAGE_BUCKET: str = "stocked-organizer-khf6nyu"
    OBJECT_STORAGE_ACCESS_KEY: str = ""
    OBJECT_STORAGE_SECRET_KEY: str = ""

    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
