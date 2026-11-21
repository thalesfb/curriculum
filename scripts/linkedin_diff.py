"""
Script determinístico e somente leitura para comparação entre o export oficial do LinkedIn e data/cv.json.

Uso:
    python scripts/linkedin_diff.py <export.zip> [--cv data/cv.json] [--out linkedin-diff.md]
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import unicodedata
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union


EXPECTED_COLUMNS: Dict[str, List[str]] = {
    "Positions.csv": ["Company Name", "Title", "Description", "Location", "Started On", "Finished On"],
    "Education.csv": ["School Name", "Start Date", "End Date", "Notes", "Degree Name", "Activities"],
    "Skills.csv": ["Name"],
    "Certifications.csv": ["Name", "Url", "Authority", "Started On", "Finished On", "License Number"],
    "Languages.csv": ["Name", "Proficiency"],
    "Profile.csv": ["First Name", "Last Name", "Headline", "Summary", "Geo Location"],
    "Projects.csv": ["Title", "Description", "Url", "Started On", "Finished On"],
}

MONTH_MAP: Dict[str, str] = {
    # English
    "jan": "01", "january": "01",
    "feb": "02", "february": "02",
    "mar": "03", "march": "03",
    "apr": "04", "april": "04",
    "may": "05",
    "jun": "06", "june": "06",
    "jul": "07", "july": "07",
    "aug": "08", "august": "08",
    "sep": "09", "sept": "09", "september": "09",
    "oct": "10", "october": "10",
    "nov": "11", "november": "11",
    "dec": "12", "december": "12",
    # Portuguese
    "janeiro": "01",
    "fev": "02", "fevereiro": "02",
    "marco": "03", "março": "03",
    "abr": "04", "abril": "04",
    "mai": "05", "maio": "05",
    "junho": "06",
    "julho": "07",
    "ago": "08", "agosto": "08",
    "set": "09", "setembro": "09",
    "out": "10", "outubro": "10",
    "dez": "12", "dezembro": "12",
}


def normalize_text(text: Any) -> str:
    """Normaliza texto: casefold, sem acentos, espaços colapsados."""
    if text is None:
        return ""
    s = str(text)
    decomposed = unicodedata.normalize("NFKD", s)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    collapsed = re.sub(r"\s+", " ", stripped).strip()
    return collapsed.casefold()


def normalize_date(val: Any) -> Optional[str]:
    """
    Normaliza datas:
    "Jan 2024", "jan 2024", "2024", "jan. de 2024", "01/2024" -> "YYYY-MM" ou "YYYY"
    Vazio / Atual -> None
    """
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None

    norm = normalize_text(s)
    if norm in {"present", "presente", "atual", "atualidade", "current", "none", "null", "-", "nao informado"}:
        return None

    # Formato YYYY
    if re.fullmatch(r"\d{4}", s):
        return s

    # Formato YYYY-MM ou YYYY-MM-DD
    m = re.fullmatch(r"(\d{4})-(\d{1,2})(?:-\d{1,2})?", s)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}"

    # Formato MM/YYYY ou M/YYYY
    m = re.fullmatch(r"(\d{1,2})/(\d{4})", s)
    if m:
        return f"{m.group(2)}-{int(m.group(1)):02d}"

    # Tokens textuais com ano (ex: "Jan 2024", "jan. de 2024", "janeiro de 2024", "set. de 2023")
    tokens = re.findall(r"[a-zA-ZçÇáéíóúÁÉÍÓÚãõÃÕ]+|\d+", s)
    years = [t for t in tokens if re.fullmatch(r"\d{4}", t)]
    if years:
        year = years[0]
        for t in tokens:
            if t == year:
                continue
            t_norm = normalize_text(t)
            if t_norm in ("de", "em", "do", "da"):
                continue
            if re.fullmatch(r"\d{1,2}", t):
                m_val = int(t)
                if 1 <= m_val <= 12:
                    return f"{year}-{m_val:02d}"
            if t_norm in MONTH_MAP:
                return f"{year}-{MONTH_MAP[t_norm]}"
        return year

    return s


def truncate_preview(text: Any, max_len: int = 120) -> str:
    """Colapsa espaços e trunca texto para as primeiras ~120 chars."""
    if not text:
        return "(vazio)"
    collapsed = re.sub(r"\s+", " ", str(text)).strip()
    if len(collapsed) > max_len:
        return collapsed[:max_len] + "..."
    return collapsed


def find_zip_entry(zf: zipfile.ZipFile, target_filename: str) -> Optional[str]:
    """Localiza arquivo no ZIP por basename, ignorando maiúsculas e subpastas."""
    target_lower = target_filename.lower()
    for name in zf.namelist():
        if Path(name).name.lower() == target_lower:
            return name
    return None


def read_csv_from_zip(
    zf: zipfile.ZipFile, target_filename: str, expected_cols: List[str]
) -> Tuple[List[Dict[str, str]], Optional[str]]:
    """
    Lê CSV direto do ZIP sem extrair para disco.
    Trata encoding utf-8-sig e detecta cabeçalho ignorando preâmbulos (ex: linhas 'Notes:').
    """
    entry_name = find_zip_entry(zf, target_filename)
    if not entry_name:
        return [], f"Arquivo `{target_filename}` não encontrado no ZIP exportado."

    try:
        raw_bytes = zf.read(entry_name)
    except Exception as exc:
        return [], f"Erro ao ler `{target_filename}` do ZIP: {exc}"

    decoded_text = raw_bytes.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(decoded_text))
    expected_lower = {col.lower(): col for col in expected_cols}
    header_indices: Optional[Dict[str, int]] = None
    rows: List[Dict[str, str]] = []

    for raw_row in reader:
        if not raw_row or not any(cell.strip() for cell in raw_row):
            continue

        # Strip stray BOMs too (some exports carry one even after utf-8-sig decoding).
        cleaned_row = [cell.replace("﻿", "").strip() for cell in raw_row]

        if header_indices is None:
            matches = [i for i, cell in enumerate(cleaned_row) if cell.lower() in expected_lower]
            threshold = 1 if len(expected_cols) <= 2 else 2
            if len(matches) >= threshold:
                header_indices = {cell.lower(): idx for idx, cell in enumerate(cleaned_row)}
        else:
            row_dict: Dict[str, str] = {}
            for col_lower, original_col in expected_lower.items():
                if col_lower in header_indices and header_indices[col_lower] < len(cleaned_row):
                    row_dict[original_col] = cleaned_row[header_indices[col_lower]]
                else:
                    row_dict[original_col] = ""
            rows.append(row_dict)

    if header_indices is None:
        return [], f"Cabeçalho esperado não detectado em `{target_filename}`."

    return rows, None


class SectionDiff:
    """Armazena resultados de comparação de uma seção."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.coincidentes: int = 0
        self.so_linkedin: List[str] = []
        self.so_cv: List[str] = []
        self.divergentes: List[Tuple[str, List[str]]] = []

    @property
    def total_linkedin(self) -> int:
        return self.coincidentes + len(self.so_linkedin) + len(self.divergentes)

    @property
    def total_cv(self) -> int:
        return self.coincidentes + len(self.so_cv) + len(self.divergentes)


