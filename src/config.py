from functools import lru_cache
from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    api_token: str = Field(min_length=1)
    private_portal_user: str = Field(default="admin", min_length=1)
    private_portal_password: str = Field(min_length=1)
    docs_host: str | None = None
    timezone: str = "America/Sao_Paulo"
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)
    disk_path: str = "/"
    docker_host: str | None = None
    ga_property_id: str | None = None
    google_application_credentials: str | None = None
    ga_cache_seconds: int = Field(default=300, ge=0)
    cors_origins: str = ""

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def now(self) -> datetime:
        return datetime.now(ZoneInfo(self.timezone))


@lru_cache
def get_settings() -> Settings:
    return Settings()
