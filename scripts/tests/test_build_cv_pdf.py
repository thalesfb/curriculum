import collections
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.build_cv_pdf import OUTPUTS, ROOT, resolve_output_dir


DATA = json.loads((ROOT / "data" / "cv.json").read_text(encoding="utf-8"))
ROLE = "data-engineer"
TOOLS = ("typst", "pdfinfo", "pdffonts", "pdftotext")
MISSING_TOOLS = [name for name in TOOLS if shutil.which(name) is None]
PDF_TEST_SKIP = "PDF integration checks need Typst and Poppler tools: " + ", ".join(MISSING_TOOLS)
CERTIFICATION_STATUS_LABELS = {"pt": "Em andamento", "en": "In progress", "es": "En curso"}


def localized(value, language):
    if isinstance(value, dict):
        return value.get(language, value.get("pt", ""))
    return value


def source_texts(language):
    personal = DATA["personal"]
    texts = [personal["name"], personal["email"], personal["phone"], personal["linkedin"], personal["github"]]
    if personal.get("lattes"):
        texts.append(personal["lattes"].split("//")[-1])
    texts += [localized(personal["location"], language), localized(personal["titles"][ROLE], language)]
    texts.append(localized(DATA["summary"][ROLE], language))
    for item in DATA["experience"]:
        if ROLE not in item.get("roles", []):
            continue
        texts += [localized(item["role"], language), item["company"]]
        if item.get("location") is not None:
            texts.append(localized(item["location"], language))
        texts += [localized(bullet, language) for bullet in item["bullets"] if ROLE in bullet.get("roles", [])]
    for item in DATA["projects"]:
        if ROLE not in item.get("roles", []):
            continue
        texts += [localized(item.get("nameByLanguage", item["name"]), language)]
        texts += [item[key] for key in ("repo", "institution", "coordinator") if item.get(key)]
        texts += [localized(item[key], language) for key in ("period", "participation", "description", "supervision") if item.get(key)]
        texts += item.get("technologies", [])
    for item in DATA["education"]:
        if ROLE in item.get("roles", []):
            for value in (localized(item["degree"], language), item["institution"], localized(item["location"], language)):
                texts.extend(tokens(value))
    for item in DATA["certifications"]:
        texts.append(localized(item["name"], language))
        if item.get("editions"):
            texts.append(localized(item["editions"], language))
        if item.get("hours"):
            hour_label = f'{item["hours"]}h'
            if item.get("hoursYear"):
                hour_label += f' ({item["hoursYear"]})'
            texts.append(hour_label)
        provider = item.get("providerByLanguage", {}).get(language, item.get("provider"))
        if provider and provider not in ("Não informado", "Not specified", "No especificado"):
            texts.append(provider)
    alura_total = sum(item["hours"] for item in DATA["certifications"] if item.get("provider") == "Alura")
    texts += ["Alura", f"{alura_total}h"]
    for skill in DATA["skills"].values():
        if ROLE not in skill.get("roles", []):
            continue
        texts.append(localized(skill["label"], language))
        for item in skill["items"]:
            texts.append(skill.get("itemTranslations", {}).get(item, {}).get(language, item))
    for item in DATA["languages"]:
        texts += [localized(item["language"], language), localized(item["level"], language)]
        if item.get("detail"):
            texts.append(localized(item["detail"], language))
    return texts


def format_date(value, language):
    if value is None:
        return {"pt": "Atual", "en": "Present", "es": "Actualidad"}[language]
    months = {
        "pt": ("janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"),
        "en": ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"),
        "es": ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"),
    }
    month = months[language][int(value[5:7]) - 1]
    year = value[:4]
    return f"{month} {year}" if language == "en" else f"{month} de {year}"


def formatted_dates(language):
    values = []
    for collection in ("experience", "education"):
        for item in DATA[collection]:
            if ROLE in item.get("roles", []):
                values.extend(format_date(item["period"][key], language) for key in ("start", "end"))
    for item in DATA["certifications"]:
        if item.get("date"):
            values.append(format_date(item["date"], language))
        if item.get("period"):
            period = item["period"]
            values.append(format_date(period["start"], language))
            if period["end"][:7] != period["start"][:7]:
                values.append(format_date(period["end"], language))
    return values


