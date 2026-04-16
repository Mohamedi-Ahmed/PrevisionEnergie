from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

try:
    from PIL import Image
except Exception:
    Image = None

BASE_DIR = Path(r'C:\Users\Ahmed\Desktop\Soutenance')
LIVRABLES_DIR = BASE_DIR / 'livrables' / 'finals'
DOCX_DIR = LIVRABLES_DIR / 'docx'
PROJECT_TITLE = (
    "Projet : Prévision de la consommation quotidienne d'électricité et de gaz "
    "par région française à partir des conditions météorologiques"
)

@dataclass(frozen=True)
class DocumentSpec:
    source_md: str
    target_docx: str
    title: str
    bloc: str
    project: str = PROJECT_TITLE
    author: str = 'Ahmed Mohamedi'
    organization: str | None = None
    version_label: str | None = None

DOCUMENTS = [
    DocumentSpec('E1_Grilles_entretien_FINAL.md', 'E1_Grilles_entretien_FINAL.docx', "E1 - Grilles d'entretien", 'Compétence / Bloc 1 - Étude de cas', organization='Organisation cible : opérateur énergétique', version_label='Version finale - Avril 2026'),
    DocumentSpec('E1_Note_de_synthese_FINAL.md', 'E1_Note_de_synthese_FINAL.docx', 'E1 - Note de synthèse', 'Compétence / Bloc 1 - Étude de cas', organization='Organisation cible : opérateur énergétique', version_label='Version finale - Avril 2026'),
    DocumentSpec('E2_Rapport_professionnel_FINAL.md', 'E2_Rapport_professionnel_FINAL.docx', 'E2 - Rapport professionnel', 'Compétence / Bloc 1 - Mise en situation professionnelle'),
    DocumentSpec('E3_Avant_projet_et_planification_FINAL.md', 'E3_Avant_projet_et_planification_FINAL.docx', 'E3 - Avant-projet et planification', 'Compétence / Bloc 1 - Jeu de rôle : lancement de projet'),
    DocumentSpec('E4_Rapport_professionnel_FINAL.md', 'E4_Rapport_professionnel_FINAL.docx', 'E4 - Rapport professionnel', 'Compétence / Bloc 2 - Collecte, stockage et mise à disposition'),
    DocumentSpec('E5_Rapport_professionnel_FINAL.md', 'E5_Rapport_professionnel_FINAL.docx', 'E5 - Rapport professionnel', 'Compétence / Bloc 3 - Modélisation et ETL DWH'),
    DocumentSpec('E6_Rapport_professionnel_FINAL.md', 'E6_Rapport_professionnel_FINAL.docx', 'E6 - Rapport professionnel', 'Compétence / Bloc 3 - Catalogue de données et variations de dimensions'),
    DocumentSpec('E7_Rapport_professionnel_FINAL.md', 'E7_Rapport_professionnel_FINAL.docx', 'E7 - Architecture et gouvernance Data Lake', 'Compétence / Bloc 4 - Encadrer la collecte massive avec un Data Lake'),
]

