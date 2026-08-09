from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_admin
from app.core.config import get_settings
from app.core.database import get_session
from app.core.permissions import sync_admin_flag
from app.core.security import create_access_token, hash_password
from app.core.timeutils import utc_now
from app.models.audit_log import AuditAction
from app.models.convite import Convite
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.schemas.convite import ConviteAccept, ConviteCreate, ConvitePublic, ConviteRead
from app.services.audit import montar_auditoria
from app.services.convites import (
    build_invite_expiry,
    enviar_email_convite,
    generate_invite_token,
    hash_invite_token,
    invite_status,
    is_invite_usable,
)

router = APIRouter()


def _to_read(convite: Convite) -> ConviteRead:
    return ConviteRead(
        id=convite.id,
        email=convite.email,
        nome=convite.nome,
        role=convite.role,
        receber_alertas=convite.receber_alertas,
        expires_at=convite.expires_at,
        used_at=convite.used_at,
        revoked_at=convite.revoked_at,
        invited_by_id=convite.invited_by_id,
        criado_em=convite.criado_em,
        status=invite_status(convite),
    )


async def _get_usable_convite(session: AsyncSession, token: str) -> Convite:
    token_hash = hash_invite_token(token)
    result = await session.exec(select(Convite).where(Convite.token_hash == token_hash))
    convite = result.first()
    if convite is None or not is_invite_usable(convite):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Convite inválido ou expirado",
        )
    return convite


@router.get("/aceitar/{token}", response_model=ConvitePublic)
async def consultar_convite(
    token: str,
    session: AsyncSession = Depends(get_session),
) -> ConvitePublic:
    convite = await _get_usable_convite(session, token)
    return ConvitePublic(
        email=convite.email,
        nome=convite.nome,
        role=convite.role,
        expires_at=convite.expires_at,
    )


@router.post("/aceitar/{token}", response_model=TokenResponse)
async def aceitar_convite(
    token: str,
    payload: ConviteAccept,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    convite = await _get_usable_convite(session, token)

    existing_user = await session.exec(select(User).where(User.email == convite.email))
    if existing_user.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com este e-mail",
        )

    user = User(
        email=convite.email,
        nome=convite.nome,
        hashed_password=hash_password(payload.password),
        role=convite.role,
        ativo=True,
        receber_alertas=convite.receber_alertas,
    )
    sync_admin_flag(user)
    session.add(user)
    await session.flush()

    convite.used_at = utc_now()
    session.add(convite)
    session.add(
        montar_auditoria(
            usuario=user,
            acao=AuditAction.convite_aceito,
            entidade="usuario",
            entidade_id=user.id,
            resumo=f"Aceitou convite e criou conta {user.nome} ({user.email})",
        )
    )
    await session.commit()

    return TokenResponse(access_token=create_access_token(user.id, extra={"email": user.email}))


@router.get("", response_model=list[ConviteRead], dependencies=[Depends(get_current_admin)])
async def listar_convites(
    session: AsyncSession = Depends(get_session),
) -> list[ConviteRead]:
    result = await session.exec(select(Convite).order_by(col(Convite.criado_em).desc()))
    return [_to_read(item) for item in result.all()]


@router.post(
    "",
    response_model=ConviteRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
)
async def criar_convite(
    payload: ConviteCreate,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_current_admin),
) -> ConviteRead:
    settings = get_settings()
    email = str(payload.email).lower()

    existing_user = await session.exec(select(User).where(User.email == email))
    if existing_user.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com este e-mail",
        )

    pending = await session.exec(
        select(Convite).where(
            Convite.email == email,
            col(Convite.used_at).is_(None),
            col(Convite.revoked_at).is_(None),
        )
    )
    for item in pending.all():
        if is_invite_usable(item):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um convite pendente para este e-mail",
            )

    token = generate_invite_token()
    convite = Convite(
        email=email,
        nome=payload.nome.strip(),
        role=payload.role,
        receber_alertas=payload.receber_alertas,
        token_hash=hash_invite_token(token),
        expires_at=build_invite_expiry(settings),
        invited_by_id=current_admin.id,
    )
    session.add(convite)
    await session.flush()

    try:
        await enviar_email_convite(
            settings=settings,
            to_email=email,
            nome=convite.nome,
            token=token,
            convidado_por=current_admin.nome,
        )
    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível enviar o e-mail de convite",
        ) from exc

    session.add(
        montar_auditoria(
            usuario=current_admin,
            acao=AuditAction.convite_criado,
            entidade="convite",
            entidade_id=convite.id,
            resumo=f"Convidou {convite.nome} ({convite.email}) como {convite.role}",
        )
    )
    await session.commit()
    await session.refresh(convite)
    return _to_read(convite)


@router.post(
    "/{convite_id}/reenviar",
    response_model=ConviteRead,
    dependencies=[Depends(get_current_admin)],
)
async def reenviar_convite(
    convite_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_current_admin),
) -> ConviteRead:
    settings = get_settings()
    convite = await session.get(Convite, convite_id)
    if convite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convite não encontrado")
    if convite.used_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este convite já foi aceito",
        )

    existing_user = await session.exec(select(User).where(User.email == convite.email))
    if existing_user.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com este e-mail",
        )

    token = generate_invite_token()
    convite.token_hash = hash_invite_token(token)
    convite.expires_at = build_invite_expiry(settings)
    convite.revoked_at = None
    session.add(convite)

    try:
        await enviar_email_convite(
            settings=settings,
            to_email=convite.email,
            nome=convite.nome,
            token=token,
            convidado_por=current_admin.nome,
        )
    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível reenviar o e-mail de convite",
        ) from exc

    session.add(
        montar_auditoria(
            usuario=current_admin,
            acao=AuditAction.convite_reenviado,
            entidade="convite",
            entidade_id=convite.id,
            resumo=f"Reenviou convite para {convite.nome} ({convite.email})",
        )
    )
    await session.commit()
    await session.refresh(convite)
    return _to_read(convite)


@router.delete(
    "/{convite_id}",
    response_model=ConviteRead,
    dependencies=[Depends(get_current_admin)],
)
async def revogar_convite(
    convite_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_current_admin),
) -> ConviteRead:
    convite = await session.get(Convite, convite_id)
    if convite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convite não encontrado")
    if convite.used_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este convite já foi aceito",
        )
    if convite.revoked_at is not None:
        return _to_read(convite)

    convite.revoked_at = utc_now()
    session.add(convite)
    session.add(
        montar_auditoria(
            usuario=current_admin,
            acao=AuditAction.convite_revogado,
            entidade="convite",
            entidade_id=convite.id,
            resumo=f"Revogou convite de {convite.nome} ({convite.email})",
        )
    )
    await session.commit()
    await session.refresh(convite)
    return _to_read(convite)
