"""Application configuration management via Pydantic settings."""
from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings object for the service."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    app_name: str = "Hermes API"
    environment: str = Field("development", description="Deployment environment name")
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = Field(
        "sqlite+aiosqlite:///./hermes.db",
        description="SQLAlchemy compatible database URL",
    )
    alembic_database_url: Optional[str] = Field(
        default=None,
        description="Override database URL for Alembic if different from runtime URL.",
    )
    redis_url: Optional[str] = None

    access_token_expire_minutes: int = 60
    jwt_secret_key: str = Field(
        "change-me", description="Secret key used to sign JWT tokens"
    )
    jwt_algorithm: str = "HS256"

    rate_limit_per_minute: int = Field(
        120,
        ge=1,
        description="Maximum number of requests allowed per minute per client",
    )
    request_timeout_seconds: float = Field(10.0, gt=0)

    cors_origins: List[AnyHttpUrl] = Field(default_factory=list)

    prometheus_multiproc_dir: Optional[str] = None
    otlp_endpoint: Optional[str] = Field(
        default=None,
        description="OTLP endpoint for OpenTelemetry export. If unset tracing is disabled.",
    )
    log_level: str = Field("INFO", description="Base logging level")

    class Config:
        env_prefix = "HERMES_"

    @property
    def sync_database_url(self) -> str:
        """Return a synchronous database URL variant for tooling like Alembic."""
        if self.database_url.startswith("sqlite+aiosqlite"):
            return self.database_url.replace("sqlite+aiosqlite", "sqlite", 1)
        if self.database_url.startswith("postgresql+asyncpg"):
            return self.database_url.replace("postgresql+asyncpg", "postgresql", 1)
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    """Return a cached instance of :class:`Settings`."""
    return Settings()
