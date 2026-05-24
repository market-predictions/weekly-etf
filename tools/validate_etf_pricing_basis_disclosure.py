from __future__ import annotations

import argparse
import re
from pathlib import Path

EN_REPORT_RE = re.compile(r"^weekly_analysis_pro_(\d{6})(?:_(\d{2}))?\.md$")
TV_LINK_RE = re.compile(r"\[([A-Z][A-Z0-9./_-]{1,14})\]\(https://www\.tradingview\.com/chart/\?symbol=[^)]+\)")

REQUIRED_EN = [
    "### Closing prices used in this report",
    "| Holding | Requested close | Close date used | Close used | Currency | Market-data source | Status |",
    "| FX basis | Requested date | Date used | Rate | Source | Status |",
]

REQUIRED_NL = [
    "### Gebruikte slotkoersen in dit rapport",
    "| Positie | Gevraagde slotdatum | Gebruikte slotdatum | Gebruikte slotkoers | Valuta | Marktdata-bron | Status |",
    "| FX-basis | Gevraagde datum | Gebruikte datum | Koers | Bron | Status |",
]

REQUIRED_TICKERS = {"SPY", "SMH", "PPA", "PAVE", "URNM", "GLD"}
FORBIDDEN_INTERNAL = ["ETF_PRICE_BASIS_DISCLOSURE", "issuer_override", "source_detail", "handler"]


def latest_pair(output_dir: Path) -> tuple[Path, Path]:
    rows: list[tuple[str, int, Path]] = []
    for path in output_dir.glob("weekly_analysis_pro_*.md"):
        if "_nl_" in path.name or path.name.endswith("_clean.md"):
            continue
        m = EN_REPORT_RE.match(path.name)
        if m:
            rows.append((m.group(1), int(m.group(2) or "1"), path))
    if not rows:
        raise SystemExit("FAIL: no English ETF Pro report found")
    rows.sort(key=lambda x: (x[0], x[1]))
    token, version, en = rows[-1]
    suffix = "" if version == 1 else f"_{version:02d}"
    nl = output_dir / f"weekly_analysis_pro_nl_{token}{suffix}.md"
    if not nl.exists():
        raise SystemExit(f"FAIL: matching Dutch report missing: {nl.name}")
    return en, nl


def disclosure(text: str, language: str) -> str:
    heading = "### Gebruikte slotkoersen in dit rapport" if language == "nl" else "### Closing prices used in this report"
    start = text.find(heading)
    if start == -1:
        return ""
    tail = text[start:]
    next_heading = re.search(r"\n###\s+|\n##\s+|\n`EQUITY_CURVE_CHART_PLACEHOLDER`", tail[len(heading):])
    if next_heading:
        return tail[: len(heading) + next_heading.start()]
    return tail


def normalize_tv_links(markdown: str) -> str:
    return TV_LINK_RE.sub(r"\1", markdown)


def ticker_row_present(block: str, ticker: str) -> bool:
    normalized = normalize_tv_links(block)
    for line in normalized.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] == ticker:
            return True
    return False


def validate_report(path: Path, language: str) -> list[str]:
    text = path.read_text(encoding="utf-8")
    block = disclosure(text, language)
    failures: list[str] = []
    if not block:
        return [f"{path.name}: missing pricing basis disclosure block"]
    required = REQUIRED_NL if language == "nl" else REQUIRED_EN
    for item in required:
        if item not in block:
            failures.append(f"{path.name}: missing {item}")
    for ticker in REQUIRED_TICKERS:
        if not ticker_row_present(block, ticker):
            failures.append(f"{path.name}: missing pricing row for {ticker}")
    if "EUR/USD" not in block:
        failures.append(f"{path.name}: missing EUR/USD FX row")
    for forbidden in FORBIDDEN_INTERNAL:
        if forbidden in text:
            failures.append(f"{path.name}: client-facing report leaks internal pricing label: {forbidden}")
    if "unknown" in block.lower() or "onbekend" in block.lower():
        failures.append(f"{path.name}: pricing disclosure contains unknown/onbekend")
    if "Yahoo" not in block and "Twelve Data" not in block and "Opgeslagen" not in block and "Persisted" not in block:
        failures.append(f"{path.name}: pricing disclosure does not show a client-facing market-data source")
    return failures


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    en, nl = latest_pair(Path(args.output_dir))
    failures = validate_report(en, "en") + validate_report(nl, "nl")
    if failures:
        raise SystemExit("FAIL: ETF pricing basis disclosure validation failed: " + "; ".join(failures[:12]))
    print(f"ETF_PRICING_BASIS_DISCLOSURE_OK | en={en.name} | nl={nl.name}")


if __name__ == "__main__":
    main()
