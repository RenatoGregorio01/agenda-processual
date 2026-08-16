from collections.abc import AsyncIterator
from datetime import date

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.router import api_router
from app.core.config import Settings
from app.core.database import get_session
from app.core.permissions import sync_admin_flag
from app.core.security import hash_password
from app.integrations.datajud.cnj import montar_cnj
from app.models import (  # noqa: F401
    AlertaEnvio,
    AuditLog,
    Convite,
    Escritorio,
    Feriado,
    Prazo,
    PrazoAlerta,
    Processo,
    User,
)
from app.models.user import Role
from tests.e2e.conftest import auth_headers, login

pytestmark = pytest.mark.e2e


@pytest_asyncio.fixture
async def two_tenant_client(
    e2e_settings: Settings,
) -> AsyncIterator[tuple[AsyncClient, dict[str, str]]]:
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

    ids: dict[str, str] = {}
    async with session_factory() as session:
        esc_a = Escritorio(nome="Alpha", slug="alpha")
        esc_b = Escritorio(nome="Beta", slug="beta")
        session.add(esc_a)
        session.add(esc_b)
        await session.flush()

        user_a = User(
            escritorio_id=esc_a.id,
            email="alpha@test.com",
            nome="Admin Alpha",
            hashed_password=hash_password("alpha123"),
            role=Role.admin,
            ativo=True,
        )
        user_b = User(
            escritorio_id=esc_b.id,
            email="beta@test.com",
            nome="Admin Beta",
            hashed_password=hash_password("beta1234"),
            role=Role.admin,
            ativo=True,
        )
        sync_admin_flag(user_a)
        sync_admin_flag(user_b)
        session.add(user_a)
        session.add(user_b)
        await session.flush()

        numero = montar_cnj("0008888", "2026", "4", "01", "0000")
        processo_b = Processo(
            escritorio_id=esc_b.id,
            numero_processo=numero,
            cliente="Cliente Beta",
        )
        session.add(processo_b)
        await session.flush()

        prazo_b = Prazo(
            escritorio_id=esc_b.id,
            processo_id=processo_b.id,
            numero_processo=numero,
            cliente="Cliente Beta",
            acao="Prazo secreto",
            data_vencimento=date.today(),
            responsavel=user_b.nome,
            responsavel_id=user_b.id,
        )
        feriado_b = Feriado(
            escritorio_id=esc_b.id,
            data=date(2026, 12, 25),
            nome="Natal Beta",
        )
        session.add(prazo_b)
        session.add(feriado_b)
        await session.commit()

        ids = {
            "prazo_b": str(prazo_b.id),
            "processo_b": str(processo_b.id),
            "feriado_b": str(feriado_b.id),
            "numero": numero,
        }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, ids

    await engine.dispose()


async def test_user_nao_le_prazo_processo_nem_feriado_de_outro_escritorio(
    two_tenant_client,
) -> None:
    client, ids = two_tenant_client
    token_a = await login(client, email="alpha@test.com", password="alpha123")
    headers = auth_headers(token_a)

    me = await client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["escritorio_nome"] == "Alpha"

    prazo = await client.get(f"/api/v1/prazos/{ids['prazo_b']}", headers=headers)
    assert prazo.status_code == 404

    listed = await client.get("/api/v1/prazos", headers=headers)
    assert listed.status_code == 200
    assert listed.json() == []

    processo = await client.get(f"/api/v1/processos/{ids['processo_b']}", headers=headers)
    assert processo.status_code == 404

    feriados = await client.get("/api/v1/feriados", headers=headers)
    assert feriados.status_code == 200
    assert feriados.json() == []

    feriado = await client.patch(
        f"/api/v1/feriados/{ids['feriado_b']}",
        headers=headers,
        json={"nome": "Hack"},
    )
    assert feriado.status_code == 404


async def test_mesmo_cnj_pode_existir_em_dois_escritorios(two_tenant_client) -> None:
    client, ids = two_tenant_client
    token_a = await login(client, email="alpha@test.com", password="alpha123")
    me = await client.get("/api/v1/auth/me", headers=auth_headers(token_a))
    admin_id = me.json()["id"]

    created = await client.post(
        "/api/v1/prazos",
        headers=auth_headers(token_a),
        json={
            "numero_processo": ids["numero"],
            "cliente": "Cliente Alpha",
            "acao": "Prazo Alpha",
            "data_vencimento": date.today().isoformat(),
            "responsavel_id": admin_id,
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["cliente"] == "Cliente Alpha"

    token_b = await login(client, email="beta@test.com", password="beta1234")
    listed_b = await client.get("/api/v1/prazos", headers=auth_headers(token_b))
    assert listed_b.status_code == 200
    assert any(item["id"] == ids["prazo_b"] for item in listed_b.json())
    assert all(item["cliente"] != "Cliente Alpha" for item in listed_b.json())
