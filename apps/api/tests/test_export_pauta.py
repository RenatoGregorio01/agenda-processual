from datetime import date, timedelta
from uuid import uuid4

from app.models.prazo import Prazo, StatusPrazo
from app.services.export_pauta import build_csv, build_pdf, describe_export


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
    assert "Pendente" in content


def test_build_pdf_generates_bytes() -> None:
    content = build_pdf([_prazo()], titulo="Pauta — Próximos 7 dias")
    assert content.startswith(b"%PDF")
    assert len(content) > 500


def test_build_pdf_empty_list() -> None:
    content = build_pdf([], titulo="Pauta vazia")
    assert content.startswith(b"%PDF")


def test_describe_export_filtro_legivel() -> None:
    titulo, filename = describe_export(filtro="7dias")
    assert titulo == "Pauta — Próximos 7 dias"
    assert filename.startswith("pauta-proximos-7-dias-")


def test_describe_export_periodo_legivel() -> None:
    titulo, filename = describe_export(
        data_inicio=date(2026, 8, 16),
        data_fim=date(2026, 8, 23),
    )
    assert titulo == "Pauta — 16/08/2026 a 23/08/2026"
    assert filename == "pauta-2026-08-16-a-2026-08-23"
