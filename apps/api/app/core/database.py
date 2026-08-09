from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import get_settings
from app.models import AuditLog, Prazo, User  # noqa: F401

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
        # Bancos já criados antes do soft delete
        await conn.execute(
            text("ALTER TABLE prazos ADD COLUMN IF NOT EXISTS excluido_em TIMESTAMP NULL")
        )
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_prazos_excluido_em ON prazos (excluido_em)"
            )
        )
