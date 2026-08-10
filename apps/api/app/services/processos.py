from uuid import UUID, uuid4

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.timeutils import utc_now
from app.models.audit_log import AuditAction, AuditLog
from app.models.prazo import Prazo
from app.models.processo import Processo
from app.models.user import User
from app.services.audit import montar_auditoria


def normalize_numero_processo(numero: str) -> str:
    return " ".join(numero.strip().split())


async def get_processo_by_numero(
    session: AsyncSession,
    numero_processo: str,
) -> Processo | None:
    numero = normalize_numero_processo(numero_processo)
    result = await session.exec(
        select(Processo).where(Processo.numero_processo == numero)
    )
    return result.first()


async def get_or_create_processo(
    session: AsyncSession,
    *,
    numero_processo: str,
    cliente: str,
    usuario: User,
) -> tuple[Processo, bool]:
    numero = normalize_numero_processo(numero_processo)
    cliente_limpo = cliente.strip()
    existing = await get_processo_by_numero(session, numero)
    if existing is not None:
        if cliente_limpo and existing.cliente != cliente_limpo:
            existing.cliente = cliente_limpo
            existing.atualizado_em = utc_now()
            session.add(existing)
            session.add(
                montar_auditoria(
                    usuario=usuario,
                    acao=AuditAction.processo_atualizado,
                    entidade="processo",
                    entidade_id=existing.id,
                    resumo=f"Atualizou cliente do processo {existing.numero_processo}",
                )
            )
        return existing, False

    processo = Processo(numero_processo=numero, cliente=cliente_limpo)
    session.add(processo)
    await session.flush()
    session.add(
        montar_auditoria(
            usuario=usuario,
            acao=AuditAction.processo_criado,
            entidade="processo",
            entidade_id=processo.id,
            resumo=f"Criou processo {processo.numero_processo} ({processo.cliente})",
        )
    )
    return processo, True


async def count_prazos_processo(session: AsyncSession, processo_id: UUID) -> int:
    result = await session.exec(
        select(Prazo).where(
            Prazo.processo_id == processo_id,
            col(Prazo.excluido_em).is_(None),
        )
    )
    return len(result.all())


async def list_prazos_processo(
    session: AsyncSession,
    processo_id: UUID,
    *,
    incluir_excluidos: bool = True,
) -> list[Prazo]:
    query = select(Prazo).where(Prazo.processo_id == processo_id)
    if not incluir_excluidos:
        query = query.where(col(Prazo.excluido_em).is_(None))
    query = query.order_by(col(Prazo.data_vencimento).asc())
    result = await session.exec(query)
    return list(result.all())


async def list_historico_processo(
    session: AsyncSession,
    processo: Processo,
    *,
    limit: int = 100,
) -> list[AuditLog]:
    prazos = await list_prazos_processo(session, processo.id, incluir_excluidos=True)
    prazo_ids = [prazo.id for prazo in prazos]

    processo_logs = await session.exec(
        select(AuditLog)
        .where(
            (AuditLog.entidade == "processo") & (AuditLog.entidade_id == processo.id)
        )
        .order_by(col(AuditLog.criado_em).desc())
        .limit(limit)
    )
    logs = list(processo_logs.all())

    if prazo_ids:
        prazo_logs = await session.exec(
            select(AuditLog)
            .where(
                (AuditLog.entidade == "prazo")
                & (col(AuditLog.entidade_id).in_(prazo_ids))
            )
            .order_by(col(AuditLog.criado_em).desc())
            .limit(limit)
        )
        logs.extend(prazo_logs.all())

    logs.sort(key=lambda item: item.criado_em, reverse=True)
    return logs[:limit]


async def backfill_processos(session: AsyncSession) -> int:
    """Cria processos a partir de prazos sem processo_id e vincula."""
    result = await session.exec(
        select(Prazo).where(col(Prazo.processo_id).is_(None))
    )
    prazos = list(result.all())
    if not prazos:
        return 0

    by_numero: dict[str, list[Prazo]] = {}
    for prazo in prazos:
        numero = normalize_numero_processo(prazo.numero_processo)
        by_numero.setdefault(numero, []).append(prazo)

    created = 0
    for numero, grupo in by_numero.items():
        existing = await get_processo_by_numero(session, numero)
        if existing is None:
            cliente = next((p.cliente for p in grupo if p.cliente), "Cliente")
            existing = Processo(
                id=uuid4(),
                numero_processo=numero,
                cliente=cliente.strip() or "Cliente",
            )
            session.add(existing)
            await session.flush()
            created += 1

        for prazo in grupo:
            prazo.processo_id = existing.id
            prazo.numero_processo = existing.numero_processo
            if not prazo.cliente:
                prazo.cliente = existing.cliente
            session.add(prazo)

    await session.commit()
    return created
