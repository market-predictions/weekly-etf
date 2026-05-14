from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

EN_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?\.md$")
NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")

TICKERS = {
    "SPY", "SMH", "PPA", "PAVE", "URNM", "GLD",
    "SOXX", "ITA", "GRID", "URA", "IEFA", "EFA",
    "IWM", "KWEB", "TLT", "ICLN", "QUAL", "GSG", "BIL",
    "MOO", "FIW", "INDA", "XBI", "FINX", "CIBR", "BUG",
    "REMX", "PICK", "XLU", "VPU", "NLR", "NUCL", "DBA",
    "CORN", "PHO", "CGW", "MCHI", "FXI", "EPI", "IBB",
    "XLV", "VHT", "KCE", "IAI", "BOTZ", "ROBO", "IRBO",
    "COPX", "DBC", "DFEN", "NATO",
}
PROTECTED = {"CASH"}
TICKER_RE = re.compile(r"(?<![A-Za-z0-9_\]/])\b(" + "|".join(sorted(TICKERS - PROTECTED, key=len, reverse=True)) + r")\b(?![A-Za-z0-9_\]])")
LINK_RE = re.compile(r"\[([A-Z]{2,6})\]\(https://www\.tradingview\.com/chart/\?symbol=\1\)")
URL_OR_CODE_RE = re.compile(r"https?://\S+|`[^`]*`")

IMPORTANT_HEADINGS = [
    "## 4. Structural Opportunity Radar",
    "## 4. Structurele kansenradar",
    "## 4A. Short Opportunity Radar",
    "## 4A. Shortkansenradar",
    "## 7A. ETF Position Performance",
    "## 7A. Rendement huidige ETF-posities",
    "## 9. Second-Order Effects Map",
    "## 9. Tweede-orde-effectenkaart",
    "## 10. Current Position Review",
    "## 10. Review huidige posities",
    "## 11. Best New Opportunities",
    "## 11. Beste nieuwe kansen",
    "## 12. Portfolio Rotation Plan",
    "## 12. Rotatieplan portefeuille",
    "## 13. Final Action Table",
    "## 13. Definitieve actietabel",
    "## 14. Position Changes Executed This Run",
    "## 14. Positiewijzigingen in deze run",
    "## 15. Current Portfolio Holdings and Cash",
    "## 15. Huidige posities en cash",
    "## 16. Continuity Input for Next Run",
    "## 16. Input voor de volgende run",
]


def latest_report(output_dir: Path, pattern: re.Pattern[str]) -> Path:
    env_key = "MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL" if pattern is NL_RE else "MRKT_RPRTS_EXPLICIT_REPORT_PATH"
    explicit = os.environ.get(env_key, "").strip()
    if explicit:
        path = Path(explicit)
        if path.exists() and pattern.match(path.name):
            return path
    reports = sorted(path for path in output_dir.glob("weekly_analysis_pro*.md") if pattern.match(path.name))
    if not reports:
        raise RuntimeError(f"No matching report found in {output_dir}")
    return reports[-1]


def important_lines(text: str) -> list[tuple[int, str]]:
    lines = text.splitlines()
    out: list[tuple[int, str]] = []
    active = False
    for idx, line in enumerate(lines, start=1):
        if line.startswith("## "):
            active = any(line.startswith(h) for h in IMPORTANT_HEADINGS)
        if active:
            out.append((idx, line))
    return out


def strip_links_urls_code(line: str) -> str:
    line = LINK_RE.sub("", line)
    line = URL_OR_CODE_RE.sub("", line)
    return line


def validate_report(path: Path) -> None:
    failures: list[str] = []
    text = path.read_text(encoding="utf-8")
    for line_no, line in important_lines(text):
        if not line.strip() or line.strip().startswith("|") and re.fullmatch(r"\|?[-:|\s]+\|?", line.strip()):
            continue
        remainder = strip_links_urls_code(line)
        for match in TICKER_RE.finditer(remainder):
            ticker = match.group(1)
            failures.append(f"line {line_no}: {ticker}: {line.strip()[:180]}")
    if failures:
        raise RuntimeError("ETF ticker link validation failed for " + path.name + ": " + "; ".join(failures[:20]))
    print(f"ETF_TICKER_LINKS_OK | report={path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    validate_report(latest_report(output_dir, EN_RE))
    validate_report(latest_report(output_dir, NL_RE))


if __name__ == "__main__":
    main()