PHRASE_REPLACEMENTS = [
    ('a partir de', 'à partir de'), ('A partir de', 'À partir de'), ('a ce stade', 'à ce stade'), ('A ce stade', 'À ce stade'),
    ("a l'oral", "à l'oral"), ('a la fois', 'à la fois'), ('a la suite', 'à la suite'), ('mise a disposition', 'mise à disposition'),
    ('jeu de role', 'jeu de rôle'), ('cote client', 'côté client'), ('de facon', 'de façon'), ("d'une facon", "d'une façon"),
    ("point d'appui a", "point d'appui à"), ("point d'acces", "point d'accès"), ('au-dela', 'au-delà'), ('a court terme', 'à court terme'),
    ('A ces', 'À ces'), ('A ce', 'À ce'), ('comprÃƒÂ©hensible', 'compréhensible'),
]
WORD_REPLACEMENTS = {
    'Prevision': 'Prévision', 'prevision': 'prévision', 'electricite': 'électricité', 'Electricite': 'Électricité',
    'region': 'région', 'Region': 'Région', 'regions': 'régions', 'Regions': 'Régions', 'francaise': 'française',
    'francais': 'français', 'francaises': 'françaises', 'meteorologiques': 'météorologiques', 'meteo': 'météo',
    'Meteo': 'Météo', 'donnee': 'donnée', 'donnees': 'données', 'Donnee': 'Donnée', 'Donnees': 'Données',
    'synthese': 'synthèse', 'Synthese': 'Synthèse', 'etude': 'étude', 'Etude': 'Étude', 'etre': 'être', 'Etre': 'Être',
    'ete': 'été', 'deja': 'déjà', 'apres': 'après', 'tres': 'très', 'meme': 'même', 'coherent': 'cohérent',
    'coherente': 'cohérente', 'coherents': 'cohérents', 'coherence': 'cohérence', 'qualite': 'qualité', 'securite': 'sécurité',
    'fiabilite': 'fiabilité', 'tracabilite': 'traçabilité', 'retention': 'rétention', 'metier': 'métier', 'Metier': 'Métier',
    'execute': 'exécute', 'executee': 'exécutée', 'executees': 'exécutées', 'executer': 'exécuter', 'execution': 'exécution',
    'executable': 'exécutable', 'executables': 'exécutables', 'reel': 'réel', 'reelle': 'réelle', 'reels': 'réels',
    'reellement': 'réellement', 'entrepot': 'entrepôt', 'modele': 'modèle', 'modelisation': 'modélisation', 'Modelisation': 'Modélisation',
    'schema': 'schéma', 'Schema': 'Schéma', 'cles': 'clés', 'cle': 'clé', 'comprehensible': 'compréhensible',
    'maturite': 'maturité', 'necessaire': 'nécessaire', 'necessaires': 'nécessaires', 'theorique': 'théorique',
    'premiere': 'première', 'deuxieme': 'deuxième', 'troisieme': 'troisième', 'quatrieme': 'quatrième', 'cinquieme': 'cinquième',
    'huitieme': 'huitième', 'annee': 'année', 'annees': 'années', 'dediee': 'dédiée', 'separee': 'séparée', 'ecriture': 'écriture',
    'controle': 'contrôle', 'controles': 'contrôles', 'critere': 'critère', 'criteres': 'critères', 'methode': 'méthode',
    'competence': 'compétence', 'Competence': 'Compétence', 'role': 'rôle', 'Role': 'Rôle', 'tache': 'tâche', 'taches': 'tâches',
    'generale': 'générale', 'general': 'général', 'generer': 'générer', 'genere': 'génère', 'generee': 'générée', 'generees': 'générées',
    'derivee': 'dérivée', 'derivees': 'dérivées', 'particuliere': 'particulière', 'exposee': 'exposée', 'exposees': 'exposées',
    'preparee': 'préparée', 'preparees': 'préparées', 'prepare': 'préparé', 'realise': 'réalisé', 'realisee': 'réalisée',
    'realisees': 'réalisées', 'utilisee': 'utilisée', 'utilisees': 'utilisées', 'reutilisable': 'réutilisable',
    'reutilisation': 'réutilisation', 'Scenarios': 'Scénarios', 'scenarios': 'scénarios', 'Scenario': 'Scénario', 'scenario': 'scénario',
    'privilegies': 'privilégiés', 'privilegie': 'privilégié', 'privilegiee': 'privilégiée', 'presente': 'présente', 'presentes': 'présentes',
    'presentee': 'présentée', 'presenter': 'présenter', 'presentation': 'présentation', 'echanges': 'échanges', 'echange': 'échange',
    'mene': 'mené', 'menes': 'menés', 'menee': 'menée', 'menees': 'menées', 'decisions': 'décisions', 'decision': 'décision',
    'modalite': 'modalité', 'modalites': 'modalités', 'operateur': 'opérateur', 'operateurs': 'opérateurs', 'energetique': 'énergétique',
    'energetiques': 'énergétiques', 'perimetre': 'périmètre', 'perimetres': 'périmètres', 'visibilite': 'visibilité', 'lisibilite': 'lisibilité',
    'heterogene': 'hétérogène', 'heterogenes': 'hétérogènes', 'immediatement': 'immédiatement', 'ambiguite': 'ambiguïté',
    'hypotheses': 'hypothèses', 'deployee': 'déployée', 'deployees': 'déployées', 'maitrise': 'maîtrise', 'maitrisee': 'maîtrisée',
    'specifique': 'spécifique', 'specifiques': 'spécifiques', 'capacite': 'capacité', 'realite': 'réalité', 'realiste': 'réaliste',
    'regularite': 'régularité', 'regulier': 'régulier', 'reguliere': 'régulière', 'reguliers': 'réguliers', 'regulieres': 'régulières',
}


