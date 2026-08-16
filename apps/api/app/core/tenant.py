from typing import TypeVar
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User

T = TypeVar("T")


def escritorio_id(user: User) -> UUID:
    return user.escritorio_id


async def get_owned(
    session: AsyncSession,
    model: type[T],
    row_id: UUID,
    tenant_id: UUID,
    *,
    detail: str = "Não encontrado",
) -> T:
    row = await session.get(model, row_id)
    if row is None or getattr(row, "escritorio_id", None) != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return row
