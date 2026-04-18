from __future__ import annotations

import argparse
import re
from datetime import date, timedelta
from pathlib import Path

from .models import PriceRequest, PricingPassResult
from .shortlist_builder import build_holdings_shortlist, merge_and_deduplicate
from .close_resolver import CloseResolver
from .fx_resolver import resolve_fx
from .audit_writer import write_price_audit

REPORT_RE = re.compile(r"weekly_analysis(?:_pro)?_(\\d{6})(?:_(\\d{2}))?\\.md$")


def latest_report_file(output_dir: Path) -> Path:
    files = []
    for path in output_dir.glob("weekly_analysis_pro_*.md"):
        m = REPORT_RE.match(path.name)
        if m:
            day = m.group(1)
            version = int(m.group(2) or "1")
            files.append((day, version, path))
    if not files:
        raise RuntimeError("No production ETF pro reports found in output/.")
    files.sort(key=lambda x: (x[0], x[1]))
    return files[-1][2]


def requested_close_from_today(today: date) -> str:
    d = today
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d.isoformat()


def _to_float(text: str) -> float | None:
    text = text.replace(",", "").replace("%", "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_section15_holdings(md_text: str) -> tuple[list[str], dict[str, float]]:
    section_start = md_text.find("## 15.")
    if section_start == -1:
        return [], {}
    section = md_text[section_start:]
    tickers: list[str] = []
    weights: dict[str, float] = {}
    in_table = False
    for line in section.splitlines():
        if line.startswith("| Ticker |"):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                break
            if "---" in line:
                continue
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            if len(parts) < 7:
                continue
            ticker = parts[0].upper()
            weight = _to_float(parts[6])
            if ticker and ticker != "CASH":
                tickers.append(ticker)
                if weight is not None:
                    weights[ticker] = weight
    return tickers, weights


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--requested-close-date", default=None)
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--pricing-dir", default="output/pricing")
    args = parser.parse_args()

    today = date.today()
    requested_close_date = args.requested_close_date or requested_close_from_today(today)
    run_date = today.isoformat()

    output_dir = Path(args.output_dir)
    latest = latest_report_file(output_dir)
    md_text = latest.read_text(encoding="utf-8")
    holdings, weights = parse_section15_holdings(md_text)
    if not holdings:
        raise RuntimeError("Could not parse current holdings from section 15.")

    shortlist = merge_and_deduplicate(build_holdings_shortlist(holdings))
    resolver = CloseResolver("pricing/source_registry.yaml", "pricing/rate_limits.yaml", run_date)

    results = []
    fresh_count = 0
    unresolved = []
    fresh_weight = 0.0

    for item in shortlist:
        result = resolver.resolve(PriceRequest(symbol=item.symbol, requested_close_date=requested_close_date, kind=item.kind))
        results.append(result)
        if result.status == "fresh_close":
            fresh_count += 1
            fresh_weight += weights.get(item.symbol.upper(), 0.0)
        if result.status == "unresolved":
            unresolved.append(item.symbol)

    fx = resolve_fx(requested_close_date)

    holdings_count = len(shortlist)
    coverage_count_pct = round((fresh_count / holdings_count) * 100.0, 2) if holdings_count else 0.0
    invested_weight_coverage_pct = round(fresh_weight, 2)

    if coverage_count_pct >= 75.0 or invested_weight_coverage_pct >= 85.0:
        decision = "update_covered_holdings_carry_unresolved"
    else:
        decision = "blocked_or_partial"

    pass_result = PricingPassResult(
        run_date=run_date,
        requested_close_date=requested_close_date,
        holdings_count=holdings_count,
        fresh_holdings_count=fresh_count,
        coverage_count_pct=coverage_count_pct,
        invested_weight_coverage_pct=invested_weight_coverage_pct,
        decision=decision,
        unresolved_tickers=unresolved,
        fx_basis=fx,
        prices=results,
    )

    audit_path = write_price_audit(args.pricing_dir, pass_result)
    print(
        f"PRICING_PASS_{'OK' if fresh_count else 'PARTIAL'} | requested_close={requested_close_date} | "
        f"holdings={holdings_count} | fresh={fresh_count} | weight_coverage={invested_weight_coverage_pct:.2f} | audit={audit_path}"
    )


if __name__ == "__main__":
    main()
