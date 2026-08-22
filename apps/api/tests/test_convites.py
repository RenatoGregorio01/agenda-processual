from datetime import datetime, timedelta
from uuid import uuid4

from app.core.config import Settings
from app.models.convite import Convite
from app.models.user import Role
from app.services.convites import (
    build_invite_expiry,
    generate_invite_token,
    hash_invite_token,
    invite_status,
    is_invite_usable,
    montar_email_convite,
)


def test_token_hash_is_stable() -> None:
    token = "abc123"
    assert hash_invite_token(token) == hash_invite_token(token)
    assert len(hash_invite_token(token)) == 64


def test_generate_invite_token_unique() -> None:
    assert generate_invite_token() != generate_invite_token()


def test_invite_status_pendente_expirado_aceito() -> None:
    agora = datetime(2026, 8, 9, 12, 0, 0)
    tenant = uuid4()
    pendente = Convite(
        escritorio_id=tenant,
        email="a@b.com",
        nome="A",
        role=Role.editor,
        token_hash="x",
        expires_at=agora + timedelta(hours=1),
        invited_by_id=uuid4(),
    )
    assert invite_status(pendente, now=agora) == "pendente"
    assert is_invite_usable(pendente, now=agora)

    expirado = Convite(
        escritorio_id=tenant,
        email="a@b.com",
        nome="A",
        role=Role.editor,
        token_hash="y",
        expires_at=agora - timedelta(minutes=1),
        invited_by_id=uuid4(),
    )
    assert invite_status(expirado, now=agora) == "expirado"
    assert not is_invite_usable(expirado, now=agora)

    aceito = Convite(
        escritorio_id=tenant,
        email="a@b.com",
        nome="A",
        role=Role.editor,
        token_hash="z",
        expires_at=agora + timedelta(hours=1),
        used_at=agora,
        invited_by_id=uuid4(),
    )
    assert invite_status(aceito, now=agora) == "aceito"


def test_build_invite_expiry_uses_settings() -> None:
    settings = Settings(invite_expire_hours=48)
    now = datetime(2026, 8, 9, 10, 0, 0)
    assert build_invite_expiry(settings, now=now) == now + timedelta(hours=48)


def test_montar_email_convite_usa_app_public_url() -> None:
    settings = Settings(app_public_url="http://localhost:3000", invite_expire_hours=72)
    subject, text, html = montar_email_convite(
        settings=settings,
        nome="Ana",
        token="tok123",
        convidado_por="Verônica",
    )
    assert "Convite" in subject
    assert "http://localhost:3000/convite/tok123" in text
    assert "http://localhost:3000/convite/tok123" in html
    assert "Ana" in text
    assert "Verônica" in text
    assert "Definir senha e ativar acesso" in html
    assert "Agenda Processual" in html


def test_montar_email_convite_escapa_html() -> None:
    settings = Settings(app_public_url="http://localhost:3000")
    _, _, html = montar_email_convite(
        settings=settings,
        nome="<script>x</script>",
        token="tok",
        convidado_por="Verônica",
    )
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "Verônica" in html
