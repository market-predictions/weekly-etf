from __future__ import annotations

import re
from pathlib import Path

CANONICAL_ENGLISH_REPORT_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?\.md$")
REPLACEMENT_SECTION = "### Best replacements to fund"
DUEL_SECTION = "### Replacement pricing and duel status"

PLACEHOLDER_PHRASES = {
    "no replacement clears",
    "geen vervanger haalt",
    "none",
    "geen",
    "n/a",
}


def latest_canonical_english_pro_report(output_dir: Path) -> Path:
    reports = sorted(
        path
        for path in output_dir.glob("weekly_analysis_pro_*.md")
        if CANONICAL_ENGLISH_REPORT_RE.match(path.name)
    )
    if not reports:
        raise RuntimeError("No canonical English ETF pro reports found in output/.")
    return reports[-1]


def section_text(md_text: str, heading: str) -> str:
    start = md_text.find(heading)
    if start == -1:
        return ""
    tail = md_text[start + len(heading):]
    next_heading = re.search(r"\n###\s+|\n##\s+", tail)
    if next_heading:
        return tail[: next_heading.start()]
    return tail


def replacement_section_mentions_challengers(md_text: str) -> bool:
    section = section_text(md_text, REPLACEMENT_SECTION)
    if not section.strip():
        return False
    compact = " ".join(line.strip() for line in section.splitlines() if line.strip()).lower()
    if not compact:
        return False
    if any(phrase in compact for phrase in PLACEHOLDER_PHRASES) and not re.search(r"\b[A-Z]{2,5}\b\s+(?:versus|vs\.?|/)", section):
        return False
    return bool(re.search(r"\b[A-Z]{2,5}\b\s+(?:versus|vs\.?|/)|\b[A-Z]{2,5}\s*/\s*[A-Z]{2,5}\b", section))


def has_duel_status_table(md_text: str) -> bool:
    section = section_text(md_text, DUEL_SECTION)
    if not section.strip():
        return False
    required_headers = ["Current holding", "Challenger", "Current close", "Challenger close", "Duel status", "Decision implication"]
    return all(header in section for header in required_headers)


def validate_replacement_duel_proof(md_text: str, report_path: Path) -> None:
    if replacement_section_mentions_challengers(md_text) and not has_duel_status_table(md_text):
        raise RuntimeError(
            "Replacement duel proof missing: report mentions replacement challengers under "
            "'Best replacements to fund' but does not include 'Replacement pricing and duel status' "
            "with current/challenger closes and duel status."
        )


if __name__ == "__main__":
    output_dir = Path("output")
    latest = latest_canonical_english_pro_report(output_dir)
    validate_replacement_duel_proof(latest.read_text(encoding="utf-8"), latest)
    print(f"REPLACEMENT_DUELS_OK | report={latest.name}")
