import collections
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.build_cv_pdf import OUTPUTS, ROOT, resolve_output_dir


DATA = json.loads((ROOT / "data" / "cv.json").read_text(encoding="utf-8"))
ROLE = "data-engineer"
TOOLS = ("typst", "pdfinfo", "pdffonts", "pdftotext")
MISSING_TOOLS = [name for name in TOOLS if shutil.which(name) is None]
PDF_TEST_SKIP = "PDF integration checks need Typst and Poppler tools: " + ", ".join(MISSING_TOOLS)


def localized(value, language):
    if isinstance(value, dict):
        return value.get(language, value.get("pt", ""))
    return value


def source_texts(language):
    personal = DATA["personal"]
    texts = [personal["name"], personal["email"], personal["phone"], personal["linkedin"], personal["github"]]
    texts += [localized(personal["location"], language), localized(personal["titles"][ROLE], language)]
    texts.append(localized(DATA["summary"][ROLE], language))
    for item in DATA["experience"]:
        if ROLE not in item.get("roles", []):
            continue
        texts += [localized(item["role"], language), item["company"], localized(item["location"], language)]
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
        if ROLE not in item.get("roles", []):
            continue
        texts.append(localized(item["name"], language))
        provider = item.get("providerByLanguage", {}).get(language, item.get("provider"))
        if provider and provider not in ("Não informado", "Not specified", "No especificado"):
            texts.append(provider)
        if item.get("details"):
            texts.append(item.get("detailsByLanguage", {}).get(language, item["details"]))
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
        if ROLE in item.get("roles", []) and item.get("date"):
            values.append(format_date(item["date"], language))
    return values


def tokens(text):
    return re.findall(r"[^\W_]+", text.casefold(), flags=re.UNICODE)


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

    def test_each_language_has_two_pages_and_only_embedded_inter_fonts(self):
        for language, filename in OUTPUTS.items():
            with self.subTest(language=language):
                pdf = self.output_dir / filename
                info = subprocess.run(["pdfinfo", str(pdf)], check=True, capture_output=True, text=True).stdout
                self.assertRegex(info, r"(?m)^Pages:\s+2$")

                fonts = subprocess.run(["pdffonts", str(pdf)], check=True, capture_output=True, text=True).stdout
                font_rows = [
                    line
                    for line in fonts.splitlines()
                    if line.strip() and not line.startswith("name") and not line.startswith("-")
                ]
                self.assertTrue(font_rows, fonts)
                for row in font_rows:
                    columns = row.split()
                    self.assertGreaterEqual(len(columns), 7, row)
                    self.assertIn("inter", columns[0].casefold(), row)
                    self.assertEqual(columns[4].casefold(), "yes", row)

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
                for value in formatted_dates(language):
                    allowed.update(tokens(value))
                actual = collections.Counter(tokens(extracted))
                self.assertFalse(actual - allowed, f"Text not sourced from cv.json: {actual - allowed}")

    def test_each_language_keeps_mailto_linkedin_and_github_annotations(self):
        expected_urls = (
            "mailto:" + DATA["personal"]["email"],
            "https://" + DATA["personal"]["linkedin"],
            "https://" + DATA["personal"]["github"],
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