def compare_profile(li_rows: List[Dict[str, str]], cv_data: Dict[str, Any]) -> SectionDiff:
    diff = SectionDiff("Perfil")
    cv_personal = cv_data.get("personal", {})
    cv_summary = cv_data.get("summary", {})

    if not li_rows:
        if cv_personal:
            diff.so_cv.append("Perfil em cv.json")
        return diff

    li_p = li_rows[0]
    li_name = f"{li_p.get('First Name', '')} {li_p.get('Last Name', '')}".strip()
    li_headline = li_p.get("Headline", "").strip()
    li_summary = li_p.get("Summary", "").strip()
    li_location = li_p.get("Geo Location", "").strip()

    cv_name = cv_personal.get("name", "").strip()
    cv_loc = cv_personal.get("location", {})
    cv_loc_str = cv_loc.get("pt", "") if isinstance(cv_loc, dict) else str(cv_loc or "").strip()

    cv_titles = cv_personal.get("titles", {})
    all_cv_titles: List[str] = []
    for r_val in cv_titles.values():
        if isinstance(r_val, dict):
            all_cv_titles.extend([str(v) for v in r_val.values()])
        elif isinstance(r_val, str):
            all_cv_titles.append(r_val)

    main_cv_title = ""
    if "data-engineer" in cv_titles and isinstance(cv_titles["data-engineer"], dict):
        main_cv_title = cv_titles["data-engineer"].get("pt", "")
    elif cv_titles:
        first_v = next(iter(cv_titles.values()))
        main_cv_title = first_v.get("pt", "") if isinstance(first_v, dict) else str(first_v)

    main_cv_summary = ""
    if "data-engineer" in cv_summary and isinstance(cv_summary["data-engineer"], dict):
        main_cv_summary = cv_summary["data-engineer"].get("pt", "")
    elif cv_summary:
        first_s = next(iter(cv_summary.values()))
        main_cv_summary = first_s.get("pt", "") if isinstance(first_s, dict) else str(first_s)

    field_diffs: List[str] = []

    if li_name and cv_name and normalize_text(li_name) != normalize_text(cv_name):
        field_diffs.append(f"- **Nome**: LinkedIn: `{li_name}` | cv.json: `{cv_name}`")

    if li_location and cv_loc_str and normalize_text(li_location) != normalize_text(cv_loc_str):
        field_diffs.append(f"- **Localização**: LinkedIn: `{li_location}` | cv.json: `{cv_loc_str}`")

    if li_headline and all_cv_titles:
        if normalize_text(li_headline) not in [normalize_text(t) for t in all_cv_titles]:
            field_diffs.append(f"- **Título (Headline)**: LinkedIn: `{li_headline}` | cv.json: `{main_cv_title}`")

    if li_summary and main_cv_summary and normalize_text(li_summary) != normalize_text(main_cv_summary):
        field_diffs.append(
            f"- **Resumo (Summary)**: difere\n"
            f"  - LinkedIn: \"{truncate_preview(li_summary)}\"\n"
            f"  - cv.json: \"{truncate_preview(main_cv_summary)}\""
        )

    if field_diffs:
        diff.divergentes.append(("Perfil Principal", field_diffs))
    else:
        diff.coincidentes += 1

    return diff


