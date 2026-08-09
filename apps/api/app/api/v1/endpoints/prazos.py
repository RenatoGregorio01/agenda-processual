from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.models.prazo import Prazo, StatusPrazo
from app.schemas.prazo import PrazoCreate, PrazoRead, PrazoUpdate

router = APIRouter()


@router.get("", response_model=list[PrazoRead])
async def listar_prazos(
    session: AsyncSession = Depends(get_session),
) -> list[Prazo]:
    result = await session.exec(
        select(Prazo).order_by(Prazo.data_vencimento.asc(), Prazo.criado_em.asc())
    )
    return list(result.all())


@router.post("", response_model=PrazoRead, status_code=status.HTTP_201_CREATED)
async def criar_prazo(
    payload: PrazoCreate,
    session: AsyncSession = Depends(get_session),
) -> Prazo:
    prazo = Prazo(**payload.model_dump())
    session.add(prazo)
    await session.commit()
    await session.refresh(prazo)
    return prazo


@router.get("/{prazo_id}", response_model=PrazoRead)
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
) -> Prazo:
    prazo = await session.get(Prazo, prazo_id)
    if prazo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prazo não encontrado")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(prazo, field, value)

    session.add(prazo)
    await session.commit()
    await session.refresh(prazo)
    return prazo


@router.post("/{prazo_id}/cumprir", response_model=PrazoRead)
async def marcar_cumprido(
    prazo_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> Prazo:
    prazo = await session.get(Prazo, prazo_id)
    if prazo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prazo não encontrado")

    prazo.status = StatusPrazo.cumprido
    session.add(prazo)
    await session.commit()
    await session.refresh(prazo)
    return prazo


@router.delete("/{prazo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_prazo(
    prazo_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> None:
    prazo = await session.get(Prazo, prazo_id)
    if prazo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prazo não encontrado")

    await session.delete(prazo)
    await session.commit()
