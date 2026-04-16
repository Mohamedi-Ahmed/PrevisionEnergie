"""Build enhanced soutenance PPTX from the existing content."""
from __future__ import annotations

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR


# --- palette -----------------------------------------------------------------
from pptx.dml.color import RGBColor

PRIMARY = RGBColor(0x0B, 0x3D, 0x91)   # deep blue — énergie
SECOND = RGBColor(0x1F, 0x6F, 0x8B)    # teal — météo
ACCENT = RGBColor(0xD4, 0xA0, 0x17)    # gold — accent
OK_GREEN = RGBColor(0x2E, 0x7D, 0x32)
NEUTRAL_BG = RGBColor(0xF5, 0xF7, 0xFA)
TEXT_DARK = RGBColor(0x1F, 0x2A, 0x44)
TEXT_MUTE = RGBColor(0x60, 0x6B, 0x7C)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

BLOC_COLORS = {
    "E1": RGBColor(0x0B, 0x3D, 0x91),
    "E2": RGBColor(0x14, 0x5D, 0xA0),
    "E3": RGBColor(0x1F, 0x6F, 0x8B),
    "E4": RGBColor(0x2E, 0x7D, 0x32),
    "E5": RGBColor(0xB4, 0x7B, 0x00),
    "E6": RGBColor(0xC0, 0x39, 0x2B),
    "E7": RGBColor(0x6A, 0x1B, 0x9A),
    "QR": RGBColor(0x37, 0x47, 0x4F),
}

STAGES = ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "QR"]

# --- layout ------------------------------------------------------------------
SLIDE_W = Emu(12192000)
SLIDE_H = Emu(6858000)
MARGIN_X = Inches(0.5)
HEADER_H = Inches(0.55)
PROGRESS_H = Inches(0.28)
FOOTER_H = Inches(0.3)
CONTENT_TOP = HEADER_H + PROGRESS_H + Inches(0.2)


def set_fill(shape, rgb):
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb
    shape.line.fill.background()


def add_text(slide, x, y, w, h, text, *, size=14, bold=False, color=TEXT_DARK,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font="Calibri"):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.name = font
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    return tb


def add_rect(slide, x, y, w, h, fill=None, line=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    if fill is not None:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    else:
        shp.fill.background()
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
    shp.shadow.inherit = False
    return shp


def add_header(slide, bloc, duree, title, subtitle=""):
    # Bloc pill top-left
    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                  MARGIN_X, Inches(0.25), Inches(0.9), Inches(0.35))
    set_fill(pill, BLOC_COLORS.get(bloc, PRIMARY))
    tf = pill.text_frame
    tf.margin_left = Inches(0.05); tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.02); tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = bloc; r.font.bold = True
    r.font.size = Pt(14); r.font.color.rgb = WHITE; r.font.name = "Calibri"

    # Duration
    add_text(slide, MARGIN_X + Inches(1.0), Inches(0.28),
             Inches(1.2), Inches(0.3), duree,
             size=11, color=TEXT_MUTE, bold=True)

    # Title
    add_text(slide, MARGIN_X + Inches(2.2), Inches(0.18),
             SLIDE_W - MARGIN_X - Inches(2.2) - MARGIN_X, Inches(0.5), title,
             size=26, bold=True, color=TEXT_DARK, anchor=MSO_ANCHOR.MIDDLE)

    if subtitle:
        add_text(slide, MARGIN_X + Inches(2.2), Inches(0.62),
                 SLIDE_W - MARGIN_X - Inches(2.2) - MARGIN_X, Inches(0.25), subtitle,
                 size=12, color=TEXT_MUTE)


def add_progress(slide, active):
    """horizontal stage bar, highlight active stage"""
    y = Inches(0.92)
    total_w = SLIDE_W - MARGIN_X * 2
    cell = total_w // len(STAGES)
    for i, s in enumerate(STAGES):
        x = MARGIN_X + cell * i
        col = BLOC_COLORS.get(s, TEXT_MUTE)
        if s == active:
            fill = col
            txt_col = WHITE
        else:
            fill = NEUTRAL_BG
            txt_col = TEXT_MUTE
        box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x + Inches(0.03), y,
                                     cell - Inches(0.06), Inches(0.22))
        set_fill(box, fill)
        tf = box.text_frame
        tf.margin_left = Inches(0.02); tf.margin_right = Inches(0.02)
        tf.margin_top = Inches(0); tf.margin_bottom = Inches(0)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = s if s != "QR" else "Q&R"
        r.font.bold = (s == active)
        r.font.size = Pt(10)
        r.font.color.rgb = txt_col
        r.font.name = "Calibri"


def add_footer(slide, n, total):
    add_text(slide, MARGIN_X, SLIDE_H - Inches(0.35),
             Inches(6), Inches(0.25),
             "MOHAMEDI Ahmed — Soutenance Data Engineer RNCP 7 — Prévision conso élec/gaz",
             size=9, color=TEXT_MUTE)
    add_text(slide, SLIDE_W - MARGIN_X - Inches(1), SLIDE_H - Inches(0.35),
             Inches(1), Inches(0.25), f"{n} / {total}",
             size=9, color=TEXT_MUTE, align=PP_ALIGN.RIGHT)


def new_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])  # blank


def content_area():
    x = MARGIN_X
    y = CONTENT_TOP
    w = SLIDE_W - 2 * MARGIN_X
    h = SLIDE_H - CONTENT_TOP - FOOTER_H - Inches(0.1)
    return x, y, w, h


def add_bullet_list(slide, x, y, w, h, items, size=14, spacing_pt=6):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.05)
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(spacing_pt)
        r = p.add_run()
        r.text = f"•  {it}"
        r.font.name = "Calibri"
        r.font.size = Pt(size)
        r.font.color.rgb = TEXT_DARK


def add_title_block(slide, x, y, w, h, title, items, *, title_color=PRIMARY,
                    title_size=14, body_size=13):
    # Card
    card = add_rect(slide, x, y, w, h, fill=WHITE, line=NEUTRAL_BG)
    # Title bar
    bar_h = Inches(0.4)
    bar = add_rect(slide, x, y, w, bar_h, fill=title_color)
    tf = bar.text_frame
    tf.margin_left = Inches(0.15); tf.margin_right = Inches(0.1)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    r = p.add_run(); r.text = title
    r.font.bold = True; r.font.size = Pt(title_size); r.font.color.rgb = WHITE
    r.font.name = "Calibri"
    # Body
    body_y = y + bar_h + Inches(0.08)
    body_h = h - bar_h - Inches(0.16)
    body = slide.shapes.add_textbox(x + Inches(0.1), body_y, w - Inches(0.2), body_h)
    btf = body.text_frame; btf.word_wrap = True
    for i, it in enumerate(items):
        p = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
        p.space_after = Pt(4)
        r = p.add_run(); r.text = f"•  {it}"
        r.font.name = "Calibri"; r.font.size = Pt(body_size)
        r.font.color.rgb = TEXT_DARK


def add_kpi_card(slide, x, y, w, h, value, label, color=PRIMARY):
    card = add_rect(slide, x, y, w, h, fill=WHITE, line=color)
    tb = slide.shapes.add_textbox(x, y + Inches(0.1), w, Inches(0.9))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = value
    r.font.bold = True; r.font.size = Pt(28); r.font.color.rgb = color
    r.font.name = "Calibri"
    tb2 = slide.shapes.add_textbox(x, y + h - Inches(0.5), w, Inches(0.4))
    tf2 = tb2.text_frame
    p2 = tf2.paragraphs[0]; p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run(); r2.text = label
    r2.font.size = Pt(11); r2.font.color.rgb = TEXT_MUTE; r2.font.name = "Calibri"


