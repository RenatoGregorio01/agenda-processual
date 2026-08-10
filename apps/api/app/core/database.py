from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import get_settings
from app.models import (  # noqa: F401
    AlertaEnvio,
    AuditLog,
    Convite,
    Feriado,
    Prazo,
    Processo,
    User,
)

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        await conn.execute(
            text("ALTER TABLE prazos ADD COLUMN IF NOT EXISTS excluido_em TIMESTAMP NULL")
        )
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_prazos_excluido_em ON prazos (excluido_em)"
            )
        )
        await conn.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20)")
        )
        await conn.execute(
            text(
                "UPDATE users SET role = CASE "
                "WHEN is_admin = true THEN 'admin' "
                "ELSE COALESCE(role, 'editor') END "
                "WHERE role IS NULL OR role = ''"
            )
        )
        await conn.execute(text("UPDATE users SET role = 'editor' WHERE role IS NULL"))
        await conn.execute(
            text("CREATE INDEX IF NOT EXISTS ix_users_role ON users (role)")
        )
        await conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS receber_alertas BOOLEAN "
                "DEFAULT TRUE NOT NULL"
            )
        )
        await conn.execute(
            text("ALTER TABLE prazos ADD COLUMN IF NOT EXISTS responsavel_id UUID NULL")
        )
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_prazos_responsavel_id ON prazos (responsavel_id)"
            )
        )
        await conn.execute(
            text(
                "UPDATE prazos SET responsavel_id = users.id "
                "FROM users "
                "WHERE prazos.responsavel_id IS NULL "
                "AND lower(prazos.responsavel) = lower(users.nome)"
            )
        )
        await conn.execute(
            text(
                "UPDATE prazos SET responsavel_id = ("
                "SELECT id FROM users WHERE is_admin = true ORDER BY criado_em ASC LIMIT 1"
                ") "
                "WHERE responsavel_id IS NULL "
                "AND EXISTS (SELECT 1 FROM users WHERE is_admin = true)"
            )
        )
        await conn.execute(
            text("ALTER TABLE prazos ADD COLUMN IF NOT EXISTS processo_id UUID NULL")
        )
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_prazos_processo_id ON prazos (processo_id)"
            )
        )


async def run_processo_backfill() -> None:
    from app.services.processos import backfill_processos

    async with AsyncSessionLocal() as session:
        await backfill_processos(session)
