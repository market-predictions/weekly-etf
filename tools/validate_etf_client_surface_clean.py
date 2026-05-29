from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.scrub_etf_client_surface import scrub_text

EN_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?\.md$")
NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")
SNAKE_CASE_RE = re.compile(r"\b[a-z]+(?:_[a-z0-9]+){1,}\b")
DOUBLE_NEGATIVE_RE = [
    re.compile(r"\breduce\s+(?:\[[^\]]+\]\([^\)]+\)|[A-Z][A-Z0-9.-]*)\s+by\s+-\d+(?:\.\d+)?%", re.IGNORECASE),
    re.compile(r"\bverlaag\s+(?:\[[^\]]+\]\([^\)]+\)|[A-Z][A-Z0-9.-]*)\s+met\s+-\d+(?:\.\d+)?%", re.IGNORECASE),
]
ALLOWLIST = {"https"}


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


def _current_files(output_dir: Path) -> list[Path]:
    en = _explicit_path("MRKT_RPRTS_EXPLICIT_REPORT_PATH", EN_RE) or _latest(output_dir, EN_RE)
    nl = _explicit_path("MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL", NL_RE) or _latest(output_dir, NL_RE)
    paths = [en, nl]
    for report in (en, nl):
        html = _matching_delivery_html(report)
        if html is not None:
            paths.append(html)
    return paths


def _scrub_file(path: Path) -> None:
    original = path.read_text(encoding="utf-8", errors="ignore")
    cleaned = scrub_text(original)
    if cleaned != original:
        path.write_text(cleaned, encoding="utf-8")
        print(f"ETF_CLIENT_SURFACE_SCRUBBED | file={path.name}")


def _scan(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    hits: list[str] = []
    for match in SNAKE_CASE_RE.finditer(text):
        token = match.group(0)
        if token not in ALLOWLIST:
            hits.append(token)
    for regex in DOUBLE_NEGATIVE_RE:
        if regex.search(text):
            hits.append(regex.pattern)
    return sorted(set(hits))


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
        raise RuntimeError("ETF client-facing surface contains internal labels in current report pair: " + " | ".join(failures))
    print("ETF_CLIENT_SURFACE_CLEAN_OK | files=" + ",".join(path.name for path in paths))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    validate(Path(args.output_dir))


if __name__ == "__main__":
    main()
