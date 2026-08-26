from datetime import date, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.integrations.datajud.client import datajud_url
from app.integrations.datajud.cnj import (
    CnjError,
    alias_do_cnj,
    mascarar_cnj,
    montar_cnj,
    so_digitos,
    validar_cnj,
    verificar_dv,
)
from app.schemas.prazo import PrazoCreate
from app.services.datajud import _payload_from_source, _payload_from_sources


def test_so_digitos_remove_mascara() -> None:
    assert so_digitos("0001234-56.2024.8.26.0100") == "00012345620248260100"


@pytest.mark.parametrize(
    ("numero", "alias"),
    [
        ("0001234-56.2024.8.26.0100", "tjsp"),
        ("0001234-56.2024.8.19.0001", "tjrj"),
        ("0001234-56.2024.4.01.0000", "trf1"),
        ("0001234-56.2024.5.02.0001", "trt2"),
        ("0001234-56.2024.5.00.0000", "tst"),
        ("0001234-56.2024.3.00.0000", "stj"),
        ("0001234-56.2024.6.26.0000", "tre-sp"),
        ("0001234-56.2024.9.26.0000", "tjmsp"),
    ],
)
def test_alias_do_cnj(numero: str, alias: str) -> None:
    digitos, got = alias_do_cnj(numero)
    assert len(digitos) == 20
    assert got == alias


def test_alias_rejeita_stf() -> None:
    with pytest.raises(CnjError, match="STF"):
        alias_do_cnj("0001234-56.2024.1.00.0000")


def test_alias_rejeita_tamanho_invalido() -> None:
    with pytest.raises(CnjError, match="20 dígitos"):
        alias_do_cnj("123")


def test_datajud_url() -> None:
    assert datajud_url("tjsp").endswith("/api_publica_tjsp/_search")


def test_payload_ordena_andamentos_recentes() -> None:
    source = {
        "tribunal": "TJSP",
        "grau": "G1",
        "classe": {"nome": "Procedimento Comum Cível"},
        "orgaoJulgador": {"nome": "1ª Vara Cível"},
        "movimentos": [
            {"dataHora": "2024-01-01T10:00:00", "codigo": 1, "nome": "Distribuição"},
            {
                "dataHora": "2024-03-10T12:00:00",
                "codigo": 2,
                "nome": "Juntada de petição",
                "complementosTabelados": [
                    {
                        "codigo": 19,
                        "descricao": "tipo_de_peticao",
                        "valor": 57,
                        "nome": "Petição (outras)",
                    }
                ],
                "orgaoJulgador": {"nome": "1ª Vara Cível"},
            },
        ],
    }
    payload = _payload_from_source("tjsp", source)
    assert payload["status"] == "ok"
    assert payload["andamentos"][0]["nome"] == "Juntada de petição"
    assert payload["andamentos"][0]["data_hora"] == datetime(2024, 3, 10, 12, 0, 0)
    assert payload["andamentos"][0]["complemento"] == "Petição (outras)"
    assert payload["andamentos"][0]["orgao"] == "1ª Vara Cível"


def test_payload_sem_hits() -> None:
    payload = _payload_from_source("tjsp", None)
    assert payload["status"] == "indisponivel"
    assert payload["andamentos"] == []


def test_payload_junta_graus_e_prioriza_o_mais_recente() -> None:
    g2 = {
        "tribunal": "TRT5",
        "grau": "G2",
        "classe": {"nome": "Recurso Ordinário Trabalhista"},
        "orgaoJulgador": {"nome": "Gab. Des. Margareth"},
        "dataHoraUltimaAtualizacao": "2026-02-27T08:55:00",
        "movimentos": [
            {"dataHora": "2026-02-27T08:55:00", "codigo": 1, "nome": "Baixa Definitiva"},
            {"dataHora": "2026-02-26T20:02:00", "codigo": 2, "nome": "Recebimento"},
        ],
    }
    g1 = {
        "tribunal": "TRT5",
        "grau": "G1",
        "classe": {"nome": "Ação Trabalhista"},
        "orgaoJulgador": {"nome": "34ª Vara do Trabalho de Salvador"},
        "dataHoraUltimaAtualizacao": "2026-08-18T14:21:00",
        "movimentos": [
            {"dataHora": "2026-08-18T14:21:00", "codigo": 3, "nome": "Juntada de Petição"},
            {"dataHora": "2026-07-23T04:41:00", "codigo": 4, "nome": "Expedição de intimação"},
        ],
    }
    payload = _payload_from_sources("trt5", [g2, g1])
    assert payload["status"] == "ok"
    assert payload["grau"] == "G1 + G2"
    assert payload["classe"] == "Ação Trabalhista"
    assert payload["orgao"] == "34ª Vara do Trabalho de Salvador"
    assert payload["andamentos"][0]["nome"] == "Juntada de Petição"
    assert payload["andamentos"][0]["data_hora"] == datetime(2026, 8, 18, 14, 21, 0)
    nomes = [item["nome"] for item in payload["andamentos"]]
    assert "Baixa Definitiva" in nomes
    assert "Juntada de Petição" in nomes


def test_montar_e_validar_cnj() -> None:
    numero = montar_cnj("0001234", "2024", "4", "01", "0000")
    assert numero == "0001234-12.2024.4.01.0000"
    assert validar_cnj(numero) == numero
    assert validar_cnj(so_digitos(numero)) == numero
    assert verificar_dv(numero)
    assert mascarar_cnj(so_digitos(numero)) == numero


def test_validar_cnj_rejeita_dv_errado() -> None:
    with pytest.raises(CnjError, match="Dígito verificador"):
        validar_cnj("0001234-56.2024.4.01.0000")


def test_validar_cnj_rejeita_tribunal_desconhecido() -> None:
    numero = montar_cnj("0001234", "2024", "4", "09", "0000")
    with pytest.raises(CnjError, match="TRF desconhecido"):
        validar_cnj(numero)


def test_prazo_create_normaliza_e_rejeita_cnj() -> None:
    numero = montar_cnj("0001234", "2024", "4", "01", "0000")
    payload = PrazoCreate(
        numero_processo=so_digitos(numero),
        cliente="Cliente",
        acao="Contestação",
        data_vencimento=date.today(),
        responsavel_id=uuid4(),
    )
    assert payload.numero_processo == numero

    with pytest.raises(ValidationError, match="Dígito verificador"):
        PrazoCreate(
            numero_processo="0001234-56.2024.4.01.0000",
            cliente="Cliente",
            acao="Contestação",
            data_vencimento=date.today(),
            responsavel_id=uuid4(),
        )
