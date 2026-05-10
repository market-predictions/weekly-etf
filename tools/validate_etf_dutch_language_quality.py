from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.nl_localization import DUTCH_DISCLAIMER, FORBIDDEN_NL_STRINGS, validate_dutch_text

NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")

REQUIRED_DUTCH_MARKERS = [
    "Kernsamenvatting",
    "Portefeuille-acties",
    "Vervangingsanalyse",
    "Review huidige posities",
    "Rotatieplan portefeuille",
    "Huidige posities en cash",
    "Input voor de volgende run",
]

FORBIDDEN_CLIENT_LABELS = [
    "Executive Summary",
    "Portfolio Action Snapshot",
    "Current Position Review",
    "Portfolio Rotation Plan",
    "Current Portfolio Holdings and Cash",
    "Continuity Input for Next Run",
    "Position Changes Executed This Run",
    "Final Action Table",
    "What changed this week",
    "Portfolio implication",
    "Current holding still leads",
    "Replacement trigger watch",
    "Needs sustained relative outperformance",
    "Confirm thesis fit",
]

ALLOWED_ENGLISH_PATTERNS = [
    r"\bETF\b",
    r"\bticker\b",
    r"\bcash\b",
    r"\bhedge\b",
    r"\bdrawdown\b",
    r"\bbeta\b",
    r"\bcapex\b",
    r"\bsmall-cap\b",
    r"\blarge-cap\b",
    r"\brisk-on\b",
    r"\brisk-off\b",
    r"\bAI\b",
    r"\bsemiconductor\b",
    r"\boutperformance\b",
    r"\bwatchlist\b",
]


def latest_nl_report(output_dir: Path) -> Path:
    explicit = os.environ.get("MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL", "").strip()
    if explicit:
        path = Path(explicit)
        if path.exists() and NL_RE.match(path.name):
            return path
    reports = sorted(path for path in output_dir.glob("weekly_analysis_pro_nl_*.md") if NL_RE.match(path.name))
    if not reports:
        raise RuntimeError(f"No Dutch ETF pro report found in {output_dir}")
    return reports[-1]


def _failures_for_text(text: str) -> list[str]:
    failures: list[str] = []
    failures.extend(validate_dutch_text(text))
    for marker in REQUIRED_DUTCH_MARKERS:
        if marker not in text:
            failures.append(f"missing Dutch marker: {marker}")
    for label in FORBIDDEN_CLIENT_LABELS:
        if label in text:
            failures.append(f"forbidden English client label: {label}")
    for token in FORBIDDEN_NL_STRINGS:
        if token in text and token not in failures:
            failures.append(f"forbidden Dutch report token: {token}")
    if DUTCH_DISCLAIMER not in text:
        failures.append("Dutch disclaimer does not match contract")
    if "and it is not a recommendation" in text or "It does not take into account" in text:
        failures.append("half-English disclaimer remains")
    return failures


def validate_report(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    failures = _failures_for_text(text)
    if failures:
        raise RuntimeError("Dutch language quality validation failed for " + path.name + ": " + "; ".join(failures))
    print(f"ETF_DUTCH_LANGUAGE_QUALITY_OK | report={path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    validate_report(latest_nl_report(Path(args.output_dir)))


if __name__ == "__main__":
    main()
