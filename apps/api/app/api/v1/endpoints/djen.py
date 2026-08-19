from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_permission
from app.core.database import get_session
from app.core.permissions import Permission
from app.core.tenant import get_owned
from app.models.audit_log import AuditAction
from app.models.djen_publicacao import DjenPublicacao, DjenStatus
from app.models.user import User
from app.schemas.djen import DjenPublicacaoRead, DjenResumoRead, DjenSyncRead
from app.services.audit import montar_auditoria
from app.services.djen import (
    ignorar_publicacao,
    list_publicacoes,
    resumo,
    sincronizar_escritorio,
    to_publicacao_read,
)

router = APIRouter()


def _parse_status(value: str | None) -> DjenStatus | None:
    if not value or value == "todas":
        return None
    try:
        return DjenStatus(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status inválido. Use nova, prazo_criado, ignorada ou todas.",
        ) from exc


@router.get("", response_model=list[DjenPublicacaoRead])
async def listar_publicacoes(
    status_filtro: str | None = Query(default="nova", alias="status"),
    processo_id: UUID | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_visualizar)),
) -> list[DjenPublicacaoRead]:
    status_enum = _parse_status(status_filtro)
    items = await list_publicacoes(
        session,
        current_user.escritorio_id,
        status=status_enum,
        processo_id=processo_id,
    )
    return [await to_publicacao_read(session, item) for item in items]


@router.get("/resumo", response_model=DjenResumoRead)
async def resumo_publicacoes(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_visualizar)),
) -> DjenResumoRead:
    return await resumo(session, current_user.escritorio_id)


@router.get("/{publicacao_id}", response_model=DjenPublicacaoRead)
async def obter_publicacao(
    publicacao_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_visualizar)),
) -> DjenPublicacaoRead:
    item = await get_owned(
        session,
        DjenPublicacao,
        publicacao_id,
        current_user.escritorio_id,
        detail="Publicação não encontrada",
    )
    return await to_publicacao_read(session, item)


@router.post("/sync", response_model=DjenSyncRead)
async def sincronizar_escritorio_djen(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_criar)),
) -> DjenSyncRead:
    result = await sincronizar_escritorio(session, current_user.escritorio_id)
    items = await list_publicacoes(
        session, current_user.escritorio_id, status=DjenStatus.nova
    )
    return DjenSyncRead(
        ok=result.ok,
        criados=result.criados,
        mensagem=result.mensagem,
        publicacoes=[await to_publicacao_read(session, item) for item in items],
    )


@router.post("/{publicacao_id}/ignorar", response_model=DjenPublicacaoRead)
async def ignorar(
    publicacao_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_criar)),
) -> DjenPublicacaoRead:
    item = await get_owned(
        session,
        DjenPublicacao,
        publicacao_id,
        current_user.escritorio_id,
        detail="Publicação não encontrada",
    )
    if item.status == DjenStatus.prazo_criado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta publicação já gerou um prazo.",
        )
    item = await ignorar_publicacao(session, item)
    session.add(
        montar_auditoria(
            usuario=current_user,
            acao=AuditAction.djen_ignorada,
            entidade="djen",
            entidade_id=item.id,
            resumo=f"Ignorou publicação DJEN: {item.tipo_comunicacao} ({item.numero_processo})",
        )
    )
    await session.commit()
    await session.refresh(item)
    return await to_publicacao_read(session, item)
