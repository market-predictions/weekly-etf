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

PROTECTED_TICKERS = {"CASH"}

TICKER_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_])\b(" + "|".join(sorted(TICKERS - PROTECTED_TICKERS, key=len, reverse=True)) + r")\b(?![A-Za-z0-9_])"
)
LINK_OR_URL_RE = re.compile(r"\[[^\]]+\]\([^\)]+\)|https?://\S+|`[^`]*`")


def latest_report(output_dir: Path, pattern: re.Pattern[str]) -> Path:
    for env_name in ("MRKT_RPRTS_EXPLICIT_REPORT_PATH", "MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL"):
        raw = os.environ.get(env_name, "").strip()
        if not raw:
            continue
        path = Path(raw)
        if pattern.match(path.name):
            if not path.exists():
                raise RuntimeError(f"Explicit report path from {env_name} does not exist: {path}")
            return path

    reports = sorted(path for path in output_dir.glob("weekly_analysis_pro*.md") if pattern.match(path.name))
    if not reports:
        raise RuntimeError(f"No matching report found in {output_dir} for {pattern.pattern}")
    return reports[-1]


def tv_url(ticker: str) -> str:
    return f"https://www.tradingview.com/chart/?symbol={ticker}"


def md_link(ticker: str) -> str:
    return f"[{ticker}]({tv_url(ticker)})"


def _split_protected_spans(text: str) -> list[tuple[str, bool]]:
    """Return (chunk, protected) spans for existing links, URLs and inline code."""
    spans: list[tuple[str, bool]] = []
    last = 0
    for match in LINK_OR_URL_RE.finditer(text):
        if match.start() > last:
            spans.append((text[last:match.start()], False))
        spans.append((match.group(0), True))
        last = match.end()
    if last < len(text):
        spans.append((text[last:], False))
    return spans


def _linkify_plain_chunk(chunk: str) -> str:
    return TICKER_PATTERN.sub(lambda match: md_link(match.group(1)), chunk)


def linkify_segment(segment: str) -> str:
    return "".join(chunk if protected else _linkify_plain_chunk(chunk) for chunk, protected in _split_protected_spans(segment))


def linkify_report(text: str) -> str:
    """Linkify all known ETF tickers in final markdown, including native NL tables.

    The older implementation only targeted a few English sections/columns. The
    native Dutch renderer creates many client-facing tables with Dutch headers,
    and the position-performance section is inserted after the old linkification
    step. This final-pass linkifier is deliberately report-wide while protecting
    existing links, URLs, inline code and CASH.
    """
    out: list[str] = []
    in_fenced_code = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fenced_code = not in_fenced_code
            out.append(line)
            continue
        if in_fenced_code:
            out.append(line)
            continue
        out.append(linkify_segment(line))
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


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
