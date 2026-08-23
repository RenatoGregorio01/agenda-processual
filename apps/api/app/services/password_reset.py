import hashlib
import secrets
from datetime import timedelta

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import get_settings
from app.core.security import hash_password
from app.core.timeutils import utc_now
from app.models.conta import Conta
from app.models.password_reset import PasswordReset
from app.models.user import User
from app.services.email import send_email
from app.services.email_templates import montar_email_recuperacao_senha


def _token() -> str:
    return secrets.token_urlsafe(32)


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def solicitar_recuperacao(session: AsyncSession, email: str) -> None:
    conta = await session.exec(select(Conta).where(Conta.email == email.lower().strip()))
    account = conta.first()
    if account is None or not account.ativo:
        return

    settings = get_settings()
    token = _token()
    reset = PasswordReset(
        account_id=account.id,
        token_hash=_hash(token),
        expires_at=utc_now() + timedelta(minutes=settings.password_reset_expire_minutes),
    )
    session.add(reset)
    await session.commit()

    subject, text_body, html_body = montar_email_recuperacao_senha(settings=settings, token=token)
    try:
        await send_email(
            settings=settings,
            to_email=account.email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
        )
    except Exception:
        await session.delete(reset)
        await session.commit()


async def redefinir_senha(session: AsyncSession, token: str, password: str) -> None:
    result = await session.exec(
        select(PasswordReset).where(PasswordReset.token_hash == _hash(token))
    )
    reset = result.first()
    now = utc_now()
    if reset is None or reset.used_at is not None or reset.expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este link é inválido ou expirou. Solicite uma nova recuperação.",
        )

    account = await session.get(Conta, reset.account_id)
    if account is None or not account.ativo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Conta indisponível")

    hashed = hash_password(password)
    account.hashed_password = hashed
    account.atualizado_em = now
    reset.used_at = now
    session.add(account)
    session.add(reset)
    memberships = await session.exec(select(User).where(User.account_id == account.id))
    for user in memberships.all():
        user.hashed_password = hashed
        user.atualizado_em = now
        session.add(user)
    await session.commit()
