from datetime import datetime, timedelta
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel, col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.audit_log import AuditAction, AuditLog
from app.models.escritorio import Escritorio
from app.services.audit import cutoff_auditoria, purgar_auditoria


@pytest.fixture
def agora() -> datetime:
    return datetime(2026, 8, 17, 12, 0, 0)


def test_cutoff_auditoria_usa_retencao(agora: datetime) -> None:
    assert cutoff_auditoria(retention_days=365, now=agora) == agora - timedelta(days=365)


@pytest_asyncio.fixture
async def session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as db:
        yield db
    await engine.dispose()


def _log(*, escritorio_id, criado_em: datetime) -> AuditLog:
    return AuditLog(
        escritorio_id=escritorio_id,
        usuario_id=uuid4(),
        usuario_nome="Teste",
        usuario_email="teste@escritorio.com",
        acao=AuditAction.login,
        entidade="auth",
        resumo="Login",
        criado_em=criado_em,
    )


async def test_purgar_auditoria_apaga_so_os_antigos(
    session: AsyncSession, agora: datetime
) -> None:
    escritorio = Escritorio(nome="Escritório", slug="escritorio")
    session.add(escritorio)
    await session.commit()
    await session.refresh(escritorio)

    velho = _log(
        escritorio_id=escritorio.id,
        criado_em=agora - timedelta(days=400),
    )
    recente = _log(
        escritorio_id=escritorio.id,
        criado_em=agora - timedelta(days=10),
    )
    session.add(velho)
    session.add(recente)
    await session.commit()

    apagados = await purgar_auditoria(
        session,
        retention_days=365,
        batch_size=10,
        now=agora,
    )
    assert apagados == 1

    restantes = list(
        (await session.exec(select(AuditLog).order_by(col(AuditLog.criado_em)))).all()
    )
    assert len(restantes) == 1
    assert restantes[0].id == recente.id


async def test_purgar_auditoria_respeita_lote(
    session: AsyncSession, agora: datetime
) -> None:
    escritorio = Escritorio(nome="Escritório", slug="lote")
    session.add(escritorio)
    await session.commit()
    await session.refresh(escritorio)

    for _ in range(5):
        session.add(
            _log(
                escritorio_id=escritorio.id,
                criado_em=agora - timedelta(days=400),
            )
        )
    await session.commit()

    apagados = await purgar_auditoria(
        session,
        retention_days=365,
        batch_size=2,
        now=agora,
    )
    assert apagados == 5
    restantes = list((await session.exec(select(AuditLog))).all())
    assert restantes == []


async def test_purgar_auditoria_rejeita_retencao_invalida(session: AsyncSession) -> None:
    with pytest.raises(ValueError, match="retention_days"):
        await purgar_auditoria(session, retention_days=0)
