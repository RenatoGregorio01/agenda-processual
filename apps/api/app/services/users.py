from app.core.permissions import permissions_for_role
from app.models.user import User
from app.schemas.user import UserRead


def to_user_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        email=user.email,
        nome=user.nome,
        ativo=user.ativo,
        role=user.role,
        is_admin=user.is_admin,
        permissions=permissions_for_role(user.role),
    )
