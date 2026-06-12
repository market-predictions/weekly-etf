from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.wp16_followup3_cleanup import clean_text, failures as residual_failures
from tools.validate_etf_pdf_polish_contract import latest_delivery_html, validate_en, validate_nl
from tools.validate_etf_pricing_lineage_contract import _manifest_path as _pricing_lineage_manifest_path
from tools.validate_etf_pricing_lineage_contract import validate_manifest_path as validate_pricing_lineage_manifest

EN_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?\.md$")
NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")
EMPTY_COMMENT_RE = re.compile(r"(?:&lt;!|<!)\s*--\s*--\s*(?:&gt;|>)", re.IGNORECASE)
DUTCH_RESIDUE_EN_RE = re.compile(r"\bn\.v\.t\.\b", re.IGNORECASE)
REMOVED_MARKDOWN_GUARD_MARKER = "wp16-nl-equity-curve-guard"
CHART_PLACEHOLDER = "`EQUITY_CURVE_CHART_PLACEHOLDER`"
NL_PRICING_HEADING = "### Gebruikte slotkoersen in dit rapport"
EN_PRICING_HEADING = "### Closing prices used in this report"


def _explicit_path(env_name: str, pattern: re.Pattern[str]) -> Path | None:
    raw = os.environ.get(env_name, "").strip()
    if not raw:
        return None
    path = Path(raw)
    if path.exists() and pattern.match(path.name):
        return path
    return None


def _latest(output_dir: Path, pattern: re.Pattern[str]) -> Path:
    reports = sorted(path for path in output_dir.glob("weekly_analysis_pro*.md") if pattern.match(path.name))
    if not reports:
        raise RuntimeError(f"No matching report found in {output_dir} for {pattern.pattern}")
    return reports[-1]


def _matching_delivery_html(report_path: Path) -> Path | None:
    candidate = report_path.with_name(report_path.stem + "_delivery.html")
    return candidate if candidate.exists() else None


def _language_for_path(path: Path) -> str:
    name = path.name
    if name.startswith("weekly_analysis_pro_nl_"):
        return "nl"
    return "en"


def _current_files(output_dir: Path) -> list[Path]:
    en = _explicit_path("MRKT_RPRTS_EXPLICIT_REPORT_PATH", EN_RE) or _latest(output_dir, EN_RE)
    nl = _explicit_path("MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL", NL_RE) or _latest(output_dir, NL_RE)
    paths = [en, nl]
    for report in (en, nl):
        html = _matching_delivery_html(report)
        if html is not None:
            paths.append(html)
    return paths


def _move_chart_before_pricing_disclosure(text: str, language: str) -> str:
    heading = NL_PRICING_HEADING if language == "nl" else EN_PRICING_HEADING
    chart_pos = text.find(CHART_PLACEHOLDER)
    heading_pos = text.find(heading)
    if chart_pos == -1 or heading_pos == -1 or chart_pos < heading_pos:
        return text
    without_chart = text[:chart_pos].rstrip() + "\n\n" + text[chart_pos + len(CHART_PLACEHOLDER):].lstrip()
    heading_pos = without_chart.find(heading)
    if heading_pos == -1:
        return without_chart + "\n\n" + CHART_PLACEHOLDER + "\n"
    return without_chart[:heading_pos].rstrip() + "\n\n" + CHART_PLACEHOLDER + "\n\n" + without_chart[heading_pos:].lstrip()


def _apply_nl_equity_curve_guard(text: str, path: Path) -> str:
    """Compatibility shim only; production must not inject CSS or markers into Markdown."""
    return text


def _scrub_file(path: Path) -> None:
    original = path.read_text(encoding="utf-8", errors="ignore")
    language = _language_for_path(path)
    cleaned = clean_text(original, language=language)
    if path.suffix == ".md":
        cleaned = _move_chart_before_pricing_disclosure(cleaned, language)
    if cleaned != original:
        path.write_text(cleaned, encoding="utf-8")
        print(f"ETF_CLIENT_SURFACE_RESIDUAL_SCRUBBED | file={path.name}")


def _scan(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    language = _language_for_path(path)
    hits = residual_failures(text, language=language)
    if EMPTY_COMMENT_RE.search(text):
        hits.append("empty comment residue")
    if REMOVED_MARKDOWN_GUARD_MARKER in text:
        hits.append("removed markdown style guard marker")
    if language == "en" and DUTCH_RESIDUE_EN_RE.search(text):
        hits.append("Dutch n.v.t. in English output")
    return sorted(set(hits))


def _validate_pricing_lineage_before_send() -> None:
    manifest_path = _pricing_lineage_manifest_path(None)
    summary = validate_pricing_lineage_manifest(manifest_path, update_manifest_status=True)
    print(
        "ETF_PRICING_LINEAGE_PRE_SEND_GATE_OK | "
        f"run_id={summary.get('run_id')} | requested_close={summary.get('requested_close_date')} | "
        f"holdings={len(summary.get('holdings_validated') or [])} | manifest={manifest_path}"
    )


def _validate_pdf_polish_contract(output_dir: Path) -> None:
    failures = validate_en(latest_delivery_html(output_dir, language="en")) + validate_nl(latest_delivery_html(output_dir, language="nl"))
    if failures:
        raise RuntimeError("ETF PDF polish contract failed: " + " | ".join(failures))
    print("ETF_PDF_POLISH_CONTRACT_OK")


def validate(output_dir: Path) -> None:
    failures: list[str] = []
    paths = _current_files(output_dir)
    for path in paths:
        _scrub_file(path)
    for path in paths:
        hits = _scan(path)
        if hits:
            failures.append(f"{path.name}: {', '.join(hits[:12])}")
    if failures:
        raise RuntimeError("ETF client-surface clean gate failed: " + " | ".join(failures))
    _validate_pdf_polish_contract(output_dir)
    _validate_pricing_lineage_before_send()
    print("ETF_CLIENT_SURFACE_CLEAN_OK | files=" + ",".join(path.name for path in paths))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    validate(Path(args.output_dir))


if __name__ == "__main__":
    main()