def compare_experience(li_rows: List[Dict[str, str]], cv_data: Dict[str, Any]) -> SectionDiff:
    diff = SectionDiff("Experiência")
    cv_exp: List[Dict[str, Any]] = cv_data.get("experience", [])

    li_by_company: Dict[str, List[Dict[str, str]]] = {}
    for r in li_rows:
        key = normalize_text(r.get("Company Name", ""))
        li_by_company.setdefault(key, []).append(r)

    cv_by_company: Dict[str, List[Dict[str, Any]]] = {}
    for c in cv_exp:
        key = normalize_text(c.get("company", ""))
        cv_by_company.setdefault(key, []).append(c)

    all_keys = set(li_by_company.keys()) | set(cv_by_company.keys())

    for k in sorted(all_keys):
        li_list = li_by_company.get(k, [])
        cv_list = cv_by_company.get(k, [])

        if not cv_list:
            for item in li_list:
                comp = item.get("Company Name", "(sem empresa)")
                title = item.get("Title", "")
                diff.so_linkedin.append(f"{comp} ({title})" if title else comp)
            continue

        if not li_list:
            for item in cv_list:
                comp = item.get("company", "(sem empresa)")
                r_dict = item.get("role", {})
                title = r_dict.get("pt", "") if isinstance(r_dict, dict) else str(r_dict or "")
                diff.so_cv.append(f"{comp} ({title})" if title else comp)
            continue

        # Casamento com desempate por data de início
        pairs: List[Tuple[Dict[str, str], Dict[str, Any]]] = []
        unmatched_cv = list(cv_list)
        unmatched_li: List[Dict[str, str]] = []

        for li_item in li_list:
            li_st = normalize_date(li_item.get("Started On"))
            matched_c: Optional[Dict[str, Any]] = None
            if li_st:
                for c_item in unmatched_cv:
                    c_st = normalize_date(c_item.get("period", {}).get("start"))
                    if c_st == li_st:
                        matched_c = c_item
                        break
            if matched_c:
                pairs.append((li_item, matched_c))
                unmatched_cv.remove(matched_c)
            else:
                unmatched_li.append(li_item)

        while unmatched_li and unmatched_cv:
            pairs.append((unmatched_li.pop(0), unmatched_cv.pop(0)))

        for li_item in unmatched_li:
            comp = li_item.get("Company Name", "")
            title = li_item.get("Title", "")
            diff.so_linkedin.append(f"{comp} ({title})" if title else comp)

        for c_item in unmatched_cv:
            comp = c_item.get("company", "")
            r_dict = c_item.get("role", {})
            title = r_dict.get("pt", "") if isinstance(r_dict, dict) else str(r_dict or "")
            diff.so_cv.append(f"{comp} ({title})" if title else comp)

        for li_item, c_item in pairs:
            field_diffs: List[str] = []
            comp_name = c_item.get("company") or li_item.get("Company Name") or "Empresa"

            # Cargo
            li_title = li_item.get("Title", "").strip()
            c_role = c_item.get("role", {})
            c_roles = [c_role.get("pt", ""), c_role.get("en", ""), c_role.get("es", "")] if isinstance(c_role, dict) else [str(c_role or "")]
            c_roles_norm = [normalize_text(r) for r in c_roles if r]
            if li_title and c_roles_norm and normalize_text(li_title) not in c_roles_norm:
                field_diffs.append(f"- **Cargo**: LinkedIn: `{li_title}` | cv.json: `{c_roles[0]}`")

            # Início
            li_start = normalize_date(li_item.get("Started On"))
            c_start = normalize_date(c_item.get("period", {}).get("start"))
            if li_start != c_start:
                field_diffs.append(f"- **Início**: LinkedIn: `{li_start or 'Atual'}` | cv.json: `{c_start or 'Atual'}`")

            # Fim
            li_end = normalize_date(li_item.get("Finished On"))
            c_end = normalize_date(c_item.get("period", {}).get("end"))
            if li_end != c_end:
                field_diffs.append(f"- **Fim**: LinkedIn: `{li_end or 'Atual'}` | cv.json: `{c_end or 'Atual'}`")

            # Localização
            li_loc = li_item.get("Location", "").strip()
            c_loc = c_item.get("location", {})
            c_loc_str = c_loc.get("pt", "") if isinstance(c_loc, dict) else str(c_loc or "").strip()
            if li_loc and c_loc_str and normalize_text(li_loc) != normalize_text(c_loc_str):
                field_diffs.append(f"- **Localização**: LinkedIn: `{li_loc}` | cv.json: `{c_loc_str}`")

            # Descrição
            li_desc = li_item.get("Description", "").strip()
            bullets = c_item.get("bullets", [])
            c_desc = " ".join((b.get("pt", "") if isinstance(b, dict) else str(b)) for b in bullets).strip()
            if li_desc and c_desc and normalize_text(li_desc) != normalize_text(c_desc):
                field_diffs.append(
                    f"- **Descrição**: difere\n"
                    f"  - LinkedIn: \"{truncate_preview(li_desc)}\"\n"
                    f"  - cv.json: \"{truncate_preview(c_desc)}\""
                )

            if field_diffs:
                diff.divergentes.append((comp_name, field_diffs))
            else:
                diff.coincidentes += 1

    return diff


