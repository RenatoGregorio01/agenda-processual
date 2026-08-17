import hashlib
import secrets
from datetime import datetime, timedelta

from app.core.config import Settings
from app.core.timeutils import utc_now
from app.models.convite import Convite
from app.services.email import send_email
from app.services.email_templates import montar_email_convite


def generate_invite_token() -> str:
    return secrets.token_urlsafe(32)


def hash_invite_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def invite_status(convite: Convite, *, now: datetime | None = None) -> str:
    current = now or utc_now()
    if convite.used_at is not None:
        return "aceito"
    if convite.revoked_at is not None:
        return "revogado"
    expires = convite.expires_at
    if expires.tzinfo is not None:
        expires = expires.replace(tzinfo=None)
    if expires <= current:
        return "expirado"
    return "pendente"


def is_invite_usable(convite: Convite, *, now: datetime | None = None) -> bool:
    return invite_status(convite, now=now) == "pendente"


def build_invite_expiry(settings: Settings, *, now: datetime | None = None) -> datetime:
    current = now or utc_now()
    return current + timedelta(hours=settings.invite_expire_hours)


async def enviar_email_convite(
    *,
    settings: Settings,
    to_email: str,
    nome: str,
    token: str,
    convidado_por: str,
) -> None:
    subject, text_body, html_body = montar_email_convite(
        settings=settings,
        nome=nome,
        token=token,
        convidado_por=convidado_por,
    )
    from_email, from_name = settings.from_convite()
    await send_email(
        settings=settings,
        to_email=to_email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
        from_email=from_email,
        from_name=from_name,
    )
