from datetime import date

from app.integrations.datajud.cnj import montar_cnj, so_digitos
from app.integrations.djen.parse import normalize_item
from app.services.djen import janela_sync


def test_normalize_item_descarta_sem_id() -> None:
    assert normalize_item({"numero_processo": "00000012320268260100"}) is None


def test_normalize_item_campos_mistos() -> None:
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
            "nomeOrgao": "1ª Vara Cível",
            "data_disponibilizacao": "2026-08-17",
        }
    )
    assert parsed is not None
    assert parsed["djen_id"] == "661000001"
    assert parsed["tribunal"] == "TJSP"
    assert parsed["tipo_comunicacao"] == "Intimação"
    assert parsed["data_disponibilizacao"] == date(2026, 8, 17)
    assert parsed["motivo_cancelamento"] is None


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
