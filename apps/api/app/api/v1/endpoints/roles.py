from fastapi import APIRouter, Depends

from app.api.deps import get_current_admin
from app.core.permissions import (
    PERMISSION_LABELS,
    ROLE_DESCRIPTIONS,
    ROLE_LABELS,
    permissions_for_role,
)
from app.models.user import Role
from app.schemas.user import RoleInfo

router = APIRouter(dependencies=[Depends(get_current_admin)])


@router.get("", response_model=list[RoleInfo])
async def listar_roles() -> list[RoleInfo]:
    roles: list[RoleInfo] = []
    for role in Role:
        perms = permissions_for_role(role)
        roles.append(
            RoleInfo(
                id=role,
                label=ROLE_LABELS[role],
                description=ROLE_DESCRIPTIONS[role],
                permissions=perms,
                permission_labels=[PERMISSION_LABELS[p] for p in perms],
            )
        )
    return roles
