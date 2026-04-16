from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from fpdf import FPDF
from PIL import Image


BASE_DIR = Path(__file__).resolve().parents[2]
LIVRABLES_DIR = BASE_DIR / "livrables" / "finals"
WINDOWS_FONTS = Path(r"C:\Windows\Fonts")
PROJECT_TITLE = (
    "Projet : Prévision de la consommation quotidienne d'électricité et de gaz "
    "par région française à partir des conditions météorologiques"
)


@dataclass(frozen=True)
class DocumentSpec:
    source_md: str
    target_pdf: str
    title: str
    bloc: str
    project: str = PROJECT_TITLE
    author: str | None = "Ahmed Mohamedi"
    organization: str | None = None
    version_label: str | None = None


DOCUMENTS = [
    DocumentSpec(
        source_md="E1_Grilles_entretien_FINAL.md",
        target_pdf="E1_Grilles_entretien_FINAL.pdf",
        title="E1 - Grilles d'entretien",
        bloc="Compétence / Bloc 1 - Étude de cas",
        organization="Organisation cible : opérateur énergétique",
        version_label="Version finale - Avril 2026",
    ),
    DocumentSpec(
        source_md="E1_Note_de_synthese_FINAL.md",
        target_pdf="E1_Note_de_synthese_FINAL.pdf",
        title="E1 - Note de synthèse",
        bloc="Compétence / Bloc 1 - Étude de cas",
        organization="Organisation cible : opérateur énergétique",
        version_label="Version finale - Avril 2026",
    ),
    DocumentSpec(
        source_md="E2_Rapport_professionnel_FINAL.md",
        target_pdf="E2_Rapport_professionnel_FINAL.pdf",
        title="E2 - Rapport professionnel",
        bloc="Compétence / Bloc 1 - Mise en situation professionnelle",
    ),
    DocumentSpec(
        source_md="E3_Avant_projet_et_planification_FINAL.md",
        target_pdf="E3_Avant_projet_et_planification_FINAL.pdf",
        title="E3 - Avant-projet et planification",
        bloc="Compétence / Bloc 1 - Jeu de rôle : lancement de projet",
    ),
    DocumentSpec(
        source_md="E4_Rapport_professionnel_FINAL.md",
        target_pdf="E4_Rapport_professionnel_FINAL.pdf",
        title="E4 - Rapport professionnel",
        bloc="Compétence / Bloc 2 - Collecte, stockage et mise à disposition",
    ),
    DocumentSpec(
        source_md="E5_Rapport_professionnel_FINAL.md",
        target_pdf="E5_Rapport_professionnel_FINAL.pdf",
        title="E5 - Rapport professionnel",
        bloc="Compétence / Bloc 3 - Modélisation et ETL DWH",
    ),
    DocumentSpec(
        source_md="E6_Rapport_professionnel_FINAL.md",
        target_pdf="E6_Rapport_professionnel_FINAL.pdf",
        title="E6 - Rapport professionnel",
        bloc="Compétence / Bloc 3 - Catalogue de données et variations de dimensions",
    ),
    DocumentSpec(
        source_md="E7_Rapport_professionnel_FINAL.md",
        target_pdf="E7_Rapport_professionnel_FINAL.pdf",
        title="E7 - Architecture et gouvernance Data Lake",
        bloc="Compétence / Bloc 4 - Encadrer la collecte massive avec un Data Lake",
    ),
]


PHRASE_REPLACEMENTS = [
    ("a partir de", "à partir de"),
    ("A partir de", "À partir de"),
    ("a ce stade", "à ce stade"),
    ("A ce stade", "À ce stade"),
    ("a l'oral", "à l'oral"),
    ("a la fois", "à la fois"),
    ("a la suite", "à la suite"),
    ("a court terme", "à court terme"),
    ("A ces", "À ces"),
    ("A ce", "À ce"),
    ("a un", "à un"),
    ("a une", "à une"),
    ("mise a disposition", "mise à disposition"),
    ("jeu de role", "jeu de rôle"),
    ("cote client", "côté client"),
    ("de facon", "de façon"),
    ("d'une facon", "d'une façon"),
    ("point d'appui a", "point d'appui à"),
    ("point d'acces", "point d'accès"),
    ("au-dela", "au-delà"),
    ("d'abord", "d'abord"),
    ("Organisation cible : operateur energetique", "Organisation cible : opérateur énergétique"),
    ("comprÃƒÂ©hensible", "compréhensible"),
]