def compare_education(li_rows: List[Dict[str, str]], cv_data: Dict[str, Any]) -> SectionDiff:
    diff = SectionDiff("Formação")
    cv_edu: List[Dict[str, Any]] = cv_data.get("education", [])

    unmatched_cv = list(cv_edu)
    pairs: List[Tuple[Dict[str, str], Dict[str, Any]]] = []
    unmatched_li: List[Dict[str, str]] = []

    for li_item in li_rows:
        li_school = li_item.get("School Name", "").strip()
        li_degree = li_item.get("Degree Name", "").strip()
        matched: Optional[Dict[str, Any]] = None

        # 1. Match exato: instituicao + curso
        for c in unmatched_cv:
            c_inst = c.get("institution", "").strip()
            c_deg = c.get("degree", {})
            c_deg_pt = c_deg.get("pt", "") if isinstance(c_deg, dict) else str(c_deg or "")
            c_deg_all = [c_deg.get("pt", ""), c_deg.get("en", ""), c_deg.get("es", "")] if isinstance(c_deg, dict) else [str(c_deg or "")]

            if normalize_text(li_school) == normalize_text(c_inst):
                if normalize_text(li_degree) in [normalize_text(d) for d in c_deg_all if d]:
                    matched = c
                    break

        # 2. Match por instituição caso único
        if not matched:
            candidate_cv = [c for c in unmatched_cv if normalize_text(c.get("institution", "")) == normalize_text(li_school)]
            if len(candidate_cv) == 1:
                matched = candidate_cv[0]

        if matched:
            pairs.append((li_item, matched))
            unmatched_cv.remove(matched)
        else:
            unmatched_li.append(li_item)

    for li_item in unmatched_li:
        school = li_item.get("School Name", "(sem instituição)")
        deg = li_item.get("Degree Name", "")
        diff.so_linkedin.append(f"{school} - {deg}" if deg else school)

    for c in unmatched_cv:
        inst = c.get("institution", "(sem instituição)")
        c_deg = c.get("degree", {})
        deg = c_deg.get("pt", "") if isinstance(c_deg, dict) else str(c_deg or "")
        diff.so_cv.append(f"{inst} - {deg}" if deg else inst)

    for li_item, c in pairs:
        field_diffs: List[str] = []
        inst_name = c.get("institution") or li_item.get("School Name") or "Instituição"

        li_school = li_item.get("School Name", "").strip()
        c_inst = c.get("institution", "").strip()
        if normalize_text(li_school) != normalize_text(c_inst):
            field_diffs.append(f"- **Instituição**: LinkedIn: `{li_school}` | cv.json: `{c_inst}`")

        li_degree = li_item.get("Degree Name", "").strip()
        c_deg = c.get("degree", {})
        c_deg_pt = c_deg.get("pt", "") if isinstance(c_deg, dict) else str(c_deg or "")
        c_deg_all = [c_deg.get("pt", ""), c_deg.get("en", ""), c_deg.get("es", "")] if isinstance(c_deg, dict) else [str(c_deg or "")]
        if li_degree and normalize_text(li_degree) not in [normalize_text(d) for d in c_deg_all if d]:
            field_diffs.append(f"- **Curso / Grau**: LinkedIn: `{li_degree}` | cv.json: `{c_deg_pt}`")

        li_start = normalize_date(li_item.get("Start Date"))
        c_start = normalize_date(c.get("period", {}).get("start"))
        if li_start != c_start:
            field_diffs.append(f"- **Início**: LinkedIn: `{li_start or 'Atual'}` | cv.json: `{c_start or 'Atual'}`")

        li_end = normalize_date(li_item.get("End Date"))
        c_end = normalize_date(c.get("period", {}).get("end"))
        if li_end != c_end:
            field_diffs.append(f"- **Fim**: LinkedIn: `{li_end or 'Atual'}` | cv.json: `{c_end or 'Atual'}`")

        if field_diffs:
            diff.divergentes.append((inst_name, field_diffs))
        else:
            diff.coincidentes += 1

    return diff


