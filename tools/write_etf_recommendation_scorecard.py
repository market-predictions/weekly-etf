#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import send_report as sr

FIELDNAMES = [
    "report_date",
    "ticker",
    "weight_pct",
    "shares",
    "current_price_local",
    "currency",
    "market_value_eur",
    "pnl_pct",
    "total_score",
    "suggested_action",
    "conviction_tier",
    "portfolio_role",
    "fresh_cash_test",
    "would_initiate_today",
    "would_initiate_at_current_weight",
    "thesis_score",
    "implementation_score",
    "replaceable_status",
    "weeks_replaceable",
    "best_alternative",
    "alternative_score",
    "contribution_quality",
    "factor_overlap_flag",
    "hedge_validity_status",
    "cash_policy_flag",
    "required_next_action",
    "override_reason",
    "discipline_flags",
    "source_report",
]

SECTION13_ALIASES = {
    "ticker": "ticker",
    "etf": "etf",
    "weight inherited": "weight_inherited_pct",
    "target weight": "target_weight_pct",
    "suggested action": "suggested_action",
    "conviction tier": "conviction_tier",
    "total score": "total_score",
    "portfolio role": "portfolio_role",
    "better alternative exists?": "better_alternative_exists",
    "short reason": "short_reason",
}

SECTION16_ALIASES = {
    "ticker": "ticker",
    "etf name": "etf_name",
    "direction": "direction",
    "weight %": "weight_pct",
    "avg entry": "avg_entry_local",
    "current price": "current_price_local",
    "p/l %": "pnl_pct",
    "original thesis": "original_thesis",
    "role": "role",
}

ALT_BY_TICKER = {
    "SPY": "QQQ/QUAL/IEFA",
    "SMH": "SOXX",
    "PPA": "ITA",
    "PAVE": "GRID",
    "URNM": "URA",
    "GLD": "GSG/DJP/BIL",
}

