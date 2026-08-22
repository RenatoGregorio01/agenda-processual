import pytest

from tests.e2e.conftest import auth_headers, login

pytestmark = pytest.mark.e2e


async def test_purge_auditoria_admin(e2e_client) -> None:
    client, _, _ = e2e_client
    token = await login(client)
    response = await client.post(
        "/api/v1/auditoria/purge",
        headers=auth_headers(token),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["apagados"] == 0
    assert body["retention_days"] == 365


async def test_purge_auditoria_exige_auth(e2e_client) -> None:
    client, _, _ = e2e_client
    response = await client.post("/api/v1/auditoria/purge")
    assert response.status_code == 401
