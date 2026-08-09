import csv
import io
from datetime import date
from pathlib import Path

from fpdf import FPDF

from app.models.prazo import Prazo

FONTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"


def _format_date(value: date | None) -> str:
    if value is None:
        return ""
    return value.strftime("%d/%m/%Y")


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
                prazo.status.value,
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


def build_pdf(prazos: list[Prazo], *, titulo: str = "Pauta de prazos") -> bytes:
    pdf = PautaPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("DejaVu", "", str(FONTS_DIR / "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", "B", str(FONTS_DIR / "DejaVuSans-Bold.ttf"))
    pdf.add_page()

    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 7, titulo, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 9)
    pdf.cell(0, 6, f"{len(prazos)} prazo(s)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    if not prazos:
        pdf.cell(0, 8, "Nenhum prazo para exportar com os filtros atuais.")
        return bytes(pdf.output())

    usable_width = pdf.epw
    for prazo in prazos:
        pdf.set_x(pdf.l_margin)
        pdf.set_font("DejaVu", "B", 11)
        pdf.cell(
            usable_width,
            7,
            _format_date(prazo.data_vencimento),
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.set_font("DejaVu", "", 10)
        pdf.multi_cell(usable_width, 5, prazo.acao)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(
            usable_width,
            5,
            (
                f"{prazo.numero_processo} · {prazo.cliente} · {prazo.responsavel} · "
                f"{prazo.status.value}"
            ),
        )
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

    return bytes(pdf.output())
