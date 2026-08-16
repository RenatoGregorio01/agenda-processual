from fastapi import APIRouter, Depends, Query
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_session
from app.core.permissions import Permission, user_has_permission
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogRead

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[AuditLogRead])
async def listar_auditoria(
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[AuditLog]:
    query = (
        select(AuditLog)
        .where(AuditLog.escritorio_id == current_user.escritorio_id)
        .order_by(col(AuditLog.criado_em).desc())
        .limit(limit)
    )

    if not user_has_permission(current_user, Permission.auditoria_ver_tudo):
        query = query.where(AuditLog.usuario_id == current_user.id)

    result = await session.exec(query)
    return list(result.all())
