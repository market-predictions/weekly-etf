from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.build_etf_report_state import build_runtime_state

EN_RE = re.compile(r"^weekly_analysis_pro_\d{6}(?:_\d{2})?\.md$")
SECTION_7A_RE = re.compile(r"## 7A\. ETF Position Performance\n(?P<section>.*?)(?=\n## 8\. )", re.DOTALL)

REQUIRED_HEADERS = [
    "Portfolio sleeve",
    "Investment thesis",
    "Tradable ETF",
    "Weight %",
    "1w return",
    "1m return",
    "3m return",
    "Since-entry",
    "P/L EUR",
    "Contribution %",
]

REQUIRED_SEMANTIC_THESES = {
    "CIBR": "Cybersecurity resilience",
    "DFEN": "Defense innovation / tactical defense beta",
    "GSG": "Commodity-breadth hedge exposure",
    "IEFA": "Non-U.S. developed-market diversification",
    "XLU": "Defensive utilities / rate-sensitive ballast",
}

GENERIC_THESIS_CELLS = {
    "",
    "Position",
    "Portfolio exposure",
    "Rotation destination",
    "Portefeuilleblootstelling",
}


def _latest_report(output_dir: Path) -> Path:
    explicit = os.environ.get("MRKT_RPRTS_EXPLICIT_REPORT_PATH", "").strip()
    if explicit:
        path = Path(explicit)
        if path.exists() and EN_RE.match(path.name):
            return path
    reports = sorted(path for path in output_dir.glob("weekly_analysis_pro_*.md") if EN_RE.match(path.name))
    if not reports:
        raise RuntimeError(f"No canonical English ETF pro report found in {output_dir}")
    return reports[-1]


def _current_tickers() -> list[str]:
    state = build_runtime_state()
    out: list[str] = []
    for position in state.get("positions", []) or []:
        ticker = str(position.get("ticker") or "").upper()
        if ticker and ticker != "CASH":
            out.append(ticker)
    return out


def _ticker_link_cell_pattern(ticker: str) -> re.Pattern[str]:
    return re.compile(rf"^\s*(?:\[{re.escape(ticker)}\]\([^\)]*\)|{re.escape(ticker)})\s*$")


def _section_7a(text: str, report_name: str) -> str:
    match = SECTION_7A_RE.search(text)
    if not match:
        raise RuntimeError(f"ETF position performance validation failed for {report_name}: section 7A missing.")
    return match.group("section")


def _rows_by_ticker(section: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped or "Tradable ETF" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 3:
            continue
        for ticker in _current_tickers():
            if _ticker_link_cell_pattern(ticker).match(cells[2]):
                rows[ticker] = cells
    return rows


def validate(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    section = _section_7a(text, path.name)
    for header in REQUIRED_HEADERS:
        if header not in section:
            raise RuntimeError(f"ETF position performance validation failed for {path.name}: missing header {header!r}.")

    rows = _rows_by_ticker(section)
    current = _current_tickers()
    missing = [ticker for ticker in current if ticker not in rows]
    if missing:
        raise RuntimeError(f"ETF position performance validation failed for {path.name}: missing ticker rows: {', '.join(missing)}")

    for ticker, required_thesis in REQUIRED_SEMANTIC_THESES.items():
        if ticker not in rows:
            continue
        thesis = rows[ticker][1]
        if thesis != required_thesis:
            raise RuntimeError(
                f"ETF position performance validation failed for {path.name}: {ticker} thesis must be {required_thesis!r}, found {thesis!r}."
            )

    generic_failures = []
    ticker_only_failures = []
    for ticker, cells in rows.items():
        thesis = cells[1]
        if thesis in GENERIC_THESIS_CELLS:
            generic_failures.append(f"{ticker}={thesis!r}")
        if thesis.upper() == ticker:
            ticker_only_failures.append(ticker)
    if generic_failures:
        raise RuntimeError(
            f"ETF position performance validation failed for {path.name}: generic thesis cells remain: "
            + ", ".join(generic_failures)
        )
    if ticker_only_failures:
        raise RuntimeError(
            f"ETF position performance validation failed for {path.name}: ticker-only thesis cells remain: "
            + ", ".join(ticker_only_failures)
        )

    print(f"ETF_POSITION_PERFORMANCE_OK | report={path.name} | rows={len(current)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    validate(_latest_report(Path(args.output_dir)))


if __name__ == "__main__":
    main()
