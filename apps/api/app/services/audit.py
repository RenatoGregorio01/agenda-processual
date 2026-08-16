from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.audit_log import AuditAction, AuditLog
from app.models.user import User


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
