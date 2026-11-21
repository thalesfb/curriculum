"""
Testes unitários para scripts/linkedin_diff.py.
"""

from __future__ import annotations

import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.linkedin_diff import (
    compare_linkedin_cv,
    main,
    normalize_date,
    normalize_text,
    read_csv_from_zip,
    truncate_preview,
)

ROOT = Path(__file__).resolve().parents[2]
REAL_CV_PATH = ROOT / "data" / "cv.json"


class TestNormalizeDate(unittest.TestCase):
    """Testa parse e normalização de datas em todos os formatos esperados."""

    def test_parse_dates(self) -> None:
        test_cases = [
            ("Jan 2024", "2024-01"),
            ("jan 2024", "2024-01"),
            ("2024", "2024"),
            ("jan. de 2024", "2024-01"),
            ("01/2024", "2024-01"),
            ("1/2024", "2024-01"),
            ("2024-05", "2024-05"),
            ("2024-05-15", "2024-05"),
            ("set. de 2023", "2023-09"),
            ("setembro de 2023", "2023-09"),
            ("Março de 2022", "2022-03"),
            ("marco 2022", "2022-03"),
            ("dezembro 2025", "2025-12"),
            ("December 2025", "2025-12"),
            ("Dec 2025", "2025-12"),
            ("", None),
            ("   ", None),
            (None, None),
            ("Atual", None),
            ("atual", None),
            ("Present", None),
            ("present", None),
            ("None", None),
            ("-", None),
        ]
        for input_val, expected in test_cases:
            with self.subTest(input_val=input_val):
                self.assertEqual(normalize_date(input_val), expected)


class TestHeaderDetectionAndPreamble(unittest.TestCase):
    """Testa detecção de cabeçalho com preâmbulos, BOM e subpastas."""

    def test_header_detection_and_bom_and_folders(self) -> None:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            # 1. Preamble com "Notes:" antes do cabecalho
            positions_content = (
                "Notes:\n"
                "This export was generated on 2024-05-01\n"
                "Company Name,Title,Description,Location,Started On,Finished On\n"
                "Empresa Teste,Engenheiro,Descricao teste,Videira,01/2023,\n"
            )
            zf.writestr("Positions.csv", positions_content.encode("utf-8"))

            # 2. Arquivo com BOM (utf-8-sig)
            cert_content = (
                "\ufeffName,Url,Authority,Started On,Finished On,License Number\n"
                "Certificado AWS,https://aws.com,AWS,2023,,\n"
            )
            zf.writestr("Certifications.csv", cert_content.encode("utf-8-sig"))

            # 3. Arquivo dentro de subpasta e caixa mista
            edu_content = (
                "School Name,Start Date,End Date,Notes,Degree Name,Activities\n"
                "Instituto Federal Catarinense,2020,2024,,Ciência da Computação,\n"
            )
            zf.writestr("archive_data/nested/education.CSV", edu_content.encode("utf-8"))

        buf.seek(0)
        with zipfile.ZipFile(buf, "r") as zf:
            # Positions
            pos_rows, warn_pos = read_csv_from_zip(
                zf,
                "Positions.csv",
                ["Company Name", "Title", "Description", "Location", "Started On", "Finished On"],
            )
            self.assertIsNone(warn_pos)
            self.assertEqual(len(pos_rows), 1)
            self.assertEqual(pos_rows[0]["Company Name"], "Empresa Teste")
            self.assertEqual(pos_rows[0]["Title"], "Engenheiro")

            # Certifications com BOM
            cert_rows, warn_cert = read_csv_from_zip(
                zf,
                "Certifications.csv",
                ["Name", "Url", "Authority", "Started On", "Finished On", "License Number"],
            )
            self.assertIsNone(warn_cert)
            self.assertEqual(len(cert_rows), 1)
            self.assertEqual(cert_rows[0]["Name"], "Certificado AWS")

            # Education em subpasta
            edu_rows, warn_edu = read_csv_from_zip(
                zf,
                "Education.csv",
                ["School Name", "Start Date", "End Date", "Notes", "Degree Name", "Activities"],
            )
            self.assertIsNone(warn_edu)
            self.assertEqual(len(edu_rows), 1)
            self.assertEqual(edu_rows[0]["School Name"], "Instituto Federal Catarinense")
            self.assertEqual(edu_rows[0]["Degree Name"], "Ciência da Computação")


