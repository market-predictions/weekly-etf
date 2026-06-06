from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime import nl_terminology_contract as contract
from runtime.nl_localization import validate_dutch_text

DUTCH_DISCLAIMER = contract.term.DUTCH_DISCLAIMER
NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")

REQUIRED_DUTCH_MARKERS = contract.term.REQUIRED_DUTCH_MARKERS

FORBIDDEN_CLIENT_LABELS = contract.term.FORBIDDEN_CLIENT_LABELS

FORBIDDEN_DECISION_WORDS = contract.term.FORBIDDEN_DECISION_WORDS

PDF_AUDIT_FORBIDDEN = contract.term.PDF_AUDIT_FORBIDDEN

ALLOWED_ENGLISH_PATTERNS = [
    rf"\b{re.escape(token)}\b" for token in sorted(contract.term.ALLOWED_ENGLISH_TERMS)
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


def _strip_markdown_links(text: str) -> str:
    return re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)


def _failures_for_text(text: str) -> list[str]:
    failures: list[str] = []
    plain = _strip_markdown_links(text)
    failures.extend(validate_dutch_text(plain))
    for marker in REQUIRED_DUTCH_MARKERS:
        if marker not in plain:
            failures.append(f"missing Dutch marker: {marker}")
    for label in FORBIDDEN_CLIENT_LABELS:
        if label in plain:
            failures.append(f"forbidden English client label: {label}")
    for token in contract.term.FORBIDDEN_NL_STRINGS:
        if token in plain:
            failures.append(f"forbidden Dutch report token: {token}")
    for token in FORBIDDEN_DECISION_WORDS:
        if token in plain:
            failures.append(f"forbidden English/low-quality decision wording: {token.strip()}")
    for token in PDF_AUDIT_FORBIDDEN:
        if token in plain:
            failures.append(f"PDF-audit forbidden English or low-quality token: {token}")
    if DUTCH_DISCLAIMER not in plain:
        failures.append("Dutch disclaimer does not match contract")
    if "and it is not a recommendation" in plain or "It does not take into account" in plain:
        failures.append("half-English disclaimer remains")
    if re.search(r"\bbut\b", plain, flags=re.IGNORECASE):
        failures.append("mixed-language connector remains: but")
    return sorted(set(failures))


def validate_report(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    failures = _failures_for_text(text)
    if failures:
        raise RuntimeError("Dutch language quality validation failed for " + path.name + ": " + "; ".join(failures))
    print(f"ETF_DUTCH_LANGUAGE_QUALITY_OK | report={path.name} | terminology=central")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    validate_report(latest_nl_report(Path(args.output_dir)))


if __name__ == "__main__":
    main()