def add_table(slide, x, y, w, h, rows, *, header=True, header_color=PRIMARY,
              font_size=11):
    n_rows = len(rows); n_cols = len(rows[0])
    tbl_shape = slide.shapes.add_table(n_rows, n_cols, x, y, w, h)
    tbl = tbl_shape.table
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            cell.text = ""
            tf = cell.text_frame
            p = tf.paragraphs[0]
            r = p.add_run(); r.text = str(val)
            r.font.name = "Calibri"
            r.font.size = Pt(font_size)
            if header and i == 0:
                r.font.bold = True; r.font.color.rgb = WHITE
                cell.fill.solid(); cell.fill.fore_color.rgb = header_color
            else:
                r.font.color.rgb = TEXT_DARK
                cell.fill.solid()
                cell.fill.fore_color.rgb = NEUTRAL_BG if i % 2 == 0 else WHITE
    return tbl


# --- build -------------------------------------------------------------------
def build(out_path: Path):
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    TOTAL = 27  # final count
    idx = [0]

    def finalize(slide, bloc=None, n=None):
        add_footer(slide, n if n else idx[0], TOTAL)

    # --- Slide 1 — Cover ----------------------------------------------------
    idx[0] = 1
    s = new_slide(prs)
    add_rect(s, 0, 0, SLIDE_W, SLIDE_H, fill=PRIMARY)
    add_rect(s, 0, SLIDE_H - Inches(1.5), SLIDE_W, Inches(1.5), fill=RGBColor(0x08, 0x2E, 0x70))
    add_text(s, Inches(0.7), Inches(1.3), SLIDE_W - Inches(1.4), Inches(0.6),
             "SOUTENANCE — PROJET FINAL", size=16, bold=True, color=ACCENT,
             font="Calibri")
    add_text(s, Inches(0.7), Inches(1.9), SLIDE_W - Inches(1.4), Inches(1.3),
             "Prévision de la consommation quotidienne\nd'électricité et de gaz par région française",
             size=40, bold=True, color=WHITE)
    add_text(s, Inches(0.7), Inches(3.4), SLIDE_W - Inches(1.4), Inches(0.5),
             "à partir des conditions météorologiques",
             size=22, color=RGBColor(0xCC, 0xDD, 0xEE))
    add_text(s, Inches(0.7), Inches(4.2), SLIDE_W - Inches(1.4), Inches(0.4),
             "Expert en Ingénierie des Données — RNCP niveau 7",
             size=16, color=ACCENT)
    add_text(s, Inches(0.7), SLIDE_H - Inches(1.1), SLIDE_W - Inches(1.4), Inches(0.4),
             "MOHAMEDI Ahmed", size=20, bold=True, color=WHITE)
    add_text(s, Inches(0.7), SLIDE_H - Inches(0.7), SLIDE_W - Inches(1.4), Inches(0.3),
             "Simplon — Parcours complet E1 → E7 — 80 min + 10 min Q&R",
             size=12, color=RGBColor(0xCC, 0xDD, 0xEE))

    # --- Slide 2 — Agenda ---------------------------------------------------
    idx[0] = 2
    s = new_slide(prs)
    add_rect(s, 0, 0, SLIDE_W, Inches(0.7), fill=PRIMARY)
    add_text(s, MARGIN_X, Inches(0.15), SLIDE_W - 2 * MARGIN_X, Inches(0.5),
             "Plan de la soutenance", size=26, bold=True, color=WHITE,
             anchor=MSO_ANCHOR.MIDDLE)

    rows = [
        ["Bloc", "Livrable", "Durée", "Slides", "Thème"],
        ["1", "E1", "5 min", "2", "Cadrage besoin métier"],
        ["1", "E2", "20 min", "5", "Spécifications, périmètre, stack"],
        ["1", "E3", "10 min", "3", "Organisation projet"],
        ["2", "E4", "15 min", "5", "Architecture & mise en œuvre"],
        ["3", "E5", "10 min", "3", "DWH Gold + ML baseline"],
        ["3", "E6", "5-10 min", "2", "Catalogue & lignage"],
        ["4", "E7", "10 min", "2", "Data Lake & gouvernance"],
        ["—", "Synthèse + Q&R", "10 min", "2", "Compétences + échanges"],
    ]
    add_table(s, MARGIN_X, Inches(1.1), SLIDE_W - 2 * MARGIN_X, Inches(4.8),
              rows, font_size=13)

    add_text(s, MARGIN_X, Inches(6.1), SLIDE_W - 2 * MARGIN_X, Inches(0.3),
             "Fil rouge : partir d'un besoin métier → socle data démontrable → restitution gouvernée.",
             size=13, color=ACCENT, bold=True, align=PP_ALIGN.CENTER)
    finalize(s)

    # --- Helper for standard slide ------------------------------------------
    def std(bloc, duree, title, subtitle=""):
        idx[0] += 1
        s = new_slide(prs)
        add_header(s, bloc, duree, title, subtitle)
        add_progress(s, bloc)
        finalize(s)
        return s

    # --- Slide 3 — E1 Contexte métier ---------------------------------------
    idx[0] = 2  # will become 3
    s = std("E1", "5 min", "Contexte métier",
            "Pourquoi ce projet a du sens")
    x, y, w, h = content_area()
    # left column: contexte
    col_w = (w - Inches(0.3)) // 2
    add_title_block(s, x, y, col_w, Inches(3.0), "Situation",
                    ["Opérateur énergétique : lire et anticiper la consommation quotidienne par région",
                     "Forte sensibilité à la météo (chauffage, climatisation)",
                     "Lecture partagée métier / technique",
                     "Nécessité de distinguer électricité et gaz"],
                    title_color=PRIMARY)
    add_title_block(s, x + col_w + Inches(0.3), y, col_w, Inches(3.0),
                    "Attente principale",
                    ["Disposer d'un socle de données propre",
                     "Analyser la consommation régionale",
                     "Poser une première logique de prévision",
                     "Restitution lisible pour décideurs"],
                    title_color=SECOND)
    # KPIs row
    kpi_y = y + Inches(3.3)
    kpi_w = (w - Inches(0.4)) // 3
    add_kpi_card(s, x, kpi_y, kpi_w, Inches(1.5), "région / jour", "maille retenue", PRIMARY)
    add_kpi_card(s, x + kpi_w + Inches(0.2), kpi_y, kpi_w, Inches(1.5),
                 "élec + gaz", "énergies couvertes", SECOND)
    add_kpi_card(s, x + 2 * (kpi_w + Inches(0.2)), kpi_y, kpi_w, Inches(1.5),
                 "analyse + prévision", "usage cible", ACCENT)

    # --- Slide 4 — E1 Recueil du besoin ------------------------------------
    s = std("E1", "5 min", "Recueil du besoin",
            "Parties prenantes et méthode retenue")
    x, y, w, h = content_area()
    rows = [
        ["Interlocuteur", "Rôle", "Point recherché"],
        ["Direction", "priorités métier", "valeur attendue, arbitrages"],
        ["DSI", "cadre technique", "sources, accès, architecture"],
        ["DPO", "conformité", "RGPD, diffusion, conservation"],
        ["Service données", "réalité terrain", "qualité, formats, limites"],
    ]
    add_table(s, x, y, w, Inches(2.8), rows, font_size=13)
    add_title_block(s, x, y + Inches(3.0), w, Inches(1.8),
                    "Méthode retenue",
                    ["Entretiens semi-directifs avec trame commune mais adaptable",
                     "Traçabilité des besoins et contraintes formulés",
                     "Cadrage transverse : pas uniquement un angle technique"],
                    title_color=SECOND)
    add_text(s, x, y + Inches(4.9), w, Inches(0.4),
             "⇒ Le besoin a été cadré avec les bons interlocuteurs, dans plusieurs angles.",
             size=14, color=ACCENT, bold=True, align=PP_ALIGN.CENTER)

    # --- Slide 5 — E2 Besoin reformulé --------------------------------------
    s = std("E2", "20 min", "Besoin reformulé et objectif",
            "Transformer une demande générale en cible exploitable")
    x, y, w, h = content_area()
    # Big quote block
    qb = add_rect(s, x, y, w, Inches(1.8), fill=NEUTRAL_BG, line=PRIMARY)
    tb = s.shapes.add_textbox(x + Inches(0.3), y + Inches(0.2),
                              w - Inches(0.6), Inches(1.4))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run(); r.text = "Besoin reformulé : "
    r.font.bold = True; r.font.size = Pt(18); r.font.color.rgb = PRIMARY
    r.font.name = "Calibri"
    r2 = p.add_run()
    r2.text = ("Collecter, préparer et croiser des données énergie, météo et calendaires "
               "pour produire une base analytique exploitable, puis une première logique de prévision.")
    r2.font.size = Pt(18); r2.font.color.rgb = TEXT_DARK; r2.font.name = "Calibri"

    # 4 pillars
    pil_y = y + Inches(2.1)
    pil_w = (w - Inches(0.6)) // 4
    pils = [("Analyse", PRIMARY), ("Prévision", SECOND),
            ("Lecture régionale", ACCENT), ("Élec / Gaz", OK_GREEN)]
    for i, (t, c) in enumerate(pils):
        px = x + i * (pil_w + Inches(0.2))
        add_kpi_card(s, px, pil_y, pil_w, Inches(1.3), t, "axe clé", c)

    add_text(s, x, pil_y + Inches(1.6), w, Inches(0.5),
             "Objectif V1 : un périmètre limité mais défendable et rejouable.",
             size=14, bold=True, color=TEXT_MUTE, align=PP_ALIGN.CENTER)

    # --- Slide 6 — E2 Périmètre V1 ------------------------------------------
    s = std("E2", "20 min", "Périmètre V1",
            "Ce que la V1 couvre, et ce qu'elle ne couvre pas")
    x, y, w, h = content_area()
    col_w = (w - Inches(0.3)) // 2
    add_title_block(s, x, y, col_w, Inches(4.2), "✓  Inclus en V1",
                    ["consommation + météo + calendrier",
                     "base analytique exploitable (Bronze → Silver → Gold)",
                     "première baseline de prévision (ML)",
                     "restitution lisible : API FastAPI + SQL",
                     "orchestration batch locale (Airflow)",
                     "catalogue Atlas + lignage documenté"],
                    title_color=OK_GREEN)
    add_title_block(s, x + col_w + Inches(0.3), y, col_w, Inches(4.2),
                    "✗  Hors périmètre à ce stade",
                    ["ingestion temps réel (streaming)",
                     "optimisation automatique de production",
                     "couverture complète des renouvelables",
                     "plateforme Atlas live (vs bundle JSON)",
                     "IAM entreprise (vs RBAC local)",
                     "data lake cloud complet (GCS préparé)"],
                    title_color=RGBColor(0xC0, 0x39, 0x2B))
    add_text(s, x, y + Inches(4.5), w, Inches(0.4),
             "Positionnement : une V1 stable et démontrable vaut mieux qu'un périmètre trop large.",
             size=14, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

    # --- Slide 7 — E2 Opportunité / SMART -----------------------------------
    s = std("E2", "20 min", "Opportunité, faisabilité, critères",
            "Pourquoi ce projet est pertinent et tenable")
    x, y, w, h = content_area()
    col_w = (w - Inches(0.6)) // 3
    add_title_block(s, x, y, col_w, Inches(2.8), "Opportunité",
                    ["mieux préparer les arbitrages",
                     "poser un socle réutilisable",
                     "faire converger métier et technique"],
                    title_color=PRIMARY)
    add_title_block(s, x + col_w + Inches(0.3), y, col_w, Inches(2.8), "Faisabilité",
                    ["sources disponibles (Kaggle, APIs)",
                     "volumétrie raisonnable (~100k lignes)",
                     "approche batch suffisante"],
                    title_color=SECOND)
    add_title_block(s, x + 2 * (col_w + Inches(0.3)), y, col_w, Inches(2.8),
                    "Critères de réussite",
                    ["périmètre clair",
                     "base stable et rejouable",
                     "restitution lisible"],
                    title_color=ACCENT)
    # SMART row
    smart_y = y + Inches(3.1)
    rows = [
        ["S", "Spécifique", "prévoir la consommation quotidienne par région"],
        ["M", "Mesurable", "qualité base + stabilité pipeline + lisibilité"],
        ["A", "Atteignable", "V1 limitée, batch, outils sobres"],
        ["R", "Réaliste", "ressources solo, délai maîtrisé"],
        ["T", "Temporel", "mise en place par étapes courtes"],
    ]
    add_table(s, x, smart_y, w, Inches(2.1), [["", "Axe", "Lecture retenue"]] + rows,
              font_size=12)

    # --- Slide 8 — E2 Cartographie données avec KPIs ------------------------
    s = std("E2", "20 min", "Cartographie des données",
            "Objets métier, sources et volumétrie effective")
    x, y, w, h = content_area()
    rows = [
        ["Objet métier", "Description", "Source / Variable"],
        ["Temps", "date, jour, mois, saison", "référentiel calendaire"],
        ["Territoire", "région, code région, maille", "INSEE / données énergie"],
        ["Énergie", "électricité, gaz, unité (kWh / MWh)", "Kaggle RTE + GRDF"],
        ["Météo", "température, précipitations, vent, humidité", "APIs Météo France / Open-Meteo"],
        ["Restitution", "indicateurs, jeux exposés", "FastAPI /docs"],
    ]
    add_table(s, x, y, w, Inches(2.8), rows, font_size=12)
    # Volumétrie cards
    kpi_y = y + Inches(3.1)
    kpi_w = (w - Inches(0.9)) // 4
    cards = [
        ("4 137", "jours (2013-2024)", PRIMARY),
        ("14", "régions françaises", SECOND),
        ("49 647", "lignes Silver / Gold", OK_GREEN),
        ("99 292", "lignes fact table", ACCENT),
    ]
    for i, (v, l, c) in enumerate(cards):
        px = x + i * (kpi_w + Inches(0.3))
        add_kpi_card(s, px, kpi_y, kpi_w, Inches(1.5), v, l, c)
    add_text(s, x, kpi_y + Inches(1.8), w, Inches(0.35),
             "Une source n'est utile que si l'on sait y accéder, la transformer et l'exploiter proprement.",
             size=13, color=TEXT_MUTE, align=PP_ALIGN.CENTER, bold=True)

    # --- Slide 9 — E2 Stack & risques ---------------------------------------
    s = std("E2", "20 min", "Décisions de stack et risques",
            "Relier le besoin métier à un dispositif data soutenable")
    x, y, w, h = content_area()
    # Stack flow
    flow_y = y
    flow_h = Inches(1.5)
    items = [("Ingestion", "Python + scripts", PRIMARY),
             ("Stockage", "Bronze/Silver/Gold", SECOND),
             ("SQL", "SQLite + requêtes", OK_GREEN),
             ("API", "FastAPI / docs", ACCENT),
             ("Orchestration", "Airflow local", RGBColor(0x6A, 0x1B, 0x9A))]
    seg_w = (w - Inches(0.4)) // len(items)
    for i, (t, sub, c) in enumerate(items):
        sx = x + i * (seg_w + Inches(0.1))
        box = add_rect(s, sx, flow_y, seg_w, flow_h, fill=c)
        tb = s.shapes.add_textbox(sx, flow_y + Inches(0.3), seg_w, Inches(0.5))
        tf = tb.text_frame
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = t
        r.font.bold = True; r.font.size = Pt(14); r.font.color.rgb = WHITE
        r.font.name = "Calibri"
        tb2 = s.shapes.add_textbox(sx, flow_y + Inches(0.85), seg_w, Inches(0.4))
        tf2 = tb2.text_frame
        p2 = tf2.paragraphs[0]; p2.alignment = PP_ALIGN.CENTER
        r2 = p2.add_run(); r2.text = sub
        r2.font.size = Pt(10); r2.font.color.rgb = WHITE; r2.font.name = "Calibri"
    # Pourquoi / risques
    col_w = (w - Inches(0.3)) // 2
    col_y = flow_y + flow_h + Inches(0.3)
    add_title_block(s, x, col_y, col_w, Inches(2.7), "Pourquoi cette stack ?",
                    ["volumétrie raisonnable → pas de cluster nécessaire",
                     "batch suffisant → pas de streaming",
                     "bonne lisibilité pour l'oral",
                     "coût limité en V1, évolutif (GCS, Delta préparés)"],
                    title_color=PRIMARY)
    add_title_block(s, x + col_w + Inches(0.3), col_y, col_w, Inches(2.7),
                    "Principaux risques",
                    ["qualité variable des sources externes",
                     "dérive du périmètre (scope creep)",
                     "temps de préparation des données",
                     "diffusion et accès aux APIs officielles"],
                    title_color=RGBColor(0xC0, 0x39, 0x2B))

    # --- Slide 10 — E3 Lancement --------------------------------------------
    s = std("E3", "10 min", "Lancement du projet",
            "Objet de la réunion et répartition des responsabilités")
    x, y, w, h = content_area()
    # Intro card
    card = add_rect(s, x, y, w, Inches(1.1), fill=NEUTRAL_BG, line=PRIMARY)
    tb = s.shapes.add_textbox(x + Inches(0.3), y + Inches(0.15),
                              w - Inches(0.6), Inches(0.8))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run(); r.text = "Objet du lancement : "
    r.font.bold = True; r.font.size = Pt(16); r.font.color.rgb = PRIMARY
    r.font.name = "Calibri"
    r2 = p.add_run()
    r2.text = ("Partager un cadre commun, valider le périmètre V1 et préciser "
               "l'organisation de la suite.")
    r2.font.size = Pt(16); r2.font.color.rgb = TEXT_DARK; r2.font.name = "Calibri"
    # RACI table
    rows = [
        ["Acteur", "Responsabilité principale"],
        ["Direction", "priorités métier et arbitrages"],
        ["DSI", "choix techniques et accès"],
        ["DPO", "conformité et diffusion"],
        ["Service données", "qualité des jeux et traitements"],
        ["Porteur du projet (moi)", "coordination, réalisation, livrables"],
    ]
    add_table(s, x, y + Inches(1.4), w, Inches(3.5), rows, font_size=13)

    # --- Slide 11 — E3 Feuille de route --------------------------------------
    s = std("E3", "10 min", "Feuille de route",
            "Phases de travail et livrables attendus")
    x, y, w, h = content_area()
    phases = [
        ("Lancement", "besoin | périmètre | rôles"),
        ("Ingestion", "sources | accès | Bronze"),
        ("Préparation", "nettoyage | harmonisation | Silver"),
        ("Structuration", "Gold | DWH | idempotence"),
        ("Restitution", "API | livrables | soutenance"),
    ]
    seg_w = (w - Inches(0.4)) // len(phases)
    flow_y = y + Inches(0.5)
    for i, (t, sub) in enumerate(phases):
        sx = x + i * (seg_w + Inches(0.1))
        # phase box
        box = add_rect(s, sx, flow_y, seg_w, Inches(2.0),
                       fill=WHITE, line=PRIMARY)
        # header
        hd = add_rect(s, sx, flow_y, seg_w, Inches(0.5), fill=PRIMARY)
        tb = s.shapes.add_textbox(sx, flow_y + Inches(0.08), seg_w, Inches(0.35))
        tf = tb.text_frame
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = f"Phase {i+1}"
        r.font.bold = True; r.font.size = Pt(12); r.font.color.rgb = WHITE
        r.font.name = "Calibri"
        # title
        tb2 = s.shapes.add_textbox(sx, flow_y + Inches(0.6), seg_w, Inches(0.5))
        tf2 = tb2.text_frame
        p2 = tf2.paragraphs[0]; p2.alignment = PP_ALIGN.CENTER
        r2 = p2.add_run(); r2.text = t
        r2.font.bold = True; r2.font.size = Pt(15); r2.font.color.rgb = TEXT_DARK
        r2.font.name = "Calibri"
        # sub
        tb3 = s.shapes.add_textbox(sx + Inches(0.05), flow_y + Inches(1.15),
                                   seg_w - Inches(0.1), Inches(0.8))
        tf3 = tb3.text_frame; tf3.word_wrap = True
        p3 = tf3.paragraphs[0]; p3.alignment = PP_ALIGN.CENTER
        r3 = p3.add_run(); r3.text = sub
        r3.font.size = Pt(11); r3.font.color.rgb = TEXT_MUTE
        r3.font.name = "Calibri"
    add_text(s, x, flow_y + Inches(2.4), w, Inches(0.6),
             "Planification simple : phases courtes, livrables clairs, validations régulières.",
             size=14, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

    # --- Slide 12 — E3 Suivi --------------------------------------------------
    s = std("E3", "10 min", "Suivi et communication",
            "Supervision, arbitrages et adaptation aux interlocuteurs")
    x, y, w, h = content_area()
    col_w = (w - Inches(0.3)) // 2
    rows1 = [
        ["Élément", "Ce qui est observé"],
        ["Avancement", "jalons atteints, tâches terminées"],
        ["Charge", "temps passé, efforts à venir"],
        ["Blocages", "dépendances, retards, arbitrages"],
        ["Décisions", "validations métier, techniques, conformité"],
    ]
    add_table(s, x, y, col_w, Inches(3.3), rows1, font_size=12)
    rows2 = [
        ["Interlocuteur", "Support / Attente"],
        ["Direction", "synthèse courte — périmètre et risques"],
        ["DSI", "support technique — archi, accès, contraintes"],
        ["DPO", "note claire — conformité et diffusion"],
        ["Équipe projet", "compte rendu — avancement et blocages"],
    ]
    add_table(s, x + col_w + Inches(0.3), y, col_w, Inches(3.3), rows2, font_size=12)

    # --- Slide 13 — E4 Architecture ------------------------------------------
    s = std("E4", "15 min", "Architecture technique",
            "Du besoin de données à une chaîne démontrable")
    x, y, w, h = content_area()
    # Medallion flow
    stages = [
        ("Sources", "Kaggle • APIs • référentiels", PRIMARY),
        ("Bronze", "donnée brute\nrejouable", RGBColor(0x8D, 0x6E, 0x63)),
        ("Silver", "nettoyée\nharmonisée", RGBColor(0x90, 0xA4, 0xAE)),
        ("Gold", "DWH en étoile\nfact + dims", ACCENT),
        ("Usage", "API FastAPI\nSQL direct", OK_GREEN),
    ]
    seg_w = (w - Inches(0.5)) // len(stages)
    flow_y = y + Inches(0.3)
    flow_h = Inches(2.2)
    for i, (t, sub, c) in enumerate(stages):
        sx = x + i * (seg_w + Inches(0.1))
        box = add_rect(s, sx, flow_y, seg_w, flow_h, fill=c)
        tb = s.shapes.add_textbox(sx + Inches(0.1), flow_y + Inches(0.3),
                                  seg_w - Inches(0.2), Inches(0.6))
        tf = tb.text_frame
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = t
        r.font.bold = True; r.font.size = Pt(20); r.font.color.rgb = WHITE
        r.font.name = "Calibri"
        tb2 = s.shapes.add_textbox(sx + Inches(0.1), flow_y + Inches(1.0),
                                   seg_w - Inches(0.2), Inches(1.0))
        tf2 = tb2.text_frame; tf2.word_wrap = True
        p2 = tf2.paragraphs[0]; p2.alignment = PP_ALIGN.CENTER
        r2 = p2.add_run(); r2.text = sub
        r2.font.size = Pt(12); r2.font.color.rgb = WHITE; r2.font.name = "Calibri"
        # arrow
        if i < len(stages) - 1:
            ar_x = sx + seg_w + Inches(0.005)
            ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, ar_x,
                                    flow_y + flow_h/2 - Inches(0.15),
                                    Inches(0.09), Inches(0.3))
            set_fill(ar, TEXT_MUTE)
    add_text(s, x, flow_y + flow_h + Inches(0.4), w, Inches(0.6),
             "Le bloc E4 pose le socle technique : collecte → préparation → lecture SQL → exposition API.",
             size=14, bold=True, color=TEXT_DARK, align=PP_ALIGN.CENTER)
    # 5 KPIs
    kpi_y = flow_y + flow_h + Inches(1.1)
    kpi_w = (w - Inches(0.8)) // 5
    cards = [("6", "endpoints API", PRIMARY),
             ("4", "zones medallion", SECOND),
             ("9", "tables SQL", OK_GREEN),
             ("8", "tâches Airflow", ACCENT),
             ("≈100k", "lignes chargées", RGBColor(0x6A, 0x1B, 0x9A))]
    for i, (v, l, c) in enumerate(cards):
        px = x + i * (kpi_w + Inches(0.2))
        add_kpi_card(s, px, kpi_y, kpi_w, Inches(1.3), v, l, c)

    # --- Slide 14 — E4 Arborescence ------------------------------------------
    s = std("E4", "15 min", "Arborescence du dépôt",
            "Séparer les responsabilités pour garder un code lisible")
    x, y, w, h = content_area()
    col_w = (w - Inches(0.3)) // 2
    tree_items = [
        "code/",
        "├── app/                  cœur applicatif",
        "│   ├── ingestion/         extraction sources",
        "│   ├── processing/        nettoyage & features",
        "│   ├── db/                loaders, repositories, SQL",
        "│   ├── api/               exposition FastAPI",
        "│   ├── ml/                baseline ML",
        "│   └── governance/        RBAC, cycle de vie",
        "├── airflow/               DAGs & Dockerfile",
        "├── atlas/                 catalogue & lignage",
        "├── configs/               yaml config",
        "├── scripts/               points d'entrée CLI",
        "├── sql/                   requêtes paramétrées",
        "├── tests/                 pytest",
        "└── docs/                  ADR & dossiers",
    ]
    tb = s.shapes.add_textbox(x, y, col_w, Inches(4.8))
    tf = tb.text_frame; tf.word_wrap = True
    for i, it in enumerate(tree_items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = p.add_run(); r.text = it
        r.font.name = "Consolas"
        r.font.size = Pt(12)
        r.font.color.rgb = TEXT_DARK if i > 0 else PRIMARY
        r.font.bold = (i == 0)
    add_title_block(s, x + col_w + Inches(0.3), y, col_w, Inches(4.8),
                    "Pourquoi cette structure",
                    ["ingestion : extraire, logger, tracer le bronze",
                     "processing : construire le silver reproductible",
                     "db : orchestrer loaders + repositories SQL",
                     "api : exposer sans logique métier dupliquée",
                     "ml : isoler la baseline pour itérer",
                     "governance : RBAC, rétention, monitoring",
                     "tests : coupler pytest aux modules critiques",
                     "— Pas de script monolithique, base réutilisable."],
                    title_color=PRIMARY)

    # --- Slide 15 — E4 SQL + API ---------------------------------------------
    s = std("E4", "15 min", "Requête SQL et exposition API",
            "Deux artefacts simples qui rendent le bloc E4 crédible")
    x, y, w, h = content_area()
    col_w = (w - Inches(0.3)) // 2
    sql_code = (
        "-- sql/feature_aggregations.sql\n"
        "SELECT\n"
        "  date, region,\n"
        "  electricity_consumption,\n"
        "  gas_consumption\n"
        "FROM silver_energy_weather_daily\n"
        "WHERE (:region IS NULL OR region = :region)\n"
        "  AND date BETWEEN :start_date AND :end_date\n"
        "ORDER BY date, region;"
    )
    api_code = (
        "# app/api/routers/features.py\n"
        "@router.get('', response_model=list[FeatureRecord])\n"
        "def get_features(\n"
        "    start_date: date, end_date: date,\n"
        "    region: str | None = None,\n"
        "):\n"
        "    rows = repository.fetch_features(\n"
        "        start_date, end_date, region)\n"
        "    return [FeatureRecord(**r) for r in rows]"
    )
    for i, (label, code, color) in enumerate([
        ("SQL paramétré", sql_code, SECOND),
        ("FastAPI router", api_code, OK_GREEN),
    ]):
        cx = x + i * (col_w + Inches(0.3))
        # header
        hd = add_rect(s, cx, y, col_w, Inches(0.4), fill=color)
        tb = s.shapes.add_textbox(cx + Inches(0.15), y + Inches(0.06),
                                  col_w - Inches(0.3), Inches(0.3))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        r = p.add_run(); r.text = label
        r.font.bold = True; r.font.size = Pt(14); r.font.color.rgb = WHITE
        r.font.name = "Calibri"
        # code block
        code_box = add_rect(s, cx, y + Inches(0.45), col_w, Inches(3.3),
                            fill=RGBColor(0x1F, 0x2A, 0x44))
        tb = s.shapes.add_textbox(cx + Inches(0.15), y + Inches(0.55),
                                  col_w - Inches(0.3), Inches(3.1))
        tf = tb.text_frame; tf.word_wrap = True
        for j, line in enumerate(code.split("\n")):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            r = p.add_run(); r.text = line
            r.font.name = "Consolas"; r.font.size = Pt(11)
            r.font.color.rgb = RGBColor(0xE0, 0xE8, 0xF0)
    add_text(s, x, y + Inches(4.0), w, Inches(0.6),
             "⇒ Le SQL prépare la lecture Silver, l'API réutilise cette logique pour exposer un jeu consultable.",
             size=13, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

    # --- Slide 16 — E4 Airflow (NEW) -----------------------------------------
    s = std("E4", "15 min", "Orchestration Airflow (démo live)",
            "DAG energy_datalake_batch — 8 tâches exécutées bout en bout")
    x, y, w, h = content_area()
    # DAG chain
    tasks = ["init_db", "transform", "load", "gold",
             "manifest", "atlas_export", "monitoring", "backup"]
    seg_w = (w - Inches(0.8)) // len(tasks)
    flow_y = y + Inches(0.5)
    for i, t in enumerate(tasks):
        sx = x + i * (seg_w + Inches(0.1))
        box = add_rect(s, sx, flow_y, seg_w, Inches(1.0), fill=OK_GREEN)
        tb = s.shapes.add_textbox(sx, flow_y + Inches(0.2), seg_w, Inches(0.4))
        tf = tb.text_frame
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = t
        r.font.bold = True; r.font.size = Pt(11); r.font.color.rgb = WHITE
        r.font.name = "Consolas"
        tb2 = s.shapes.add_textbox(sx, flow_y + Inches(0.6), seg_w, Inches(0.3))
        tf2 = tb2.text_frame
        p2 = tf2.paragraphs[0]; p2.alignment = PP_ALIGN.CENTER
        r2 = p2.add_run(); r2.text = "✓"
        r2.font.bold = True; r2.font.size = Pt(14); r2.font.color.rgb = WHITE
    # under KPIs
    col_w = (w - Inches(0.3)) // 2
    col_y = flow_y + Inches(1.4)
    add_title_block(s, x, col_y, col_w, Inches(2.5), "Stack Airflow",
                    ["image apache/airflow:2.10.5-python3.11",
                     "exécuté via docker compose (container unique)",
                     "SequentialExecutor + SQLite metadata",
                     "code app monté en read-only sur /opt/prevision-energie",
                     "contraintes Airflow respectées (pip --constraint)"],
                    title_color=PRIMARY)
    add_title_block(s, x + col_w + Inches(0.3), col_y, col_w, Inches(2.5),
                    "Preuves démo",
                    ["UI : http://localhost:8080 (admin / admin)",
                     "DAG activé, trigger manuel réussi",
                     "durée totale ≈ 53 s pour les 8 tâches",
                     "logs accessibles par tâche dans l'UI",
                     "aucune dépendance conflit (constraint file)"],
                    title_color=OK_GREEN)

    # --- Slide 17 — E4 Parcours démo ----------------------------------------
    s = std("E4", "15 min", "Parcours de démonstration",
            "Préparer une démo courte, stable et lisible")
    x, y, w, h = content_area()
    # commands card
    add_title_block(s, x, y, w, Inches(1.6), "Commandes",
                    ["python scripts/run_soutenance_demo.py  → prépare la base",
                     "python scripts/run_api.py              → FastAPI sur /docs",
                     "docker compose -f airflow up -d        → orchestration"],
                    title_color=PRIMARY, body_size=13)
    # Parcours table
    rows = [
        ["Étape", "Action", "Preuve montrée"],
        ["1", "ouvrir le dépôt", "structure lisible, séparation app/"],
        ["2", "exécuter run_soutenance_demo", "Silver + Gold préparées"],
        ["3", "exécuter la requête SQL", "retour lignes Silver"],
        ["4", "ouvrir Swagger /docs", "6 routers, endpoint features"],
        ["5", "appeler /features?region=…", "réponse JSON cohérente"],
        ["6", "ouvrir Airflow UI", "DAG success, 8 tâches vertes"],
    ]
    add_table(s, x, y + Inches(1.9), w, Inches(3.0), rows, font_size=12)

    # --- Slide 18 — E5 DWH Gold ---------------------------------------------
    s = std("E5", "10 min", "Modélisation DWH Gold",
            "Schéma en étoile — fact + dimensions")
    x, y, w, h = content_area()
    # Star diagram
    center_x = x + w//2 - Inches(1.0)
    center_y = y + Inches(1.3)
    # fact in center
    fact = add_rect(s, center_x, center_y, Inches(2.0), Inches(1.3), fill=ACCENT)
    tb = s.shapes.add_textbox(center_x, center_y + Inches(0.1), Inches(2.0), Inches(0.6))
    tf = tb.text_frame; p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = "fact_energy_"
    r.font.bold = True; r.font.size = Pt(13); r.font.color.rgb = WHITE
    r.font.name = "Calibri"
    tb = s.shapes.add_textbox(center_x, center_y + Inches(0.4), Inches(2.0), Inches(0.4))
    tf = tb.text_frame; p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = "consumption_daily"
    r.font.bold = True; r.font.size = Pt(13); r.font.color.rgb = WHITE
    r.font.name = "Calibri"
    tb = s.shapes.add_textbox(center_x, center_y + Inches(0.85), Inches(2.0), Inches(0.4))
    tf = tb.text_frame; p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = "99 292 lignes"
    r.font.size = Pt(12); r.font.color.rgb = WHITE; r.font.name = "Calibri"
    # dims around
    dims = [
        ("dim_date", "4 137", Inches(-3.5), Inches(-0.5)),
        ("dim_region", "14", Inches(3.5), Inches(-0.5)),
        ("dim_energy", "2", Inches(-3.5), Inches(1.5)),
        ("dim_weather_context", "46", Inches(3.5), Inches(1.5)),
    ]
    for name, n, dx, dy in dims:
        bx = center_x + dx + Inches(0.5)
        by = center_y + dy
        box = add_rect(s, bx, by, Inches(1.8), Inches(0.9), fill=PRIMARY)
        tb = s.shapes.add_textbox(bx, by + Inches(0.08), Inches(1.8), Inches(0.4))
        tf = tb.text_frame; p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = name
        r.font.bold = True; r.font.size = Pt(12); r.font.color.rgb = WHITE
        r.font.name = "Calibri"
        tb2 = s.shapes.add_textbox(bx, by + Inches(0.45), Inches(1.8), Inches(0.35))
        tf2 = tb2.text_frame; p2 = tf2.paragraphs[0]; p2.alignment = PP_ALIGN.CENTER
        r2 = p2.add_run(); r2.text = f"{n} lignes"
        r2.font.size = Pt(11); r2.font.color.rgb = WHITE
        r2.font.name = "Calibri"
        # connector
        conn = s.shapes.add_connector(1,
            bx + (Inches(0.9) if dx < 0 else Inches(0.9)),
            by + Inches(0.45),
            center_x + Inches(1.0), center_y + Inches(0.65))
        conn.line.color.rgb = TEXT_MUTE
        conn.line.width = Pt(1.2)
    # caption
    add_text(s, x, y + Inches(4.4), w, Inches(0.8),
             "Grain = date × région × énergie  •  lecture décisionnelle facilitée",
             size=15, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

    # --- Slide 19 — E5 Pipeline idempotent ----------------------------------
    s = std("E5", "10 min", "Pipeline Silver → Gold et idempotence",
            "Le chargement doit rester stable quand on le rejoue")
    x, y, w, h = content_area()
    # Loader chain
    steps = ["read_silver()", "_prepare_silver()", "_build_dim_*()",
             "_build_fact()", "_refresh_service_table()"]
    seg_w = (w - Inches(0.5)) // len(steps)
    flow_y = y
    for i, st in enumerate(steps):
        sx = x + i * (seg_w + Inches(0.1))
        box = add_rect(s, sx, flow_y, seg_w, Inches(0.8), fill=ACCENT)
        tb = s.shapes.add_textbox(sx, flow_y + Inches(0.2), seg_w, Inches(0.4))
        tf = tb.text_frame
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = st
        r.font.bold = True; r.font.size = Pt(11); r.font.color.rgb = WHITE
        r.font.name = "Consolas"
        if i < len(steps) - 1:
            ar_x = sx + seg_w + Inches(0.005)
            ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, ar_x,
                                    flow_y + Inches(0.3),
                                    Inches(0.09), Inches(0.2))
            set_fill(ar, TEXT_MUTE)
    rows = [
        ["Élément", "Lecture retenue"],
        ["Clé métier du fait", "date + région + énergie"],
        ["Chargement", "upsert (ON CONFLICT DO UPDATE)"],
        ["Stabilité", "pas de doublons à la relance"],
        ["Compatibilité", "gold_daily_features conservée"],
    ]
    add_table(s, x, flow_y + Inches(1.1), w, Inches(2.6), rows, font_size=13)
    add_text(s, x, flow_y + Inches(3.9), w, Inches(0.5),
             "⇒ Rejouer avec les mêmes données produit le même résultat (idempotence).",
             size=14, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

    # --- Slide 20 — E5 ML baseline (NEW) ------------------------------------
    s = std("E5", "10 min", "Baseline ML (C15 - C16)",
            "Premier modèle de prévision exploitant la Gold")
    x, y, w, h = content_area()
    col_w = (w - Inches(0.3)) // 2
    add_title_block(s, x, y, col_w, Inches(3.3), "Approche baseline",
                    ["Features Gold : météo + calendrier + région + énergie",
                     "2 cibles distinctes : électricité / gaz",
                     "Split temporel (pas de fuite de données)",
                     "Modèle simple : régression (scikit-learn)",
                     "Point d'entrée : python scripts/run_ml_baseline.py",
                     "Sorties sérialisées + métriques (MAE / RMSE)"],
                    title_color=ACCENT)
    add_title_block(s, x + col_w + Inches(0.3), y, col_w, Inches(3.3),
                    "Pourquoi une baseline",
                    ["établir un seuil mesurable avant d'optimiser",
                     "prouver que la Gold est exploitable telle quelle",
                     "boucler Bronze → Silver → Gold → ML (pipeline complet)",
                     "ouvrir la voie à LightGBM / Prophet en V2",
                     "objectif : justifier les choix d'architecture",
                     "pas une finalité du projet"],
                    title_color=PRIMARY)
    add_text(s, x, y + Inches(3.6), w, Inches(0.4),
             "La baseline ferme la boucle : du besoin métier à une prédiction mesurée.",
             size=14, bold=True, color=OK_GREEN, align=PP_ALIGN.CENTER)

    # --- Slide 21 — E6 Catalogue Atlas --------------------------------------
    s = std("E6", "5-10 min", "Catalogue et lignage",
            "Rendre les actifs plus lisibles, traçables et évolutifs")
    x, y, w, h = content_area()
    rows = [
        ["Dimension", "Apport"],
        ["Sémantique", "glossaire métier et vocabulaire partagé"],
        ["Modèles", "description des tables et objets"],
        ["Flux / lignage", "chaîne source → traitement → sortie"],
        ["Usage", "lecture, fréquence, points de consommation"],
    ]
    add_table(s, x, y, w, Inches(2.3), rows, font_size=12)
    # Bundle files
    add_title_block(s, x, y + Inches(2.5), w, Inches(1.5), "Atlas bundle — fichiers exportés",
                    ["atlas/glossary/prevision_energie_glossary.json",
                     "atlas/entities/core_entities.json",
                     "atlas/processes/lineage_processes.json",
                     "atlas/atlas_bundle.json (agrégé)"],
                    title_color=SECOND, body_size=12)
    # Lineage
    lineage = ["Kaggle / APIs", "Bronze", "Silver", "Gold", "DWH", "API"]
    flow_y = y + Inches(4.2)
    seg_w = (w - Inches(0.5)) // len(lineage)
    for i, t in enumerate(lineage):
        sx = x + i * (seg_w + Inches(0.05))
        box = add_rect(s, sx, flow_y, seg_w, Inches(0.45), fill=PRIMARY)
        tb = s.shapes.add_textbox(sx, flow_y + Inches(0.08), seg_w, Inches(0.3))
        tf = tb.text_frame
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = t
        r.font.bold = True; r.font.size = Pt(11); r.font.color.rgb = WHITE
        r.font.name = "Calibri"

    # --- Slide 22 — E6 SCD2 --------------------------------------------------
    s = std("E6", "5-10 min", "SCD Type 2 sur dim_region",
            "Historiser une dimension sans écraser la version précédente")
    x, y, w, h = content_area()
    rows = [
        ["Colonne / mécanisme", "Rôle"],
        ["region_key", "clé de substitution (surrogate)"],
        ["region_code", "clé naturelle métier"],
        ["valid_from / valid_to", "période de validité de la ligne"],
        ["is_current", "version active (flag booléen)"],
        ["attr_hash_md5", "détection simple des changements"],
    ]
    add_table(s, x, y, w, Inches(3.0), rows, font_size=12)
    add_title_block(s, x, y + Inches(3.3), w, Inches(1.7), "Principe et lecture V1",
                    ["Changement détecté → clôture de l'ancienne ligne (valid_to)",
                     "Insertion d'une nouvelle version avec is_current = true",
                     "La fact table pointe sur la version pertinente par date",
                     "V1 : SCD2 implémenté sur dim_region uniquement (lisibilité démo)"],
                    title_color=SECOND)

    # --- Slide 23 — E7 Data Lake zones --------------------------------------
    s = std("E7", "10 min", "Architecture Data Lake et cycle de vie",
            "Requalifier l'existant avec une lecture plus gouvernée")
    x, y, w, h = content_area()
    zones = [
        ("Raw", "≈ Bronze", "trace source • rejouabilité", PRIMARY, "longue"),
        ("Curated", "≈ Silver", "fiabilisation • harmonisation", SECOND, "raisonnable"),
        ("Consumption", "≈ Gold", "DWH + restitution • usage métier", ACCENT, "plus courte"),
    ]
    seg_w = (w - Inches(0.4)) // len(zones)
    for i, (name, equiv, role, c, ret) in enumerate(zones):
        sx = x + i * (seg_w + Inches(0.2))
        box = add_rect(s, sx, y, seg_w, Inches(2.8), fill=c)
        tb = s.shapes.add_textbox(sx + Inches(0.2), y + Inches(0.3),
                                  seg_w - Inches(0.4), Inches(0.6))
        tf = tb.text_frame
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = name
        r.font.bold = True; r.font.size = Pt(24); r.font.color.rgb = WHITE
        r.font.name = "Calibri"
        tb = s.shapes.add_textbox(sx + Inches(0.2), y + Inches(1.0),
                                  seg_w - Inches(0.4), Inches(0.4))
        tf = tb.text_frame
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = equiv
        r.font.italic = True; r.font.size = Pt(14); r.font.color.rgb = WHITE
        r.font.name = "Calibri"
        tb = s.shapes.add_textbox(sx + Inches(0.2), y + Inches(1.6),
                                  seg_w - Inches(0.4), Inches(0.7))
        tf = tb.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = role
        r.font.size = Pt(12); r.font.color.rgb = WHITE; r.font.name = "Calibri"
        tb = s.shapes.add_textbox(sx + Inches(0.2), y + Inches(2.3),
                                  seg_w - Inches(0.4), Inches(0.4))
        tf = tb.text_frame
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = f"rétention : {ret}"
        r.font.bold = True; r.font.size = Pt(11); r.font.color.rgb = WHITE
        r.font.name = "Calibri"
    add_text(s, x, y + Inches(3.1), w, Inches(0.5),
             "E7 ne remplace pas l'existant : il lui donne une lecture Data Lake plus mature.",
             size=14, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    add_text(s, x, y + Inches(3.7), w, Inches(0.4),
             "Rétention pilotée par configs/retention_policy.yml • documentée dans app/governance/lifecycle.py",
             size=12, color=TEXT_MUTE, align=PP_ALIGN.CENTER)

    # --- Slide 24 — E7 Gouvernance RBAC -------------------------------------
    s = std("E7", "10 min", "Gouvernance, RBAC et lecture de maturité",
            "Distinguer ce qui tourne déjà de ce qui prépare la suite")
    x, y, w, h = content_area()
    rows = [
        ["Rôle", "Lecture simplifiée"],
        ["data_reader", "consulter les jeux exposés (API + SQL lecture)"],
        ["data_engineer", "lire, écrire, exécuter les traitements"],
        ["data_admin", "administrer les accès et la gouvernance"],
    ]
    add_table(s, x, y, w, Inches(1.9), rows, font_size=13)
    # 3-col maturity
    col_w = (w - Inches(0.4)) // 3
    col_y = y + Inches(2.2)
    add_title_block(s, x, col_y, col_w, Inches(2.7), "✓ Implémenté localement",
                    ["pipeline batch Python",
                     "stockage local (SQLite + zones)",
                     "SQL paramétré + FastAPI",
                     "DWH Gold + RBAC applicatif",
                     "DAG Airflow local"],
                    title_color=OK_GREEN)
    add_title_block(s, x + col_w + Inches(0.2), col_y, col_w, Inches(2.7),
                    "Préparé pour la suite",
                    ["backend GCS (factory storage)",
                     "scripts Delta Lake",
                     "Atlas bundle (format live)",
                     "configs de rétention",
                     "Airflow ready production"],
                    title_color=ACCENT)
    add_title_block(s, x + 2 * (col_w + Inches(0.2)), col_y, col_w, Inches(2.7),
                    "Hors périmètre V1",
                    ["ingestion temps réel",
                     "IAM entreprise / SSO",
                     "plateforme Atlas live",
                     "data lake cloud complet",
                     "MLOps déploiement continu"],
                    title_color=RGBColor(0xC0, 0x39, 0x2B))

    # --- Slide 25 — Compétences C1-C21 (NEW) --------------------------------
    s = std("QR", "—", "Alignement avec les compétences RNCP",
            "Couverture des 21 compétences par bloc")
    x, y, w, h = content_area()
    rows = [
        ["Bloc", "Compétences", "Preuves dans le projet"],
        ["1 — Besoin", "C1 → C7",
         "entretiens, SMART, périmètre V1, SWOT, cadrage DPO/DSI"],
        ["2 — Architecture", "C8 → C12",
         "stack Python/SQL/FastAPI, medallion, repo structuré, ADR"],
        ["3 — Mise en œuvre", "C13 → C17",
         "ETL idempotent, DWH Gold (fact + 4 dims), baseline ML, monitoring"],
        ["4 — Data Lake", "C18 → C21",
         "zones Raw/Curated/Consumption, Atlas, RBAC, rétention, DAG Airflow"],
    ]
    add_table(s, x, y, w, Inches(3.3), rows, font_size=12)
    add_text(s, x, y + Inches(3.6), w, Inches(0.5),
             "Chaque bloc documenté dans docs/ (ADR, dossiers E1-E7) + livré sur le dépôt.",
             size=13, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
    add_text(s, x, y + Inches(4.2), w, Inches(0.4),
             "Référentiel simplon.co : Expert Data Engineer niveau 7 — parcours complet E1 → E7.",
             size=12, color=TEXT_MUTE, align=PP_ALIGN.CENTER)

    # --- Slide 26 — Livrables concrets (NEW) --------------------------------
    s = std("QR", "—", "Livrables concrets du projet",
            "Ce qui tourne, ce qui se démontre")
    x, y, w, h = content_area()
    kpi_h = Inches(1.2)
    kpi_w = (w - Inches(0.9)) // 4
    cards = [
        ("9", "tables SQL", PRIMARY),
        ("6", "routers API", SECOND),
        ("8", "tâches Airflow", OK_GREEN),
        ("≈100k", "lignes chargées", ACCENT),
    ]
    for i, (v, l, c) in enumerate(cards):
        px = x + i * (kpi_w + Inches(0.3))
        add_kpi_card(s, px, y, kpi_w, kpi_h, v, l, c)
    # Artefacts list
    col_w = (w - Inches(0.3)) // 2
    col_y = y + Inches(1.5)
    add_title_block(s, x, col_y, col_w, Inches(3.4), "Exécutables",
                    ["prevision_energie.db (SQLite, toutes zones)",
                     "scripts/run_soutenance_demo.py",
                     "scripts/run_api.py (FastAPI /docs)",
                     "DAG airflow/dags/energy_datalake_batch.py",
                     "Dockerfile + docker-compose Airflow",
                     "baseline ML scripts/run_ml_baseline.py"],
                    title_color=OK_GREEN)
    add_title_block(s, x + col_w + Inches(0.3), col_y, col_w, Inches(3.4),
                    "Documentation & gouvernance",
                    ["atlas/atlas_bundle.json (catalogue)",
                     "docs/ADR-*.md (décisions techniques)",
                     "docs/dossier-E1..E7.md",
                     "configs/retention_policy.yml",
                     "app/governance/ (RBAC + monitoring)",
                     "tests/ pytest sur modules critiques"],
                    title_color=PRIMARY)

    # --- Slide 27 — Conclusion + Q&R ----------------------------------------
    s = std("QR", "10 min", "Conclusion et échanges",
            "Un même fil rouge du Bloc 1 au Bloc 4")
    x, y, w, h = content_area()
    # big quote
    qb = add_rect(s, x, y, w, Inches(1.5), fill=PRIMARY)
    tb = s.shapes.add_textbox(x + Inches(0.3), y + Inches(0.2),
                              w - Inches(0.6), Inches(1.1))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = ("Partir d'un besoin métier clair, construire un socle technique démontrable,\n"
              "structurer une couche analytique, puis formaliser une lecture Data Lake gouvernée.")
    r.font.size = Pt(18); r.font.color.rgb = WHITE; r.font.name = "Calibri"
    r.font.italic = True
    # 4 pillars
    pil_y = y + Inches(1.8)
    pil_w = (w - Inches(0.6)) // 4
    pils = [("Projet cohérent", PRIMARY),
            ("Démo maîtrisée", OK_GREEN),
            ("Montée en maturité", ACCENT),
            ("Crédible & défendable", SECOND)]
    for i, (t, c) in enumerate(pils):
        px = x + i * (pil_w + Inches(0.2))
        card = add_rect(s, px, pil_y, pil_w, Inches(1.2), fill=c)
        tb = s.shapes.add_textbox(px, pil_y + Inches(0.4), pil_w, Inches(0.5))
        tf = tb.text_frame
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = t
        r.font.bold = True; r.font.size = Pt(14); r.font.color.rgb = WHITE
        r.font.name = "Calibri"
    # Q&R
    add_text(s, x, pil_y + Inches(1.7), w, Inches(0.6),
             "Questions / échanges avec le jury",
             size=28, bold=True, color=TEXT_DARK, align=PP_ALIGN.CENTER)
    add_text(s, x, pil_y + Inches(2.4), w, Inches(0.4),
             "Merci pour votre attention.",
             size=16, color=TEXT_MUTE, align=PP_ALIGN.CENTER)

    # --- save ---------------------------------------------------------------
    prs.save(out_path)
    print(f"Wrote {out_path}  ({len(prs.slides)} slides)")


if __name__ == "__main__":
    import sys
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "MOHAMEDI_Ahmed_Soutenance_FINAL.pptx")
    build(out)
