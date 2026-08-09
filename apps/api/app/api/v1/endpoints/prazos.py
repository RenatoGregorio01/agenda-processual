from datetime import date, timedelta
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_session
from app.models.prazo import Prazo, StatusPrazo
from app.schemas.prazo import PrazoCreate, PrazoRead, PrazoUpdate

router = APIRouter(dependencies=[Depends(get_current_user)])

FiltroPrazo = Literal["todos", "atrasados", "7dias", "cumpridos"]


@router.get("", response_model=list[PrazoRead])
async def listar_prazos(
    filtro: FiltroPrazo = Query(default="todos"),
    session: AsyncSession = Depends(get_session),
) -> list[Prazo]:
    today = date.today()
    query = select(Prazo)

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

    query = query.order_by(Prazo.data_vencimento.asc(), Prazo.criado_em.asc())
    result = await session.exec(query)
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
