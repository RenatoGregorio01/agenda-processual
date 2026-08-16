import csv
import io
import re
from datetime import date
from pathlib import Path

from fpdf import FPDF

from app.models.prazo import Prazo

FONTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"

FILTRO_LABELS: dict[str, str] = {
    "hoje": "Hoje",
    "atrasados": "Atrasados",
    "7dias": "Próximos 7 dias",
    "cumpridos": "Cumpridos",
    "todos": "Todos",
}

STATUS_LABELS: dict[str, str] = {
    "pendente": "Pendente",
    "cumprido": "Cumprido",
}


def _format_date(value: date | None) -> str:
    if value is None:
        return ""
    return value.strftime("%d/%m/%Y")


def _slug(value: str) -> str:
    normalized = (
        value.lower()
        .replace("á", "a")
        .replace("à", "a")
        .replace("ã", "a")
        .replace("â", "a")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ô", "o")
        .replace("õ", "o")
        .replace("ú", "u")
        .replace("ç", "c")
    )
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return normalized or "pauta"


def describe_export(
    *,
    filtro: str | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> tuple[str, str]:
    """Retorna (titulo legível, base do filename sem extensão)."""
    hoje = date.today().strftime("%Y%m%d")

    if data_inicio is not None or data_fim is not None:
        inicio_br = _format_date(data_inicio) if data_inicio else "início"
        fim_br = _format_date(data_fim) if data_fim else "fim"
        titulo = f"Pauta — {inicio_br} a {fim_br}"
        inicio_file = data_inicio.isoformat() if data_inicio else "inicio"
        fim_file = data_fim.isoformat() if data_fim else "fim"
        filename_base = f"pauta-{inicio_file}-a-{fim_file}"
        return titulo, filename_base

    label = FILTRO_LABELS.get(filtro or "", filtro or "prazos")
    titulo = f"Pauta — {label}"
    filename_base = f"pauta-{_slug(label)}-{hoje}"
    return titulo, filename_base


def build_csv(prazos: list[Prazo]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(
        [
            "Vencimento",
            "Status",
            "Processo",
            "Cliente",
            "Ação",
            "Responsável",
            "Disponibilização",
        ]
    )
    for prazo in prazos:
        writer.writerow(
            [
                _format_date(prazo.data_vencimento),
                STATUS_LABELS.get(prazo.status.value, prazo.status.value),
                prazo.numero_processo,
                prazo.cliente,
                prazo.acao,
                prazo.responsavel,
                _format_date(prazo.data_disponibilizacao),
            ]
        )
    # utf-8-sig ajuda o Excel no Windows a reconhecer acentos
    return buffer.getvalue().encode("utf-8-sig")


class PautaPDF(FPDF):
    def header(self) -> None:
        self.set_font("DejaVu", "B", 14)
        self.cell(0, 8, "Agenda Processual — Pauta", new_x="LMARGIN", new_y="NEXT")
        self.set_font("DejaVu", "", 9)
        self.set_text_color(90, 90, 90)
        self.cell(
            0,
            6,
            f"Gerado em {_format_date(date.today())}",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Página {self.page_no()}", align="C")


def _draw_labeled_row(pdf: PautaPDF, label: str, value: str, usable_width: float) -> None:
    if not value:
        return
    label_w = 32
    pdf.set_x(pdf.l_margin)
    pdf.set_font("DejaVu", "B", 9)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(label_w, 5, label)
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(usable_width - label_w, 5, value)


def build_pdf(prazos: list[Prazo], *, titulo: str = "Pauta de prazos") -> bytes:
    pdf = PautaPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("DejaVu", "", str(FONTS_DIR / "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", "B", str(FONTS_DIR / "DejaVuSans-Bold.ttf"))
    pdf.add_page()

    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 7, titulo, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(0, 6, f"{len(prazos)} prazo(s) no intervalo", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)

    if not prazos:
        pdf.cell(0, 8, "Nenhum prazo para exportar com os filtros atuais.")
        return bytes(pdf.output())

    usable_width = pdf.epw
    for index, prazo in enumerate(prazos):
        if index > 0:
            pdf.set_draw_color(220, 220, 220)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + usable_width, pdf.get_y())
            pdf.ln(3)

        vencimento = _format_date(prazo.data_vencimento) or "—"
        status = STATUS_LABELS.get(prazo.status.value, prazo.status.value)

        pdf.set_x(pdf.l_margin)
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(usable_width * 0.62, 7, f"Vencimento: {vencimento}")
        pdf.set_font("DejaVu", "B", 9)
        pdf.cell(usable_width * 0.38, 7, status, align="R", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("DejaVu", "", 10)
        pdf.multi_cell(usable_width, 5, prazo.acao or "—")
        pdf.ln(1)

        _draw_labeled_row(pdf, "Processo", prazo.numero_processo or "—", usable_width)
        _draw_labeled_row(pdf, "Cliente", prazo.cliente or "—", usable_width)
        _draw_labeled_row(pdf, "Responsável", prazo.responsavel or "—", usable_width)
        if prazo.data_disponibilizacao:
            _draw_labeled_row(
                pdf,
                "Disponibiliz.",
                _format_date(prazo.data_disponibilizacao),
                usable_width,
            )
        pdf.ln(2)

    return bytes(pdf.output())