WORD_REPLACEMENTS = {
    "Prevision": "Prévision",
    "prevision": "prévision",
    "electricite": "électricité",
    "Electricite": "Électricité",
    "gaz": "gaz",
    "region": "région",
    "Region": "Région",
    "regions": "régions",
    "Regions": "Régions",
    "francaise": "française",
    "francais": "français",
    "francaises": "françaises",
    "meteorologiques": "météorologiques",
    "meteo": "météo",
    "Meteo": "Météo",
    "donnee": "donnée",
    "donnees": "données",
    "Donnee": "Donnée",
    "Donnees": "Données",
    "synthese": "synthèse",
    "Synthese": "Synthèse",
    "etude": "étude",
    "Etude": "Étude",
    "etre": "être",
    "Etre": "Être",
    "ete": "été",
    "deja": "déjà",
    "apres": "après",
    "tres": "très",
    "meme": "même",
    "coherent": "cohérent",
    "coherente": "cohérente",
    "coherents": "cohérents",
    "coherence": "cohérence",
    "qualite": "qualité",
    "securite": "sécurité",
    "fiabilite": "fiabilité",
    "tracabilite": "traçabilité",
    "retention": "rétention",
    "metier": "métier",
    "Metier": "Métier",
    "execute": "exécute",
    "executee": "exécutée",
    "executees": "exécutées",
    "executer": "exécuter",
    "execution": "exécution",
    "executable": "exécutable",
    "executables": "exécutables",
    "reel": "réel",
    "reelle": "réelle",
    "reels": "réels",
    "reellement": "réellement",
    "entrepot": "entrepôt",
    "modele": "modèle",
    "modelisation": "modélisation",
    "Modelisation": "Modélisation",
    "schema": "schéma",
    "Schema": "Schéma",
    "cles": "clés",
    "cle": "clé",
    "comprehensible": "compréhensible",
    "comprehensibles": "compréhensibles",
    "maturite": "maturité",
    "necessaire": "nécessaire",
    "necessaires": "nécessaires",
    "theorique": "théorique",
    "theoriques": "théoriques",
    "premiere": "première",
    "deuxieme": "deuxième",
    "troisieme": "troisième",
    "quatrieme": "quatrième",
    "cinquieme": "cinquième",
    "huitieme": "huitième",
    "annee": "année",
    "annees": "années",
    "dediee": "dédiée",
    "separee": "séparée",
    "ecriture": "écriture",
    "controle": "contrôle",
    "controles": "contrôles",
    "critere": "critère",
    "criteres": "critères",
    "methode": "méthode",
    "competence": "compétence",
    "Competence": "Compétence",
    "role": "rôle",
    "Role": "Rôle",
    "tache": "tâche",
    "taches": "tâches",
    "generale": "générale",
    "general": "général",
    "generer": "générer",
    "genere": "génère",
    "generee": "générée",
    "generees": "générées",
    "derivee": "dérivée",
    "derivees": "dérivées",
    "particuliere": "particulière",
    "exposee": "exposée",
    "exposees": "exposées",
    "preparee": "préparée",
    "preparees": "préparées",
    "prepare": "préparé",
    "realise": "réalisé",
    "realisee": "réalisée",
    "realisees": "réalisées",
    "utilisee": "utilisée",
    "utilisees": "utilisées",
    "reutilisable": "réutilisable",
    "reutilisation": "réutilisation",
    "analysee": "analysée",
    "analysees": "analysées",
    "privilegies": "privilégiés",
    "priviligies": "privilégiés",
    "scenarios": "scénarios",
    "scenario": "scénario",
    "specifique": "spécifique",
    "specifiques": "spécifiques",
    "capacite": "capacité",
    "modalites": "modalités",
    "priorise": "priorisé",
    "priorisee": "priorisée",
    "priorisee": "priorisée",
    "inventaire": "inventaire",
    "echanges": "échanges",
    "mene": "mené",
    "menes": "menés",
    "integre": "intègre",
    "integrees": "intégrées",
    "integree": "intégrée",
    "reguliere": "régulière",
    "regulier": "régulier",
    "reguliers": "réguliers",
    "ecart": "écart",
    "ecarts": "écarts",
    "elargir": "élargir",
    "ambiguite": "ambiguïté",
    "hypotheses": "hypothèses",
    "deployee": "déployée",
    "deployees": "déployées",
    "maitrise": "maîtrise",
    "maitrisee": "maîtrisée",
    "maitrises": "maîtrisés",
    "precis": "précis",
    "precise": "précise",
    "precision": "précision",
    "economique": "économique",
    "energetique": "énergétique",
    "energetiques": "énergétiques",
    "reglementation": "réglementation",
    "supervision": "supervision",
    "valorisee": "valorisée",
    "modalite": "modalité",
    "interlocuteurs": "interlocuteurs",
    "artefacts": "artefacts",
    "privilegie": "privilégié",
    "privilegiee": "privilégiée",
    "ajoute": "ajoute",
    "specifque": "spécifique",
}