def compare_certifications(li_rows: List[Dict[str, str]], cv_data: Dict[str, Any]) -> SectionDiff:
    diff = SectionDiff("Certificações")
    cv_certs: List[Dict[str, Any]] = cv_data.get("certifications", [])

    unmatched_cv = list(cv_certs)
    pairs: List[Tuple[Dict[str, str], Dict[str, Any]]] = []
    unmatched_li: List[Dict[str, str]] = []

    for li_item in li_rows:
        li_name = li_item.get("Name", "").strip()
        li_auth = li_item.get("Authority", "").strip()
        norm_li_name = normalize_text(li_name)
        norm_li_auth = normalize_text(li_auth)

        matched: Optional[Dict[str, Any]] = None

        # 1. Match direto por nome (pt, en, es)
        for c in unmatched_cv:
            c_name = c.get("name", {})
            c_names = [c_name.get("pt", ""), c_name.get("en", ""), c_name.get("es", "")] if isinstance(c_name, dict) else [str(c_name or "")]
            if norm_li_name in [normalize_text(n) for n in c_names if n]:
                matched = c
                break

        # 2. Fallback: provider + nome contido
        if not matched and norm_li_auth:
            for c in unmatched_cv:
                c_prov = normalize_text(c.get("provider", ""))
                c_name = c.get("name", {})
                c_names = [c_name.get("pt", ""), c_name.get("en", ""), c_name.get("es", "")] if isinstance(c_name, dict) else [str(c_name or "")]
                if c_prov == norm_li_auth:
                    if any(norm_li_name in normalize_text(n) or normalize_text(n) in norm_li_name for n in c_names if n):
                        matched = c
                        break

        # 3. Fallback: autoridade + nome combinados
        if not matched:
            for c in unmatched_cv:
                c_prov = normalize_text(c.get("provider", ""))
                c_name = c.get("name", {})
                c_pt = c_name.get("pt", "") if isinstance(c_name, dict) else str(c_name or "")
                if normalize_text(f"{norm_li_auth} {norm_li_name}") == normalize_text(f"{c_prov} {c_pt}"):
                    matched = c
                    break

        if matched:
            pairs.append((li_item, matched))
            unmatched_cv.remove(matched)
        else:
            unmatched_li.append(li_item)

    for li_item in unmatched_li:
        name = li_item.get("Name", "(sem nome)")
        auth = li_item.get("Authority", "")
        diff.so_linkedin.append(f"{name} ({auth})" if auth else name)

    for c in unmatched_cv:
        c_name = c.get("name", {})
        name = c_name.get("pt", "") if isinstance(c_name, dict) else str(c_name or "")
        prov = c.get("provider", "")
        diff.so_cv.append(f"{name} ({prov})" if prov else name)

    for li_item, c in pairs:
        field_diffs: List[str] = []
        c_name_obj = c.get("name", {})
        cert_display = c_name_obj.get("pt", "") if isinstance(c_name_obj, dict) else str(c_name_obj or li_item.get("Name", "Certificação"))

        li_auth = li_item.get("Authority", "").strip()
        c_prov = c.get("provider", "").strip()
        if li_auth and c_prov and normalize_text(li_auth) != normalize_text(c_prov):
            field_diffs.append(f"- **Emissor / Autoridade**: LinkedIn: `{li_auth}` | cv.json: `{c_prov}`")

        li_url = li_item.get("Url", "").strip()
        c_url = c.get("credentialUrl", "").strip()
        if li_url and c_url and normalize_text(li_url) != normalize_text(c_url):
            field_diffs.append(f"- **URL da Credencial**: LinkedIn: `{li_url}` | cv.json: `{c_url}`")

        li_start = normalize_date(li_item.get("Started On"))
        c_start = normalize_date(c.get("period", {}).get("start") or c.get("date"))
        if li_start and c_start and li_start != c_start:
            field_diffs.append(f"- **Início / Data**: LinkedIn: `{li_start}` | cv.json: `{c_start}`")

        li_end = normalize_date(li_item.get("Finished On"))
        c_end = normalize_date(c.get("period", {}).get("end"))
        if li_end and c_end and li_end != c_end:
            field_diffs.append(f"- **Fim**: LinkedIn: `{li_end}` | cv.json: `{c_end}`")

        if field_diffs:
            diff.divergentes.append((cert_display, field_diffs))
        else:
            diff.coincidentes += 1

    return diff


