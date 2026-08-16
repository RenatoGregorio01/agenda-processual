import pytest

from tests.e2e.conftest import auth_headers, login

pytestmark = pytest.mark.e2e


async def test_login_e_me(e2e_client) -> None:
    client, _, _ = e2e_client
    token = await login(client)

    me = await client.get("/api/v1/auth/me", headers=auth_headers(token))
    assert me.status_code == 200
    body = me.json()
    assert body["email"] == "admin@test.com"
    assert body["role"] == "admin"
    assert body["escritorio_nome"]
    assert body["escritorio_id"]
    assert "usuarios_gerenciar" in body["permissions"]


async def test_login_invalido(e2e_client) -> None:
    client, _, _ = e2e_client
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "errada1"},
    )
    assert response.status_code == 401


async def test_rota_protegida_sem_token(e2e_client) -> None:
    client, _, _ = e2e_client
    response = await client.get("/api/v1/prazos")
    assert response.status_code == 401
