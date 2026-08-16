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
    app_public_url: str = "http://localhost:3000"

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
    seed_escritorio_nome: str = "Escritório"
    seed_escritorio_slug: str = "escritorio"

    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "agenda@local.test"
    smtp_from_name: str = "Agenda Processual"
    # STARTTLS (porta 587). Para 465 use smtp_ssl=true e smtp_tls=false.
    smtp_tls: bool = False
    smtp_ssl: bool = False

    alertas_enabled: bool = True
    alertas_cron_hour: int = 8

    invite_expire_hours: int = 72

    redis_url: str = "redis://localhost:6379/0"

    datajud_api_key: str = ""
    datajud_base_url: str = "https://api-publica.datajud.cnj.jus.br"
    datajud_cache_ttl_seconds: int = 60 * 60 * 12
    datajud_empty_ttl_seconds: int = 60 * 60 * 6
    datajud_lock_ttl_seconds: int = 45
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    seed_example_data: bool = True
    metrics_enabled: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
