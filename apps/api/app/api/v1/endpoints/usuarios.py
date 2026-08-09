from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_admin, get_current_user
from app.core.database import get_session
from app.core.permissions import Permission, sync_admin_flag, user_has_permission
from app.core.security import hash_password
from app.models.audit_log import AuditAction
from app.models.user import Role, User
from app.schemas.user import UserCreate, UserOption, UserRead, UserUpdate
from app.services.audit import montar_auditoria
from app.services.users import to_user_read

router = APIRouter()


@router.get("/opcoes", response_model=list[UserOption])
async def listar_opcoes_usuarios(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[UserOption]:
    if not (
        user_has_permission(current_user, Permission.prazos_criar)
        or user_has_permission(current_user, Permission.prazos_alterar)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para esta ação",
        )

    result = await session.exec(
        select(User).where(col(User.ativo).is_(True)).order_by(col(User.nome).asc())
    )
    return [
        UserOption(id=user.id, nome=user.nome, email=user.email) for user in result.all()
    ]


@router.get("", response_model=list[UserRead], dependencies=[Depends(get_current_admin)])
async def listar_usuarios(
    session: AsyncSession = Depends(get_session),
) -> list[UserRead]:
    result = await session.exec(select(User).order_by(col(User.nome).asc()))
    return [to_user_read(user) for user in result.all()]


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
)
async def criar_usuario(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_current_admin),
) -> UserRead:
    email = payload.email.lower()
    existing = await session.exec(select(User).where(User.email == email))
    if existing.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com este e-mail",
        )

    user = User(
        email=email,
        nome=payload.nome.strip(),
        hashed_password=hash_password(payload.password),
        role=payload.role,
        ativo=payload.ativo,
        receber_alertas=payload.receber_alertas,
    )
    sync_admin_flag(user)
    session.add(user)
    await session.flush()
    session.add(
        montar_auditoria(
            usuario=current_admin,
            acao=AuditAction.usuario_criado,
            entidade="usuario",
            entidade_id=user.id,
            resumo=f"Criou usuário {user.nome} ({user.email}) com role {user.role}",
        )
    )
    await session.commit()
    await session.refresh(user)
    return to_user_read(user)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(get_current_admin)],
)
async def atualizar_usuario(
    user_id: UUID,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_current_admin),
) -> UserRead:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    data = payload.model_dump(exclude_unset=True)

    if user.id == current_admin.id:
        if data.get("ativo") is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Você não pode desativar a própria conta",
            )
        if data.get("role") is not None and data["role"] != Role.admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Você não pode remover o próprio perfil de administrador",
            )

    if "email" in data and data["email"] is not None:
        email = str(data["email"]).lower()
        existing = await session.exec(select(User).where(User.email == email, User.id != user.id))
        if existing.first() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um usuário com este e-mail",
            )
        user.email = email

    if "nome" in data and data["nome"] is not None:
        user.nome = data["nome"].strip()
    if "role" in data and data["role"] is not None:
        user.role = data["role"]
        sync_admin_flag(user)
    if "ativo" in data and data["ativo"] is not None:
        user.ativo = data["ativo"]
    if "receber_alertas" in data and data["receber_alertas"] is not None:
        user.receber_alertas = data["receber_alertas"]
    if data.get("password"):
        user.hashed_password = hash_password(data["password"])

    user.atualizado_em = datetime.utcnow()
    session.add(user)
    session.add(
        montar_auditoria(
            usuario=current_admin,
            acao=AuditAction.usuario_atualizado,
            entidade="usuario",
            entidade_id=user.id,
            resumo=f"Atualizou usuário {user.nome} ({user.email}) role={user.role}",
        )
    )
    await session.commit()
    await session.refresh(user)
    return to_user_read(user)