def compare_skills(li_rows: List[Dict[str, str]], cv_data: Dict[str, Any]) -> SectionDiff:
    diff = SectionDiff("Competências")
    raw_skills = cv_data.get("skills", {})

    cv_skill_items: Set[str] = set()
    cv_skill_canon: Dict[str, str] = {}

    if isinstance(raw_skills, dict):
        for grp in raw_skills.values():
            if isinstance(grp, dict):
                for item in grp.get("items", []):
                    item_str = str(item)
                    norm = normalize_text(item_str)
                    cv_skill_items.add(norm)
                    cv_skill_canon[norm] = item_str
                # Translations
                for orig, trs in grp.get("itemTranslations", {}).items():
                    if isinstance(trs, dict):
                        for tr_val in trs.values():
                            norm_tr = normalize_text(tr_val)
                            cv_skill_items.add(norm_tr)
                            cv_skill_canon[norm_tr] = str(orig)
    elif isinstance(raw_skills, list):
        for item in raw_skills:
            item_str = str(item)
            norm = normalize_text(item_str)
            cv_skill_items.add(norm)
            cv_skill_canon[norm] = item_str

    li_skill_items: Dict[str, str] = {}
    for r in li_rows:
        name = r.get("Name", "").strip()
        if name:
            li_skill_items[normalize_text(name)] = name

    all_keys = set(cv_skill_items) | set(li_skill_items.keys())

    for k in sorted(all_keys):
        in_li = k in li_skill_items
        in_cv = k in cv_skill_items

        if in_li and in_cv:
            diff.coincidentes += 1
        elif in_li:
            diff.so_linkedin.append(li_skill_items[k])
        elif in_cv:
            diff.so_cv.append(cv_skill_canon.get(k, k))

    # Remove duplicatas preservando ordem
    diff.so_cv = sorted(list(set(diff.so_cv)), key=normalize_text)
    diff.so_linkedin = sorted(list(set(diff.so_linkedin)), key=normalize_text)

    return diff


def compare_languages(li_rows: List[Dict[str, str]], cv_data: Dict[str, Any]) -> SectionDiff:
    diff = SectionDiff("Idiomas")
    cv_langs: List[Dict[str, Any]] = cv_data.get("languages", [])

    unmatched_cv = list(cv_langs)
    pairs: List[Tuple[Dict[str, str], Dict[str, Any]]] = []
    unmatched_li: List[Dict[str, str]] = []

    for li_item in li_rows:
        li_name = li_item.get("Name", "").strip()
        matched: Optional[Dict[str, Any]] = None

        for c in unmatched_cv:
            c_lang = c.get("language", {})
            c_names = [c_lang.get("pt", ""), c_lang.get("en", ""), c_lang.get("es", "")] if isinstance(c_lang, dict) else [str(c_lang or "")]
            if normalize_text(li_name) in [normalize_text(n) for n in c_names if n]:
                matched = c
                break

        if matched:
            pairs.append((li_item, matched))
            unmatched_cv.remove(matched)
        else:
            unmatched_li.append(li_item)

    for li_item in unmatched_li:
        name = li_item.get("Name", "")
        prof = li_item.get("Proficiency", "")
        diff.so_linkedin.append(f"{name} ({prof})" if prof else name)

    for c in unmatched_cv:
        c_lang = c.get("language", {})
        name = c_lang.get("pt", "") if isinstance(c_lang, dict) else str(c_lang or "")
        c_lvl = c.get("level", {})
        lvl = c_lvl.get("pt", "") if isinstance(c_lvl, dict) else str(c_lvl or "")
        diff.so_cv.append(f"{name} ({lvl})" if lvl else name)

    for li_item, c in pairs:
        field_diffs: List[str] = []
        c_lang_obj = c.get("language", {})
        lang_display = c_lang_obj.get("pt", "") if isinstance(c_lang_obj, dict) else str(c_lang_obj or li_item.get("Name", "Idioma"))

        li_prof = li_item.get("Proficiency", "").strip()
        c_lvl = c.get("level", {})
        c_lvls = [c_lvl.get("pt", ""), c_lvl.get("en", ""), c_lvl.get("es", "")] if isinstance(c_lvl, dict) else [str(c_lvl or "")]
        if li_prof and normalize_text(li_prof) not in [normalize_text(l) for l in c_lvls if l]:
            field_diffs.append(f"- **Nível / Proficiência**: LinkedIn: `{li_prof}` | cv.json: `{c_lvls[0]}`")

        if field_diffs:
            diff.divergentes.append((lang_display, field_diffs))
        else:
            diff.coincidentes += 1

    return diff