class JuryPDF(FPDF):
    def __init__(self) -> None:
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.set_margins(25.4, 23.5, 25.4)
        self.set_auto_page_break(auto=True, margin=22)
        self.add_page()


def register_fonts(pdf: JuryPDF) -> None:
    pdf.add_font("ArialCustom", "", str(WINDOWS_FONTS / "arial.ttf"))
    pdf.add_font("ArialCustom", "B", str(WINDOWS_FONTS / "arialbd.ttf"))
    pdf.add_font("TimesCustom", "", str(WINDOWS_FONTS / "times.ttf"))
    pdf.add_font("TimesCustom", "B", str(WINDOWS_FONTS / "timesbd.ttf"))
    pdf.add_font("TimesCustom", "I", str(WINDOWS_FONTS / "timesi.ttf"))


def normalize_french_text(text: str) -> str:
    normalized = text
    for source, target in PHRASE_REPLACEMENTS:
        normalized = normalized.replace(source, target)
    for source, target in WORD_REPLACEMENTS.items():
        normalized = re.sub(rf"\b{re.escape(source)}\b", target, normalized)
    normalized = normalized.replace("’", "'")
    return normalized


def ensure_space(pdf: JuryPDF, needed_mm: float) -> None:
    remaining = pdf.h - pdf.get_y() - pdf.b_margin
    if remaining < needed_mm:
        pdf.add_page()


def write_title_block(pdf: JuryPDF, spec: DocumentSpec) -> None:
    pdf.set_font("ArialCustom", "B", 15)
    pdf.multi_cell(0, 7.0, normalize_french_text(spec.project))
    pdf.ln(3.5)

    pdf.set_font("ArialCustom", "", 11)
    pdf.multi_cell(0, 5.4, normalize_french_text(spec.author or "Ahmed Mohamedi"))
    pdf.ln(2.8)

    pdf.set_font("ArialCustom", "B", 14)
    pdf.multi_cell(0, 6.6, normalize_french_text(spec.title))
    pdf.ln(2)

    pdf.set_font("TimesCustom", "B", 10)
    pdf.multi_cell(0, 5.2, normalize_french_text(spec.bloc))
    pdf.ln(1.2)

    pdf.set_font("TimesCustom", "", 10)
    if spec.organization:
        pdf.multi_cell(0, 5.2, normalize_french_text(spec.organization))
        pdf.ln(1.0)
    if spec.version_label:
        pdf.multi_cell(0, 5.2, normalize_french_text(spec.version_label))
        pdf.ln(1.0)
    pdf.ln(2.5)


def write_body_paragraph(pdf: JuryPDF, text: str, *, indent: float = 0.0) -> None:
    current_x = pdf.get_x()
    if indent:
        pdf.set_x(pdf.l_margin + indent)
    pdf.set_font("TimesCustom", "", 10)
    pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - indent, 5.2, normalize_french_text(text))
    pdf.set_x(current_x)
    pdf.ln(1.1)