def normalize_french_text(text: str) -> str:
    out = text.replace('’', "'")
    for s, t in PHRASE_REPLACEMENTS:
        out = out.replace(s, t)
    for s, t in WORD_REPLACEMENTS.items():
        out = re.sub(rf'\b{re.escape(s)}\b', t, out)
    return out


def twips(mm: float) -> int:
    return int(mm / 25.4 * 1440)


def image_size(path: Path) -> tuple[int, int]:
    if path.suffix.lower() == '.svg':
        root = ET.fromstring(path.read_text(encoding='utf-8'))
        def parse(v: str | None):
            if not v:
                return None
            m = re.match(r'([0-9]+(?:\.[0-9]+)?)', v)
            return float(m.group(1)) if m else None
        w = parse(root.attrib.get('width'))
        h = parse(root.attrib.get('height'))
        if w and h:
            return int(w), int(h)
        vb = root.attrib.get('viewBox') or root.attrib.get('viewbox')
        if vb:
            parts = vb.replace(',', ' ').split()
            if len(parts) == 4:
                return int(float(parts[2])), int(float(parts[3]))
        return 800, 450
    if Image is not None:
        with Image.open(path) as img:
            return img.size
    return 800, 450


def para(text: str, style: str | None = None, bold: bool = False, italic: bool = False) -> str:
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ''
    run_props = ''
    if bold or italic:
        rp = []
        if bold:
            rp.append('<w:b/>')
        if italic:
            rp.append('<w:i/>')
        run_props = f"<w:rPr>{''.join(rp)}</w:rPr>"
    safe = escape(normalize_french_text(text))
    return f'<w:p>{style_xml}<w:r>{run_props}<w:t xml:space="preserve">{safe}</w:t></w:r></w:p>'


def image_paragraph(rid: str, cx: int, cy: int) -> str:
    return f'''<w:p><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"
      xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
      xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
      xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"
      xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
      <wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/><wp:docPr id="1" name="Image"/>
      <wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>
      <a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
      <pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="Image"/><pic:cNvPicPr/></pic:nvPicPr>
      <pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
      <pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
      </pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'''


def build_styles() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/>
    <w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="22"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:qFormat/>
    <w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:sz w:val="30"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:qFormat/>
    <w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="22"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:qFormat/>
    <w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:sz w:val="28"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:qFormat/>
    <w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:sz w:val="24"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="Caption"/><w:qFormat/>
    <w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:i/><w:sz w:val="18"/></w:rPr></w:style>
