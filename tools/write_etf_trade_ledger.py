#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import send_report as sr

SECTION13_ALIASES = {
    "ticker": "ticker",
    "target weight": "target_weight_pct",
    "suggested action": "suggested_action",
    "conviction tier": "conviction_tier",
    "portfolio role": "portfolio_role",
}

SECTION14_ALIASES = {
    "ticker": "ticker",
    "previous weight %": "previous_weight_pct",
    "new weight %": "new_weight_pct",
    "weight change %": "weight_change_pct",
    "shares delta": "shares_delta",
    "action executed": "action_executed",
    "funding source / note": "funding_source_note",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Write ETF trade ledger from canonical pro reports")
    p.add_argument("--output-dir", default="output")
    p.add_argument("--check-only", action="store_true")
    return p.parse_args()


def safe_float(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return sr._to_float(str(value))


def normalize_header(text: str) -> str:
    cleaned = sr.clean_md_inline(text or "").strip().lower()
    cleaned = cleaned.replace("–", "-").replace("—", "-")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def parse_first_table(lines: list[str], alias_map: dict[str, str]) -> list[dict]:
    block = sr._first_markdown_table(lines)
    if not block:
        return []
    rows = sr.parse_markdown_table(block)
    if len(rows) < 2:
        return []
    headers = [alias_map.get(normalize_header(h), normalize_header(h)) for h in rows[0]]
    parsed: list[dict] = []
    for raw_row in rows[1:]:
        row = {}
        for idx, header in enumerate(headers):
            row[header] = sr.clean_md_inline(raw_row[idx]) if idx < len(raw_row) else ""
        parsed.append(row)
    return parsed


def parse_section13_map(md_text: str) -> dict[str, dict]:
    rows = parse_first_table(sr.extract_section_by_number(md_text, 13), SECTION13_ALIASES)
    out = {}
    for row in rows:
        ticker = row.get("ticker", "").upper()
        if ticker:
            out[ticker] = {
                "target_weight_pct": safe_float(row.get("target_weight_pct")),
                "suggested_action": row.get("suggested_action") or None,
                "conviction_tier": row.get("conviction_tier") or None,
                "portfolio_role": row.get("portfolio_role") or None,
            }
    return out


def parse_section14_rows(md_text: str) -> list[dict]:
    rows = parse_first_table(sr.extract_section_by_number(md_text, 14), SECTION14_ALIASES)
    out = []
    for row in rows:
        ticker = row.get("ticker", "").upper()
        if not ticker or ticker == "CASH":
            continue
        out.append(
            {
                "ticker": ticker,
                "previous_weight_pct": safe_float(row.get("previous_weight_pct")),
                "new_weight_pct": safe_float(row.get("new_weight_pct")),
                "weight_change_pct": safe_float(row.get("weight_change_pct")),
                "shares_delta": safe_float(row.get("shares_delta")),
                "action_executed": row.get("action_executed") or None,
                "funding_source_note": row.get("funding_source_note") or None,
            }
        )
    return out


def canonical_pro_reports(output_dir: Path) -> list[Path]:
    reports = []
    for path in sorted(output_dir.glob("weekly_analysis_pro_*.md")):
        if "_nl_" in path.name:
            continue
        reports.append(path)
    return reports


def should_record(row: dict) -> bool:
    shares_delta = row.get("shares_delta")
    action = (row.get("action_executed") or "").strip().lower()
    if shares_delta is not None and abs(shares_delta) > 0:
        return True
    if action and action not in {"none", "no change", "hold", "maintain"}:
        return True
    return False


def build_trade_rows(output_dir: Path) -> list[dict]:
    ledger_rows: list[dict] = []
    for report_path in canonical_pro_reports(output_dir):
        md_text = sr.strip_citations(sr.normalize_markdown_text(report_path.read_text(encoding="utf-8")))
        report_date = sr.parse_report_date(md_text)
        section13 = parse_section13_map(md_text)
        for row in parse_section14_rows(md_text):
            if not should_record(row):
                continue
            ticker = row["ticker"]
            s13 = section13.get(ticker, {})
            ledger_rows.append(
                {
                    "trade_id": f"{report_path.stem}-{ticker}",
                    "trade_date": report_date,
                    "source_report": report_path.name,
                    "ticker": ticker,
                    "action": row.get("action_executed") or s13.get("suggested_action") or "Unknown",
                    "shares_delta": "" if row.get("shares_delta") is None else round(row.get("shares_delta"), 6),
                    "previous_weight_pct": "" if row.get("previous_weight_pct") is None else round(row.get("previous_weight_pct"), 4),
                    "new_weight_pct": "" if row.get("new_weight_pct") is None else round(row.get("new_weight_pct"), 4),
                    "weight_change_pct": "" if row.get("weight_change_pct") is None else round(row.get("weight_change_pct"), 4),
                    "target_weight_pct": "" if s13.get("target_weight_pct") is None else round(s13.get("target_weight_pct"), 4),
                    "conviction_tier": s13.get("conviction_tier") or "",
                    "portfolio_role": s13.get("portfolio_role") or "",
                    "funding_source_note": row.get("funding_source_note") or "",
                }
            )
    ledger_rows.sort(key=lambda r: (r["trade_date"], r["trade_id"]))
    return ledger_rows


def write_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = [
        "trade_id",
        "trade_date",
        "source_report",
        "ticker",
        "action",
        "shares_delta",
        "previous_weight_pct",
        "new_weight_pct",
        "weight_change_pct",
        "target_weight_pct",
        "conviction_tier",
        "portfolio_role",
        "funding_source_note",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    ledger_path = output_dir / "etf_trade_ledger.csv"
    rows = build_trade_rows(output_dir)
    if args.check_only:
        print(f"ETF_TRADE_LEDGER_DERIVATION_OK | ledger={ledger_path.name} | rows={len(rows)}")
        return
    write_csv(ledger_path, rows)
    print(f"ETF_TRADE_LEDGER_OK | ledger={ledger_path.name} | rows={len(rows)}")


if __name__ == "__main__":
    main()