class TestMatchingAndDiffs(unittest.TestCase):
    """Testa casamentos com acentos/caixa e as 3 categorias de diferenças."""

    def setUp(self) -> None:
        self.fixture_cv = {
            "personal": {
                "name": "Thales Ferreira",
                "location": {"pt": "Videira, SC, Brasil"},
                "titles": {"data-engineer": {"pt": "Líder Técnico & Engenheiro de Dados"}},
            },
            "summary": {
                "data-engineer": {"pt": "Resumo profissional completo no cv.json."}
            },
            "experience": [
                {
                    "company": "OPTIMIZR",
                    "role": {"pt": "Líder Técnico"},
                    "period": {"start": "2023-01", "end": None},
                    "location": {"pt": "Videira, SC"},
                    "bullets": [{"pt": "Desenvolvimento de soluções analíticas."}],
                },
                {
                    "company": "Empresa Apenas CV",
                    "role": {"pt": "Analista"},
                    "period": {"start": "2020-01", "end": "2021-12"},
                    "location": {"pt": "Videira, SC"},
                    "bullets": [],
                },
                {
                    "company": "Empresa Ambos Divergente",
                    "role": {"pt": "Desenvolvedor Backend"},
                    "period": {"start": "2022-01", "end": "2022-12"},
                    "location": {"pt": "Videira, SC"},
                    "bullets": [{"pt": "Texto longo original no cv.json que difere do linkedin."}],
                },
            ],
            "education": [
                {
                    "institution": "Instituto Federal Catarinense",
                    "degree": {"pt": "Bacharelado em Ciência da Computação"},
                    "period": {"start": "2023-02", "end": "2026-12"},
                }
            ],
            "certifications": [
                {
                    "name": {"pt": "Trilha Django REST Framework"},
                    "provider": "Alura",
                    "credentialUrl": "https://alura.com.br/cert1",
                    "period": {"start": "2024-07", "end": "2025-09"},
                }
            ],
            "skills": {
                "prog": {
                    "items": ["Python", "Modelagem de Dados", "Apenas CV Skill"],
                    "itemTranslations": {"Modelagem de Dados": {"en": "Data Modeling"}},
                }
            },
            "languages": [
                {
                    "language": {"pt": "Português", "en": "Portuguese"},
                    "level": {"pt": "Nativo", "en": "Native"},
                }
            ],
            "projects": [
                {
                    "name": "Projeto Alpha",
                    "repo": "github.com/thalesfb/alpha",
                    "description": {"pt": "Descricao do projeto Alpha"},
                }
            ],
        }

    def _create_synthetic_zip(self) -> io.BytesIO:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            # Profile
            zf.writestr(
                "Profile.csv",
                (
                    "First Name,Last Name,Headline,Summary,Geo Location\n"
                    "Thales,Ferreira,Lider Tecnico & Engenheiro de Dados,Resumo no linkedin difere um pouco,Videira, SC, Brasil\n"
                ).encode("utf-8"),
            )
            # Positions
            zf.writestr(
                "Positions.csv",
                (
                    "Company Name,Title,Description,Location,Started On,Finished On\n"
                    # Coincidente (com acentos e caixa normalizados)
                    "optimizr,lider tecnico,Desenvolvimento de soluções analíticas.,Videira, SC,01/2023,\n"
                    # Só no LinkedIn
                    "Empresa Apenas LinkedIn,Consultor,Atividades de consultoria,Remoto,06/2021,12/2021\n"
                    # Divergente
                    "Empresa Ambos Divergente,Engenheiro Backend,Texto diferente no linkedin para teste,SP,02/2022,11/2022\n"
                ).encode("utf-8"),
            )
            # Education (coincidente)
            zf.writestr(
                "Education.csv",
                (
                    "School Name,Start Date,End Date,Notes,Degree Name,Activities\n"
                    "instituto federal catarinense,2023-02,2026-12,,bacharelado em ciencia da computacao,\n"
                ).encode("utf-8"),
            )
            # Certifications (coincidente)
            zf.writestr(
                "Certifications.csv",
                (
                    "Name,Url,Authority,Started On,Finished On,License Number\n"
                    "trilha django rest framework,https://alura.com.br/cert1,Alura,07/2024,09/2025,\n"
                ).encode("utf-8"),
            )
            # Skills
            zf.writestr(
                "Skills.csv",
                (
                    "Name\n"
                    "python\n"
                    "modelagem de dados\n"
                    "Apenas LinkedIn Skill\n"
                ).encode("utf-8"),
            )
            # Languages
            zf.writestr(
                "Languages.csv",
                (
                    "Name,Proficiency\n"
                    "Português,Nativo\n"
                ).encode("utf-8"),
            )
            # Projects
            zf.writestr(
                "Projects.csv",
                (
                    "Title,Description,Url,Started On,Finished On\n"
                    "Projeto Alpha,Descricao do projeto Alpha,github.com/thalesfb/alpha,,\n"
                ).encode("utf-8"),
            )
        buf.seek(0)
        return buf

    def test_matching_accents_and_case(self) -> None:
        """Verifica que casefold e remoção de acentos garantem coincidência perfeita."""
        self.assertEqual(normalize_text("Líder Técnico"), "lider tecnico")
        self.assertEqual(normalize_text("OPTIMIZR"), "optimizr")
        self.assertEqual(normalize_text("Ciência da Computação"), "ciencia da computacao")
        self.assertEqual(normalize_text("  Espaços   múltiplos  "), "espacos multiplos")

    def test_three_categories_of_difference(self) -> None:
        """Verifica (a) só no LinkedIn, (b) só no cv.json e (c) divergentes campo a campo."""
        zip_buf = self._create_synthetic_zip()
        report, sections = compare_linkedin_cv(zip_buf, self.fixture_cv)

        # 1. Verifica Experiência
        exp_sec = next(s for s in sections if s.name == "Experiência")

        # (a) Só no LinkedIn
        self.assertTrue(any("Empresa Apenas LinkedIn" in item for item in exp_sec.so_linkedin))
        self.assertIn("Empresa Apenas LinkedIn", report)

        # (b) Só no cv.json
        self.assertTrue(any("Empresa Apenas CV" in item for item in exp_sec.so_cv))
        self.assertIn("Empresa Apenas CV", report)

        # (c) Divergentes
        self.assertTrue(any("Empresa Ambos Divergente" in item[0] for item in exp_sec.divergentes))
        self.assertIn("Empresa Ambos Divergente", report)
        self.assertIn("- **Cargo**: LinkedIn: `Engenheiro Backend` | cv.json: `Desenvolvedor Backend`", report)
        self.assertIn("- **Início**: LinkedIn: `2022-02` | cv.json: `2022-01`", report)
        self.assertIn("- **Fim**: LinkedIn: `2022-11` | cv.json: `2022-12`", report)
        self.assertIn("- **Localização**: LinkedIn: `SP` | cv.json: `Videira, SC`", report)
        self.assertIn("- **Descrição**: difere", report)

        # 2. Verifica Skills
        skills_sec = next(s for s in sections if s.name == "Competências")
        self.assertIn("Apenas LinkedIn Skill", skills_sec.so_linkedin)
        self.assertIn("Apenas CV Skill", skills_sec.so_cv)
        self.assertGreaterEqual(skills_sec.coincidentes, 2)  # Python e Modelagem de Dados

    def test_missing_csv_becomes_warning(self) -> None:
        """Verifica que a ausência de CSVs não causa erro, virando aviso no markdown."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr(
                "Positions.csv",
                "Company Name,Title,Description,Location,Started On,Finished On\nEmpresa,Dev,,,,\n".encode("utf-8"),
            )
        buf.seek(0)

        report, _ = compare_linkedin_cv(buf, self.fixture_cv)
        self.assertIn("## Avisos", report)
        self.assertIn("Arquivo `Profile.csv` não encontrado no ZIP exportado.", report)
        self.assertIn("Arquivo `Education.csv` não encontrado no ZIP exportado.", report)
        self.assertIn("Arquivo `Certifications.csv` não encontrado no ZIP exportado.", report)

    def test_deterministic_output(self) -> None:
        """Verifica que rodar a comparação duas vezes produz saída 100% idêntica."""
        zip_buf1 = self._create_synthetic_zip()
        zip_buf2 = self._create_synthetic_zip()

        report1, _ = compare_linkedin_cv(zip_buf1, self.fixture_cv)
        report2, _ = compare_linkedin_cv(zip_buf2, self.fixture_cv)

        self.assertEqual(report1, report2)

    def test_non_zip_file_exit_code_2(self) -> None:
        """Verifica que arquivos não-ZIP retornam código de saída 2."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tf:
            tf.write(b"Este nao e um arquivo zip")
            invalid_path = tf.name

        try:
            exit_code = main([invalid_path])
            self.assertEqual(exit_code, 2)

            exit_code_missing = main(["caminho/inexistente/export.zip"])
            self.assertEqual(exit_code_missing, 2)
        finally:
            Path(invalid_path).unlink(missing_ok=True)

    def test_smoke_with_real_cv(self) -> None:
        """Teste de fumaça usando data/cv.json real para verificar execução limpa."""
        if not REAL_CV_PATH.is_file():
            self.skipTest("data/cv.json não encontrado para teste de fumaça.")

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr(
                "Positions.csv",
                (
                    "Company Name,Title,Description,Location,Started On,Finished On\n"
                    "CPEL,Full Stack Data Engineer with Software and DevOps Expertise,,\"Pinheiro Preto, SC\",05/2022,10/2025\n"
                ).encode("utf-8"),
            )
            zf.writestr(
                "Skills.csv",
                "Name\nPython\nDocker\n".encode("utf-8"),
            )
        buf.seek(0)

        report, sections = compare_linkedin_cv(buf, str(REAL_CV_PATH))
        self.assertTrue(report.startswith("# Relatório de Comparação: LinkedIn vs cv.json"))
        self.assertIn("## Resumo Geral", report)

        # CPEL deve ser coincidente
        exp_sec = next(s for s in sections if s.name == "Experiência")
        self.assertGreaterEqual(exp_sec.coincidentes, 1)


if __name__ == "__main__":
    unittest.main()
