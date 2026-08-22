from datetime import date

from app.integrations.datajud.cnj import montar_cnj, so_digitos
from app.integrations.djen.parse import extrair_dias_prazo, normalize_item
from app.services.djen import janela_sync


def test_normalize_item_descarta_sem_id() -> None:
    assert normalize_item({"numero_processo": "00000012320268260100"}) is None


def test_normalize_item_campos_completos() -> None:
    numero = montar_cnj("0000123", "2026", "8", "26", "0100")
    parsed = normalize_item(
        {
            "id": 661000001,
            "hash": "abc",
            "numero_processo": so_digitos(numero),
            "numeroprocessocommascara": numero,
            "siglaTribunal": "TJSP",
            "tipoComunicacao": "Intimação",
            "tipoDocumento": "Despacho",
            "nomeClasse": "Procedimento Comum Cível",
            "nomeOrgao": "1ª Vara Cível",
            "data_disponibilizacao": "2026-08-17",
            "texto": "DESPACHO Intime-se a parte autora para ciência. Prazo de 5 dias.",
            "link": "https://pje.tjsp.jus.br/validacao/123",
            "destinatarioadvogados": [
                {
                    "advogado": {
                        "nome": "RENATO GREGORIO",
                        "numero_oab": "12345",
                        "uf_oab": "BA",
                    }
                }
            ],
        }
    )
    assert parsed is not None
    assert parsed["djen_id"] == "661000001"
    assert parsed["tribunal"] == "TJSP"
    assert parsed["tipo_comunicacao"] == "Intimação"
    assert parsed["nome_classe"] == "Procedimento Comum Cível"
    assert parsed["texto"] == "DESPACHO Intime-se a parte autora para ciência. Prazo de 5 dias."
    assert parsed["link"] == "https://pje.tjsp.jus.br/validacao/123"
    assert "RENATO GREGORIO (OAB/BA 12345)" in parsed["destinatarios"]
    assert parsed["dias_identificados"] == 5
    assert parsed["data_disponibilizacao"] == date(2026, 8, 17)
    assert parsed["motivo_cancelamento"] is None


def test_extrair_dias_prazo_variacoes() -> None:
    assert extrair_dias_prazo("Prazo de 5 dias.") == 5
    assert extrair_dias_prazo("Manifestar no prazo de 15 (quinze) dias.") == 15
    assert extrair_dias_prazo("Fica a parte intimada em 8 dias.") == 8
    assert extrair_dias_prazo("Prazo legal de 10 dias.") == 10
    assert extrair_dias_prazo("Apresentar defesa no prazo de trinta dias.") == 30
    assert extrair_dias_prazo("Apresentar resposta em cinco dias.") == 5
    assert extrair_dias_prazo("Sem prazo especificado no despacho.") is None
    assert extrair_dias_prazo(None) is None


def test_normalize_item_cancelamento() -> None:
    numero = so_digitos(montar_cnj("0000123", "2026", "8", "26", "0100"))
    parsed = normalize_item(
        {
            "id": 2,
            "numero_processo": numero,
            "motivo_cancelamento": "Erro material",
        }
    )
    assert parsed is not None
    assert parsed["motivo_cancelamento"] == "Erro material"


def test_janela_primeira_sync_tem_lookback() -> None:
    inicio, fim = janela_sync(None)
    assert (fim - inicio).days == 7
    assert inicio <= fim


def test_janela_incremental_folga_um_dia() -> None:
    from datetime import datetime

    ultima = datetime(2026, 8, 10, 10, 0, 0)
    inicio, _fim = janela_sync(ultima)
    assert inicio == date(2026, 8, 9)
