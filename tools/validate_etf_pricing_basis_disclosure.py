from __future__ import annotations

import argparse
import re
from pathlib import Path

START = "<!-- ETF_PRICE_BASIS_DISCLOSURE_START -->"
END = "<!-- ETF_PRICE_BASIS_DISCLOSURE_END -->"
EN_REPORT_RE = re.compile(r"^weekly_analysis_pro_(\d{6})(?:_(\d{2}))?\.md$")

REQUIRED_EN = [
    "### Closing prices used in this report",
    "| Holding | Close date used | Close used | Currency | Pricing source | Status |",
    "| FX basis | Date used | Rate | Source | Status |",
]

REQUIRED_NL = [
    "### Gebruikte slotkoersen in dit rapport",
    "| Positie | Gebruikte slotdatum | Gebruikte slotkoers | Valuta | Prijsbron | Status |",
    "| FX-basis | Gebruikte datum | Koers | Bron | Status |",
]

REQUIRED_TICKERS = {"SPY", "SMH", "PPA", "PAVE", "URNM", "GLD"}


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


def disclosure(text: str) -> str:
    m = re.search(rf"{re.escape(START)}(.*?){re.escape(END)}", text, re.S)
    if not m:
        return ""
    return m.group(1)


def validate_report(path: Path, language: str) -> list[str]:
    text = path.read_text(encoding="utf-8")
    block = disclosure(text)
    failures: list[str] = []
    if not block:
        return [f"{path.name}: missing pricing basis disclosure block"]
    required = REQUIRED_NL if language == "nl" else REQUIRED_EN
    for item in required:
        if item not in block:
            failures.append(f"{path.name}: missing {item}")
    for ticker in REQUIRED_TICKERS:
        if not re.search(rf"\|\s*{ticker}\s*\|", block):
            failures.append(f"{path.name}: missing pricing row for {ticker}")
    if "EUR/USD" not in block:
        failures.append(f"{path.name}: missing EUR/USD FX row")
    if "unknown" in block.lower() or "onbekend" in block.lower():
        failures.append(f"{path.name}: pricing disclosure contains unknown/onbekend")
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
