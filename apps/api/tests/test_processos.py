from app.services.processos import normalize_numero_processo


def test_normalize_numero_processo() -> None:
    assert normalize_numero_processo("  0001-22.2024  ") == "0001-22.2024"
    assert normalize_numero_processo("0001  22") == "0001 22"
