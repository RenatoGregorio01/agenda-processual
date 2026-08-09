import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from app.core.config import Settings
from app.models.convite import Convite
from app.services.email import send_email


def generate_invite_token() -> str:
    return secrets.token_urlsafe(32)


def hash_invite_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def invite_status(convite: Convite, *, now: datetime | None = None) -> str:
    current = now or datetime.utcnow()
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
    current = now or datetime.now(UTC).replace(tzinfo=None)
    return current + timedelta(hours=settings.invite_expire_hours)


def montar_email_convite(
    *,
    settings: Settings,
    nome: str,
    token: str,
    convidado_por: str,
) -> tuple[str, str, str]:
    link = f"{settings.app_public_url.rstrip('/')}/convite/{token}"
    horas = settings.invite_expire_hours
    subject = "Convite para a Agenda Processual"
    text_body = (
        f"Olá, {nome}.\n\n"
        f"{convidado_por} convidou você para acessar a Agenda Processual.\n\n"
        f"Defina sua senha neste link (válido por {horas}h):\n{link}\n\n"
        "Se você não esperava este convite, ignore este e-mail.\n"
    )
    html_body = (
        f"<p>Olá, <strong>{nome}</strong>.</p>"
        f"<p><strong>{convidado_por}</strong> convidou você para acessar a "
        "Agenda Processual.</p>"
        f"<p><a href=\"{link}\">Definir senha e ativar acesso</a></p>"
        f"<p>O link é válido por {horas} horas.</p>"
        "<p>Se você não esperava este convite, ignore este e-mail.</p>"
    )
    return subject, text_body, html_body


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
    await send_email(
        settings=settings,
        to_email=to_email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )
