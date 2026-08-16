from datetime import date, timedelta

import pytest

from app.integrations.datajud.cnj import montar_cnj, so_digitos
from tests.e2e.conftest import auth_headers, login

pytestmark = pytest.mark.e2e


async def test_dois_prazos_mesmo_processo_ficam_na_ficha(e2e_client) -> None:
    client, _, _ = e2e_client
    token = await login(client)
    me = await client.get("/api/v1/auth/me", headers=auth_headers(token))
    admin_id = me.json()["id"]
    numero = montar_cnj("1111222", "2026", "4", "01", "0000")

    first = await client.post(
        "/api/v1/prazos",
        headers=auth_headers(token),
        json={
            "numero_processo": numero,
            "cliente": "Cliente Processo",
            "acao": "Contestação",
            "data_vencimento": (date.today() + timedelta(days=5)).isoformat(),
            "responsavel_id": admin_id,
        },
    )
    assert first.status_code == 201, first.text
    first_body = first.json()
    assert first_body["processo_id"] is not None
    processo_id = first_body["processo_id"]

    second = await client.post(
        "/api/v1/prazos",
        headers=auth_headers(token),
        json={
            "numero_processo": numero,
            "cliente": "Cliente Processo",
            "acao": "Juntar documentos",
            "data_vencimento": (date.today() + timedelta(days=10)).isoformat(),
            "responsavel_id": admin_id,
        },
    )
    assert second.status_code == 201, second.text
    assert second.json()["processo_id"] == processo_id

    detail = await client.get(
        f"/api/v1/processos/{processo_id}",
        headers=auth_headers(token),
    )
    assert detail.status_code == 200, detail.text
    body = detail.json()
    assert body["processo"]["numero_processo"] == numero
    assert body["processo"]["prazos_count"] == 2
    assert len(body["prazos"]) == 2
    assert len(body["historico"]) >= 2
    assert body["datajud"]["status"] == "nunca_consultado"
    assert body["datajud"]["andamentos"] == []

    by_numero = await client.get(
        f"/api/v1/processos/by-numero/{numero}",
        headers=auth_headers(token),
    )
    assert by_numero.status_code == 200
    assert by_numero.json()["processo"]["id"] == processo_id


async def test_lookup_processo_inexistente(e2e_client) -> None:
    client, _, _ = e2e_client
    token = await login(client)
    response = await client.get(
        "/api/v1/processos/by-numero/9999999-00.0000.0.00.0000",
        headers=auth_headers(token),
    )
    assert response.status_code == 404


async def test_validar_numero_processo(e2e_client) -> None:
    client, _, _ = e2e_client
    token = await login(client)
    numero = montar_cnj("0008888", "2026", "4", "01", "0000")

    incompleto = await client.get(
        "/api/v1/processos/validar",
        headers=auth_headers(token),
        params={"numero": "0008888"},
    )
    assert incompleto.status_code == 200
    body = incompleto.json()
    assert body["incompleto"] is True
    assert body["valido"] is None

    invalido = await client.get(
        "/api/v1/processos/validar",
        headers=auth_headers(token),
        params={"numero": "0001234-56.2024.4.01.0000"},
    )
    assert invalido.status_code == 200
    assert invalido.json()["valido"] is False

    valido = await client.get(
        "/api/v1/processos/validar",
        headers=auth_headers(token),
        params={"numero": numero},
    )
    assert valido.status_code == 200
    ok = valido.json()
    assert ok["valido"] is True
    assert ok["cadastrado"] is False
    assert ok["mascarado"] == numero
    assert ok["datajud"] is None

    me = await client.get("/api/v1/auth/me", headers=auth_headers(token))
    created = await client.post(
        "/api/v1/prazos",
        headers=auth_headers(token),
        json={
            "numero_processo": numero,
            "cliente": "Cliente Validar",
            "acao": "Contestação",
            "data_vencimento": (date.today() + timedelta(days=5)).isoformat(),
            "responsavel_id": me.json()["id"],
        },
    )
    assert created.status_code == 201, created.text

    cadastrado = await client.get(
        "/api/v1/processos/validar",
        headers=auth_headers(token),
        params={"numero": so_digitos(numero)},
    )
    assert cadastrado.status_code == 200
    found = cadastrado.json()
    assert found["valido"] is True
    assert found["cadastrado"] is True
    assert found["cliente"] == "Cliente Validar"
