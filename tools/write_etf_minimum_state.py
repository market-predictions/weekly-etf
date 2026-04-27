#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import send_report as sr

SCHEMA_VERSION = "1.0"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Write minimum ETF state files from the latest pro report")
    p.add_argument("--output-dir", default="output")
    p.add_argument("--mode", default="pro")
    p.add_argument("--check-only", action="store_true")
    return p.parse_args()


def safe_float(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return sr._to_float(str(value))


def extract_section7_metadata(md_text: str) -> dict:
    lines = sr.extract_section_by_number(md_text, 7)
    pairs = sr._extract_label_pairs(lines)
    return {
        "starting_capital_eur": safe_float(pairs.get("starting capital (eur)")),
        "current_portfolio_value_eur": safe_float(pairs.get("current portfolio value (eur)")),
        "since_inception_return_pct": safe_float(pairs.get("since inception return (%)")),
        "equity_curve_state": pairs.get("equity-curve state"),
        "eurusd_used": safe_float(pairs.get("eur/usd used")),
        "notes": pairs.get("notes"),
    }


def parse_section7_rows(md_text: str) -> list[dict]:
    lines = sr.extract_section_by_number(md_text, 7)
    block = sr._first_markdown_table(lines)
    if not block:
        return []
    rows = sr.parse_markdown_table(block)
    if len(rows) < 2:
        return []
    headers = [sr._match_header_alias(h, sr.SECTION7_HEADER_ALIASES) for h in rows[0]]
    try:
        date_idx = headers.index("date")
        value_idx = headers.index("portfolio value (eur)")
    except ValueError:
        return []
    comment_idx = headers.index("comment") if "comment" in headers else None
    parsed = []
    for row in rows[1:]:
        if len(row) <= max(date_idx, value_idx):
            continue
        report_date = sr.clean_md_inline(row[date_idx])
        nav = safe_float(row[value_idx])
        comment = sr.clean_md_inline(row[comment_idx]) if comment_idx is not None and len(row) > comment_idx else ""
        if report_date and nav is not None:
            parsed.append({"date": report_date, "nav_eur": nav, "comment": comment})
    return parsed


def dedupe_history(rows: list[dict]) -> list[dict]:
    by_date: dict[str, dict] = {}
    for row in rows:
        by_date[row["date"]] = row
    ordered_dates = sorted(by_date.keys())
    return [by_date[d] for d in ordered_dates]


def enrich_history(rows: list[dict], latest_totals: dict, report_name: str, eurusd_used: float | None) -> list[dict]:
    if not rows:
        return []
    start_nav = rows[0]["nav_eur"]
    peak = 0.0
    prev_nav = None
    enriched = []
    for idx, row in enumerate(rows):
        nav = row["nav_eur"]
        peak = max(peak, nav)
        daily_return = 0.0 if prev_nav in (None, 0) else ((nav / prev_nav) - 1.0) * 100.0
        since_inception = ((nav / start_nav) - 1.0) * 100.0 if start_nav else 0.0
        drawdown = ((nav / peak) - 1.0) * 100.0 if peak else 0.0
        out = {
            "date": row["date"],
            "nav_eur": round(nav, 2),
            "cash_eur": "",
            "invested_market_value_eur": "",
            "daily_return_pct": round(daily_return, 4),
            "since_inception_return_pct": round(since_inception, 4),
            "drawdown_pct": round(drawdown, 4),
            "eurusd_used": "",
            "comment": row.get("comment", ""),
            "source_report": report_name,
        }
        if idx == len(rows) - 1:
            out["cash_eur"] = round(latest_totals.get("Cash (EUR)", 0.0), 2)
            out["invested_market_value_eur"] = round(latest_totals.get("Invested market value (EUR)", 0.0), 2)
            out["eurusd_used"] = "" if eurusd_used is None else round(eurusd_used, 4)
        enriched.append(out)
        prev_nav = nav
    return enriched


def parse_positions(md_text: str) -> list[dict]:
    positions = []
    for row in sr.parse_section15_holdings_rows_generic(md_text):
        ticker = sr.clean_md_inline(row.get("ticker", "")).upper()
        if not ticker or ticker == "CASH":
            continue
        positions.append(
            {
                "ticker": ticker,
                "shares": safe_float(row.get("shares")),
                "current_price_local": safe_float(row.get("price (local)")),
                "currency": sr.clean_md_inline(row.get("currency", "")),
                "market_value_local": safe_float(row.get("market value (local)")),
                "market_value_eur": safe_float(row.get("market value (eur)")),
                "current_weight_pct": safe_float(row.get("weight %")),
            }
        )
    return positions


def find_matching_pricing_audit(output_dir: Path, report_date: str) -> str | None:
    pricing_dir = output_dir / "pricing"
    if not pricing_dir.exists():
        return None
    compact = report_date.replace("-", "")
    matches = sorted(pricing_dir.glob(f"price_audit_{compact}*.json"))
    return matches[-1].name if matches else None


def build_portfolio_state(md_text: str, report_path: Path, output_dir: Path) -> tuple[dict, list[dict]]:
    report_date = sr.parse_report_date(md_text)
    section7_meta = extract_section7_metadata(md_text)
    totals = sr.parse_section15_totals_generic(md_text)
    history_rows = enrich_history(
        dedupe_history(parse_section7_rows(md_text)),
        totals,
        report_path.name,
        section7_meta.get("eurusd_used"),
    )
    if not history_rows:
        raise RuntimeError("Could not derive ETF valuation history from section 7.")
    positions = parse_positions(md_text)
    peak_nav = max(row["nav_eur"] for row in history_rows)
    max_drawdown = min(row["drawdown_pct"] for row in history_rows)
    latest_history = history_rows[-1]
    pricing_audit_file = find_matching_pricing_audit(output_dir, report_date)
    state = {
        "schema_version": SCHEMA_VERSION,
        "portfolio_mode": "client_long_only_thematic",
        "base_currency": "EUR",
        "valuation_source": "Latest Weekly ETF Pro report section 15 holdings table and section 7 equity curve",
        "pricing_audit_file": pricing_audit_file,
        "inception_date": history_rows[0]["date"],
        "starting_capital_eur": round(totals.get("Starting capital (EUR)", section7_meta.get("starting_capital_eur") or 0.0), 2),
        "cash_eur": round(totals.get("Cash (EUR)", 0.0), 2),
        "invested_market_value_eur": round(totals.get("Invested market value (EUR)", 0.0), 2),
        "nav_eur": round(totals.get("Total portfolio value (EUR)", section7_meta.get("current_portfolio_value_eur") or 0.0), 2),
        "peak_nav_eur": round(peak_nav, 2),
        "max_drawdown_pct": round(max_drawdown, 4),
        "positions": positions,
        "last_report": {
            "date": report_date,
            "source_report": report_path.name,
            "position_count": len(positions),
        },
        "last_valuation": {
            "date": report_date,
            "nav_eur": round(totals.get("Total portfolio value (EUR)", 0.0), 2),
            "invested_market_value_eur": round(totals.get("Invested market value (EUR)", 0.0), 2),
            "cash_eur": round(totals.get("Cash (EUR)", 0.0), 2),
            "since_inception_return_pct": round(totals.get("Since inception return (%)", section7_meta.get("since_inception_return_pct") or 0.0), 4),
            "daily_return_pct": latest_history["daily_return_pct"],
            "drawdown_pct": latest_history["drawdown_pct"],
            "eurusd_used": None if section7_meta.get("eurusd_used") is None else round(section7_meta.get("eurusd_used"), 4),
            "equity_curve_state": section7_meta.get("equity_curve_state"),
            "valuation_notes": section7_meta.get("notes"),
        },
    }
    return state, history_rows


def write_history_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = [
        "date",
        "nav_eur",
        "cash_eur",
        "invested_market_value_eur",
        "daily_return_pct",
        "since_inception_return_pct",
        "drawdown_pct",
        "eurusd_used",
        "comment",
        "source_report",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    report_path = sr.latest_report_file(output_dir, mode=args.mode)
    md_text = sr.strip_citations(sr.normalize_markdown_text(report_path.read_text(encoding="utf-8")))
    state, history_rows = build_portfolio_state(md_text, report_path, output_dir)
    state_path = output_dir / "etf_portfolio_state.json"
    history_path = output_dir / "etf_valuation_history.csv"
    if args.check_only:
        print(
            f"ETF_STATE_DERIVATION_OK | report={report_path.name} | state={state_path.name} | history_rows={len(history_rows)} | positions={len(state['positions'])}"
        )
        return
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    write_history_csv(history_path, history_rows)
    print(
        f"ETF_STATE_OK | report={report_path.name} | state={state_path.name} | history={history_path.name} | history_rows={len(history_rows)} | positions={len(state['positions'])}"
    )


if __name__ == "__main__":
    main()
