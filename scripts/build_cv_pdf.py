"""Compile localized CV PDFs with the pinned Typst CLI."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "cv.json"
TEMPLATE_PATH = ROOT / "cv" / "cv.typ"
FONT_PATH = ROOT / "cv" / "fonts"
PUBLIC_REFS = (ROOT / "public" / "refs").resolve()
TYPST_VERSION = "0.15.1"
LANGUAGES = ("pt", "en", "es")
OUTPUTS = {
    "pt": "curriculo_thales_ferreira_pt.pdf",
    "en": "resume_thales_ferreira_en.pdf",
    "es": "curriculo_thales_ferreira_es.pdf",
}


def resolve_output_dir(
    output_dir: str | Path | None,
    publish_public_refs: bool,
) -> Path:
    """Resolve output while requiring explicit opt-in for public artifacts."""
    if publish_public_refs:
        if output_dir is not None and Path(output_dir).resolve() != PUBLIC_REFS:
            raise ValueError("--publish-public-refs is only valid with public/refs")
        return PUBLIC_REFS

    if output_dir is None:
        return Path(tempfile.mkdtemp(prefix="curriculum-cv-pdf-")).resolve()

    destination = Path(output_dir).resolve()
    public_root = (ROOT / "public").resolve()
    if destination == public_root or public_root in destination.parents:
        raise ValueError("writing inside public/ is disabled without --publish-public-refs")
    return destination


def find_typst(binary: str | None = None) -> str:
    executable = binary or shutil.which("typst")
    if not executable:
        raise RuntimeError("Typst 0.15.1 was not found on PATH")

    version = subprocess.run(
        [executable, "--version"], check=True, capture_output=True, text=True
    ).stdout.strip()
    if not version.startswith(f"typst {TYPST_VERSION} "):
        raise RuntimeError(f"Expected Typst {TYPST_VERSION}, found: {version}")
    return executable


def compile_pdf(typst: str, language: str, role: str, destination: Path) -> None:
    command = [
        typst,
        "compile",
        "--font-path",
        str(FONT_PATH),
        "--root",
        str(ROOT),
        "--ignore-system-fonts",
        "--input",
        f"lang={language}",
        "--input",
        f"role={role}",
        "--input",
        "path=../data/cv.json",
        str(TEMPLATE_PATH),
        str(destination),
    ]
    subprocess.run(command, cwd=ROOT, check=True)
    if not destination.is_file() or destination.stat().st_size == 0:
        raise RuntimeError(f"Typst did not create a PDF for language {language}")


def build_pdfs(
    output_dir: str | Path | None = None,
    publish_public_refs: bool = False,
    role: str = "data-engineer",
    typst_binary: str | None = None,
) -> dict[str, Path]:
    """Build all languages, staging the public replacement until compilation succeeds."""
    output = resolve_output_dir(output_dir, publish_public_refs)
    typst = find_typst(typst_binary)
    output.mkdir(parents=True, exist_ok=True)

    if publish_public_refs:
        with tempfile.TemporaryDirectory(prefix="curriculum-cv-publish-") as stage_name:
            stage = Path(stage_name)
            for language in LANGUAGES:
                compile_pdf(typst, language, role, stage / OUTPUTS[language])
            for language in LANGUAGES:
                shutil.copy2(stage / OUTPUTS[language], output / OUTPUTS[language])
    else:
        for language in LANGUAGES:
            compile_pdf(typst, language, role, output / OUTPUTS[language])

    return {language: output / filename for language, filename in OUTPUTS.items()}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="write drafts to this non-public directory")
    parser.add_argument("--publish-public-refs", action="store_true", help="replace PDFs in public/refs")
    parser.add_argument("--role", default="data-engineer", help="CV role to render (default: data-engineer)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        outputs = build_pdfs(
            output_dir=args.output_dir,
            publish_public_refs=args.publish_public_refs,
            role=args.role,
        )
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        print(f"CV PDF generation failed: {error}", file=sys.stderr)
        return 1

    for language, path in outputs.items():
        print(f"{language}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
