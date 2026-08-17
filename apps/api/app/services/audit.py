from datetime import datetime, timedelta
from uuid import UUID

from sqlmodel import col, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.metrics import record_audit_purge
from app.core.timeutils import utc_now
from app.models.audit_log import AuditAction, AuditLog
from app.models.user import User


def cutoff_auditoria(
    *,
    retention_days: int,
    now: datetime | None = None,
) -> datetime:
    current = now or utc_now()
    return current - timedelta(days=retention_days)


def montar_auditoria(
    *,
    usuario: User,
    acao: AuditAction,
    resumo: str,
    entidade: str = "prazo",
    entidade_id: UUID | None = None,
) -> AuditLog:
    return AuditLog(
        escritorio_id=usuario.escritorio_id,
        usuario_id=usuario.id,
        usuario_nome=usuario.nome,
        usuario_email=usuario.email,
        acao=acao,
        entidade=entidade,
        entidade_id=entidade_id,
        resumo=resumo[:500],
    )


async def registrar_auditoria(
    session: AsyncSession,
    *,
    usuario: User,
    acao: AuditAction,
    resumo: str,
    entidade: str = "prazo",
    entidade_id: UUID | None = None,
) -> AuditLog:
    log = montar_auditoria(
        usuario=usuario,
        acao=acao,
        resumo=resumo,
        entidade=entidade,
        entidade_id=entidade_id,
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log


async def purgar_auditoria(
    session: AsyncSession,
    *,
    retention_days: int,
    batch_size: int = 1000,
    now: datetime | None = None,
) -> int:
    if retention_days < 1:
        raise ValueError("retention_days deve ser >= 1")
    if batch_size < 1:
        raise ValueError("batch_size deve ser >= 1")

    cutoff = cutoff_auditoria(retention_days=retention_days, now=now)
    deleted = 0

    while True:
        result = await session.exec(
            select(AuditLog.id)
            .where(col(AuditLog.criado_em) < cutoff)
            .limit(batch_size)
        )
        ids = list(result.all())
        if not ids:
            break
        await session.exec(delete(AuditLog).where(col(AuditLog.id).in_(ids)))
        await session.commit()
        deleted += len(ids)

    record_audit_purge(deleted=deleted)
    return deleted
