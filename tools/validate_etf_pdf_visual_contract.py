from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import matplotlib.image as mpimg
import numpy as np

EN_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?\.pdf$")
NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.pdf$")


def _latest_pdf(output_dir: Path, language: str) -> Path:
    pattern = NL_RE if language == "nl" else EN_RE
    candidates = sorted(path for path in output_dir.glob("weekly_analysis_pro*.pdf") if pattern.match(path.name))
    if not candidates:
        raise RuntimeError(f"PDF visual contract failed: no {language} PDF found in {output_dir}.")
    return candidates[-1]


def _require_poppler() -> None:
    missing = [tool for tool in ("pdftotext", "pdftoppm") if not shutil.which(tool)]
    if missing:
        raise RuntimeError(
            "PDF visual contract failed: missing Poppler tool(s): "
            + ", ".join(missing)
            + ". Install poppler-utils in the workflow before this validator runs."
        )


def _pdf_pages_text(pdf_path: Path) -> list[str]:
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.split("\f")


def _find_equity_page(pdf_path: Path, language: str) -> int:
    pages = _pdf_pages_text(pdf_path)
    tokens = ["Portefeuillecurve", "Portefeuillewaarde"] if language == "nl" else ["Equity Curve", "Portfolio value"]
    for idx, page in enumerate(pages, start=1):
        if all(token.lower() in page.lower() for token in tokens):
            return idx
    raise RuntimeError(f"PDF visual contract failed for {pdf_path.name}: could not find equity-curve page using tokens {tokens}.")


def _render_page_png(pdf_path: Path, page_number: int, tmpdir: Path) -> Path:
    prefix = tmpdir / "page"
    subprocess.run(
        ["pdftoppm", "-f", str(page_number), "-l", str(page_number), "-r", "120", "-png", str(pdf_path), str(prefix)],
        check=True,
        text=True,
        capture_output=True,
    )
    rendered = sorted(tmpdir.glob("page-*.png"))
    if not rendered:
        raise RuntimeError(f"PDF visual contract failed for {pdf_path.name}: pdftoppm did not render page {page_number}.")
    return rendered[0]


def _blue_pixel_count(png_path: Path) -> int:
    image = mpimg.imread(png_path)
    if image.max() > 1.0:
        image = image / 255.0
    rgb = image[:, :, :3]
    red = rgb[:, :, 0]
    green = rgb[:, :, 1]
    blue = rgb[:, :, 2]
    # Detect the report chart line/markers. Links and section badges also contain blue,
    # so the threshold intentionally requires a substantial number of blue pixels.
    mask = (blue > 0.33) & (blue > red + 0.08) & (blue > green + 0.02) & (red < 0.55) & (green < 0.75)
    return int(np.count_nonzero(mask))


def _validate_product_name_text(pdf_path: Path, language: str) -> None:
    if language != "nl":
        return
    text = "\n".join(_pdf_pages_text(pdf_path))
    lower = text.lower()
    forbidden = ["iaantal aandelen", "spdr gold aantal aandelen"]
    found = [token for token in forbidden if token in lower]
    if found:
        raise RuntimeError(f"PDF visual contract failed for {pdf_path.name}: Dutch product-name corruption found: {', '.join(found)}")
    if "ishares s&p gsci commodity-indexed" not in lower:
        raise RuntimeError(f"PDF visual contract failed for {pdf_path.name}: expected protected GSG product name was not found.")


def validate_pdf(pdf_path: Path, *, language: str, min_blue_pixels: int = 900) -> None:
    _require_poppler()
    _validate_product_name_text(pdf_path, language)
    page_number = _find_equity_page(pdf_path, language)
    with tempfile.TemporaryDirectory() as raw_tmp:
        png_path = _render_page_png(pdf_path, page_number, Path(raw_tmp))
        blue_pixels = _blue_pixel_count(png_path)
    if blue_pixels < min_blue_pixels:
        raise RuntimeError(
            f"PDF visual contract failed for {pdf_path.name}: equity-curve page {page_number} has too few visible blue chart pixels "
            f"({blue_pixels} < {min_blue_pixels})."
        )
    print(f"ETF_PDF_VISUAL_CONTRACT_OK | pdf={pdf_path.name} | language={language} | equity_page={page_number} | blue_pixels={blue_pixels}")


def validate(output_dir: Path) -> None:
    validate_pdf(_latest_pdf(output_dir, "en"), language="en")
    validate_pdf(_latest_pdf(output_dir, "nl"), language="nl")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render EN/NL ETF PDFs and validate visible equity-curve/product-name surfaces.")
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    validate(Path(args.output_dir))


if __name__ == "__main__":
    main()
