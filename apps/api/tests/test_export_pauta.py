from datetime import date, timedelta
from uuid import uuid4

from app.models.prazo import Prazo, StatusPrazo
from app.services.export_pauta import build_csv, build_pdf


def _prazo(**kwargs) -> Prazo:
    base = {
        "escritorio_id": uuid4(),
        "numero_processo": "0001234-56.2024.4.01.0000",
        "cliente": "Maria Souza",
        "acao": "Protocolar contestação",
        "data_vencimento": date.today() + timedelta(days=2),
        "responsavel": "Verônica",
        "status": StatusPrazo.pendente,
    }
    base.update(kwargs)
    return Prazo(**base)


def test_build_csv_includes_headers_and_row() -> None:
    content = build_csv([_prazo()]).decode("utf-8-sig")
    assert "Vencimento" in content
    assert "Maria Souza" in content
    assert "Protocolar contestação" in content


def test_build_pdf_generates_bytes() -> None:
    content = build_pdf([_prazo()], titulo="Pauta (7dias)")
    assert content.startswith(b"%PDF")
    assert len(content) > 500


def test_build_pdf_empty_list() -> None:
    content = build_pdf([], titulo="Pauta vazia")
    assert content.startswith(b"%PDF")