def compare_projects(li_rows: List[Dict[str, str]], cv_data: Dict[str, Any]) -> SectionDiff:
    diff = SectionDiff("Projetos")
    cv_projs: List[Dict[str, Any]] = cv_data.get("projects", [])

    unmatched_cv = list(cv_projs)
    pairs: List[Tuple[Dict[str, str], Dict[str, Any]]] = []
    unmatched_li: List[Dict[str, str]] = []

    for li_item in li_rows:
        li_title = li_item.get("Title", "").strip()
        matched: Optional[Dict[str, Any]] = None

        for c in unmatched_cv:
            c_name = c.get("name", "")
            c_lang_names = c.get("nameByLanguage", {})
            c_all = [c_name]
            if isinstance(c_lang_names, dict):
                c_all.extend([str(v) for v in c_lang_names.values()])
            if normalize_text(li_title) in [normalize_text(n) for n in c_all if n]:
                matched = c
                break

        if matched:
            pairs.append((li_item, matched))
            unmatched_cv.remove(matched)
        else:
            unmatched_li.append(li_item)

    for li_item in unmatched_li:
        title = li_item.get("Title", "(sem título)")
        diff.so_linkedin.append(title)

    for c in unmatched_cv:
        title = c.get("name") or c.get("nameByLanguage", {}).get("pt", "(sem título)")
        diff.so_cv.append(title)

    for li_item, c in pairs:
        field_diffs: List[str] = []
        proj_display = c.get("name") or c.get("nameByLanguage", {}).get("pt", li_item.get("Title", "Projeto"))

        # URL
        li_url = li_item.get("Url", "").strip()
        c_url = c.get("repo", "") or c.get("sourceUrl", "")
        if li_url and c_url and normalize_text(li_url) != normalize_text(c_url):
            field_diffs.append(f"- **URL / Repositório**: LinkedIn: `{li_url}` | cv.json: `{c_url}`")

        # Início
        li_start = normalize_date(li_item.get("Started On"))
        c_period = c.get("period", {})
        c_start = normalize_date(c_period.get("start") if isinstance(c_period, dict) else c_period)
        if li_start and c_start and li_start != c_start:
            field_diffs.append(f"- **Início**: LinkedIn: `{li_start}` | cv.json: `{c_start}`")

        # Fim
        li_end = normalize_date(li_item.get("Finished On"))
        c_end = normalize_date(c_period.get("end") if isinstance(c_period, dict) else None)
        if li_end and c_end and li_end != c_end:
            field_diffs.append(f"- **Fim**: LinkedIn: `{li_end}` | cv.json: `{c_end}`")

        # Descrição
        li_desc = li_item.get("Description", "").strip()
        c_desc_obj = c.get("description", {})
        c_desc = c_desc_obj.get("pt", "") if isinstance(c_desc_obj, dict) else str(c_desc_obj or "")
        if li_desc and c_desc and normalize_text(li_desc) != normalize_text(c_desc):
            field_diffs.append(
                f"- **Descrição**: difere\n"
                f"  - LinkedIn: \"{truncate_preview(li_desc)}\"\n"
                f"  - cv.json: \"{truncate_preview(c_desc)}\""
            )

        if field_diffs:
            diff.divergentes.append((proj_display, field_diffs))
        else:
            diff.coincidentes += 1

    return diff


