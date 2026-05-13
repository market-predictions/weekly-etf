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


def validate(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "## 7A. ETF Position Performance" not in text:
        raise RuntimeError(f"ETF position performance validation failed for {path.name}: section 7A missing.")
    for header in REQUIRED_HEADERS:
        if header not in text:
            raise RuntimeError(f"ETF position performance validation failed for {path.name}: missing header {header!r}.")
    missing = [ticker for ticker in _current_tickers() if f"| {ticker} |" not in text and f"| {ticker} |" not in text.replace("[", "").replace("]", "")]
    # After linkification, ticker cells may become markdown links. Keep a regex fallback.
    for ticker in list(missing):
        if re.search(rf"\|\s*\[{re.escape(ticker)}\]\([^\)]*\)\s*\|", text):
            missing.remove(ticker)
    if missing:
        raise RuntimeError(f"ETF position performance validation failed for {path.name}: missing ticker rows: {', '.join(missing)}")
    print(f"ETF_POSITION_PERFORMANCE_OK | report={path.name} | rows={len(_current_tickers())}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    validate(_latest_report(Path(args.output_dir)))


if __name__ == "__main__":
    main()
