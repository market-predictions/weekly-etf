from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from runtime.nl_dates import localize_english_report_dates

NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")

ENGLISH_DATE_TOKENS = [
    "Monday,",
    "Tuesday,",
    "Wednesday,",
    "Thursday,",
    "Friday,",
    "Saturday,",
    "Sunday,",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    report_path = latest_nl_report(Path(args.output_dir))
    text = report_path.read_text(encoding="utf-8")
    localized = localize_english_report_dates(text)

    remaining = [token for token in ENGLISH_DATE_TOKENS if token in localized]
    if remaining:
        raise RuntimeError("Dutch report date localization failed; remaining English date tokens: " + ", ".join(sorted(set(remaining))))

    report_path.write_text(localized, encoding="utf-8")
    print(f"ETF_NL_DATE_LOCALIZATION_OK | report={report_path.name}")


if __name__ == "__main__":
    main()
