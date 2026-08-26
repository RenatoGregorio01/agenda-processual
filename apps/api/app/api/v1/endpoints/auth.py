from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_session
from app.core.security import create_access_token, verify_password
from app.models.audit_log import AuditAction
from app.models.conta import Conta
from app.models.escritorio import Escritorio
from app.models.user import User
from app.schemas.auth import (
    LoginEscritorio,
    LoginRequest,
    LoginResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    UserRead,
)
from app.services.audit import registrar_auditoria
from app.services.password_reset import redefinir_senha, solicitar_recuperacao
from app.services.users import to_user_read_with_escritorio

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> LoginResponse:
    result = await session.exec(select(Conta).where(Conta.email == payload.email.lower()))
    conta = result.first()
    # Compatibilidade para bancos de teste e instalações ainda sem a migração aplicada.
    if conta is None:
        legacy_result = await session.exec(
            select(User).where(User.email == payload.email.lower())
        )
        legacy_user = legacy_result.first()
        if legacy_user is not None and verify_password(
            payload.password, legacy_user.hashed_password
        ):
            conta = Conta(
                email=legacy_user.email,
                nome=legacy_user.nome,
                hashed_password=legacy_user.hashed_password,
                ativo=legacy_user.ativo,
            )
            session.add(conta)
            await session.flush()
            legacy_user.account_id = conta.id
            session.add(legacy_user)
            await session.commit()
    if conta is None or not conta.ativo or not verify_password(
        payload.password, conta.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
        )
    memberships = await session.exec(
        select(User).where(User.account_id == conta.id, User.ativo.is_(True))
    )
    users = memberships.all()
    if not users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo",
        )

    if payload.escritorio_id is None and len(users) > 1:
        escritorios: list[LoginEscritorio] = []
        for member in users:
            escritorio = await session.get(Escritorio, member.escritorio_id)
            if escritorio is not None:
                escritorios.append(LoginEscritorio(id=escritorio.id, nome=escritorio.nome))
        return LoginResponse(selecionar_escritorio=True, escritorios=escritorios)

    user = next((item for item in users if item.escritorio_id == payload.escritorio_id), None)
    if user is None:
        user = users[0] if len(users) == 1 else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Escritório não disponível",
        )

    await registrar_auditoria(
        session,
        usuario=user,
        acao=AuditAction.login,
        entidade="usuario",
        entidade_id=user.id,
        resumo=f"Login realizado ({user.email})",
    )

    token = create_access_token(
        user.id,
        extra={"email": user.email, "escritorio_id": str(user.escritorio_id)},
    )
    return LoginResponse(access_token=token)


@router.get("/me", response_model=UserRead)
async def me(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    return await to_user_read_with_escritorio(session, current_user)


@router.post("/recuperar-senha")
async def recuperar_senha(
    payload: PasswordResetRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, bool]:
    await solicitar_recuperacao(session, str(payload.email))
    return {"ok": True}


@router.post("/redefinir-senha/{token}")
async def confirmar_recuperacao_senha(
    token: str,
    payload: PasswordResetConfirm,
    session: AsyncSession = Depends(get_session),
) -> dict[str, bool]:
    await redefinir_senha(session, token, payload.password)
    return {"ok": True}
