from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_permission
from app.core.database import get_session
from app.core.permissions import Permission
from app.models.audit_log import AuditAction
from app.models.prazo import Prazo, StatusPrazo
from app.models.user import User
from app.schemas.prazo import PrazoCreate, PrazoRead, PrazoUpdate
from app.services.alertas import status_alertas_enviados
from app.services.audit import montar_auditoria
from app.services.export_pauta import build_csv, build_pdf
from app.services.prazos_query import FiltroPrazo, listar_prazos_filtrados

router = APIRouter()

ExportFormat = Literal["csv", "pdf"]


async def _get_prazo_ativo(session: AsyncSession, prazo_id: UUID) -> Prazo:
    prazo = await session.get(Prazo, prazo_id)
    if prazo is None or prazo.excluido_em is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prazo não encontrado")
    return prazo


async def _resolve_responsavel(session: AsyncSession, responsavel_id: UUID) -> User:
    user = await session.get(User, responsavel_id)
    if user is None or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Responsável inválido ou inativo",
        )
    return user


@router.get(
    "",
    response_model=list[PrazoRead],
    dependencies=[Depends(require_permission(Permission.prazos_visualizar))],
)
async def listar_prazos(
    filtro: FiltroPrazo = Query(default="todos"),
    responsavel_id: UUID | None = Query(default=None),
    q: str | None = Query(default=None, max_length=120),
    session: AsyncSession = Depends(get_session),
) -> list[Prazo]:
    return await listar_prazos_filtrados(
        session,
        filtro=filtro,
        responsavel_id=responsavel_id,
        q=q,
    )


@router.get(
    "/export",
    dependencies=[Depends(require_permission(Permission.prazos_visualizar))],
)
async def exportar_prazos(
    formato: ExportFormat = Query(default="csv"),
    filtro: FiltroPrazo = Query(default="7dias"),
    responsavel_id: UUID | None = Query(default=None),
    q: str | None = Query(default=None, max_length=120),
    session: AsyncSession = Depends(get_session),
) -> Response:
    prazos = await listar_prazos_filtrados(
        session,
        filtro=filtro,
        responsavel_id=responsavel_id,
        q=q,
    )
    hoje = datetime.utcnow().strftime("%Y%m%d")
    titulo = f"Pauta ({filtro})"
    if formato == "pdf":
        content = build_pdf(prazos, titulo=titulo)
        return Response(
            content=content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="pauta-{filtro}-{hoje}.pdf"'
            },
        )

    content = build_csv(prazos)
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="pauta-{filtro}-{hoje}.csv"'
        },
    )


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
    responsavel = await _resolve_responsavel(session, payload.responsavel_id)
    data = payload.model_dump()
    prazo = Prazo(
        **data,
        responsavel=responsavel.nome,
    )
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
) -> PrazoRead:
    prazo = await session.get(Prazo, prazo_id)
    if prazo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prazo não encontrado")
    enviados = await status_alertas_enviados(session, prazo.id)
    return PrazoRead.model_validate(prazo, from_attributes=True).model_copy(update=enviados)


@router.patch("/{prazo_id}", response_model=PrazoRead)
async def atualizar_prazo(
    prazo_id: UUID,
    payload: PrazoUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_alterar)),
) -> Prazo:
    prazo = await _get_prazo_ativo(session, prazo_id)
    data = payload.model_dump(exclude_unset=True)

    if "responsavel_id" in data and data["responsavel_id"] is not None:
        responsavel = await _resolve_responsavel(session, data["responsavel_id"])
        prazo.responsavel_id = responsavel.id
        prazo.responsavel = responsavel.nome
        data.pop("responsavel_id")

    for field, value in data.items():
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
