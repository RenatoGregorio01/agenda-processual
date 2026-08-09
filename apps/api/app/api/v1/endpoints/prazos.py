from datetime import date, datetime, timedelta
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_permission
from app.core.database import get_session
from app.core.permissions import Permission
from app.models.audit_log import AuditAction
from app.models.prazo import Prazo, StatusPrazo
from app.models.user import User
from app.schemas.prazo import PrazoCreate, PrazoRead, PrazoUpdate
from app.services.audit import montar_auditoria

router = APIRouter()

FiltroPrazo = Literal["todos", "atrasados", "7dias", "cumpridos", "excluidos"]


async def _get_prazo_ativo(session: AsyncSession, prazo_id: UUID) -> Prazo:
    prazo = await session.get(Prazo, prazo_id)
    if prazo is None or prazo.excluido_em is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prazo não encontrado")
    return prazo


@router.get(
    "",
    response_model=list[PrazoRead],
    dependencies=[Depends(require_permission(Permission.prazos_visualizar))],
)
async def listar_prazos(
    filtro: FiltroPrazo = Query(default="todos"),
    session: AsyncSession = Depends(get_session),
) -> list[Prazo]:
    today = date.today()
    query = select(Prazo)

    if filtro == "excluidos":
        query = query.where(col(Prazo.excluido_em).is_not(None))
    else:
        query = query.where(col(Prazo.excluido_em).is_(None))
        if filtro == "atrasados":
            query = query.where(
                Prazo.status == StatusPrazo.pendente,
                Prazo.data_vencimento < today,
            )
        elif filtro == "7dias":
            query = query.where(
                Prazo.status == StatusPrazo.pendente,
                Prazo.data_vencimento >= today,
                Prazo.data_vencimento <= today + timedelta(days=7),
            )
        elif filtro == "cumpridos":
            query = query.where(Prazo.status == StatusPrazo.cumprido)

    if filtro == "excluidos":
        query = query.order_by(col(Prazo.excluido_em).desc())
    else:
        query = query.order_by(Prazo.data_vencimento.asc(), Prazo.criado_em.asc())

    result = await session.exec(query)
    return list(result.all())


@router.post(
    "",
    response_model=PrazoRead,
    status_code=status.HTTP_201_CREATED,
)
async def criar_prazo(
    payload: PrazoCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_criar)),
) -> Prazo:
    prazo = Prazo(**payload.model_dump())
    session.add(prazo)
    await session.flush()
    session.add(
        montar_auditoria(
            usuario=current_user,
            acao=AuditAction.prazo_criado,
            entidade_id=prazo.id,
            resumo=f"Criou prazo: {prazo.acao} ({prazo.numero_processo})",
        )
    )
    await session.commit()
    await session.refresh(prazo)
    return prazo


@router.get(
    "/{prazo_id}",
    response_model=PrazoRead,
    dependencies=[Depends(require_permission(Permission.prazos_visualizar))],
)
async def obter_prazo(
    prazo_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> Prazo:
    prazo = await session.get(Prazo, prazo_id)
    if prazo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prazo não encontrado")
    return prazo


@router.patch("/{prazo_id}", response_model=PrazoRead)
async def atualizar_prazo(
    prazo_id: UUID,
    payload: PrazoUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_alterar)),
) -> Prazo:
    prazo = await _get_prazo_ativo(session, prazo_id)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(prazo, field, value)
    prazo.atualizado_em = datetime.utcnow()

    session.add(prazo)
    session.add(
        montar_auditoria(
            usuario=current_user,
            acao=AuditAction.prazo_atualizado,
            entidade_id=prazo.id,
            resumo=f"Editou prazo: {prazo.acao} ({prazo.numero_processo})",
        )
    )
    await session.commit()
    await session.refresh(prazo)
    return prazo


@router.post("/{prazo_id}/cumprir", response_model=PrazoRead)
async def marcar_cumprido(
    prazo_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_cumprir)),
) -> Prazo:
    prazo = await _get_prazo_ativo(session, prazo_id)
    prazo.status = StatusPrazo.cumprido
    prazo.atualizado_em = datetime.utcnow()
    session.add(prazo)
    session.add(
        montar_auditoria(
            usuario=current_user,
            acao=AuditAction.prazo_cumprido,
            entidade_id=prazo.id,
            resumo=f"Marcou como cumprido: {prazo.acao} ({prazo.numero_processo})",
        )
    )
    await session.commit()
    await session.refresh(prazo)
    return prazo


@router.post("/{prazo_id}/restaurar", response_model=PrazoRead)
async def restaurar_prazo(
    prazo_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_restaurar)),
) -> Prazo:
    prazo = await session.get(Prazo, prazo_id)
    if prazo is None or prazo.excluido_em is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prazo excluído não encontrado",
        )

    prazo.excluido_em = None
    prazo.atualizado_em = datetime.utcnow()
    session.add(prazo)
    session.add(
        montar_auditoria(
            usuario=current_user,
            acao=AuditAction.prazo_restaurado,
            entidade_id=prazo.id,
            resumo=f"Restaurou prazo: {prazo.acao} ({prazo.numero_processo})",
        )
    )
    await session.commit()
    await session.refresh(prazo)
    return prazo


@router.delete("/{prazo_id}", response_model=PrazoRead)
async def excluir_prazo(
    prazo_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_excluir)),
) -> Prazo:
    prazo = await _get_prazo_ativo(session, prazo_id)
    prazo.excluido_em = datetime.utcnow()
    prazo.atualizado_em = datetime.utcnow()
    session.add(prazo)
    session.add(
        montar_auditoria(
            usuario=current_user,
            acao=AuditAction.prazo_excluido,
            entidade_id=prazo.id,
            resumo=f"Excluiu prazo: {prazo.acao} ({prazo.numero_processo})",
        )
    )
    await session.commit()
    await session.refresh(prazo)
    return prazo
