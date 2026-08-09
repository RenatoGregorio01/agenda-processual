from __future__ import annotations

import re
from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.database import get_session
from app.core.seed import seed_admin_user
from app.models import AlertaEnvio, AuditLog, Convite, Feriado, Prazo, User  # noqa: F401
from app.services.convites import montar_email_convite


@pytest.fixture
def e2e_settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    monkeypatch.setenv("JWT_SECRET", "test-secret-for-e2e-tests-32bytes!!")
    monkeypatch.setenv("SEED_ADMIN_EMAIL", "admin@test.com")
    monkeypatch.setenv("SEED_ADMIN_PASSWORD", "admin123")
    monkeypatch.setenv("SEED_ADMIN_NAME", "Admin Test")
    monkeypatch.setenv("APP_PUBLIC_URL", "http://localhost:3000")
    monkeypatch.setenv("INVITE_EXPIRE_HOURS", "72")
    monkeypatch.setenv("ALERTAS_ENABLED", "false")
    get_settings.cache_clear()
    settings = get_settings()
    yield settings
    get_settings.cache_clear()


@pytest_asyncio.fixture
async def e2e_client(
    e2e_settings: Settings,
) -> AsyncIterator[tuple[AsyncClient, list[dict[str, Any]], Settings]]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app = FastAPI()
    app.include_router(api_router, prefix=e2e_settings.api_v1_prefix)
    app.dependency_overrides[get_session] = override_get_session

    async with session_factory() as session:
        await seed_admin_user(session, e2e_settings)

    sent_emails: list[dict[str, Any]] = []

    async def fake_enviar_email_convite(
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
        sent_emails.append(
            {
                "to": to_email,
                "subject": subject,
                "text": text_body,
                "html": html_body,
                "token": token,
            }
        )

    with patch(
        "app.api.v1.endpoints.convites.enviar_email_convite",
        new=AsyncMock(side_effect=fake_enviar_email_convite),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client, sent_emails, e2e_settings

    await engine.dispose()


async def login(
    client: AsyncClient,
    *,
    email: str = "admin@test.com",
    password: str = "admin123",
) -> str:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def extract_invite_token(email_text: str) -> str:
    match = re.search(r"/convite/([A-Za-z0-9_-]+)", email_text)
    assert match is not None, f"Token não encontrado no e-mail: {email_text}"
    return match.group(1)
