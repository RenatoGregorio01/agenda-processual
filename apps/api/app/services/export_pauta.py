import csv
import io
import re
from datetime import date
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

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
        self.set_x(self.l_margin)
        self.set_font("DejaVu", "B", 14)
        self.multi_cell(
            self.epw,
            8,
            "Agenda Processual — Pauta",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.set_font("DejaVu", "", 9)
        self.set_text_color(90, 90, 90)
        self.multi_cell(
            self.epw,
            6,
            f"Gerado em {_format_date(date.today())}",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_x(self.l_margin)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(self.epw, 8, f"Página {self.page_no()}", align="C")


def _line(pdf: PautaPDF, text: str, *, bold: bool = False, size: int = 10, color=(0, 0, 0)) -> None:
    """Uma linha completa na margem esquerda — evita o bug de multi_cell colado à direita."""
    pdf.set_x(pdf.l_margin)
    pdf.set_font("DejaVu", "B" if bold else "", size)
    pdf.set_text_color(*color)
    pdf.multi_cell(pdf.epw, 5, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)


def build_pdf(prazos: list[Prazo], *, titulo: str = "Pauta de prazos") -> bytes:
    pdf = PautaPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("DejaVu", "", str(FONTS_DIR / "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", "B", str(FONTS_DIR / "DejaVuSans-Bold.ttf"))
    pdf.add_page()

    _line(pdf, titulo, bold=True, size=11)
    _line(pdf, f"{len(prazos)} prazo(s) no intervalo", size=9, color=(90, 90, 90))
    pdf.ln(2)

    if not prazos:
        _line(pdf, "Nenhum prazo para exportar com os filtros atuais.", size=10)
        return bytes(pdf.output())

    for index, prazo in enumerate(prazos):
        if index > 0:
            y = pdf.get_y()
            pdf.set_draw_color(220, 220, 220)
            pdf.line(pdf.l_margin, y, pdf.l_margin + pdf.epw, y)
            pdf.ln(3)

        vencimento = _format_date(prazo.data_vencimento) or "—"
        status = STATUS_LABELS.get(prazo.status.value, prazo.status.value)

        _line(pdf, f"Vencimento: {vencimento}  ·  {status}", bold=True, size=11)
        _line(pdf, f"Ação: {prazo.acao or '—'}", size=10)
        _line(pdf, f"Processo: {prazo.numero_processo or '—'}", size=9, color=(60, 60, 60))
        _line(pdf, f"Cliente: {prazo.cliente or '—'}", size=9, color=(60, 60, 60))
        _line(pdf, f"Responsável: {prazo.responsavel or '—'}", size=9, color=(60, 60, 60))
        if prazo.data_disponibilizacao:
            _line(
                pdf,
                f"Disponibilização: {_format_date(prazo.data_disponibilizacao)}",
                size=9,
                color=(60, 60, 60),
            )
        pdf.ln(2)

    return bytes(pdf.output())