def write_section_heading(pdf: JuryPDF, text: str) -> None:
    ensure_space(pdf, 28)
    pdf.ln(2)
    pdf.set_font("ArialCustom", "B", 14)
    pdf.multi_cell(0, 6.6, normalize_french_text(text))
    pdf.ln(1.2)


def write_subheading(pdf: JuryPDF, text: str) -> None:
    ensure_space(pdf, 18)
    pdf.set_font("TimesCustom", "B", 10)
    pdf.multi_cell(0, 5.2, normalize_french_text(text))
    pdf.ln(0.4)


def _parse_svg_dimension(value: str | None) -> float | None:
    if not value:
        return None
    match = re.match(r"([0-9]+(?:\.[0-9]+)?)", value)
    return float(match.group(1)) if match else None


def get_image_dimensions(image_path: Path) -> tuple[float, float]:
    if image_path.suffix.lower() == ".svg":
        root = ET.fromstring(image_path.read_text(encoding="utf-8"))
        width = _parse_svg_dimension(root.attrib.get("width"))
        height = _parse_svg_dimension(root.attrib.get("height"))
        if width and height:
            return width, height
        view_box = root.attrib.get("viewBox") or root.attrib.get("viewbox")
        if view_box:
            parts = view_box.replace(",", " ").split()
            if len(parts) == 4:
                return float(parts[2]), float(parts[3])
        raise ValueError(f"Impossible de lire les dimensions du SVG : {image_path}")

    with Image.open(image_path) as img:
        return img.size


def write_image(pdf: JuryPDF, image_path: Path, caption: str) -> None:
    if not image_path.exists():
        write_body_paragraph(pdf, f"[Visuel manquant : {image_path}]")
        return

    width_px, height_px = get_image_dimensions(image_path)
    max_width = pdf.w - pdf.l_margin - pdf.r_margin
    target_width = min(max_width, 150)
    scale = target_width / width_px
    target_height = height_px * scale

    ensure_space(pdf, target_height + 12)
    x = pdf.l_margin + (max_width - target_width) / 2
    y = pdf.get_y()
    pdf.image(str(image_path), x=x, y=y, w=target_width)
    pdf.set_y(y + target_height + 2.5)
    pdf.set_font("TimesCustom", "I", 9)
    pdf.multi_cell(0, 4.6, normalize_french_text(caption))
    pdf.ln(1.8)


def render_source(pdf: JuryPDF, content: str) -> None:
    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            pdf.ln(1.6)
            continue

        if stripped.startswith("## "):
            write_section_heading(pdf, stripped[3:].strip())
            continue

        if stripped.startswith("### "):
            write_subheading(pdf, stripped[4:].strip())
            continue

        if stripped.startswith("![") and "](" in stripped and stripped.endswith(")"):
            caption = stripped[2:stripped.index("](")].strip()
            image_rel = stripped[stripped.index("](") + 2 : -1].strip()
            write_image(pdf, (LIVRABLES_DIR / image_rel).resolve(), caption)
            continue

        if stripped.startswith("- "):
            write_body_paragraph(pdf, f"• {stripped[2:].strip()}", indent=5.5)
            continue

        write_body_paragraph(pdf, stripped)


def generate_document(spec: DocumentSpec) -> Path:
    source_path = LIVRABLES_DIR / spec.source_md
    target_path = LIVRABLES_DIR / spec.target_pdf
    content = source_path.read_text(encoding="utf-8")

    pdf = JuryPDF()
    register_fonts(pdf)
    pdf.set_title(normalize_french_text(spec.title))
    pdf.set_author(spec.author or "Ahmed Mohamedi")
    pdf.set_subject(normalize_french_text(spec.bloc))
    pdf.set_creator("FPDF")
    pdf.set_keywords("RNCP 7, Data Engineer, projet final, livrable final")
    write_title_block(pdf, spec)
    render_source(pdf, content)
    pdf.output(str(target_path))
    return target_path


def main() -> None:
    LIVRABLES_DIR.mkdir(parents=True, exist_ok=True)
    for spec in DOCUMENTS:
        print(generate_document(spec))


if __name__ == "__main__":
    main()