</w:styles>'''


def build_document(spec: DocumentSpec) -> tuple[str, dict[str, bytes], list[tuple[str, str]]]:
    md = (LIVRABLES_DIR / spec.source_md).read_text(encoding='utf-8')
    blocks: list[str] = []
    media: dict[str, bytes] = {}
    rels: list[tuple[str, str]] = []
    rid_counter = 1
    image_counter = 1

    blocks.append(para(spec.project, 'Title'))
    blocks.append(para(spec.author, 'Subtitle'))
    blocks.append(para(spec.title, 'Heading1'))
    blocks.append(para(spec.bloc, 'Heading2'))
    if spec.organization:
        blocks.append(para(spec.organization))
    if spec.version_label:
        blocks.append(para(spec.version_label))
    blocks.append(para(''))

    for raw in md.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            blocks.append(para(''))
            continue
        if stripped.startswith('## '):
            blocks.append(para(stripped[3:].strip(), 'Heading1'))
            continue
        if stripped.startswith('### '):
            blocks.append(para(stripped[4:].strip(), 'Heading2'))
            continue
        if stripped.startswith('![') and '](' in stripped and stripped.endswith(')'):
            caption = stripped[2:stripped.index('](')].strip()
            image_rel = stripped[stripped.index('](') + 2:-1].strip()
            image_path = (LIVRABLES_DIR / image_rel).resolve()
            if image_path.exists():
                ext = image_path.suffix.lower().lstrip('.')
                media_name = f'image{image_counter}.{ext}'
                rid = f'rId{rid_counter}'
                rels.append((rid, f'media/{media_name}'))
                media[media_name] = image_path.read_bytes()
                w_px, h_px = image_size(image_path)
                max_cx = int(6.0 * 914400)
                scale = min(1.0, max_cx / max(w_px, 1))
                cx = int(w_px * 9525 * scale)
                cy = int(h_px * 9525 * scale)
                blocks.append(image_paragraph(rid, cx, cy))
                blocks.append(para(caption, 'Caption'))
                rid_counter += 1
                image_counter += 1
            else:
                blocks.append(para(f'[Visuel manquant : {image_rel}]', 'Caption'))
            continue
        if stripped.startswith('- '):
            blocks.append(para('• ' + stripped[2:].strip()))
            continue
        blocks.append(para(stripped))

    sect = f'''<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="{twips(23.5)}" w:right="{twips(25.4)}" w:bottom="{twips(22)}" w:left="{twips(25.4)}" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>'''
    doc_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
 xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
 xmlns:v="urn:schemas-microsoft-com:vml"
 xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:w10="urn:schemas-microsoft-com:office:word"
 xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
 xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup"
 xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk"
 xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml"
 xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
 mc:Ignorable="w14 wp14"><w:body>{''.join(blocks)}{sect}</w:body></w:document>'''
    return doc_xml, media, rels


def build_content_types(media_names: list[str]) -> str:
    defaults = [
        ('rels', 'application/vnd.openxmlformats-package.relationships+xml'),
        ('xml', 'application/xml'),
    ]
    seen = set()
    for name in media_names:
        ext = name.rsplit('.', 1)[-1].lower()
        if ext in seen:
            continue
        seen.add(ext)
        ctype = {
            'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'gif': 'image/gif', 'svg': 'image/svg+xml'
        }.get(ext, 'application/octet-stream')
        defaults.append((ext, ctype))
    defs = ''.join(f'<Default Extension="{e}" ContentType="{c}"/>' for e, c in defaults)
    overrides = ''.join([
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>',
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>',
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
    ])
    return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">{defs}{overrides}</Types>'


def build_doc_rels(rels: list[tuple[str, str]]) -> str:
    image_rels = ''.join(
        f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="{target}"/>'
        for rid, target in rels
    )
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  {image_rels}
</Relationships>'''


def build_root_rels() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''


def build_core(spec: DocumentSpec) -> str:
    title = escape(spec.title)
    author = escape(spec.author)
    subject = escape(spec.bloc)
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{title}</dc:title><dc:subject>{subject}</dc:subject><dc:creator>{author}</dc:creator>
</cp:coreProperties>'''


def build_app() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>OpenAI Codex</Application></Properties>'''


def generate_docx(spec: DocumentSpec) -> Path:
    DOCX_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DOCX_DIR / spec.target_docx
    document_xml, media, rels = build_document(spec)
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', build_content_types(list(media.keys())))
        zf.writestr('_rels/.rels', build_root_rels())
        zf.writestr('docProps/core.xml', build_core(spec))
        zf.writestr('docProps/app.xml', build_app())
        zf.writestr('word/document.xml', document_xml)
        zf.writestr('word/styles.xml', build_styles())
        zf.writestr('word/_rels/document.xml.rels', build_doc_rels(rels))
        for name, data in media.items():
            zf.writestr(f'word/media/{name}', data)
    return out_path


def main() -> None:
    for spec in DOCUMENTS:
        print(generate_docx(spec))


if __name__ == '__main__':
    main()
