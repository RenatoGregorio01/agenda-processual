from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Agenda Processual API"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    database_url: str = (
        "postgresql+asyncpg://agenda:agenda@localhost:5432/agenda_processual"
    )
    database_url_sync: str = (
        "postgresql+psycopg://agenda:agenda@localhost:5432/agenda_processual"
    )

    jwt_secret: str = "dev-secret-change-me-please-32b+"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 12

    seed_admin_email: str = "veronica@escritorio.com"
    seed_admin_password: str = "agenda123"
    seed_admin_name: str = "Verônica"


@lru_cache
def get_settings() -> Settings:
    return Settings()
