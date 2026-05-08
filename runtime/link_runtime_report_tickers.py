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
    "CIBR", "BUG", "REMX", "PICK", "XLU", "VPU", "NLR", "NUCL",
    "DBA", "CORN", "PHO", "CGW", "MCHI", "FXI", "EPI", "IBB",
    "XLV", "VHT", "KCE", "IAI", "BOTZ", "ROBO", "IRBO", "COPX",
    "DBC", "DFEN", "NATO",
}

SECTION_TEXT_BOUNDS = [
    ("## 11. Best New Opportunities", "## 12. Portfolio Rotation Plan"),
]

SECTION_TABLE_BOUNDS = [
    ("## 4A. Short Opportunity Radar", "## 5. Key Risks / Invalidators", {"candidate etf"}),
    (
        "## 9. Second-Order Effects Map",
        "## 10. Current Position Review",
        {"first-order effect", "second-order effect", "likely beneficiaries", "likely losers", "etf implication"},
    ),
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


def is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and "|" in stripped[1:-1]


def is_separator_line(line: str) -> bool:
    if not is_table_line(line):
        return False
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def cell_text(cell: str) -> str:
    cell = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cell)
    cell = cell.replace("**", "").replace("`", "")
    return re.sub(r"\s+", " ", cell).strip()


def _is_inside_existing_link(text: str, start: int, end: int) -> bool:
    prefix = text[max(0, start - 120):start]
    suffix = text[end:min(len(text), end + 120)]
    open_bracket = prefix.rfind("[")
    close_bracket = prefix.rfind("]")
    open_paren = suffix.find("(")
    close_paren = suffix.find(")")
    return open_bracket > close_bracket and 0 <= open_paren < close_paren


def linkify_segment(segment: str) -> str:
    ticker_pattern = re.compile(
        r"(?<![A-Za-z0-9_\]/])\b(" + "|".join(sorted(TICKERS, key=len, reverse=True)) + r")\b(?![A-Za-z0-9_\]])"
    )
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


def linkify_text_sections(text: str) -> str:
    for start_heading, end_heading in SECTION_TEXT_BOUNDS:
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


def split_table_row(row: str) -> list[str]:
    return row.strip().strip("|").split("|")


def join_table_row(cells: list[str]) -> str:
    return "|" + "|".join(cells) + "|"


def linkify_table_block(block: list[str], allowed_headers: set[str]) -> list[str]:
    if len(block) < 3:
        return block
    headers = [cell_text(cell).lower() for cell in split_table_row(block[0])]
    linkable_indexes = [idx for idx, header in enumerate(headers) if header in allowed_headers]
    if not linkable_indexes:
        return block

    out = [block[0], block[1]]
    for row in block[2:]:
        cells = split_table_row(row)
        for idx in linkable_indexes:
            if idx < len(cells):
                cells[idx] = linkify_segment(cells[idx])
        out.append(join_table_row(cells))
    return out


def linkify_tables_in_section(section: str, allowed_headers: set[str]) -> str:
    lines = section.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        if i + 1 < len(lines) and is_table_line(lines[i]) and is_separator_line(lines[i + 1]):
            j = i + 2
            block = [lines[i], lines[i + 1]]
            while j < len(lines) and is_table_line(lines[j]):
                block.append(lines[j])
                j += 1
            out.extend(linkify_table_block(block, allowed_headers))
            i = j
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def linkify_table_sections(text: str) -> str:
    for start_heading, end_heading, allowed_headers in SECTION_TABLE_BOUNDS:
        start = text.find(start_heading)
        if start == -1:
            continue
        body_start = start + len(start_heading)
        end = text.find(end_heading, body_start)
        if end == -1:
            continue
        body = text[body_start:end]
        text = text[:body_start] + linkify_tables_in_section(body, allowed_headers) + text[end:]
    return text


def linkify_report(text: str) -> str:
    # Section 2 is deliberately not markdown-linkified. The branded action
    # snapshot renderer converts pure ticker values to TradingView anchors.
    text = linkify_text_sections(text)
    text = linkify_table_sections(text)
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    for pattern in (EN_RE, NL_RE):
        report_path = latest_report(output_dir, pattern)
        report_path.write_text(linkify_report(report_path.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"ETF_LINKIFY_OK | report={report_path.name}")


if __name__ == "__main__":
    main()
