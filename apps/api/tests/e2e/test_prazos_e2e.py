from datetime import date, timedelta

import pytest

from app.integrations.datajud.cnj import montar_cnj
from tests.e2e.conftest import auth_headers, login

pytestmark = pytest.mark.e2e


async def test_criar_listar_cumprir_prazo(e2e_client) -> None:
    client, _, _ = e2e_client
    token = await login(client)

    me = await client.get("/api/v1/auth/me", headers=auth_headers(token))
    admin_id = me.json()["id"]
    vencimento = (date.today() + timedelta(days=5)).isoformat()

    created = await client.post(
        "/api/v1/prazos",
        headers=auth_headers(token),
        json={
            "numero_processo": montar_cnj("0001111", "2026", "4", "01", "0000"),
            "cliente": "Cliente E2E",
            "acao": "Protocolar contestação",
            "data_disponibilizacao": date.today().isoformat(),
            "data_vencimento": vencimento,
            "responsavel_id": admin_id,
        },
    )
    assert created.status_code == 201, created.text
    prazo = created.json()
    prazo_id = prazo["id"]
    assert prazo["status"] == "pendente"
    assert prazo["cliente"] == "Cliente E2E"
    assert [item["dias_antes"] for item in prazo["alertas"]] == [3, 1]

    patched = await client.patch(
        f"/api/v1/prazos/{prazo_id}",
        headers=auth_headers(token),
        json={"alertas": [7, 1]},
    )
    assert patched.status_code == 200, patched.text
    assert [item["dias_antes"] for item in patched.json()["alertas"]] == [7, 1]

    listed = await client.get("/api/v1/prazos", headers=auth_headers(token))
    assert listed.status_code == 200
    assert any(item["id"] == prazo_id for item in listed.json())

    search = await client.get(
        "/api/v1/prazos",
        headers=auth_headers(token),
        params={"q": "Cliente E2E"},
    )
    assert search.status_code == 200
    assert len(search.json()) >= 1

    fulfill = await client.post(
        f"/api/v1/prazos/{prazo_id}/cumprir",
        headers=auth_headers(token),
    )
    assert fulfill.status_code == 200
    assert fulfill.json()["status"] == "cumprido"


async def test_viewer_nao_pode_criar_prazo(e2e_client) -> None:
    client, _, _ = e2e_client
    admin_token = await login(client)

    created_user = await client.post(
        "/api/v1/usuarios",
        headers=auth_headers(admin_token),
        json={
            "nome": "Viewer E2E",
            "email": "viewer@test.com",
            "password": "viewer1",
            "role": "viewer",
            "ativo": True,
            "receber_alertas": False,
        },
    )
    assert created_user.status_code == 201, created_user.text

    viewer_token = await login(client, email="viewer@test.com", password="viewer1")
    me = await client.get("/api/v1/auth/me", headers=auth_headers(viewer_token))
    admin_me = await client.get("/api/v1/auth/me", headers=auth_headers(admin_token))

    response = await client.post(
        "/api/v1/prazos",
        headers=auth_headers(viewer_token),
        json={
            "numero_processo": montar_cnj("0002222", "2026", "4", "01", "0000"),
            "cliente": "Bloqueado",
            "acao": "Não deve criar",
            "data_vencimento": (date.today() + timedelta(days=2)).isoformat(),
            "responsavel_id": admin_me.json()["id"],
        },
    )
    assert response.status_code == 403
    assert me.json()["role"] == "viewer"


async def test_criar_prazo_rejeita_cnj_invalido(e2e_client) -> None:
    client, _, _ = e2e_client
    token = await login(client)
    me = await client.get("/api/v1/auth/me", headers=auth_headers(token))

    response = await client.post(
        "/api/v1/prazos",
        headers=auth_headers(token),
        json={
            "numero_processo": "0001234-56.2024.4.01.0000",
            "cliente": "Inválido",
            "acao": "Não deve criar",
            "data_vencimento": (date.today() + timedelta(days=2)).isoformat(),
            "responsavel_id": me.json()["id"],
        },
    )
    assert response.status_code == 422
