from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

EN_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?_delivery\.html$")
NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?_delivery\.html$")
SECTION_LABEL_RE = re.compile(r"<span\s+class=['\"]section-label['\"]>\s*(.*?)\s*</span>", re.I | re.S)
MARKDOWN_HEADING_RE = re.compile(r"<h[1-6][^>]*>\s*(.*?)\s*</h[1-6]>", re.I | re.S)
EN_REFLECTED_HEADING = "Position Changes Reflected in Official State"
EN_PROPOSED_HEADING = "Proposed Position Changes / Rotation Trade Intents"
NL_REFLECTED_HEADING = "Positiewijzigingen verwerkt in de officiële portefeuillestaat"
NL_PROPOSED_HEADING = "Voorgestelde positiewijzigingen / rotatie-intenties"


def _explicit_delivery_html(output_dir: Path, *, language: str) -> Path | None:
    env_name = "MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL" if language == "nl" else "MRKT_RPRTS_EXPLICIT_REPORT_PATH"
    raw = os.environ.get(env_name, "").strip()
    if not raw:
        return None
    report_path = Path(raw)
    if not report_path.is_absolute():
        report_path = Path.cwd() / report_path
    candidate = report_path.with_name(report_path.stem + "_delivery.html")
    if candidate.exists():
        return candidate
    # Some callers pass paths relative to the output dir rather than cwd.
    fallback = output_dir / (Path(raw).stem + "_delivery.html")
    return fallback if fallback.exists() else None


def latest_delivery_html(output_dir: Path, *, language: str) -> Path:
    explicit = _explicit_delivery_html(output_dir, language=language)
    if explicit is not None:
        return explicit
    regex = NL_RE if language == "nl" else EN_RE
    files = sorted(path for path in output_dir.glob("weekly_analysis_pro*_delivery.html") if regex.match(path.name))
    if not files:
        raise RuntimeError(f"No {language} delivery HTML found in {output_dir}")
    return files[-1]


def plain(html: str) -> str:
    text = re.sub(r"<style.*?</style>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", text).strip()


def _strip_tags(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = value.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", value).strip()


def heading_surface_count(html: str, title: str) -> int:
    """Count actual visual section/panel headings, not body prose.

    Body prose may legitimately mention terms such as Vervangingsanalyse. The
    PDF-polish contract should fail only when the heading/panel surface is
    duplicated.
    """
    count = 0
    for match in SECTION_LABEL_RE.finditer(html):
        if _strip_tags(match.group(1)) == title:
            count += 1
    for match in MARKDOWN_HEADING_RE.finditer(html):
        if _strip_tags(match.group(1)) == title:
            count += 1
    return count


def has_stale_section_number(html: str, title: str) -> bool:
    text = plain(html)
    if f"11 {title}" in text:
        return True
    pattern = re.compile(
        r"<span\s+class=['\"]section-badge['\"]>\s*11\s*</span>\s*</td>\s*<td\s+class=['\"]section-label-cell['\"]>\s*<span\s+class=['\"]section-label['\"]>\s*"
        + re.escape(title)
        + r"\s*</span>",
        re.I | re.S,
    )
    return bool(pattern.search(html))


def _has_valid_change_heading(text: str, *, reflected: str, proposed: str) -> bool:
    return reflected in text or proposed in text


def validate_en(path: Path) -> list[str]:
    html = path.read_text(encoding="utf-8")
    text = plain(html)
    failures: list[str] = []
    if "Executive Summary" not in text:
        failures.append(f"{path.name}: missing visible Executive Summary marker")
    if heading_surface_count(html, "Replacement Duel Table") > 1:
        failures.append(f"{path.name}: duplicate Replacement Duel Table surface")
    if has_stale_section_number(html, "Replacement Duel Table"):
        failures.append(f"{path.name}: stale replacement-duel section number 11 remains")
    if "Position Changes Executed This Run" in text:
        failures.append(f"{path.name}: idempotent execution heading still says executed this run")
    if not _has_valid_change_heading(text, reflected=EN_REFLECTED_HEADING, proposed=EN_PROPOSED_HEADING):
        failures.append(f"{path.name}: missing reflected-or-proposed position-change heading")
    return failures


def validate_nl(path: Path) -> list[str]:
    html = path.read_text(encoding="utf-8")
    text = plain(html)
    failures: list[str] = []
    if "Kernsamenvatting" not in text:
        failures.append(f"{path.name}: missing visible Kernsamenvatting marker")
    if heading_surface_count(html, "Vervangingsanalyse") > 1:
        failures.append(f"{path.name}: duplicate Vervangingsanalyse surface")
    if has_stale_section_number(html, "Vervangingsanalyse"):
        failures.append(f"{path.name}: stale replacement-duel section number 11 remains")
    if "Positiewijzigingen in deze run" in text:
        failures.append(f"{path.name}: idempotent execution heading still says in deze run")
    if not _has_valid_change_heading(text, reflected=NL_REFLECTED_HEADING, proposed=NL_PROPOSED_HEADING):
        failures.append(f"{path.name}: missing reflected-or-proposed position-change heading")
    if "Guarded auto-execution" in text:
        failures.append(f"{path.name}: Dutch execution note still contains English Guarded auto-execution")
    if "reduce PPA to fund CIBR" in text or "buy CIBR funded by PPA" in text:
        failures.append(f"{path.name}: Dutch execution note still contains English funding sentence")
    return failures


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    failures = validate_en(latest_delivery_html(output_dir, language="en")) + validate_nl(latest_delivery_html(output_dir, language="nl"))
    if failures:
        raise SystemExit("FAIL: ETF PDF polish contract failed: " + "; ".join(failures))
    print("ETF_PDF_POLISH_CONTRACT_OK")


if __name__ == "__main__":
    main()
