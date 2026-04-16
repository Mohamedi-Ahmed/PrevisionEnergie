from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fpdf import FPDF


BASE_DIR = Path(__file__).resolve().parents[2]
LIVRABLES_DIR = BASE_DIR / "livrables"


@dataclass(frozen=True)
class DocumentSpec:
    source_md: str
    target_pdf: str
    title: str


DOCUMENTS = [
    DocumentSpec(
        source_md="E4_Rapport_professionnel_aligne.md",
        target_pdf="E4_Rapport_professionnel_aligne.pdf",
        title="E4 - Rapport Professionnel Aligne",
    ),
    DocumentSpec(
        source_md="E5_Rapport_professionnel_aligne.md",
        target_pdf="E5_Rapport_professionnel_aligne.pdf",
        title="E5 - Rapport Professionnel Aligne",
    ),
    DocumentSpec(
        source_md="E6_Rapport_professionnel_aligne.md",
        target_pdf="E6_Rapport_professionnel_aligne.pdf",
        title="E6 - Rapport Professionnel Aligne",
    ),
    DocumentSpec(
        source_md="E7_Rapport_professionnel_aligne.md",
        target_pdf="E7_Rapport_professionnel_aligne.pdf",
        title="E7 - Rapport Professionnel Aligne",
    ),
]


class LivrablePDF(FPDF):
    def __init__(self, title: str) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.title = title
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(18, 18, 18)
        self.alias_nb_pages()

    def header(self) -> None:
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(35, 35, 35)
        self.cell(0, 8, self.title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(180, 180, 180)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(90, 90, 90)
        self.cell(0, 6, f"Page {self.page_no()}/{{nb}}", align="C")


def add_cover(pdf: LivrablePDF, title: str) -> None:
    pdf.add_page()
    pdf.set_y(45)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(25, 25, 25)
    pdf.multi_cell(0, 11, title, align="C")
    pdf.ln(6)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(70, 70, 70)
    pdf.multi_cell(
        0,
        7,
        "Version alignee avec l'etat reel du code du depot PrevisionEnergie.\n"
        "Document genere automatiquement pour preparation de soutenance.",
        align="C",
    )
    pdf.ln(18)


def write_paragraph(pdf: LivrablePDF, text: str, *, font: str = "Helvetica", style: str = "", size: int = 11) -> None:
    pdf.set_font(font, style, size)
    pdf.set_text_color(25, 25, 25)
    pdf.multi_cell(0, 6.2, text, wrapmode="CHAR")
    pdf.ln(1)


def render_markdown(pdf: LivrablePDF, content: str) -> None:
    in_code_block = False
    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            if not in_code_block:
                pdf.ln(1)
            continue

        if not stripped:
            pdf.ln(2)
            continue

        if in_code_block:
            pdf.set_font("Courier", "", 10)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(0, 5.2, stripped, wrapmode="CHAR")
            continue

        if stripped.startswith("# "):
            write_paragraph(pdf, stripped[2:].strip(), style="B", size=18)
            pdf.ln(1)
            continue

        if stripped.startswith("## "):
            write_paragraph(pdf, stripped[3:].strip(), style="B", size=14)
            continue

        if stripped.startswith("### "):
            write_paragraph(pdf, stripped[4:].strip(), style="B", size=12)
            continue

        if stripped.startswith("- "):
            write_paragraph(pdf, f"- {stripped[2:].strip()}")
            continue

        write_paragraph(pdf, stripped)


def generate_document(spec: DocumentSpec) -> Path:
    source_path = LIVRABLES_DIR / spec.source_md
    target_path = LIVRABLES_DIR / spec.target_pdf

    content = source_path.read_text(encoding="utf-8")
    pdf = LivrablePDF(title=spec.title)
    add_cover(pdf, spec.title)
    render_markdown(pdf, content)
    pdf.output(str(target_path))
    return target_path


def main() -> None:
    generated = [generate_document(spec) for spec in DOCUMENTS]
    for path in generated:
        print(path)


if __name__ == "__main__":
    main()
