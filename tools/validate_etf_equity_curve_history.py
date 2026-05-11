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
    return path


def latest_report(output_dir: Path) -> Path:
    explicit = _explicit_report_path()
    if explicit is not None:
        return explicit
    candidates: list[tuple[str, int, Path]] = []
    for path in output_dir.glob("weekly_analysis_pro_*.md"):
        key = _canonical_report_key(path)
        if key:
            candidates.append((key[0], key[1], path))
    if not candidates:
        raise RuntimeError(f"No canonical English ETF pro report found in {output_dir}")
    candidates.sort(key=lambda item: (item[0], item[1]))
    return candidates[-1][2]


def validate_report(path: Path, min_points: int) -> None:
    md_text = report_module.strip_citations(report_module.normalize_markdown_text(path.read_text(encoding="utf-8")))
    points = report_module.parse_section7_equity_points_generic(md_text)
    totals = report_module.parse_section15_totals_generic(md_text)
    total_nav = totals.get("Total portfolio value (EUR)")

    if len(points) < min_points:
        raise RuntimeError(
            f"ETF equity curve history validation failed for {path.name}: "
            f"Section 7 has only {len(points)} point(s); expected at least {min_points}."
        )
    if total_nav is None:
        raise RuntimeError(f"ETF equity curve history validation failed for {path.name}: Section 15 total NAV missing.")
    latest_date, latest_nav = points[-1]
    if abs(float(latest_nav) - float(total_nav)) > 0.05:
        raise RuntimeError(
            f"ETF equity curve history validation failed for {path.name}: latest Section 7 NAV {latest_nav:.2f} "
            f"does not reconcile with Section 15 total NAV {total_nav:.2f}."
        )
    unique_dates = {date for date, _ in points}
    if len(unique_dates) != len(points):
        raise RuntimeError(f"ETF equity curve history validation failed for {path.name}: duplicate dates in Section 7 table.")
    print(f"ETF_EQUITY_CURVE_HISTORY_OK | report={path.name} | points={len(points)} | latest_date={latest_date} | latest_nav={latest_nav:.2f}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--min-points", type=int, default=3)
    args = parser.parse_args()
    validate_report(latest_report(Path(args.output_dir)), args.min_points)


if __name__ == "__main__":
    main()
