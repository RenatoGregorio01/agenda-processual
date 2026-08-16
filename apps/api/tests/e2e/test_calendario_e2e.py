from datetime import date

import pytest

from tests.e2e.conftest import auth_headers, login

pytestmark = pytest.mark.e2e


async def test_feriado_e_calculo_dias_uteis(e2e_client) -> None:
    client, _, _ = e2e_client
    token = await login(client)

    # sexta 2026-09-04; segunda 2026-09-07 feriado → +1 útil = terça 2026-09-08
    feriado = await client.post(
        "/api/v1/feriados",
        headers=auth_headers(token),
        json={"data": "2026-09-07", "nome": "Independência"},
    )
    assert feriado.status_code == 201, feriado.text

    calc = await client.post(
        "/api/v1/calendario/calcular-vencimento",
        headers=auth_headers(token),
        json={"data_base": "2026-09-04", "dias": 1},
    )
    assert calc.status_code == 200, calc.text
    body = calc.json()
    assert body["data_vencimento"] == "2026-09-08"
    assert body["feriados_no_intervalo"] == [
        {"data": "2026-09-07", "nome": "Independência"}
    ]

    listed = await client.get("/api/v1/feriados", headers=auth_headers(token))
    assert listed.status_code == 200
    assert any(item["data"] == "2026-09-07" for item in listed.json())


async def test_calculo_pula_fim_de_semana(e2e_client) -> None:
    client, _, _ = e2e_client
    token = await login(client)

    calc = await client.post(
        "/api/v1/calendario/calcular-vencimento",
        headers=auth_headers(token),
        json={"data_base": "2026-08-07", "dias": 1},  # sexta
    )
    assert calc.status_code == 200
    assert calc.json()["data_vencimento"] == "2026-08-10"  # segunda


async def test_feriado_duplicado(e2e_client) -> None:
    client, _, _ = e2e_client
    token = await login(client)
    payload = {"data": date(2026, 12, 25).isoformat(), "nome": "Natal"}

    first = await client.post(
        "/api/v1/feriados",
        headers=auth_headers(token),
        json=payload,
    )
    assert first.status_code == 201

    second = await client.post(
        "/api/v1/feriados",
        headers=auth_headers(token),
        json=payload,
    )
    assert second.status_code == 409
