from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.oab import slugify, validate_advogado_oab
from app.core.permissions import sync_admin_flag
from app.core.security import create_access_token, hash_password
from app.models.escritorio import Escritorio
from app.models.user import Role, User
from app.schemas.auth import TokenResponse
from app.schemas.cadastro import CadastroEscritorioRequest


async def _unique_slug(session: AsyncSession, base: str) -> str:
    slug = slugify(base)
    candidate = slug
    suffix = 2
    while True:
        existing = await session.exec(select(Escritorio).where(Escritorio.slug == candidate))
        if existing.first() is None:
            return candidate
        candidate = f"{slug}-{suffix}"[:80]
        suffix += 1


async def cadastrar_escritorio(
    session: AsyncSession,
    payload: CadastroEscritorioRequest,
) -> TokenResponse:
    email = str(payload.email).lower()
    existing_user = await session.exec(select(User).where(User.email == email))
    if existing_user.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com este e-mail",
        )

    oab_numero, oab_uf = validate_advogado_oab(
        eh_advogado=payload.eh_advogado,
        oab_numero=payload.oab_numero,
        oab_uf=payload.oab_uf,
    )

    slug_base = payload.slug.strip() if payload.slug else payload.escritorio_nome
    slug = await _unique_slug(session, slug_base)

    escritorio = Escritorio(
        nome=payload.escritorio_nome.strip(),
        slug=slug,
    )
    session.add(escritorio)
    await session.flush()

    user = User(
        escritorio_id=escritorio.id,
        email=email,
        nome=payload.nome.strip(),
        hashed_password=hash_password(payload.password),
        role=Role.admin,
        ativo=True,
        receber_alertas=False,
        eh_advogado=payload.eh_advogado,
        oab_numero=oab_numero,
        oab_uf=oab_uf,
    )
    sync_admin_flag(user)
    session.add(user)
    await session.commit()

    return TokenResponse(
        access_token=create_access_token(
            user.id,
            extra={"email": user.email, "escritorio_id": str(user.escritorio_id)},
        )
    )
