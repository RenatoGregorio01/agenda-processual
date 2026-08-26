from datetime import date, timedelta
from unittest.mock import AsyncMock, patch

import pytest

from app.integrations.datajud.cnj import montar_cnj, so_digitos
from tests.e2e.conftest import auth_headers, login

pytestmark = pytest.mark.e2e


def _item_djen(numero: str, djen_id: int = 661000001) -> dict:
    return {
        "id": djen_id,
        "hash": "abcHash",
        "numero_processo": so_digitos(numero),
        "numeroprocessocommascara": numero,
        "siglaTribunal": "TJSP",
        "tipoComunicacao": "Intimação",
        "tipoDocumento": "Despacho",
        "nomeOrgao": "1ª Vara Cível",
        "data_disponibilizacao": date.today().isoformat(),
    }


async def test_sync_inbox_criar_prazo_e_dedupe(e2e_client) -> None:
    client, _, _ = e2e_client
    token = await login(client)
    headers = auth_headers(token)
    me = await client.get("/api/v1/auth/me", headers=headers)
    admin_id = me.json()["id"]
    numero = montar_cnj("3333444", "2026", "8", "26", "0100")

    created = await client.post(
        "/api/v1/prazos",
        headers=headers,
        json={
            "numero_processo": numero,
            "cliente": "Cliente DJEN",
            "acao": "Acompanhar",
            "data_vencimento": (date.today() + timedelta(days=10)).isoformat(),
            "responsavel_id": admin_id,
        },
    )
    assert created.status_code == 201, created.text
    processo_id = created.json()["processo_id"]

    with (
        patch("app.services.djen.get_redis", new=AsyncMock(return_value=None)),
        patch(
            "app.services.djen.consultar_comunicacoes",
            new=AsyncMock(return_value=[_item_djen(numero)]),
        ),
    ):
        sync = await client.post(
            f"/api/v1/processos/{processo_id}/djen/sync?force=true",
            headers=headers,
        )
    assert sync.status_code == 200, sync.text
    body = sync.json()
    assert body["ok"] is True
    assert body["criados"] == 1
    assert len(body["publicacoes"]) == 1
    publicacao_id = body["publicacoes"][0]["id"]
    assert body["publicacoes"][0]["status"] == "nova"
    assert body["publicacoes"][0]["vencimento_sugerido"] is not None

    inbox = await client.get("/api/v1/djen?status=nova", headers=headers)
    assert inbox.status_code == 200
    assert len(inbox.json()) == 1

    resumo = await client.get("/api/v1/djen/resumo", headers=headers)
    assert resumo.status_code == 200
    assert resumo.json()["novas"] == 1

    prazo = await client.post(
        "/api/v1/prazos",
        headers=headers,
        json={
            "numero_processo": numero,
            "cliente": "Cliente DJEN",
            "acao": "Intimação — Despacho",
            "data_disponibilizacao": date.today().isoformat(),
            "data_vencimento": (date.today() + timedelta(days=15)).isoformat(),
            "responsavel_id": admin_id,
            "djen_publicacao_id": publicacao_id,
        },
    )
    assert prazo.status_code == 201, prazo.text

    inbox_depois = await client.get("/api/v1/djen?status=nova", headers=headers)
    assert inbox_depois.json() == []
    criada = await client.get("/api/v1/djen?status=prazo_criado", headers=headers)
    assert len(criada.json()) == 1
    assert criada.json()[0]["prazo_id"] == prazo.json()["id"]

    with (
        patch("app.services.djen.get_redis", new=AsyncMock(return_value=None)),
        patch(
            "app.services.djen.consultar_comunicacoes",
            new=AsyncMock(return_value=[_item_djen(numero)]),
        ),
    ):
        sync2 = await client.post(
            f"/api/v1/processos/{processo_id}/djen/sync?force=true",
            headers=headers,
        )
    assert sync2.status_code == 200
    assert sync2.json()["criados"] == 0
    assert len(sync2.json()["publicacoes"]) == 1
    assert sync2.json()["publicacoes"][0]["status"] == "prazo_criado"


async def test_ignorar_publicacao_djen(e2e_client) -> None:
    client, _, _ = e2e_client
    token = await login(client)
    headers = auth_headers(token)
    me = await client.get("/api/v1/auth/me", headers=headers)
    admin_id = me.json()["id"]
    numero = montar_cnj("5555666", "2026", "8", "26", "0100")

    created = await client.post(
        "/api/v1/prazos",
        headers=headers,
        json={
            "numero_processo": numero,
            "cliente": "Cliente Ignorar",
            "acao": "Acompanhar",
            "data_vencimento": (date.today() + timedelta(days=5)).isoformat(),
            "responsavel_id": admin_id,
        },
    )
    processo_id = created.json()["processo_id"]

    with (
        patch("app.services.djen.get_redis", new=AsyncMock(return_value=None)),
        patch(
            "app.services.djen.consultar_comunicacoes",
            new=AsyncMock(return_value=[_item_djen(numero, djen_id=77)]),
        ),
    ):
        sync = await client.post(
            f"/api/v1/processos/{processo_id}/djen/sync?force=true",
            headers=headers,
        )
    publicacao_id = sync.json()["publicacoes"][0]["id"]

    ignored = await client.post(f"/api/v1/djen/{publicacao_id}/ignorar", headers=headers)
    assert ignored.status_code == 200, ignored.text
    assert ignored.json()["status"] == "ignorada"
    inbox = await client.get("/api/v1/djen?status=nova", headers=headers)
    assert inbox.json() == []


async def test_viewer_nao_pode_ignorar_nem_sync_escritorio(e2e_client) -> None:
    client, _, _ = e2e_client
    admin_token = await login(client)
    admin_headers = auth_headers(admin_token)
    created_user = await client.post(
        "/api/v1/usuarios",
        headers=admin_headers,
        json={
            "nome": "Viewer DJEN",
            "email": "viewer-djen@test.com",
            "password": "viewer1",
            "role": "viewer",
            "ativo": True,
            "receber_alertas": False,
        },
    )
    assert created_user.status_code == 201, created_user.text
    viewer_headers = auth_headers(
        await login(client, email="viewer-djen@test.com", password="viewer1")
    )

    inbox = await client.get("/api/v1/djen?status=nova", headers=viewer_headers)
    assert inbox.status_code == 200

    sync = await client.post("/api/v1/djen/sync", headers=viewer_headers)
    assert sync.status_code == 403

    ignorar = await client.post(
        "/api/v1/djen/00000000-0000-0000-0000-000000000001/ignorar",
        headers=viewer_headers,
    )
    assert ignorar.status_code in {403, 404}
