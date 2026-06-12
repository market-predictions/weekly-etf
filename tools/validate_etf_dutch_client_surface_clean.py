from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.scrub_etf_client_surface import scrub_text

NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")
SNAKE_CASE_RE = re.compile(r"\b[a-z]+(?:_[a-z0-9]+){1,}\b")
DOUBLE_NEGATIVE_RE = re.compile(r"\bverlaag\s+[A-Z][A-Z0-9.-]*\s+met\s+-\d+(?:\.\d+)?%", re.IGNORECASE)
EMPTY_COMMENT_ARTIFACT_RE = re.compile(r"(?:&lt;!|<!)\s*--\s*--\s*(?:&gt;|>)", re.IGNORECASE)
DUPLICATE_NL_CONSTRAINT_RE = re.compile(
    r"(zachte bovengrens.*zachte bovengrens|zachte doelstelling.*zachte doelstelling)",
    re.IGNORECASE | re.DOTALL,
)
FORBIDDEN_LABELS = ["Redencodes", "Reason codes"]
FORBIDDEN_STALE_GLD_SURFACE = [
    "GLD moet zijn hedgefunctie bewijzen",
    "Houd GLD onder herbeoordeling",
    "GLD blijft een hedgepositie onder herbeoordeling",
    "Herbeoordeling goudhedge",
    "GLD: hedge-validiteitstest vereist",
]


def latest_nl_report(output_dir: Path) -> Path:
    reports = sorted(path for path in output_dir.glob("weekly_analysis_pro_nl_*.md") if NL_RE.match(path.name))
    if not reports:
        raise RuntimeError(f"No Dutch ETF pro report found in {output_dir}")
    return reports[-1]


def _plain_ticker_text(md_text: str) -> str:
    return re.sub(r"\[([A-Z][A-Z0-9.-]*)\]\([^\)]*\)", r"\1", md_text)


def validate(path: Path) -> None:
    original = path.read_text(encoding="utf-8", errors="ignore")
    scrubbed = scrub_text(original)
    if scrubbed != original:
        path.write_text(scrubbed, encoding="utf-8")
        print(f"ETF_DUTCH_CLIENT_SURFACE_SCRUBBED_BEFORE_VALIDATION | report={path.name}")
    text = path.read_text(encoding="utf-8", errors="ignore")
    plain_text = _plain_ticker_text(text)
    failures = sorted(set(match.group(0) for match in SNAKE_CASE_RE.finditer(text)))
    failures.extend(label for label in FORBIDDEN_LABELS if label in text)
    failures.extend(label for label in FORBIDDEN_STALE_GLD_SURFACE if label in text or label in plain_text)
    if DOUBLE_NEGATIVE_RE.search(text):
        failures.append("double-negative reduction wording")
    if EMPTY_COMMENT_ARTIFACT_RE.search(text):
        failures.append("empty HTML comment residue")
    if DUPLICATE_NL_CONSTRAINT_RE.search(text):
        failures.append("duplicate Dutch constraint wording")
    if failures:
        raise RuntimeError("Dutch client-surface cleanliness failed for " + path.name + ": " + "; ".join(sorted(set(failures))))
    print(f"ETF_DUTCH_CLIENT_SURFACE_CLEAN_OK | report={path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    validate(latest_nl_report(Path(args.output_dir)))


if __name__ == "__main__":
    main()
