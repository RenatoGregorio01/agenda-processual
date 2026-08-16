from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.permissions import permissions_for_role
from app.models.escritorio import Escritorio
from app.models.user import User
from app.schemas.user import UserRead


def to_user_read(user: User, *, escritorio_nome: str = "") -> UserRead:
    return UserRead(
        id=user.id,
        escritorio_id=user.escritorio_id,
        escritorio_nome=escritorio_nome,
        email=user.email,
        nome=user.nome,
        ativo=user.ativo,
        role=user.role,
        receber_alertas=user.receber_alertas,
        is_admin=user.is_admin,
        permissions=permissions_for_role(user.role),
    )


async def to_user_read_with_escritorio(
    session: AsyncSession,
    user: User,
) -> UserRead:
    escritorio = await session.get(Escritorio, user.escritorio_id)
    return to_user_read(user, escritorio_nome=escritorio.nome if escritorio else "")
