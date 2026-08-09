from datetime import date, timedelta
from typing import Literal
from uuid import UUID

from sqlalchemy import or_
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.prazo import Prazo, StatusPrazo

FiltroPrazo = Literal[
    "todos", "atrasados", "hoje", "amanha", "7dias", "cumpridos", "excluidos"
]


async def listar_prazos_filtrados(
    session: AsyncSession,
    *,
    filtro: FiltroPrazo = "todos",
    responsavel_id: UUID | None = None,
    q: str | None = None,
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
        elif filtro == "hoje":
            query = query.where(
                Prazo.status == StatusPrazo.pendente,
                Prazo.data_vencimento == today,
            )
        elif filtro == "amanha":
            query = query.where(
                Prazo.status == StatusPrazo.pendente,
                Prazo.data_vencimento == today + timedelta(days=1),
            )
        elif filtro == "7dias":
            query = query.where(
                Prazo.status == StatusPrazo.pendente,
                Prazo.data_vencimento >= today,
                Prazo.data_vencimento <= today + timedelta(days=7),
            )
        elif filtro == "cumpridos":
            query = query.where(Prazo.status == StatusPrazo.cumprido)

    if responsavel_id is not None:
        query = query.where(Prazo.responsavel_id == responsavel_id)

    term = (q or "").strip()
    if term:
        pattern = f"%{term}%"
        query = query.where(
            or_(
                col(Prazo.numero_processo).ilike(pattern),
                col(Prazo.cliente).ilike(pattern),
                col(Prazo.acao).ilike(pattern),
                col(Prazo.responsavel).ilike(pattern),
            )
        )

    if filtro == "excluidos":
        query = query.order_by(col(Prazo.excluido_em).desc())
    else:
        query = query.order_by(Prazo.data_vencimento.asc(), Prazo.criado_em.asc())

    result = await session.exec(query)
    return list(result.all())