def tokens(text):
    return re.findall(r"[^\W_]+", text.casefold(), flags=re.UNICODE)


def bbox_lines(pdf, page_number):
    result = subprocess.run(
        ["pdftotext", "-bbox-layout", "-f", str(page_number), "-l", str(page_number), str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    root = ET.fromstring(result.stdout)
    page = root.find(".//{http://www.w3.org/1999/xhtml}page")
    if page is None:
        raise AssertionError(f"Missing page {page_number} in bbox output for {pdf}")
    lines = []
    for element in page.findall(".//{http://www.w3.org/1999/xhtml}line"):
        text = " ".join("".join(element.itertext()).split())
        if text:
            lines.append({
                "text": text,
                "xMin": float(element.attrib["xMin"]),
                "xMax": float(element.attrib["xMax"]),
                "yMin": float(element.attrib["yMin"]),
                "yMax": float(element.attrib["yMax"]),
            })
    return float(page.attrib["width"]), lines


def visual_rows(lines, baseline_tolerance=0.5):
    rows = []
    for line in sorted(lines, key=lambda item: (item["yMin"], item["xMin"])):
        if rows and line["yMin"] - rows[-1]["yMin"] <= baseline_tolerance:
            row = rows[-1]
            row["xMin"] = min(row["xMin"], line["xMin"])
            row["xMax"] = max(row["xMax"], line["xMax"])
            row["yMin"] = min(row["yMin"], line["yMin"])
            row["yMax"] = max(row["yMax"], line["yMax"])
            row["text"] += " | " + line["text"]
        else:
            rows.append(dict(line))
    return rows


@unittest.skipUnless(not MISSING_TOOLS, PDF_TEST_SKIP)
class GeneratedPdfTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory(prefix="curriculum-pdf-tests-")
        cls.output_dir = Path(cls.temp_dir.name)
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "build_cv_pdf.py"),
                "--output-dir",
                str(cls.output_dir),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise AssertionError(f"CV PDF generation failed in tests:\n{result.stderr}\n{result.stdout}")

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_each_language_uses_embedded_libertinus_and_fits_in_two_pages(self):
        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                pdf = self.output_dir / filename
                info = subprocess.run(["pdfinfo", str(pdf)], check=True, capture_output=True, text=True).stdout
                page_match = re.search(r"(?m)^Pages:\s+(\d+)$", info)
                self.assertIsNotNone(page_match, info)
                self.assertEqual(int(page_match.group(1)), 2, info)

                fonts = subprocess.run(["pdffonts", str(pdf)], check=True, capture_output=True, text=True).stdout
                font_rows = [
                    line
                    for line in fonts.splitlines()
                    if line.strip() and not line.startswith("name") and not line.startswith("-")
                ]
                self.assertTrue(font_rows, fonts)
                for row in font_rows:
                    columns = row.split()
                    self.assertGreaterEqual(len(columns), 8, row)
                    self.assertIn("libertinusserif", columns[0].casefold(), row)
                    self.assertRegex(row, r"\byes\s+yes\s+yes\s+\d+\s+\d+$", row)

    def test_sections_follow_summary_education_experience_order(self):
        section_order = {
            "pt": ("SUMÁRIO", "FORMAÇÃO", "EXPERIÊNCIA", "PROJETOS", "COMPETÊNCIAS TÉCNICAS", "CERTIFICAÇÕES", "IDIOMAS"),
            "en": ("SUMMARY", "EDUCATION", "EXPERIENCE", "PROJECTS", "TECHNICAL SKILLS", "CERTIFICATIONS", "LANGUAGES"),
            "es": ("RESUMEN", "FORMACIÓN", "EXPERIENCIA", "PROYECTOS", "COMPETENCIAS TÉCNICAS", "CERTIFICACIONES", "IDIOMAS"),
        }
        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                extracted = subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", str(self.output_dir / filename), "-"],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                ).stdout
                lines = [line.strip() for line in extracted.splitlines()]
                positions = [lines.index(section) for section in section_order[language]]
                self.assertEqual(positions, sorted(positions), extracted)

    def test_optimizr_location_is_absent_from_cv_json(self):
        optimizr = next(item for item in DATA["experience"] if item["company"] == "OPTIMIZR")
        self.assertNotIn("location", optimizr)

    def test_optimizr_company_line_has_no_remote_location(self):
        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                extracted = subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", "-layout", str(self.output_dir / filename), "-"],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                ).stdout
                company_line = next(line for line in extracted.splitlines() if "OPTIMIZR" in line)
                self.assertNotRegex(company_line, r"\b(?:Remoto|Remote)\b", company_line)

    def test_published_pdfs_match_current_cv_json_text(self):
        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                generated = subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", "-layout", str(self.output_dir / filename), "-"],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                ).stdout
                published = subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", "-layout", str(ROOT / "public" / "refs" / filename), "-"],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                ).stdout
                self.assertEqual(published, generated, f"Published {language} PDF is stale relative to cv.json")

    def test_ongoing_aws_certification_has_localized_status_and_no_date(self):
        aws = next(item for item in DATA["certifications"] if item["name"]["pt"] == "AWS Academy Cloud Architecting")
        self.assertEqual(aws["status"], "in-progress")
        self.assertNotIn("date", aws)

        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                lines = subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", "-raw", str(self.output_dir / filename), "-"],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                ).stdout.splitlines()
                aws_line = next((" ".join(tokens(line)) for line in lines if localized(aws["name"], language) in line), "")
                self.assertIn(" ".join(tokens(CERTIFICATION_STATUS_LABELS[language])), aws_line)


    def test_latinoware_is_one_entry_with_2025_hours_and_both_editions(self):
        items = [item for item in DATA["certifications"] if item["name"]["pt"].startswith("Latinoware")]
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["provider"], "Itaipu Parquetec")
        self.assertEqual((item["hours"], item["hoursYear"]), (28, 2025))
        expected_editions = {"pt": "Edições 2014 e 2025", "en": "2014 and 2025 editions", "es": "Ediciones de 2014 y 2025"}
        self.assertEqual(item["editions"], expected_editions)

        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                extracted = subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", "-layout", str(self.output_dir / filename), "-"],
                    check=True, capture_output=True, text=True, encoding="utf-8",
                ).stdout
                self.assertEqual(extracted.count(localized(item["name"], language)), 1)
                self.assertIn(localized(item["editions"], language), extracted)
                self.assertIn("28h (2025)", extracted)

    def test_non_alura_certifications_are_sorted_pending_then_dated_descending(self):
        expected = [
            "AWS Academy Cloud Architecting",
            "AWS Academy Graduate – Cloud Foundations",
            "Latinoware",
            "Techstars Startup Weekend Videira 2025",
            "Red Hat OpenShift (Containers/Podman) DO188",
            "Red Hat Enterprise Linux Automation with Ansible RH294",
        ]
        self.assertEqual(sum(item["hours"] for item in DATA["certifications"] if item.get("provider") == "Alura"), 403)
        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                extracted = subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", "-layout", str(self.output_dir / filename), "-"],
                    check=True, capture_output=True, text=True, encoding="utf-8",
                ).stdout
                positions = [extracted.index(name) for name in expected]
                self.assertEqual(positions, sorted(positions), extracted)
                self.assertLess(extracted.index("Alura"), positions[0])

    def test_each_language_contains_all_selected_content_without_invented_text(self):
        section_labels = {
            "pt": ["SUMÁRIO", "EXPERIÊNCIA", "PROJETOS", "COMPETÊNCIAS TÉCNICAS", "FORMAÇÃO", "CERTIFICAÇÕES", "IDIOMAS"],
            "en": ["SUMMARY", "EXPERIENCE", "PROJECTS", "TECHNICAL SKILLS", "EDUCATION", "CERTIFICATIONS", "LANGUAGES"],
            "es": ["RESUMEN", "EXPERIENCIA", "PROYECTOS", "COMPETENCIAS TÉCNICAS", "FORMACIÓN", "CERTIFICACIONES", "IDIOMAS"],
        }
        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                pdf = self.output_dir / filename
                extracted = subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", "-layout", str(pdf), "-"],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                ).stdout
                self.assertNotIn("\ufffd", extracted)
                normalized = " ".join(extracted.split())
                normalized_tokens = " ".join(tokens(extracted))
                for item in DATA["experience"]:
                    if ROLE in item.get("roles", []):
                        for bullet in item.get("bullets", []):
                            if ROLE in bullet.get("roles", []):
                                self.assertIn(" ".join(localized(bullet, language).split()), normalized)
                for source_text in source_texts(language):
                    expected_tokens = " ".join(tokens(source_text))
                    if expected_tokens:
                        self.assertIn(expected_tokens, normalized_tokens, source_text)

                allowed = collections.Counter(token for value in source_texts(language) for token in tokens(value))
                allowed.update(token for value in section_labels[language] for token in tokens(value))
                allowed.update(tokens(CERTIFICATION_STATUS_LABELS[language]))
                for value in formatted_dates(language):
                    allowed.update(tokens(value))
                actual = collections.Counter(tokens(extracted))
                self.assertFalse(actual - allowed, f"Text not sourced from cv.json: {actual - allowed}")

    def test_each_language_keeps_mailto_linkedin_and_github_annotations(self):
        expected_urls = (
            "mailto:" + DATA["personal"]["email"],
            "https://" + DATA["personal"]["linkedin"],
            "https://" + DATA["personal"]["github"],
            DATA["personal"]["lattes"],
            *(item["credentialUrl"] for item in DATA["certifications"] if item.get("credentialUrl")),
        )
        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                urls = subprocess.run(
                    ["pdfinfo", "-url", str(self.output_dir / filename)],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout
                for url in expected_urls:
                    self.assertIn(url, urls)

    def test_certification_provider_placeholders_are_not_published(self):
        placeholders = ("Não informado", "Not specified", "No especificado")
        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                extracted = subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", str(self.output_dir / filename), "-"],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                ).stdout
                for placeholder in placeholders:
                    self.assertNotIn(placeholder, extracted)

    def test_certifications_include_items_from_all_roles(self):
        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                extracted = subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", str(self.output_dir / filename), "-"],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                ).stdout
                for item in DATA["certifications"]:
                    expected = localized(item["name"], language)
                    self.assertIn(expected, extracted)

    def test_certification_dates_share_their_item_line(self):
        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                lines = subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", "-raw", str(self.output_dir / filename), "-"],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                ).stdout.splitlines()
                for item in DATA["certifications"]:
                    if not item.get("date") and not item.get("period"):
                        continue
                    name = localized(item["name"], language)
                    dates = [item["date"]] if item.get("date") else [item["period"]["start"]]
                    if item.get("period") and item["period"]["end"][:7] != item["period"]["start"][:7]:
                        dates.append(item["period"]["end"])
                    expected_dates = [" ".join(tokens(format_date(value, language))) for value in dates]
                    matching = [" ".join(tokens(line)) for line in lines if name in line]
                    self.assertTrue(matching, f"Missing certification line: {name}")
                    self.assertTrue(any(all(expected_date in line for expected_date in expected_dates) for line in matching), f"Dates not on item line: {name}")

    def test_alura_groups_follow_a_single_403_hour_header_without_repeating_provider(self):
        groups = [item for item in DATA["certifications"] if item.get("provider") == "Alura"]
        self.assertEqual(len(groups), 9)
        self.assertEqual(sum(item["hours"] for item in groups), 403)
        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                lines = subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", "-raw", str(self.output_dir / filename), "-"],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                ).stdout.splitlines()
                matching_header = [line for line in lines if "Alura" in line and "403h" in line]
                self.assertEqual(len(matching_header), 1, lines)
                for group in groups:
                    name = localized(group["name"], language)
                    matching = [" ".join(tokens(line)) for line in lines if name in line]
                    self.assertTrue(matching, f"Missing Alura group: {name}")
                    self.assertTrue(any(f'{group["hours"]}h' in line for line in matching), f"Group hours not on line: {name}")
                    self.assertFalse(any("alura" in line for line in matching), f"Repeated provider on group line: {name}")
                extracted = " ".join(
                    subprocess.run(
                        ["pdftotext", "-enc", "UTF-8", str(self.output_dir / filename), "-"],
                        check=True,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                    ).stdout.split()
                )
                for course in (
                    "Django REST Framework: crie APIs com Python",
                    "Excel: cenários, análise, PROCV, tabelas dinâmicas, macros e VBA (5 cursos)",
                    "Figma: Conhecendo o programa",
                ):
                    self.assertNotIn(" ".join(tokens(course)), " ".join(tokens(extracted)), course)

    def test_lattes_is_on_a_second_contact_line_with_social_links(self):
        target = "lattes.cnpq.br/9042504768658064"
        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                extracted = subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", "-layout", str(self.output_dir / filename), "-"],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                ).stdout
                self.assertIn(target, extracted)
                contact_line = next(line for line in extracted.splitlines() if target in line)
                self.assertIn(DATA["personal"]["linkedin"], contact_line)
                self.assertIn(DATA["personal"]["github"], contact_line)
                email_line = next(line for line in extracted.splitlines() if DATA["personal"]["email"] in line)
                self.assertIn(DATA["personal"]["phone"], email_line)
                self.assertNotIn(DATA["personal"]["linkedin"], email_line)
                self.assertNotIn(DATA["personal"]["github"], email_line)
                urls = subprocess.run(
                    ["pdfinfo", "-url", str(self.output_dir / filename)],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout
                self.assertIn(target, urls)

    def test_contact_and_certification_lines_do_not_overlap_vertically(self):
        section_labels = {
            "pt": ("CERTIFICAÇÕES", "IDIOMAS"),
            "en": ("CERTIFICATIONS", "LANGUAGES"),
            "es": ("CERTIFICACIONES", "IDIOMAS"),
        }
        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                pdf = self.output_dir / filename
                page_width, first_page = bbox_lines(pdf, 1)
                contact_rows = visual_rows(first_page)
                email_line = next(line for line in contact_rows if DATA["personal"]["email"] in line["text"])
                lattes_line = next(line for line in contact_rows if "lattes.cnpq.br/9042504768658064" in line["text"])
                self.assertIn(DATA["personal"]["phone"], email_line["text"])
                for profile in (DATA["personal"]["linkedin"], DATA["personal"]["github"]):
                    self.assertIn(profile, lattes_line["text"])
                self.assertGreaterEqual(lattes_line["yMin"], email_line["yMax"], "Contact rows overlap")
                self.assertAlmostEqual((lattes_line["xMin"] + lattes_line["xMax"]) / 2, page_width / 2, delta=5)

                _, second_page = bbox_lines(pdf, 2)
                heading, next_heading = section_labels[language]
                certification_heading = next(line for line in second_page if line["text"] == heading)
                next_section = next(line for line in second_page if line["text"] == next_heading and line["yMin"] > certification_heading["yMin"])
                section_lines = [
                    line for line in second_page
                    if certification_heading["yMax"] <= line["yMin"] < next_section["yMin"]
                ]
                rows = visual_rows(section_lines)
                self.assertTrue(any("Alura" in row["text"] for row in rows), rows)
                for previous, following in zip(rows, rows[1:]):
                    self.assertGreaterEqual(
                        following["yMin"], previous["yMax"],
                        f"{language} certification rows overlap: {previous['text']} / {following['text']}",
                    )

    def test_senai_courses_share_one_institution_heading(self):
        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                extracted = subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", str(self.output_dir / filename), "-"],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                ).stdout
                self.assertEqual(extracted.count("SENAI"), 1, extracted)
                for item in DATA["education"]:
                    if item["institution"] == "SENAI":
                        self.assertIn(localized(item["degree"], language), extracted)

    def test_first_project_description_follows_title_without_blank_line(self):
        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                lines = subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", "-raw", str(self.output_dir / filename), "-"],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                ).stdout.splitlines()
                first_project = localized(DATA["projects"][0].get("nameByLanguage", DATA["projects"][0]["name"]), language)
                title_index = next(i for i, line in enumerate(lines) if first_project in line)
                self.assertTrue(lines[title_index + 1].strip(), "Unexpected blank line after first project title")

    def test_education_periods_are_kept_unbroken(self):
        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                extracted = subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", "-raw", str(self.output_dir / filename), "-"],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                ).stdout
                normalized_lines = [" ".join(tokens(line)) for line in extracted.splitlines()]
                for item in DATA["education"]:
                    if ROLE not in item.get("roles", []):
                        continue
                    expected_period = " ".join(tokens(
                        format_date(item["period"]["start"], language)
                        + " " + format_date(item["period"]["end"], language)
                    ))
                    matching_lines = [line for line in normalized_lines if expected_period in line]
                    self.assertTrue(matching_lines, f"Wrapped education period for {language}: {item['degree']}")


class OutputProtectionTests(unittest.TestCase):
    def test_experience_location_cell_is_only_rendered_when_present(self):
        template = (ROOT / "cv" / "cv.typ").read_text(encoding="utf-8")
        experience = template[template.index('== #section("experience")'):template.index('== #section("projects")')]
        self.assertIn('item.at("location", default: none)', experience)
        self.assertIn('if location != "" [#h(1fr) *#location*]', experience)
        self.assertNotIn("item.location", experience)

    def test_major_cv_entries_share_one_vertical_spacing_constant(self):
        template = (ROOT / "cv" / "cv.typ").read_text(encoding="utf-8")
        self.assertIn("#let item-spacing = 1.25em", template)
        for section, next_section in (
            ('== #section("education")', '== #section("experience")'),
            ('== #section("experience")', '== #section("projects")'),
            ('== #section("projects")', '== #section("skills")'),
        ):
            segment = template[template.index(section):template.index(next_section)]
            self.assertIn("above: item-spacing", segment, section)
        self.assertIn("#let course-spacing = 0.25em", template)
        self.assertIn("#v(course-spacing)", template)

    def test_alura_groups_use_regular_certification_spacing_and_indent(self):
        template = (ROOT / "cv" / "cv.typ").read_text(encoding="utf-8")
        certifications = template[template.index('== #section("certifications")'):template.index('== #section("languages")')]
        self.assertIn("#let certification-spacing = 0.65em", template)
        self.assertEqual(certifications.count("above: certification-spacing"), 3)
        self.assertIn("#h(0.6em) *#localized(item.name)*", certifications)

    def test_default_output_is_outside_public_refs(self):
        output = resolve_output_dir(None, publish_public_refs=False)
        try:
            self.assertNotEqual(output.resolve(), (ROOT / "public" / "refs").resolve())
            self.assertNotIn((ROOT / "public").resolve(), output.resolve().parents)
        finally:
            shutil.rmtree(output, ignore_errors=True)

    def test_public_refs_requires_explicit_publish_flag(self):
        with self.assertRaisesRegex(ValueError, "--publish-public-refs"):
            resolve_output_dir(ROOT / "public" / "refs", publish_public_refs=False)

    def test_publish_flag_only_allows_public_refs_as_destination(self):
        with self.assertRaisesRegex(ValueError, "only valid with public/refs"):
            resolve_output_dir(ROOT / "tmp-cv-output", publish_public_refs=True)
        output = resolve_output_dir(None, publish_public_refs=True)
        self.assertEqual(output.resolve(), (ROOT / "public" / "refs").resolve())

    def test_package_and_ci_use_only_the_new_explicit_generator(self):
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        scripts = package["scripts"]
        self.assertEqual(scripts["cv:pdf"], "python scripts/build_cv_pdf.py")
        self.assertNotIn("generate:pdfs", scripts)
        self.assertNotIn("generate_cv_pdfs.py", workflow)
        self.assertNotIn("--publish-public-refs", workflow)


if __name__ == "__main__":
    unittest.main()
