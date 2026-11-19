import unittest
import xml.etree.ElementTree as ET
import json
import zipfile
from pathlib import Path

from scripts.generate_cv_pdfs import (
    ROOT,
    build_document_xml,
    format_period,
    load_section_labels,
    localized,
    localized_items,
    localized_provider,
    paragraph_text,
    resolve_output_dir,
    select_for_role,
    set_education_line,
    set_paragraph_text,
    validate_page_count,
)


class GenerateCvPdfsTests(unittest.TestCase):
    def test_default_generation_output_is_not_public_refs(self):
        output = resolve_output_dir(None, preview=False, publish_public_refs=False)
        self.assertNotEqual(output, (ROOT / "public" / "refs").resolve())

    def test_public_refs_requires_explicit_publish_flag(self):
        with self.assertRaisesRegex(ValueError, "--publish-public-refs"):
            resolve_output_dir(ROOT / "public" / "refs", preview=False, publish_public_refs=False)

    def test_public_subdirectories_are_never_generation_targets(self):
        with self.assertRaisesRegex(ValueError, "inside public/ is disabled"):
            resolve_output_dir(ROOT / "public" / "refs" / "preview", preview=True, publish_public_refs=False)

    def test_publish_flag_requires_public_refs_output(self):
        with self.assertRaisesRegex(ValueError, "only valid with .*public/refs"):
            resolve_output_dir(ROOT / "tmp-cv-output", preview=False, publish_public_refs=True)

    def test_publish_flag_allows_public_refs_output(self):
        output = resolve_output_dir(ROOT / "public" / "refs", preview=False, publish_public_refs=True)
        self.assertEqual(output, (ROOT / "public" / "refs").resolve())

    def test_automated_build_workflows_do_not_run_pdf_generator(self):
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        workflows = ROOT / ".github" / "workflows"
        automated_commands = "\n".join(
            [str(value) for key, value in package["scripts"].items() if key != "generate:pdfs"]
            + [path.read_text(encoding="utf-8") for path in workflows.glob("*.yml")]
        )
        self.assertNotIn("generate:pdfs", automated_commands)
        self.assertNotIn("generate_cv_pdfs.py", automated_commands)

    def test_formats_current_education_start_in_all_languages(self):
        expected = {
            "pt": "FEV DE 2023 - Atual",
            "en": "FEBRUARY 2023 - Present",
            "es": "FEBRERO DE 2023 - Actualidad",
        }

        for language, value in expected.items():
            with self.subTest(language=language):
                self.assertEqual(format_period("2023-02", None, language), value)

    def test_formats_closed_periods_in_all_languages(self):
        expected = {
            "pt": "MAI DE 2022 - OUT DE 2025",
            "en": "MAY 2022 - OCTOBER 2025",
            "es": "MAYO DE 2022 - OCTUBRE DE 2025",
        }

        for language, value in expected.items():
            with self.subTest(language=language):
                self.assertEqual(format_period("2022-05", "2025-10", language), value)

    def test_localized_rejects_missing_locale_instead_of_silently_falling_back(self):
        with self.assertRaisesRegex(ValueError, "Missing 'es' translation"):
            localized({"pt": "Texto", "en": "Text"}, "es")

    def test_section_labels_come_from_ui_translations(self):
        ui_path = ROOT / "src" / "i18n" / "ui.ts"
        self.assertEqual(load_section_labels(ui_path, "en")[0], "SUMMARY")
        self.assertEqual(load_section_labels(ui_path, "es")[3], "EDUCACIÓN")

    def test_skill_items_use_optional_json_translations(self):
        skill = {
            "items": ["Python", "Modelagem de Dados"],
            "itemTranslations": {
                "Modelagem de Dados": {
                    "en": "Data Modeling",
                    "es": "Modelado de Datos",
                }
            },
        }
        self.assertEqual(localized_items(skill, "en"), ["Python", "Data Modeling"])
        self.assertEqual(localized_items(skill, "pt"), ["Python", "Modelagem de Dados"])

    def test_certification_provider_uses_optional_locale_translation(self):
        certification = {
            "provider": "Não informado",
            "providerByLanguage": {"en": "Not specified", "es": "No especificado"},
        }
        self.assertEqual(localized_provider(certification, "pt"), "Não informado")
        self.assertEqual(localized_provider(certification, "en"), "Not specified")
        self.assertEqual(localized_provider(certification, "es"), "No especificado")
        self.assertEqual(localized_provider({"provider": "Alura"}, "es"), "Alura")

    def test_skill_categories_follow_the_pdf_profile_role(self):
        entries = [
            {"id": "data", "roles": ["data-engineer"]},
            {"id": "frontend", "roles": ["frontend"]},
        ]
        self.assertEqual(select_for_role(entries, "data-engineer"), [entries[0]])

    def test_template_rejects_s1_content_until_layout_supports_it(self):
        data = json.loads((ROOT / "data" / "cv.json").read_text(encoding="utf-8"))
        template = ROOT / "refs" / "template" / "curriculo_thales_ferreira_pt.docx"
        with zipfile.ZipFile(template) as archive:
            source_xml = archive.read("word/document.xml")

        with self.assertRaisesRegex(ValueError, "OPTIMIZR has more JSON bullets than the template can hold"):
            build_document_xml(source_xml, data, "pt")

    def test_education_line_omits_optional_status_label(self):
        namespace = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        ET.register_namespace("w", namespace)
        paragraph = ET.fromstring(
            f'<w:p xmlns:w="{namespace}">'
            '<w:r><w:t>old degree and status</w:t></w:r>'
            '<w:r><w:t>old period</w:t></w:r></w:p>'
        )
        degree = {"pt": "Bacharelado em Ciência da Computação", "en": "Bachelor's Degree in Computer Science", "es": "Grado en Ciencias de la Computación"}

        set_education_line(paragraph, degree, {"start": "2023-02", "end": "2026-12"}, "pt")

        text = paragraph_text(paragraph)
        self.assertEqual(text, "Bacharelado em Ciência da Computação | FEV DE 2023 - DEZ DE 2026")
        self.assertNotIn("status", text.lower())

    def test_replacing_paragraph_text_keeps_run_formatting(self):
        namespace = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        ET.register_namespace("w", namespace)
        root = ET.fromstring(
            f'<w:p xmlns:w="{namespace}">'
            '<w:r><w:rPr><w:b/></w:rPr><w:t>old bold</w:t></w:r>'
            '<w:r><w:t>old normal</w:t></w:r></w:p>'
        )

        set_paragraph_text(root, "new content")

        bold = root.find("w:r/w:rPr/w:b", {"w": namespace})
        texts = [node.text or "" for node in root.findall(".//w:t", {"w": namespace})]
        self.assertIsNotNone(bold)
        self.assertEqual(texts, ["new content", ""])

    def test_page_count_mismatch_is_a_hard_failure(self):
        with self.assertRaisesRegex(ValueError, "expected 3 pages, got 4"):
            validate_page_count(3, 4, "en")


if __name__ == "__main__":
    unittest.main()
