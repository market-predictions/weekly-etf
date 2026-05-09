from __future__ import annotations

import re
from pathlib import Path

import send_report as report_module
from runtime.delivery_html_overrides import build_report_html_with_state

PRO_REPORT_RE = re.compile(r"^weekly_analysis_pro_(\d{6})(?:_(\d{2}))?\.md$")
STANDARD_REPORT_RE = re.compile(r"^weekly_analysis_(\d{6})(?:_(\d{2}))?\.md$")


def _canonical_report_key(path: Path, mode: str) -> tuple[str, int] | None:
    match = PRO_REPORT_RE.match(path.name) if mode == "pro" else STANDARD_REPORT_RE.match(path.name)
    if not match:
        return None
    return match.group(1), int(match.group(2) or "1")


def _latest_canonical_report_file(output_dir: Path, mode: str = "standard") -> Path:
    normalized_mode = report_module.normalize_report_mode(mode)
    candidates: list[tuple[str, int, Path]] = []
    for path in output_dir.glob("weekly_analysis*.md"):
        key = _canonical_report_key(path, normalized_mode)
        if key is not None:
            candidates.append((key[0], key[1], path))
    if not candidates:
        raise RuntimeError(f"No canonical {normalized_mode} report files found in {output_dir}.")
    candidates.sort(key=lambda item: (item[0], item[1]))
    return candidates[-1][2]


def _latest_canonical_reports_by_day(output_dir: Path, mode: str = "standard") -> list[Path]:
    normalized_mode = report_module.normalize_report_mode(mode)
    by_day: dict[str, tuple[int, Path]] = {}
    for path in output_dir.glob("weekly_analysis*.md"):
        key = _canonical_report_key(path, normalized_mode)
        if key is None:
            continue
        day, version = key
        if day not in by_day or version > by_day[day][0]:
            by_day[day] = (version, path)
    return [item[1] for item in sorted(by_day.values(), key=lambda row: row[1].name)]


report_module.latest_report_file = _latest_canonical_report_file
report_module.latest_reports_by_day = _latest_canonical_reports_by_day
report_module.build_report_html = build_report_html_with_state(report_module.build_report_html, report_module._base)

if __name__ == "__main__":
    report_module.main()
