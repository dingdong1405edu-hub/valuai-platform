from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/valuai",
    )

    # Redis / Celery
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Anthropic / Claude
    ANTHROPIC_API_KEY: str = Field(default="")
    CLAUDE_MODEL: str = Field(default="claude-sonnet-4-6")

    # Supabase (optional — system works without it)
    SUPABASE_URL: str = Field(default="")
    SUPABASE_SERVICE_KEY: str = Field(default="")
    SUPABASE_ANON_KEY: str = Field(default="")
    SUPABASE_BUCKET: str = Field(default="valuai-documents")

    # Backend public URL (used for PDF download links)
    BACKEND_URL: str = Field(default="http://localhost:8000")

    # JWT / Auth
    SECRET_KEY: str = Field(default="change-me-in-production-use-a-long-random-string")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=10080)

    # App
    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")
    MAX_FILE_SIZE_MB: int = Field(default=50)
    MAX_FILES_PER_REPORT: int = Field(default=20)

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
