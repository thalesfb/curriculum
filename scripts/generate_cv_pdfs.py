"""Generate the three downloadable CV PDFs from data/cv.json.

The DOCX is an immutable formatting template. This script changes only text
in its document XML, exports through Microsoft Word, and rejects pagination
changes instead of changing fonts, margins, or spacing to make content fit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "cv.json"
TEMPLATE_PATH = ROOT / "refs" / "template" / "curriculo_thales_ferreira_pt.docx"
EXPORTER_PATH = ROOT / "scripts" / "export_docx_pdf.ps1"
TEMPLATE_SHA256 = "0d7d807b48ec8bb6fde348b3b2439efe3e009be49cfcb8ba1a4c7df918d1d1d2"
EXPECTED_PAGE_COUNT = 3

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_NS = "http://www.w3.org/XML/1998/namespace"
NS = {"w": W_NS}
ET.register_namespace("w", W_NS)

OUTPUTS = {
    "pt": "curriculo_thales_ferreira_pt.pdf",
    "en": "resume_thales_ferreira_en.pdf",
    "es": "curriculo_thales_ferreira_es.pdf",
}

SECTION_KEYS = (
    "cv.summary",
    "cv.skills",
    "cv.experience",
    "cv.education",
    "cv.certifications",
    "cv.languages",
)

MONTHS = {
    "pt": ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"],
    "en": ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"],
    "es": ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"],
}

CURRENT_LABELS = {"pt": "Atual", "en": "Present", "es": "Actualidad"}


def localized(value: object, language: str) -> str:
    if not isinstance(value, dict) or language not in value:
        raise ValueError(f"Missing '{language}' translation in {value!r}")
    result = value[language]
    if not isinstance(result, str) or not result.strip():
        raise ValueError(f"Empty '{language}' translation in {value!r}")
    return result


def load_section_labels(ui_path: Path, language: str) -> list[str]:
    source = ui_path.read_text(encoding="utf-8")
    language_blocks = list(re.finditer(r"(?m)^  (pt|en|es): \{\n", source))
    block = next((match for match in language_blocks if match.group(1) == language), None)
    if block is None:
        raise ValueError(f"Missing UI translation block for {language}")
    following = next((match.start() for match in language_blocks if match.start() > block.start()), len(source))
    content = source[block.end():following]
    labels = []
    for key in SECTION_KEYS:
        match = re.search(rf"(?m)^\s*'{re.escape(key)}': '([^']*)',?$", content)
        if match is None or not match.group(1).strip():
            raise ValueError(f"Missing UI label {key!r} for {language}")
        labels.append(match.group(1))
    return labels


def localized_items(skill: dict, language: str) -> list[str]:
    translations = skill.get("itemTranslations", {})
    return [
        translations.get(item, {}).get(language, item)
        for item in skill["items"]
    ]


def select_for_role(items: list[dict], role: str) -> list[dict]:
    return [item for item in items if role in item.get("roles", [])]


def format_month(year_month: str, language: str) -> str:
    try:
        year, month = year_month.split("-", maxsplit=1)
        month_index = int(month) - 1
        return MONTHS[language][month_index]
    except (KeyError, ValueError, IndexError) as error:
        raise ValueError(f"Invalid date {year_month!r} for language {language!r}") from error


def _month_year(year_month: str, language: str) -> str:
    year = year_month.split("-", maxsplit=1)[0]
    month = format_month(year_month, language)
    if language == "en":
        return f"{month} {year}"
    return f"{month} DE {year}"


def format_period(start: str, end: str | None, language: str) -> str:
    finish = _month_year(end, language) if end else CURRENT_LABELS[language]
    return f"{_month_year(start, language)} - {finish}"


def validate_page_count(expected: int, actual: int, language: str) -> None:
    if actual != expected:
        raise ValueError(
            f"{language}: expected {expected} pages, got {actual}; "
            "content does not fit the fixed template. No PDF was published."
        )


def _text_nodes(element: ET.Element) -> list[ET.Element]:
    return element.findall(".//w:t", NS)


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in _text_nodes(paragraph))


def _set_node_text(node: ET.Element, value: str) -> None:
    node.text = value
    if value[:1].isspace() or value[-1:].isspace():
        node.set(f"{{{XML_NS}}}space", "preserve")
    else:
        node.attrib.pop(f"{{{XML_NS}}}space", None)


def set_paragraph_text(paragraph: ET.Element, value: str) -> None:
    nodes = _text_nodes(paragraph)
    if not nodes:
        run = ET.SubElement(paragraph, f"{{{W_NS}}}r")
        nodes = [ET.SubElement(run, f"{{{W_NS}}}t")]
    _set_node_text(nodes[0], value)
    for node in nodes[1:]:
        _set_node_text(node, "")


def set_paragraph_segments(paragraph: ET.Element, values: list[str]) -> None:
    """Replace text around existing manual line breaks without moving them."""
    segments: list[list[ET.Element]] = [[]]
    for element in paragraph.iter():
        if element.tag == f"{{{W_NS}}}br":
            segments.append([])
        elif element.tag == f"{{{W_NS}}}t":
            segments[-1].append(element)
    if len(segments) != len(values) or any(not nodes for nodes in segments):
        raise ValueError("Template contact line breaks changed; refusing to reflow them")
    for nodes, value in zip(segments, values, strict=True):
        _set_node_text(nodes[0], value)
        for node in nodes[1:]:
            _set_node_text(node, "")


def set_run_text(paragraph: ET.Element, run_index: int, value: str) -> None:
    runs = paragraph.findall("w:r", NS)
    if run_index >= len(runs):
        raise ValueError(f"Template paragraph has no run {run_index}")
    nodes = _text_nodes(runs[run_index])
    if not nodes:
        node = ET.SubElement(runs[run_index], f"{{{W_NS}}}t")
        nodes = [node]
    _set_node_text(nodes[0], value)
    for node in nodes[1:]:
        _set_node_text(node, "")


def _date_runs(start: str, end: str | None, language: str) -> tuple[str, str, str]:
    start_month = format_month(start, language) + " "
    start_year = start.split("-", maxsplit=1)[0]
    if end is None:
        middle = f"DE {start_year} - " if language != "en" else f"{start_year} - "
        return start_month, middle, CURRENT_LABELS[language]
    end_month = format_month(end, language)
    end_year = end.split("-", maxsplit=1)[0]
    if language == "en":
        return start_month, f"{start_year} - {end_month} {end_year}", ""
    return start_month, f"DE {start_year} - {end_month} DE {end_year}", ""


def _set_role_period(paragraph: ET.Element, role: str, period: dict, language: str) -> None:
    start_month, middle, end_label = _date_runs(period["start"], period.get("end"), language)
    set_run_text(paragraph, 0, role + " | ")
    set_run_text(paragraph, 1, start_month)
    set_run_text(paragraph, 2, middle)
    set_run_text(paragraph, 3, end_label)


def _set_date_line(paragraph: ET.Element, prefix: str, period: dict, language: str) -> None:
    set_run_text(paragraph, 0, prefix)
    set_run_text(paragraph, 1, format_period(period["start"], period.get("end"), language))


def _ensure_paragraph_anchors(paragraphs: list[ET.Element]) -> None:
    anchors = {
        0: "Thales Ferreira",
        7: "SUMÁRIO",
        9: "COMPETÊNCIAS",
        16: "EXPERIÊNCIA PROFISSIONAL",
        17: "OPTIMIZR",
        24: "CPEL",
        31: "CMAQ",
        34: "TBC NETWORK",
        37: "FORMAÇÃO ACADÊMICA",
        47: "CURSOS E CERTIFICAÇÕES",
        64: "IDIOMAS",
    }
    if len(paragraphs) != 68:
        raise ValueError(f"Unexpected template structure: expected 68 paragraphs, got {len(paragraphs)}")
    for index, expected in anchors.items():
        if not paragraph_text(paragraphs[index]).startswith(expected):
            raise ValueError(f"Template anchor {index} changed; refusing to rewrite the document")


def build_document_xml(source_xml: bytes, data: dict, language: str) -> bytes:
    if language not in OUTPUTS:
        raise ValueError(f"Unsupported language: {language}")
    for _, namespace in ET.iterparse(__import__("io").BytesIO(source_xml), events=("start-ns",)):
        prefix, uri = namespace
        ET.register_namespace(prefix or "", uri)
    root = ET.fromstring(source_xml)
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("DOCX template has no document body")
    paragraphs = body.findall("w:p", NS)
    _ensure_paragraph_anchors(paragraphs)

    # The downloadable documents are the data-engineer profile; role tags select its skills.
    skill_rows = paragraphs[10:16]
    skills = select_for_role(list(data["skills"].values()), "data-engineer")
    if len(skills) > len(skill_rows):
        raise ValueError(f"Template has {len(skill_rows)} skill rows for {len(skills)} JSON groups")

    lang = language
    labels = load_section_labels(ROOT / "src" / "i18n" / "ui.ts", lang)
    removed: list[ET.Element] = []
    set_paragraph_text(paragraphs[0], data["personal"]["name"])
    set_paragraph_text(paragraphs[1], localized(data["personal"]["titles"]["data-engineer"], lang))
    set_paragraph_text(paragraphs[3], localized(data["personal"]["location"], lang))
    set_paragraph_text(paragraphs[4], data["personal"]["phone"])
    linkedin_slug = data["personal"]["linkedin"].rstrip("/").split("/")[-1]
    set_paragraph_segments(paragraphs[5], [data["personal"]["email"], f"LinkedIn: /in/{linkedin_slug}"])
    github_slug = data["personal"]["github"].rstrip("/").split("/")[-1]
    set_paragraph_text(paragraphs[6], f"GitHub: /{github_slug}")

    for index, label in zip((7, 9, 16, 37, 47, 64), labels, strict=True):
        set_paragraph_text(paragraphs[index], label)
    set_paragraph_text(paragraphs[8], localized(data["summary"]["data-engineer"], lang))

    for row, skill in zip(skill_rows, skills, strict=False):
        set_run_text(row, 0, localized(skill["label"], lang))
        set_run_text(row, 1, ": " + ", ".join(localized_items(skill, lang)))
    removed.extend(skill_rows[len(skills):])

    experiences = data["experience"]
    if len(experiences) != 4:
        raise ValueError(f"Template expects four experience entries, got {len(experiences)}")
    experience_slots = [
        (17, 18, [19, 20, 21, 22]),
        (24, 25, [26, 27, 28, 29, 30]),
        (31, 32, [33]),
        (34, 35, [36]),
    ]
    for entry, (company_index, role_index, bullet_indexes) in zip(experiences, experience_slots, strict=True):
        company = entry["company"]
        location = localized(entry.get("location", {lang: ""}), lang) if entry.get("location") else ""
        if company_index == 34:
            company = company.upper()
        set_paragraph_text(paragraphs[company_index], f"{company}, {location}".rstrip(", "))
        if company_index == 17:
            _set_role_period(paragraphs[role_index], localized(entry["role"], lang), entry["period"], lang)
        elif company_index == 24:
            start_month, middle, end_label = _date_runs(entry["period"]["start"], entry["period"].get("end"), lang)
            set_run_text(paragraphs[role_index], 0, localized(entry["role"], lang) + " | ")
            set_run_text(paragraphs[role_index], 1, start_month)
            set_run_text(paragraphs[role_index], 2, middle + end_label)
        else:
            _set_date_line(paragraphs[role_index], localized(entry["role"], lang) + " | ", entry["period"], lang)

        bullets = entry["bullets"]
        if len(bullets) > len(bullet_indexes):
            raise ValueError(f"{entry['company']} has more JSON bullets than the template can hold")
        for index, bullet in zip(bullet_indexes, bullets, strict=False):
            set_paragraph_text(paragraphs[index], localized(bullet, lang))
        removed.extend(paragraphs[index] for index in bullet_indexes[len(bullets):])

    education = data["education"]
    if len(education) != 2:
        raise ValueError(f"Template expects two education entries, got {len(education)}")
    first, second = education
    set_paragraph_text(paragraphs[38], f"{first['institution']}, {first['location']}")
    set_run_text(
        paragraphs[39],
        0,
        f"{localized(first['degree'], lang)} | {localized(first['status'], lang)} | ",
    )
    set_run_text(paragraphs[39], 1, format_period(first["period"]["start"], first["period"].get("end"), lang))
    set_paragraph_text(paragraphs[41], f"{second['institution']}, {second['location']}")
    set_run_text(paragraphs[42], 0, localized(second["degree"], lang) + " | ")
    set_run_text(paragraphs[42], 1, format_period(second["period"]["start"], second["period"].get("end"), lang))

    certifications = data["certifications"]
    certification_headings = [48, 52, 56]
    certification_rows = [49, 50, 53, 54, 57, 58, 59, 62, 63]
    if len(certifications) != len(certification_rows):
        raise ValueError(f"Template expects nine certifications, got {len(certifications)}")
    providers: list[str] = []
    for certification in certifications:
        provider = certification["provider"]
        if not providers or providers[-1] != provider:
            providers.append(provider)
    if len(providers) > len(certification_headings):
        raise ValueError("Template has no heading slot for a new certification provider")
    for index, provider in zip(certification_headings, providers, strict=False):
        set_paragraph_text(paragraphs[index], provider)
    removed.extend(paragraphs[index] for index in certification_headings[len(providers):])
    for index, certification in zip(certification_rows, certifications, strict=True):
        name = localized(certification["name"], lang)
        details = certification.get("detailsByLanguage", {}).get(lang, certification.get("details"))
        set_paragraph_text(paragraphs[index], f"{name}: {details}" if details else name)

    languages = data["languages"]
    language_slots = [65, 66, 67]
    if len(languages) > len(language_slots):
        raise ValueError(f"Template has {len(language_slots)} language rows, got {len(languages)}")
    for index, entry in zip(language_slots, languages, strict=False):
        name = localized(entry["language"], lang)
        level = localized(entry["level"], lang)
        detail = localized(entry["detail"], lang) if entry.get("detail") else ""
        set_run_text(paragraphs[index], 0, name + ":")
        set_run_text(paragraphs[index], 1, f" {level}" + (f" – {detail}." if detail else ""))
    removed.extend(paragraphs[index] for index in language_slots[len(languages):])

    # The JSON has no SENAI/technical education records; remove those stale template paragraphs.
    removed.extend(paragraphs[index] for index in (43, 44, 45, 61))
    for paragraph in removed:
        if paragraph in list(body):
            body.remove(paragraph)

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def build_docx(template_path: Path, output_path: Path, data: dict, language: str) -> None:
    source_hash = hashlib.sha256(template_path.read_bytes()).hexdigest()
    if source_hash != TEMPLATE_SHA256:
        raise ValueError(
            "DOCX template changed; revalidate its formatting and update the pinned checksum before generation"
        )
    with zipfile.ZipFile(template_path, "r") as source, zipfile.ZipFile(output_path, "w") as target:
        for info in source.infolist():
            content = source.read(info.filename)
            if info.filename == "word/document.xml":
                content = build_document_xml(content, data, language)
            target.writestr(info, content)


def _experience_page_pairs(data: dict, language: str) -> list[str]:
    pairs = []
    for entry in data["experience"]:
        company = entry["company"]
        if company.casefold() == "tbc network eireli":
            company = company.upper()
        location = localized(entry["location"], language)
        first_bullet = localized(entry["bullets"][0], language)
        pairs.append(f"{company}, {location}|{first_bullet[:36]}")
    return pairs


def export_docx(
    docx_path: Path,
    pdf_path: Path,
    language: str,
    data: dict,
    allow_overflow_preview: bool,
) -> None:
    if sys.platform != "win32":
        raise RuntimeError("PDF generation requires Microsoft Word on Windows to preserve the DOCX layout")
    command = [
        "pwsh",
        "-NoProfile",
        "-NonInteractive",
        "-File",
        str(EXPORTER_PATH),
        "-Source",
        str(docx_path),
        "-Pdf",
        str(pdf_path),
        "-ExpectedPages",
        str(EXPECTED_PAGE_COUNT),
        "-RequiredPairsJson",
        json.dumps(_experience_page_pairs(data, language)),
        ]
    if allow_overflow_preview:
        command.append("-AllowOverflowPreview")
    subprocess.run(command, check=True)
    if not pdf_path.is_file() or not pdf_path.read_bytes().startswith(b"%PDF-"):
        raise RuntimeError(f"Word did not create a valid PDF: {pdf_path}")


def generate(output_dir: Path, allow_overflow_preview: bool = False) -> list[Path]:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="curriculum-cv-") as temp_dir:
        temp = Path(temp_dir)
        staged: list[tuple[Path, Path]] = []
        for language, filename in OUTPUTS.items():
            docx = temp / f"curriculum-{language}.docx"
            pdf = temp / filename
            build_docx(TEMPLATE_PATH, docx, data, language)
            export_docx(docx, pdf, language, data, allow_overflow_preview)
            staged.append((pdf, output_dir / filename))
        for source, destination in staged:
            shutil.copy2(source, destination)
    return [destination for _, destination in staged]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="output directory (default: public/refs, or a temp folder with --preview)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="export review-only PDFs even when overflow checks fail; never write to public/refs",
    )
    args = parser.parse_args()
    try:
        output_dir = args.output_dir
        if output_dir is None:
            output_dir = Path(tempfile.gettempdir()) / "cv-generation-preview" if args.preview else ROOT / "public" / "refs"
        output_dir = output_dir.resolve()
        public_refs = (ROOT / "public" / "refs").resolve()
        if args.preview and output_dir == public_refs:
            raise ValueError("--preview cannot write to public/refs")
        for path in generate(output_dir, args.preview):
            print(f"Generated {path}")
    except (OSError, ValueError, subprocess.CalledProcessError, zipfile.BadZipFile) as error:
        print(f"PDF generation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
