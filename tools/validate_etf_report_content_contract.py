from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import send_report as report_module

PRO_REPORT_RE = re.compile(r"^weekly_analysis_pro_(\d{6})(?:_(\d{2}))?\.md$")

FORBIDDEN_TOKENS = [
    "Placeholder for runtime replacement",
    "runtime rebuild required",
    "Pending classification",
    "None / None:",
]

REQUIRED_SECTION_TITLES = {
    1: "Executive Summary",
    2: "Portfolio Action Snapshot",
    3: "Regime Dashboard",
    4: "Structural Opportunity Radar",
    5: "Key Risks / Invalidators",
    6: "Bottom Line",
    7: "Equity Curve and Portfolio Development",
    8: "Asset Allocation Map",
    9: "Second-Order Effects Map",
    10: "Current Position Review",
    11: "Best New Opportunities",
    12: "Portfolio Rotation Plan",
    13: "Final Action Table",
    14: "Position Changes Executed This Run",
    15: "Current Portfolio Holdings and Cash",
    16: "Continuity Input for Next Run",
    17: "Disclaimer",
}

MIN_SECTION_CHARS = {
    3: 180,
    4: 240,
    5: 120,
    7: 180,
    8: 160,
    9: 180,
    13: 180,
    15: 240,
    16: 240,
}


def _canonical_report_key(path: Path) -> tuple[str, int] | None:
    match = PRO_REPORT_RE.match(path.name)
    if not match:
        return None
    return match.group(1), int(match.group(2) or "1")


def _explicit_report_path() -> Path | None:
    raw = os.environ.get("MRKT_RPRTS_EXPLICIT_REPORT_PATH", "").strip()
    if not raw:
        return None
    path = Path(raw)
    if not path.exists():
        raise RuntimeError(f"Explicit report path does not exist: {path}")
    if _canonical_report_key(path) is None:
        raise RuntimeError(f"Explicit report path is not a canonical English pro report: {path}")
    return path


def latest_canonical_report(output_dir: Path) -> Path:
    explicit = _explicit_report_path()
    if explicit is not None:
        return explicit
    candidates: list[tuple[str, int, Path]] = []
    for path in output_dir.glob("weekly_analysis_pro_*.md"):
        if path.name.startswith("weekly_analysis_pro_nl_"):
            continue
        key = _canonical_report_key(path)
        if key is not None:
            candidates.append((key[0], key[1], path))
    if not candidates:
        raise RuntimeError(f"No canonical English pro reports found in {output_dir}.")
    candidates.sort(key=lambda item: (item[0], item[1]))
    return candidates[-1][2]


def normalize(md_text: str) -> str:
    return report_module.strip_citations(report_module.normalize_markdown_text(md_text))


def section_lines(md_text: str, section_number: int) -> list[str]:
    return report_module.extract_section_by_number(md_text, section_number)


def section_text(md_text: str, section_number: int) -> str:
    return "\n".join(section_lines(md_text, section_number)).strip()


def has_markdown_table(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines()]
    for i in range(len(lines) - 1):
        if lines[i].startswith("|") and lines[i].endswith("|") and re.match(r"^\|\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|$", lines[i + 1]):
            return True
    return False


def validate_no_forbidden_tokens(md_text: str, report_path: Path) -> None:
    lower = md_text.lower()
    for token in FORBIDDEN_TOKENS:
        if token.lower() in lower:
            raise RuntimeError(f"ETF content contract failed for {report_path.name}: forbidden placeholder token found: {token!r}")


def validate_required_sections(md_text: str, report_path: Path) -> None:
    for section_number, title in REQUIRED_SECTION_TITLES.items():
        text = section_text(md_text, section_number)
        if not text:
            raise RuntimeError(f"ETF content contract failed for {report_path.name}: missing section {section_number} ({title}).")
        if title.lower() not in text.splitlines()[0].lower():
            raise RuntimeError(f"ETF content contract failed for {report_path.name}: section {section_number} title mismatch; expected {title!r}.")
        min_chars = MIN_SECTION_CHARS.get(section_number)
        if min_chars is not None and len(text) < min_chars:
            raise RuntimeError(f"ETF content contract failed for {report_path.name}: section {section_number} ({title}) is too thin ({len(text)} chars).")


def validate_structural_radar(md_text: str, report_path: Path) -> None:
    text = section_text(md_text, 4)
    required = ["Theme", "Primary ETF", "Alternative ETF", "Why it matters"]
    missing = [item for item in required if item not in text]
    if missing or not has_markdown_table(text):
        raise RuntimeError(f"ETF content contract failed for {report_path.name}: Structural Opportunity Radar table is missing/incomplete: {', '.join(missing)}")


def validate_equity_curve(md_text: str, report_path: Path) -> None:
    text = section_text(md_text, 7)
    required = ["Current portfolio value (EUR)", "Since inception return (%)", "Portfolio value (EUR)"]
    missing = [item for item in required if item not in text]
    if missing or not has_markdown_table(text):
        raise RuntimeError(f"ETF content contract failed for {report_path.name}: Section 7 equity curve content is missing/incomplete: {', '.join(missing)}")


def validate_final_action_table(md_text: str, report_path: Path) -> None:
    text = section_text(md_text, 13)
    required = ["Ticker", "Suggested Action", "Total Score", "Portfolio Role"]
    missing = [item for item in required if item not in text]
    if missing or not has_markdown_table(text):
        raise RuntimeError(f"ETF content contract failed for {report_path.name}: Final Action Table is missing/incomplete: {', '.join(missing)}")


def validate_section15(md_text: str, report_path: Path) -> None:
    text = section_text(md_text, 15)
    required = [
        "Invested market value (EUR)",
        "Cash (EUR)",
        "Total portfolio value (EUR)",
        "Ticker",
        "Market value (EUR)",
        "Weight %",
    ]
    missing = [item for item in required if item not in text]
    if missing or not has_markdown_table(text):
        raise RuntimeError(f"ETF content contract failed for {report_path.name}: Section 15 holdings/cash table is missing/incomplete: {', '.join(missing)}")
    report_module.validate_section15_arithmetic(md_text)
    report_module.validate_equity_curve_alignment(md_text)


def validate_report(report_path: Path) -> None:
    md_text = normalize(report_path.read_text(encoding="utf-8"))
    validate_no_forbidden_tokens(md_text, report_path)
    validate_required_sections(md_text, report_path)
    validate_structural_radar(md_text, report_path)
    validate_equity_curve(md_text, report_path)
    validate_final_action_table(md_text, report_path)
    validate_section15(md_text, report_path)
    print(f"ETF_REPORT_CONTENT_CONTRACT_OK | report={report_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    report_path = latest_canonical_report(Path(args.output_dir))
    validate_report(report_path)


if __name__ == "__main__":
    main()
