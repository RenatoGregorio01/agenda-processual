from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_admin
from app.core.database import get_session
from app.core.security import hash_password
from app.models.audit_log import AuditAction
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.audit import montar_auditoria

router = APIRouter(dependencies=[Depends(get_current_admin)])


@router.get("", response_model=list[UserRead])
async def listar_usuarios(
    session: AsyncSession = Depends(get_session),
) -> list[User]:
    result = await session.exec(select(User).order_by(col(User.nome).asc()))
    return list(result.all())


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def criar_usuario(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_current_admin),
) -> User:
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
        is_admin=payload.is_admin,
        ativo=payload.ativo,
    )
    session.add(user)
    await session.flush()
    session.add(
        montar_auditoria(
            usuario=current_admin,
            acao=AuditAction.usuario_criado,
            entidade="usuario",
            entidade_id=user.id,
            resumo=f"Criou usuário {user.nome} ({user.email})",
        )
    )
    await session.commit()
    await session.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def atualizar_usuario(
    user_id: UUID,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_current_admin),
) -> User:
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
        if data.get("is_admin") is False:
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
    if "is_admin" in data and data["is_admin"] is not None:
        user.is_admin = data["is_admin"]
    if "ativo" in data and data["ativo"] is not None:
        user.ativo = data["ativo"]
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
            resumo=f"Atualizou usuário {user.nome} ({user.email})",
        )
    )
    await session.commit()
    await session.refresh(user)
    return user