THEME_BY_TICKER = {
    "SPY": "U.S. equity beta / tech overlap",
    "SMH": "AI compute / semiconductor leadership",
    "PPA": "defense / sovereign resilience",
    "PAVE": "infrastructure / grid capex",
    "URNM": "uranium / nuclear fuel cycle",
    "GLD": "gold / hard-asset hedge",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Write ETF recommendation scorecard from the latest canonical pro report")
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


def clean(value: str | None) -> str:
    return sr.clean_md_inline(value or "").strip()


def norm_header(value: str) -> str:
    value = clean(value).lower()
    value = value.replace("–", "-").replace("—", "-")
    value = re.sub(r"\s+", " ", value)
    return value


def first_table_rows(lines: list[str], aliases: dict[str, str]) -> list[dict[str, str]]:
    block = sr._first_markdown_table(lines)
    if not block:
        return []
    rows = sr.parse_markdown_table(block)
    if len(rows) < 2:
        return []
    headers = [aliases.get(norm_header(h), norm_header(h)) for h in rows[0]]
    parsed = []
    for raw in rows[1:]:
        item = {}
        for i, h in enumerate(headers):
            item[h] = clean(raw[i]) if i < len(raw) else ""
        parsed.append(item)
    return parsed


def section13_map(md_text: str) -> dict[str, dict[str, str]]:
    rows = first_table_rows(sr.extract_section_by_number(md_text, 13), SECTION13_ALIASES)
    return {clean(r.get("ticker")).upper(): r for r in rows if clean(r.get("ticker"))}


def section16_map(md_text: str) -> dict[str, dict[str, str]]:
    rows = first_table_rows(sr.extract_section_by_number(md_text, 16), SECTION16_ALIASES)
    return {clean(r.get("ticker")).upper(): r for r in rows if clean(r.get("ticker"))}


def section15_rows(md_text: str) -> list[dict[str, str]]:
    return sr.parse_section15_holdings_rows_generic(md_text)


def parse_action_snapshot_replaceables(md_text: str) -> set[str]:
    section = "\n".join(sr.extract_section_by_number(md_text, 2))
    match = re.search(r"###\s*(?:⚠️\s*)?Hold but replaceable\s*(.*?)(?:\n###|\Z)", section, flags=re.I | re.S)
    if not match:
        return set()
    found = set()
    for token in re.split(r"[^A-Z0-9]+", match.group(1).upper()):
        if token and len(token) <= 8 and token not in {"NONE", "NO", "N", "A"}:
            found.add(token)
    return found


def previous_scorecard(output_dir: Path) -> dict[str, dict[str, str]]:
    path = output_dir / "etf_recommendation_scorecard.csv"
    if not path.exists():
        return {}
    rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    latest: dict[str, dict[str, str]] = {}
    for row in rows:
        ticker = row.get("ticker", "").upper()
        if ticker:
            latest[ticker] = row
    return latest


def classify_fresh_cash(total_score: float | None, pnl_pct: float | None, replaceable: bool, role: str) -> tuple[str, str, str]:
    role_l = role.lower()
    if total_score is None:
        return "Unresolved", "Unresolved", "No"
    if total_score >= 4.25 and not replaceable:
        return "Add/Hold", "Yes", "Yes"
    if total_score >= 4.0 and not replaceable:
        return "Hold", "Yes", "Yes"
    if total_score >= 3.5:
        if replaceable or (pnl_pct is not None and pnl_pct < -10):
            return "Smaller / under review", "Smaller", "No"
        return "Hold", "Yes", "Yes"
    if total_score >= 2.75:
        return "Reduce", "Smaller", "No"
    return "Close", "No", "No"


def thesis_and_implementation_scores(total_score: float | None, pnl_pct: float | None, ticker: str, replaceable: bool) -> tuple[str, str]:
    if total_score is None:
        return "", ""
    thesis = total_score
    implementation = total_score
    if ticker in {"PPA", "URNM", "PAVE", "SMH"}:
        thesis = min(5.0, thesis + 0.15)
    if ticker == "GLD":
        thesis = max(1.0, thesis - 0.05)
    if pnl_pct is not None and pnl_pct < -10:
        implementation -= 0.45
    elif pnl_pct is not None and pnl_pct < 0:
        implementation -= 0.2
    if replaceable:
        implementation -= 0.25
    return f"{max(1.0, min(5.0, thesis)):.2f}", f"{max(1.0, min(5.0, implementation)):.2f}"


def contribution_quality(pnl_pct: float | None, weight: float | None) -> str:
    if pnl_pct is None or weight is None:
        return "Unresolved"
    if pnl_pct > 10:
        return "Strong positive contributor"
    if pnl_pct > 3:
        return "Positive contributor"
    if pnl_pct >= -3:
        return "Flat / opportunity-cost review"
    if pnl_pct > -10:
        return "Negative contributor"
    return "Material drag"


def factor_flag(ticker: str, weight: float | None) -> str:
    if ticker in {"SPY", "SMH"}:
        return "U.S. tech / AI overlap"
    if ticker in {"SPY", "PAVE"}:
        return "U.S. growth / capex beta"
    if ticker == "GLD":
        return "Hedge / real-rate sensitivity"
    if ticker == "PPA":
        return "Defense resilience concentration"
    return ""


def hedge_status(ticker: str, pnl_pct: float | None, pricing_note: str) -> str:
    if ticker != "GLD":
        return "Not hedge sleeve"
    note = pricing_note.lower()
    if pnl_pct is not None and pnl_pct < -10 and ("carried" in note or "not recovered" in note or "unverified" in note):
        return "Hedge review: drawdown plus pricing uncertainty"
    if pnl_pct is not None and pnl_pct < -10:
        return "Hedge review: drawdown"
    return "Valid but monitor"


def required_action(total_score: float | None, pnl_pct: float | None, replaceable: bool, hedge: str, weeks: int) -> str:
    if total_score is None:
        return "Re-underwrite; score unresolved"
    if hedge.startswith("Hedge review"):
        return "Run hedge validity test and compare with alternatives"
    if pnl_pct is not None and pnl_pct < -10:
        return "Re-underwrite and run alternative duel"
    if replaceable and weeks >= 2:
        return "Force alternative duel; upgrade, reduce, replace, or close"
    if replaceable:
        return "Hold under review; name best alternative"
    if total_score >= 4.25:
        return "Consider add if cash policy allows"
    return "Hold"


def build_rows(output_dir: Path, report_path: Path, md_text: str) -> list[dict[str, str]]:
    report_date = sr.parse_report_date(md_text)
    s13 = section13_map(md_text)
    s16 = section16_map(md_text)
    replaceables = parse_action_snapshot_replaceables(md_text)
    previous = previous_scorecard(output_dir)
    rows = []
    for row in section15_rows(md_text):
        ticker = clean(row.get("ticker")).upper()
        if not ticker or ticker == "CASH":
            continue
        sec13 = s13.get(ticker, {})
        sec16 = s16.get(ticker, {})
        weight = safe_float(row.get("weight %"))
        pnl = safe_float(sec16.get("pnl_pct"))
        total_score = safe_float(sec13.get("total_score"))
        role = sec13.get("portfolio_role") or sec16.get("role") or THEME_BY_TICKER.get(ticker, "")
        replaceable = ticker in replaceables or clean(sec13.get("better_alternative_exists")).lower() in {"yes", "y", "true"}
        prev = previous.get(ticker, {})
        prev_weeks = safe_float(prev.get("weeks_replaceable")) or 0
        weeks = int(prev_weeks + 1) if replaceable else 0
        fresh_cash, would_today, would_weight = classify_fresh_cash(total_score, pnl, replaceable, role)
        thesis_score, implementation_score = thesis_and_implementation_scores(total_score, pnl, ticker, replaceable)
        pricing_note = " ".join([clean(sec13.get("short_reason")), clean(row.get("funding source / note"))])
        hedge = hedge_status(ticker, pnl, pricing_note)
        flags = []
        if replaceable:
            flags.append("replaceable")
        if pnl is not None and pnl < -10:
            flags.append("loss_gt_10pct")
        if ticker in {"SPY", "SMH"}:
            flags.append("factor_overlap")
        if hedge.startswith("Hedge review"):
            flags.append("hedge_review")
        required = required_action(total_score, pnl, replaceable, hedge, weeks)
        rows.append({
            "report_date": report_date,
            "ticker": ticker,
            "weight_pct": "" if weight is None else f"{weight:.2f}",
            "shares": clean(row.get("shares")),
            "current_price_local": clean(row.get("price (local)")),
            "currency": clean(row.get("currency")),
            "market_value_eur": clean(row.get("market value (eur)")),
            "pnl_pct": "" if pnl is None else f"{pnl:.2f}",
            "total_score": "" if total_score is None else f"{total_score:.2f}",
            "suggested_action": clean(sec13.get("suggested_action")),
            "conviction_tier": clean(sec13.get("conviction_tier")),
            "portfolio_role": role,
            "fresh_cash_test": fresh_cash,
            "would_initiate_today": would_today,
            "would_initiate_at_current_weight": would_weight,
            "thesis_score": thesis_score,
            "implementation_score": implementation_score,
            "replaceable_status": "Hold under review" if replaceable else "None",
            "weeks_replaceable": str(weeks),
            "best_alternative": ALT_BY_TICKER.get(ticker, ""),
            "alternative_score": "",
            "contribution_quality": contribution_quality(pnl, weight),
            "factor_overlap_flag": factor_flag(ticker, weight),
            "hedge_validity_status": hedge,
            "cash_policy_flag": "Review if cash >3% and actionable lanes exist",
            "required_next_action": required,
            "override_reason": "Required if final action remains Hold despite failed discipline checks" if flags and clean(sec13.get("suggested_action")).lower() == "hold" else "",
            "discipline_flags": ";".join(flags),
            "source_report": report_path.name,
        })
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    report_path = sr.latest_report_file(output_dir, mode=args.mode)
    md_text = sr.strip_citations(sr.normalize_markdown_text(report_path.read_text(encoding="utf-8")))
    rows = build_rows(output_dir, report_path, md_text)
    if not rows:
        raise RuntimeError(f"Could not derive recommendation scorecard rows from {report_path.name}")
    path = output_dir / "etf_recommendation_scorecard.csv"
    if args.check_only:
        flagged = sum(1 for r in rows if r.get("discipline_flags"))
        print(f"ETF_RECOMMENDATION_SCORECARD_DERIVATION_OK | report={report_path.name} | rows={len(rows)} | flagged={flagged} | scorecard={path.name}")
        return
    write_csv(path, rows)
    flagged = sum(1 for r in rows if r.get("discipline_flags"))
    print(f"ETF_RECOMMENDATION_SCORECARD_OK | report={report_path.name} | rows={len(rows)} | flagged={flagged} | scorecard={path.name}")


if __name__ == "__main__":
    main()
