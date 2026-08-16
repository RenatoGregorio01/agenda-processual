from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import require_permission
from app.core.database import get_session
from app.core.permissions import Permission
from app.core.tenant import get_owned
from app.core.timeutils import utc_now
from app.models.checklist_item import ChecklistItem
from app.models.prazo import Prazo
from app.models.user import User
from app.schemas.checklist import ChecklistItemCreate, ChecklistItemRead, ChecklistItemUpdate

router = APIRouter()


async def _get_prazo(session: AsyncSession, prazo_id: UUID, tenant_id: UUID) -> Prazo:
    return await get_owned(
        session, Prazo, prazo_id, tenant_id, detail="Prazo não encontrado"
    )


async def _get_item(
    session: AsyncSession,
    prazo_id: UUID,
    item_id: UUID,
) -> ChecklistItem:
    item = await session.get(ChecklistItem, item_id)
    if item is None or item.prazo_id != prazo_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item do checklist não encontrado",
        )
    return item


@router.get(
    "/{prazo_id}/checklist",
    response_model=list[ChecklistItemRead],
)
async def listar_checklist(
    prazo_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_visualizar)),
) -> list[ChecklistItem]:
    await _get_prazo(session, prazo_id, current_user.escritorio_id)
    result = await session.exec(
        select(ChecklistItem)
        .where(ChecklistItem.prazo_id == prazo_id)
        .order_by(col(ChecklistItem.ordem).asc(), col(ChecklistItem.criado_em).asc())
    )
    return list(result.all())


@router.post(
    "/{prazo_id}/checklist",
    response_model=ChecklistItemRead,
    status_code=status.HTTP_201_CREATED,
)
async def criar_item_checklist(
    prazo_id: UUID,
    payload: ChecklistItemCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_alterar)),
) -> ChecklistItem:
    await _get_prazo(session, prazo_id, current_user.escritorio_id)
    texto = payload.texto.strip()
    if not texto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe o texto do item",
        )

    result = await session.exec(
        select(ChecklistItem)
        .where(ChecklistItem.prazo_id == prazo_id)
        .order_by(col(ChecklistItem.ordem).desc())
    )
    ultimo = result.first()
    ordem = (ultimo.ordem + 1) if ultimo else 0

    item = ChecklistItem(prazo_id=prazo_id, texto=texto, ordem=ordem)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.patch(
    "/{prazo_id}/checklist/{item_id}",
    response_model=ChecklistItemRead,
)
async def atualizar_item_checklist(
    prazo_id: UUID,
    item_id: UUID,
    payload: ChecklistItemUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_alterar)),
) -> ChecklistItem:
    await _get_prazo(session, prazo_id, current_user.escritorio_id)
    item = await _get_item(session, prazo_id, item_id)
    data = payload.model_dump(exclude_unset=True)
    if "texto" in data and data["texto"] is not None:
        texto = data["texto"].strip()
        if not texto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Informe o texto do item",
            )
        item.texto = texto
    if "concluido" in data and data["concluido"] is not None:
        item.concluido = data["concluido"]
    item.atualizado_em = utc_now()
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.delete(
    "/{prazo_id}/checklist/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def excluir_item_checklist(
    prazo_id: UUID,
    item_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission(Permission.prazos_alterar)),
) -> None:
    await _get_prazo(session, prazo_id, current_user.escritorio_id)
    item = await _get_item(session, prazo_id, item_id)
    await session.delete(item)
    await session.commit()
