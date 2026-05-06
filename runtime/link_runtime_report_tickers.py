from __future__ import annotations

import argparse
import re
from pathlib import Path

EN_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?\.md$")
NL_RE = re.compile(r"^weekly_analysis_pro_nl_\d{6}(?:_\d{2})?\.md$")

TICKERS = {
    "SPY", "SMH", "PPA", "PAVE", "URNM", "GLD",
    "SOXX", "ITA", "GRID", "URA", "IEFA", "EFA",
    "IWM", "KWEB", "TLT", "ICLN",
    "QUAL", "GSG", "BIL", "MOO", "FIW", "INDA", "XBI", "FINX",
}

SECTION_BOUNDS = [
    ("## 2. Portfolio Action Snapshot", "## 3. Regime Dashboard"),
    ("## 4A. Short Opportunity Radar", "## 5. Key Risks / Invalidators"),
    ("## 9. Second-Order Effects Map", "## 10. Current Position Review"),
    ("## 11. Best New Opportunities", "## 12. Portfolio Rotation Plan"),
]


def latest_report(output_dir: Path, pattern: re.Pattern[str]) -> Path:
    reports = sorted(path for path in output_dir.glob("weekly_analysis_pro*.md") if pattern.match(path.name))
    if not reports:
        raise RuntimeError(f"No matching report found in {output_dir} for {pattern.pattern}")
    return reports[-1]


def tv_url(ticker: str) -> str:
    return f"https://www.tradingview.com/chart/?symbol={ticker}"


def md_link(ticker: str) -> str:
    return f"[{ticker}]({tv_url(ticker)})"


def _is_inside_existing_link(text: str, start: int, end: int) -> bool:
    prefix = text[max(0, start - 120):start]
    suffix = text[end:min(len(text), end + 120)]
    open_bracket = prefix.rfind("[")
    close_bracket = prefix.rfind("]")
    open_paren = suffix.find("(")
    close_paren = suffix.find(")")
    return open_bracket > close_bracket and 0 <= open_paren < close_paren


def linkify_segment(segment: str) -> str:
    ticker_pattern = re.compile(r"(?<![A-Za-z0-9_\]/])\b(" + "|".join(sorted(TICKERS, key=len, reverse=True)) + r")\b(?![A-Za-z0-9_\]])")
    result: list[str] = []
    last = 0
    for match in ticker_pattern.finditer(segment):
        ticker = match.group(1)
        start, end = match.span(1)
        if _is_inside_existing_link(segment, start, end):
            continue
        result.append(segment[last:start])
        result.append(md_link(ticker))
        last = end
    result.append(segment[last:])
    return "".join(result)


def linkify_sections(text: str) -> str:
    for start_heading, end_heading in SECTION_BOUNDS:
        start = text.find(start_heading)
        if start == -1:
            continue
        body_start = start + len(start_heading)
        end = text.find(end_heading, body_start)
        if end == -1:
            continue
        body = text[body_start:end]
        text = text[:body_start] + linkify_segment(body) + text[end:]
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    for pattern in (EN_RE, NL_RE):
        report_path = latest_report(output_dir, pattern)
        report_path.write_text(linkify_sections(report_path.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"ETF_LINKIFY_OK | report={report_path.name}")


if __name__ == "__main__":
    main()
