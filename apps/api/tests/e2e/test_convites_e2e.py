import pytest

from tests.e2e.conftest import auth_headers, extract_invite_token, login

pytestmark = pytest.mark.e2e


async def test_fluxo_completo_convite_por_email(e2e_client) -> None:
    client, sent_emails, _ = e2e_client
    admin_token = await login(client)

    create = await client.post(
        "/api/v1/convites",
        headers=auth_headers(admin_token),
        json={
            "nome": "Ana Advogada",
            "email": "ana@escritorio.com",
            "role": "editor",
            "receber_alertas": True,
        },
    )
    assert create.status_code == 201, create.text
    convite = create.json()
    assert convite["status"] == "pendente"
    assert convite["email"] == "ana@escritorio.com"
    assert len(sent_emails) == 1
    assert sent_emails[0]["to"] == "ana@escritorio.com"

    token = sent_emails[0]["token"]
    assert token == extract_invite_token(sent_emails[0]["text"])

    public = await client.get(f"/api/v1/convites/aceitar/{token}")
    assert public.status_code == 200
    assert public.json()["nome"] == "Ana Advogada"

    accept = await client.post(
        f"/api/v1/convites/aceitar/{token}",
        json={"password": "senha456"},
    )
    assert accept.status_code == 200, accept.text
    user_token = accept.json()["access_token"]

    me = await client.get("/api/v1/auth/me", headers=auth_headers(user_token))
    assert me.status_code == 200
    assert me.json()["email"] == "ana@escritorio.com"
    assert me.json()["role"] == "editor"

    login_again = await login(client, email="ana@escritorio.com", password="senha456")
    assert login_again

    reused = await client.post(
        f"/api/v1/convites/aceitar/{token}",
        json={"password": "outra789"},
    )
    assert reused.status_code == 404


async def test_convite_duplicado_pendente(e2e_client) -> None:
    client, _, _ = e2e_client
    admin_token = await login(client)
    payload = {
        "nome": "Bruno",
        "email": "bruno@escritorio.com",
        "role": "viewer",
        "receber_alertas": False,
    }

    first = await client.post(
        "/api/v1/convites",
        headers=auth_headers(admin_token),
        json=payload,
    )
    assert first.status_code == 201

    second = await client.post(
        "/api/v1/convites",
        headers=auth_headers(admin_token),
        json=payload,
    )
    assert second.status_code == 409


async def test_reenviar_e_revogar_convite(e2e_client) -> None:
    client, sent_emails, _ = e2e_client
    admin_token = await login(client)

    created = await client.post(
        "/api/v1/convites",
        headers=auth_headers(admin_token),
        json={
            "nome": "Carla",
            "email": "carla@escritorio.com",
            "role": "viewer",
            "receber_alertas": True,
        },
    )
    assert created.status_code == 201
    convite_id = created.json()["id"]
    first_token = sent_emails[0]["token"]

    resend = await client.post(
        f"/api/v1/convites/{convite_id}/reenviar",
        headers=auth_headers(admin_token),
    )
    assert resend.status_code == 200
    assert len(sent_emails) == 2
    second_token = sent_emails[1]["token"]
    assert second_token != first_token

    old = await client.get(f"/api/v1/convites/aceitar/{first_token}")
    assert old.status_code == 404

    revoke = await client.delete(
        f"/api/v1/convites/{convite_id}",
        headers=auth_headers(admin_token),
    )
    assert revoke.status_code == 200
    assert revoke.json()["status"] == "revogado"

    new = await client.get(f"/api/v1/convites/aceitar/{second_token}")
    assert new.status_code == 404
