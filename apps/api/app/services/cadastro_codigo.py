import secrets

from fastapi import HTTPException, status
from pydantic import EmailStr
from redis.asyncio import Redis
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import get_settings
from app.core.redis import get_redis
from app.models.user import User
from app.services.email import send_email
from app.services.email_templates import montar_email_codigo_cadastro

CODIGO_TTL_SECONDS = 15 * 60
REENVIAR_COOLDOWN_SECONDS = 60
CODIGO_KEY = "cadastro:codigo:{email}"
COOLDOWN_KEY = "cadastro:codigo:cd:{email}"


def _gerar_codigo() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


async def enviar_codigo_cadastro(session: AsyncSession, email: EmailStr) -> dict[str, str | int]:
    email_norm = str(email).lower().strip()
    existing = await session.exec(select(User).where(User.email == email_norm))
    if existing.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com este e-mail",
        )

    redis = await get_redis()
    if redis is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível enviar o código agora. Tente novamente em instantes.",
        )

    if await redis.exists(COOLDOWN_KEY.format(email=email_norm)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Aguarde um minuto antes de solicitar um novo código.",
        )

    codigo = _gerar_codigo()
    await redis.set(CODIGO_KEY.format(email=email_norm), codigo, ex=CODIGO_TTL_SECONDS)
    await redis.set(
        COOLDOWN_KEY.format(email=email_norm),
        "1",
        ex=REENVIAR_COOLDOWN_SECONDS,
    )

    settings = get_settings()
    subject, text_body, html_body = montar_email_codigo_cadastro(
        settings=settings,
        codigo=codigo,
    )
    from_email, from_name = settings.from_convite()
    try:
        await send_email(
            settings=settings,
            to_email=email_norm,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            from_email=from_email,
            from_name=from_name,
        )
    except Exception as exc:
        await redis.delete(CODIGO_KEY.format(email=email_norm))
        await redis.delete(COOLDOWN_KEY.format(email=email_norm))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível enviar o e-mail com o código",
        ) from exc

    return {"ok": True, "expires_in_seconds": CODIGO_TTL_SECONDS}


async def validar_codigo_cadastro(redis: Redis, *, email: str, codigo: str) -> None:
    email_norm = email.lower().strip()
    codigo_norm = codigo.strip()
    if len(codigo_norm) != 6 or not codigo_norm.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe o código de 6 dígitos enviado por e-mail",
        )

    stored = await redis.get(CODIGO_KEY.format(email=email_norm))
    if stored is None or stored != codigo_norm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código inválido ou expirado. Solicite um novo código.",
        )


async def consumir_codigo_cadastro(redis: Redis, *, email: str) -> None:
    email_norm = email.lower().strip()
    await redis.delete(CODIGO_KEY.format(email=email_norm))
    await redis.delete(COOLDOWN_KEY.format(email=email_norm))
