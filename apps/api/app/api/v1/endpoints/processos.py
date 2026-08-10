from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_permission
from app.core.database import get_session
from app.core.permissions import Permission
from app.core.timeutils import utc_now
from app.models.audit_log import AuditAction
from app.models.processo import Processo
from app.models.user import User
from app.schemas.audit import AuditLogRead
from app.schemas.prazo import PrazoRead
from app.schemas.processo import ProcessoDetail, ProcessoRead, ProcessoUpdate
from app.services.alertas import status_alertas_enviados
from app.services.audit import montar_auditoria
from app.services.processos import (
    count_prazos_processo,
    get_processo_by_numero,
    list_historico_processo,
    list_prazos_processo,
)

router = APIRouter()


async def _to_processo_read(session: AsyncSession, processo: Processo) -> ProcessoRead:
    return ProcessoRead(
        id=processo.id,
        numero_processo=processo.numero_processo,
        cliente=processo.cliente,
        criado_em=processo.criado_em,
        atualizado_em=processo.atualizado_em,
        prazos_count=await count_prazos_processo(session, processo.id),
    )


async def _to_prazo_read(session: AsyncSession, prazo) -> PrazoRead:
    enviados = await status_alertas_enviados(session, prazo.id)
    return PrazoRead.model_validate(prazo, from_attributes=True).model_copy(update=enviados)


async def _detail(session: AsyncSession, processo: Processo) -> ProcessoDetail:
    prazos = await list_prazos_processo(session, processo.id, incluir_excluidos=True)
    historico = await list_historico_processo(session, processo)
    prazo_reads = [await _to_prazo_read(session, prazo) for prazo in prazos]
    return ProcessoDetail(
        processo=await _to_processo_read(session, processo),
        prazos=prazo_reads,
        historico=[
            AuditLogRead.model_validate(item, from_attributes=True) for item in historico
        ],
    )


@router.get(
    "",
    response_model=list[ProcessoRead],
    dependencies=[Depends(require_permission(Permission.prazos_visualizar))],
)
async def listar_processos(
    q: str | None = Query(default=None, max_length=120),
    session: AsyncSession = Depends(get_session),
) -> list[ProcessoRead]:
    query = select(Processo).order_by(col(Processo.atualizado_em).desc())
    if q and q.strip():
        term = f"%{q.strip().lower()}%"
        query = query.where(
            col(Processo.numero_processo).ilike(term) | col(Processo.cliente).ilike(term)
        )
    result = await session.exec(query.limit(100))
    processos = list(result.all())
    return [await _to_processo_read(session, item) for item in processos]


@router.get(
    "/by-numero/{numero_processo:path}",
    response_model=ProcessoDetail,
    dependencies=[Depends(require_permission(Permission.prazos_visualizar))],
)
async def obter_processo_por_numero(
    numero_processo: str,
    session: AsyncSession = Depends(get_session),
) -> ProcessoDetail:
    processo = await get_processo_by_numero(session, numero_processo)
    if processo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processo não encontrado",
        )
    return await _detail(session, processo)


@router.get(
    "/{processo_id}",
    response_model=ProcessoDetail,
    dependencies=[Depends(require_permission(Permission.prazos_visualizar))],
)
async def obter_processo(
    processo_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> ProcessoDetail:
    processo = await session.get(Processo, processo_id)
    if processo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processo não encontrado",
        )
    return await _detail(session, processo)


@router.patch("/{processo_id}", response_model=ProcessoRead)
async def atualizar_processo(
    processo_id: UUID,
    payload: ProcessoUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_alterar)),
) -> ProcessoRead:
    processo = await session.get(Processo, processo_id)
    if processo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processo não encontrado",
        )

    data = payload.model_dump(exclude_unset=True)
    if "cliente" in data and data["cliente"] is not None:
        processo.cliente = data["cliente"].strip()
        prazos = await list_prazos_processo(session, processo.id, incluir_excluidos=True)
        for prazo in prazos:
            prazo.cliente = processo.cliente
            session.add(prazo)

    processo.atualizado_em = utc_now()
    session.add(processo)
    session.add(
        montar_auditoria(
            usuario=current_user,
            acao=AuditAction.processo_atualizado,
            entidade="processo",
            entidade_id=processo.id,
            resumo=f"Atualizou processo {processo.numero_processo}",
        )
    )
    await session.commit()
    await session.refresh(processo)
    return await _to_processo_read(session, processo)