def format_markdown_report(
    sections: List[SectionDiff], warnings: List[str], export_name: str, cv_name: str
) -> str:
    """Gera o relatório Markdown em PT-BR com ordenação determinística estável."""
    lines: List[str] = []
    lines.append("# Relatório de Comparação: LinkedIn vs cv.json\n")
    lines.append(f"- **Arquivo exportado**: `{export_name}`")
    lines.append(f"- **Fonte de dados**: `{cv_name}`\n")

    # Resumo Geral
    lines.append("## Resumo Geral\n")
    lines.append("| Seção | Coincidentes | Só no LinkedIn | Só no cv.json | Com divergências |")
    lines.append("| :--- | :---: | :---: | :---: | :---: |")

    tot_coin = 0
    tot_li = 0
    tot_cv = 0
    tot_div = 0

    for s in sections:
        c_coin = s.coincidentes
        c_li = len(s.so_linkedin)
        c_cv = len(s.so_cv)
        c_div = len(s.divergentes)

        tot_coin += c_coin
        tot_li += c_li
        tot_cv += c_cv
        tot_div += c_div

        lines.append(f"| {s.name} | {c_coin} | {c_li} | {c_cv} | {c_div} |")

    lines.append(f"| **Total** | **{tot_coin}** | **{tot_li}** | **{tot_cv}** | **{tot_div}** |\n")

    # Avisos
    if warnings:
        lines.append("## Avisos\n")
        for w in sorted(warnings):
            lines.append(f"- {w}")
        lines.append("")

    # Detalhamento por Seção
    lines.append("## Detalhamento por Seção\n")

    for s in sections:
        lines.append(f"### {s.name}\n")

        # Só no LinkedIn
        lines.append("#### Só no LinkedIn")
        if s.so_linkedin:
            for item in sorted(s.so_linkedin, key=normalize_text):
                lines.append(f"- {item}")
        else:
            lines.append("_Nenhum item._")
        lines.append("")

        # Só no cv.json
        lines.append("#### Só no cv.json")
        if s.so_cv:
            for item in sorted(s.so_cv, key=normalize_text):
                lines.append(f"- {item}")
        else:
            lines.append("_Nenhum item._")
        lines.append("")

        # Divergências
        lines.append("#### Divergências campo a campo")
        if s.divergentes:
            for ident, f_diffs in sorted(s.divergentes, key=lambda x: normalize_text(x[0])):
                lines.append(f"- **{ident}**")
                for fd in f_diffs:
                    lines.append(f"  {fd}")
        else:
            lines.append("_Nenhuma divergência._")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def compare_linkedin_cv(
    zip_source: Union[str, Path, io.BytesIO, zipfile.ZipFile],
    cv_source: Union[str, Path, Dict[str, Any]] = "data/cv.json",
    export_label: str = "LinkedIn Data Export",
    cv_label: str = "data/cv.json",
) -> Tuple[str, List[SectionDiff]]:
    """Compara o ZIP do LinkedIn com cv.json e retorna o relatório Markdown."""
    # Carrega cv.json
    if isinstance(cv_source, (str, Path)):
        cv_path = Path(cv_source)
        cv_data = json.loads(cv_path.read_text(encoding="utf-8"))
        cv_label = str(cv_path)
    else:
        cv_data = cv_source

    # Abre ZIP
    if isinstance(zip_source, zipfile.ZipFile):
        zf = zip_source
        close_zip = False
    elif isinstance(zip_source, io.BytesIO):
        zf = zipfile.ZipFile(zip_source, "r")
        close_zip = True
    else:
        zip_path = Path(zip_source)
        export_label = zip_path.name
        zf = zipfile.ZipFile(zip_path, "r")
        close_zip = True

    try:
        warnings: List[str] = []

        def get_rows(filename: str) -> List[Dict[str, str]]:
            rows, warn = read_csv_from_zip(zf, filename, EXPECTED_COLUMNS[filename])
            if warn:
                warnings.append(warn)
            return rows

        sections: List[SectionDiff] = [
            compare_profile(get_rows("Profile.csv"), cv_data),
            compare_experience(get_rows("Positions.csv"), cv_data),
            compare_education(get_rows("Education.csv"), cv_data),
            compare_certifications(get_rows("Certifications.csv"), cv_data),
            compare_skills(get_rows("Skills.csv"), cv_data),
            compare_languages(get_rows("Languages.csv"), cv_data),
            compare_projects(get_rows("Projects.csv"), cv_data),
        ]

        report = format_markdown_report(sections, warnings, export_label, cv_label)
        return report, sections
    finally:
        if close_zip:
            zf.close()


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compara deterministicamente o export oficial do LinkedIn (ZIP) com data/cv.json.",
    )
    parser.add_argument("export_zip", help="Caminho para o arquivo ZIP exportado do LinkedIn.")
    parser.add_argument(
        "--cv",
        default="data/cv.json",
        help="Caminho para o arquivo cv.json (padrão: data/cv.json).",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Caminho para salvar o relatório Markdown (padrão: imprime no stdout).",
    )

    args = parser.parse_args(argv)

    zip_path = Path(args.export_zip)
    if not zip_path.is_file() or not zipfile.is_zipfile(zip_path):
        sys.stderr.write(f"Erro: '{args.export_zip}' não é um arquivo ZIP válido.\n")
        return 2

    cv_path = Path(args.cv)
    if not cv_path.is_file():
        sys.stderr.write(f"Erro: Arquivo cv.json '{args.cv}' não foi encontrado.\n")
        return 1

    try:
        report, _ = compare_linkedin_cv(zip_path, cv_path)
    except Exception as exc:
        sys.stderr.write(f"Erro ao processar dados: {exc}\n")
        return 1

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
