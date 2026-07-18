from __future__ import annotations

import argparse
import csv
import json
import math
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf

from runtime.position_count_contract import (
    DEFAULT_MAX_ACTIVE_POSITIONS,
    assess_position_count_transition,
    count_active_positions,
)

EPS = 1e-9
MIN_TRADE_PCT_NAV = 2.0
BLOCKED_SURFACE_TERMS = ("shadow", "engine", "workflow", "override", "guarded", "release score")


def num(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def text(value: Any) -> str:
    return str(value or "").strip()


def lower(value: Any) -> str:
    return text(value).lower()


def clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected object in {path}")
    return payload


def read_scorecard(path: Path) -> dict[str, dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {
            text(row.get("ticker")).upper(): row
            for row in csv.DictReader(handle)
            if text(row.get("ticker"))
        }


def read_lane_scores(path: Path) -> dict[str, dict[str, Any]]:
    payload = read_json(path)
    rows: dict[str, dict[str, Any]] = {}
    for lane in payload.get("assessed_lanes", []) or []:
        for key in ("primary_etf", "alternative_etf"):
            ticker = text(lane.get(key)).upper()
            if ticker and ticker not in rows:
                rows[ticker] = dict(lane)
    return rows


def active_positions(state: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [dict(row) for row in state.get("positions", []) or [] if num(row.get("shares")) > EPS]
    if count_active_positions(rows) != len(rows):
        raise ValueError("Official state contains duplicate or invalid active positions")
    return rows


def continuity_rows(
    state: dict[str, Any],
    scorecard: dict[str, dict[str, Any]],
    lanes: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in active_positions(state):
        ticker = text(row.get("ticker")).upper()
        card = scorecard.get(ticker, {})
        lane = lanes.get(ticker, {})
        holding_score = num(row.get("total_score"), num(card.get("total_score"), 3.0))
        lane_score = num(lane.get("total_score"), holding_score)
        decision_quality_score = min(holding_score, lane_score)
        result[ticker] = {
            "ticker": ticker,
            "shares": int(round(num(row.get("shares")))),
            "current_weight_pct": num(row.get("current_weight_pct")),
            "portfolio_role": text(row.get("portfolio_role") or card.get("portfolio_role")),
            "conviction_tier": text(row.get("conviction_tier") or card.get("conviction_tier")),
            "holding_score": round(holding_score, 2),
            "lane_score": round(lane_score, 2),
            "total_score": round(decision_quality_score, 2),
            "lane_evidence_summary": text(lane.get("evidence_summary")),
            "lane_why_now": text(lane.get("why_now")),
            "macro_freshness_note": text(lane.get("macro_freshness_note")),
            "suggested_action": text(row.get("suggested_action") or card.get("suggested_action")),
            "fresh_cash_test": text(row.get("fresh_cash_test") or card.get("fresh_cash_test")),
            "replaceable_status": text(row.get("replaceable_status") or card.get("replaceable_status")),
            "weeks_replaceable": int(round(num(row.get("weeks_replaceable"), num(card.get("weeks_replaceable"))))),
            "contribution_quality": text(row.get("contribution_quality") or card.get("contribution_quality")),
            "pnl_pct": num(row.get("pnl_pct"), num(card.get("pnl_pct"))),
            "release_score": num(row.get("rotation_release_score")),
            "reason_codes": list(row.get("rotation_reason_codes") or []),
            "action_executed_this_run": text(row.get("action_executed_this_run")),
        }
    return result


def _field(raw: pd.DataFrame, tickers: list[str], field_name: str) -> pd.DataFrame:
    if raw is None or raw.empty:
        return pd.DataFrame()
    if isinstance(raw.columns, pd.MultiIndex):
        if field_name not in raw.columns.get_level_values(0):
            return pd.DataFrame()
        frame = raw[field_name].copy()
    else:
        if field_name not in raw.columns:
            return pd.DataFrame()
        frame = raw[[field_name]].copy()
        if len(tickers) == 1:
            frame.columns = tickers
    frame.columns = [text(col).upper() for col in frame.columns]
    return frame.sort_index().dropna(how="all").ffill()


def _ret(series: pd.Series, days: int) -> float | None:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if len(clean) <= days:
        return None
    start = float(clean.iloc[-days - 1])
    return round((float(clean.iloc[-1]) / start - 1.0) * 100.0, 2) if start else None


def _trend(series: pd.Series) -> float | None:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if len(clean) < 60:
        return None
    last = float(clean.iloc[-1])
    ma20 = float(clean.iloc[-20:].mean())
    ma50 = float(clean.iloc[-50:].mean())
    prior20 = float(clean.iloc[-40:-20].mean())
    score = 1.5 * (last > ma20) + 1.5 * (ma20 > ma50) + 1.0 * (last > ma50) + 1.0 * (ma20 > prior20)
    return round(min(float(score), 5.0), 2)


def fetch_market_snapshot(tickers: list[str], close_date: date) -> dict[str, Any]:
    requested = sorted(set(tickers) | {"SPY", "EURUSD=X"})
    raw = yf.download(
        tickers=requested,
        start=(close_date - timedelta(days=220)).isoformat(),
        end=(close_date + timedelta(days=4)).isoformat(),
        interval="1d",
        auto_adjust=False,
        group_by="column",
        threads=True,
        progress=False,
    )
    closes = _field(raw, requested, "Close")
    adjusted = _field(raw, requested, "Adj Close")
    if adjusted.empty:
        adjusted = closes.copy()
    volumes = _field(raw, requested, "Volume")
    for frame in (closes, adjusted, volumes):
        if not frame.empty:
            frame.drop(frame.index[pd.to_datetime(frame.index).date > close_date], inplace=True)

    spy = adjusted["SPY"] if "SPY" in adjusted.columns else pd.Series(dtype=float)
    spy_1m = _ret(spy, 21)
    spy_3m = _ret(spy, 63)
    rows: dict[str, Any] = {}
    for ticker in requested:
        series = pd.to_numeric(closes[ticker], errors="coerce").dropna() if ticker in closes.columns else pd.Series(dtype=float)
        if series.empty:
            rows[ticker] = {"status": "missing", "observed_price_date": "", "close": None}
            continue
        observed = pd.Timestamp(series.index[-1]).date()
        adj = adjusted[ticker] if ticker in adjusted.columns else series
        r1 = _ret(adj, 21)
        r3 = _ret(adj, 63)
        avg_volume = None
        if ticker in volumes.columns:
            clean_volume = pd.to_numeric(volumes[ticker], errors="coerce").dropna().iloc[-63:]
            avg_volume = float(clean_volume.mean()) if not clean_volume.empty else None
        last_close = float(series.iloc[-1])
        rows[ticker] = {
            "status": "complete" if observed == close_date else "stale",
            "observed_price_date": observed.isoformat(),
            "close": round(last_close, 6),
            "return_1m_pct": r1,
            "return_3m_pct": r3,
            "rs_vs_spy_1m_pct": round(r1 - spy_1m, 2) if r1 is not None and spy_1m is not None else None,
            "rs_vs_spy_3m_pct": round(r3 - spy_3m, 2) if r3 is not None and spy_3m is not None else None,
            "trend_quality": _trend(adj),
            "avg_dollar_volume_3m": round(avg_volume * last_close, 2) if avg_volume is not None else None,
        }
    missing = [ticker for ticker in requested if rows.get(ticker, {}).get("status") != "complete"]
    return {
        "source": "yfinance",
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "requested_close_date": close_date.isoformat(),
        "required_tickers": requested,
        "missing_or_stale_tickers": missing,
        "freshness_status": "complete" if not missing else "incomplete",
        "rows": rows,
    }


def _discipline(row: dict[str, Any]) -> tuple[float, list[str], set[str]]:
    points = 0.0
    reasons: list[str] = []
    families: set[str] = set()
    action = lower(row.get("suggested_action"))
    fresh = lower(row.get("fresh_cash_test"))
    replaceable = lower(row.get("replaceable_status"))
    contribution = lower(row.get("contribution_quality"))
    codes = {lower(code) for code in row.get("reason_codes", [])}
    if any(token in action for token in ("replace", "reduce", "close")):
        points += 5; reasons.append("action_calls_for_reduction_or_replacement"); families.add("discipline")
    elif "hold_with_override" in action or "hold with" in action:
        points += 3; reasons.append("hold_requires_exception"); families.add("discipline")
    if fresh.startswith("no"):
        points += 5; reasons.append("failed_fresh_cash_test"); families.add("fresh_cash")
    elif "smaller" in fresh or "under review" in fresh:
        points += 2; reasons.append("fresh_cash_only_smaller_or_review"); families.add("fresh_cash")
    if "under review" in replaceable:
        points += 4; reasons.append("replaceable_under_review"); families.add("replaceability")
    if int(row.get("weeks_replaceable") or 0) >= 2:
        points += 3; reasons.append("replaceability_review_age"); families.add("replaceability")
    if "material drag" in contribution:
        points += 4; reasons.append("material_performance_drag"); families.add("contribution")
    elif "opportunity-cost" in contribution or "opportunity cost" in contribution:
        points += 1; reasons.append("opportunity_cost_review"); families.add("contribution")
    if "role_failed" in codes:
        points += 5; reasons.append("portfolio_role_failed"); families.add("role")
    elif "role_impaired" in codes:
        points += 2; reasons.append("portfolio_role_impaired"); families.add("role")
    if num(row.get("pnl_pct")) < -20:
        points += 4; reasons.append("loss_exceeds_twenty_percent"); families.add("loss")
    elif num(row.get("pnl_pct")) < -10:
        points += 2; reasons.append("loss_exceeds_ten_percent"); families.add("loss")
    return min(points, 20.0), reasons, families


def rank_sources(continuity: dict[str, dict[str, Any]], snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for ticker, row in continuity.items():
        market = (snapshot.get("rows") or {}).get(ticker, {})
        total_score = num(row.get("total_score"), 3.0)
        release_score = clip(num(row.get("release_score")), 0, 100)
        release_points = release_score * 0.35
        quality_points = clip((4.5 - total_score) * (20.0 / 1.5), 0, 20)
        rs1 = num(market.get("rs_vs_spy_1m_pct"))
        rs3 = num(market.get("rs_vs_spy_3m_pct"))
        trend = num(market.get("trend_quality"), 2.5)
        market_points = min((min(8.0, abs(rs1) * 0.5) if rs1 < 0 else 0) + (min(8.0, abs(rs3) * 0.33) if rs3 < 0 else 0) + (4.0 if trend < 2.5 else 2.0 if trend < 4.0 else 0), 20.0)
        discipline_points, reasons, families = _discipline(row)
        if rs1 < 0 or rs3 < 0 or trend < 4.0:
            families.add("market")
        preservation = 0.0
        preservation_reasons: list[str] = []
        if lower(row.get("action_executed_this_run")) == "buy":
            preservation += 12; preservation_reasons.append("recently_added_position")
        if "tier 1" in lower(row.get("conviction_tier")):
            preservation += 6; preservation_reasons.append("highest_conviction_tier")
        if "growth engine" in lower(row.get("portfolio_role")):
            preservation += 6; preservation_reasons.append("core_growth_role")
        if total_score >= 4.5:
            preservation += 5; preservation_reasons.append("high_structural_score")
        if rs3 > 10:
            preservation += 5; preservation_reasons.append("strong_three_month_relative_strength")
        if "strong positive" in lower(row.get("contribution_quality")):
            preservation += 4; preservation_reasons.append("strong_positive_contribution")
        weight = num(row.get("current_weight_pct"))
        practicality = 5.0 if weight <= 1 else 3.0 if weight <= 2 else 1.0 if weight <= 5 else 0.0
        non_size = clip(release_points + quality_points + market_points + discipline_points - preservation, 0, 100)
        if release_score >= 65:
            families.add("release")
        if total_score < 3.75:
            families.add("quality")
        ranked.append({
            **row,
            "market": market,
            "score_components": {
                "release": round(release_points, 2),
                "quality_weakness": round(quality_points, 2),
                "market_weakness": round(market_points, 2),
                "discipline": round(discipline_points, 2),
                "preservation_credit": round(preservation, 2),
                "implementation_practicality": round(practicality, 2),
            },
            "non_size_priority_score": round(non_size, 2),
            "close_priority_score": round(clip(non_size + practicality, 0, 100), 2),
            "independent_issue_families": sorted(families),
            "issue_family_count": len(families),
            "priority_reasons": reasons,
            "preservation_reasons": preservation_reasons,
        })
    return sorted(ranked, key=lambda row: (-row["close_priority_score"], row["ticker"]))


def _transition(current: list[dict[str, Any]], projected: list[dict[str, Any]]) -> dict[str, Any]:
    return assess_position_count_transition(current, projected, max_active_positions=DEFAULT_MAX_ACTIVE_POSITIONS, trade_intents_present=True).to_dict()


def decide(state: dict[str, Any], ranked: list[dict[str, Any]], snapshot: dict[str, Any]) -> dict[str, Any]:
    current = active_positions(state)
    cash = num(state.get("cash_eur"))
    nav = num(state.get("nav_eur"))
    no_change = assess_position_count_transition(current, current, max_active_positions=DEFAULT_MAX_ACTIVE_POSITIONS, trade_intents_present=False).to_dict()
    if snapshot.get("freshness_status") != "complete" or len(ranked) != len(current):
        return {"conclusion": "no_trade_insufficient_evidence", "selected_source": "", "selected_destination": "", "rationale_codes": ["fresh_market_evidence_incomplete"], "projected_positions": deepcopy(current), "projected_cash_eur": round(cash, 2), "proceeds_eur": 0.0, "destination_shares_added": 0, "transition": no_change}
    top = ranked[0]
    second = ranked[1]
    margin = top["close_priority_score"] - second["close_priority_score"]
    independent = top["issue_family_count"] >= 2 and (num(top.get("release_score")) >= 65 or any(token in lower(top.get("suggested_action")) for token in ("replace", "reduce", "close"))) and top["non_size_priority_score"] >= second["non_size_priority_score"] and margin >= 2.0
    if not independent:
        return {"conclusion": "no_trade_insufficient_evidence", "selected_source": "", "selected_destination": "", "rationale_codes": ["no_candidate_has_sufficient_independent_support", "small_position_size_not_used_as_sole_reason"], "projected_positions": deepcopy(current), "projected_cash_eur": round(cash, 2), "proceeds_eur": 0.0, "destination_shares_added": 0, "transition": no_change}
    source = top["ticker"]
    projected = deepcopy(current)
    source_row = next(row for row in projected if text(row.get("ticker")).upper() == source)
    eurusd = num(snapshot["rows"]["EURUSD=X"]["close"])
    proceeds = num(source_row.get("shares")) * num(snapshot["rows"][source]["close"]) / eurusd
    source_row["shares"] = 0
    transition = _transition(current, projected)
    destination = ""
    destination_added = 0
    conclusion = "close_to_cash_supported"
    projected_cash = cash + proceeds
    if nav > 0 and proceeds / nav * 100 >= MIN_TRADE_PCT_NAV:
        candidates = [row for row in ranked if row["ticker"] != source and num(row.get("total_score")) >= 4.0 and num(row.get("current_weight_pct")) < 20 and num((row.get("market") or {}).get("rs_vs_spy_3m_pct")) > 0 and num((row.get("market") or {}).get("trend_quality")) >= 3.5 and lower(row.get("action_executed_this_run")) != "buy"]
        candidates.sort(key=lambda row: (-num(row.get("total_score")), -num((row.get("market") or {}).get("rs_vs_spy_3m_pct")), row["ticker"]))
        if candidates:
            destination = candidates[0]["ticker"]
            dest_row = next(row for row in projected if text(row.get("ticker")).upper() == destination)
            dest_price_eur = num(snapshot["rows"][destination]["close"]) / eurusd
            destination_added = int(math.floor(proceeds / dest_price_eur))
            if destination_added > 0:
                dest_row["shares"] = int(round(num(dest_row.get("shares")))) + destination_added
                projected_cash -= destination_added * dest_price_eur
                transition = _transition(current, projected)
                conclusion = "close_and_reallocate_existing_supported"
    return {"conclusion": conclusion, "selected_source": source, "selected_destination": destination, "rationale_codes": ["active_count_restored", "source_selected_on_multiple_independent_factors", "small_position_size_not_used_as_sole_reason"], "projected_positions": projected, "projected_cash_eur": round(projected_cash, 2), "proceeds_eur": round(proceeds, 2), "destination_shares_added": destination_added, "transition": transition}


def render(evidence: dict[str, Any]) -> tuple[str, str]:
    decision = evidence["decision"]
    source = decision.get("selected_source") or "None"
    destination = decision.get("selected_destination") or "cash"
    rows = "\n".join(f"| {index} | {row['ticker']} | {row['close_priority_score']:.2f} | {row['total_score']:.2f} | {row['market'].get('rs_vs_spy_3m_pct')} | {row['current_weight_pct']:.2f}% |" for index, row in enumerate(evidence["ranking"], start=1))
    en = f"""# Portfolio count-restoration review\n\n**Evidence date:** {evidence['market_snapshot']['requested_close_date']}  \n**Current active positions:** {evidence['current_state']['active_count']}  \n**Maximum active positions:** {evidence['current_state']['maximum']}  \n**Conclusion:** {decision['conclusion']}  \n**Selected source:** {source}  \n**Destination:** {destination}  \n\nThe comparison considered portfolio role, recommendation quality, relative strength, contribution, liquidity, concentration and implementation practicality. Position size was not sufficient on its own to select a source.\n\n| Rank | Ticker | Close priority | Decision quality | 3-month relative strength vs SPY | Current weight |\n|---:|---|---:|---:|---:|---:|\n{rows}\n\nProjected active positions: {decision['transition']['projected_count']}. Projected cash: EUR {decision['projected_cash_eur']:.2f}. Official portfolio state was not changed. Any implementation requires separate authorization.\n"""
    nl = f"""# Beoordeling voor herstel van het positieaantal\n\n**Bewijsdatum:** {evidence['market_snapshot']['requested_close_date']}  \n**Huidig aantal actieve posities:** {evidence['current_state']['active_count']}  \n**Maximaal aantal actieve posities:** {evidence['current_state']['maximum']}  \n**Conclusie:** {decision['conclusion']}  \n**Geselecteerde bron:** {source}  \n**Bestemming:** {'cash' if destination == 'cash' else destination}  \n\nDe vergelijking omvatte portefeuillerol, aanbevelingskwaliteit, relatieve sterkte, bijdrage, liquiditeit, concentratie en uitvoerbaarheid. De omvang van een positie was op zichzelf niet voldoende om een bron te selecteren.\n\n| Rang | Ticker | Prioriteit voor sluiting | Besliskwaliteit | Relatieve sterkte over drie maanden versus SPY | Huidig gewicht |\n|---:|---|---:|---:|---:|---:|\n{rows}\n\nVerwacht aantal actieve posities: {decision['transition']['projected_count']}. Verwachte cash: EUR {decision['projected_cash_eur']:.2f}. De officiële portefeuille is niet gewijzigd. Voor uitvoering is afzonderlijke toestemming vereist.\n"""
    for surface in (en, nl):
        leaked = [term for term in BLOCKED_SURFACE_TERMS if term in surface.lower()]
        if leaked:
            raise ValueError(f"Blocked client terms: {leaked}")
    return en, nl


def build_evidence(state: dict[str, Any], scorecard: dict[str, dict[str, Any]], lanes: dict[str, dict[str, Any]], snapshot: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
    continuity = continuity_rows(state, scorecard, lanes)
    ranked = rank_sources(continuity, snapshot)
    decision = decide(state, ranked, snapshot)
    current = active_positions(state)
    evidence = {
        "schema_version": "portfolio_close_first_execution_review_v1",
        "artifact_type": "weekly_etf_portfolio_close_first_execution_review",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "validated_no_mutation_review",
        "current_state": {"active_count": len(current), "maximum": DEFAULT_MAX_ACTIVE_POSITIONS, "cash_eur": round(num(state.get("cash_eur")), 2), "nav_eur": round(num(state.get("nav_eur")), 2), "tickers": sorted(text(row.get("ticker")).upper() for row in current)},
        "market_snapshot": snapshot,
        "ranking": ranked,
        "decision": decision,
        "selection_proof": {"smallest_position_not_automatic": True, "selected_source": decision.get("selected_source"), "selected_source_issue_families": ranked[0]["independent_issue_families"] if decision.get("selected_source") else [], "selected_source_remains_top_without_size_points": bool(decision.get("selected_source") and ranked[0]["non_size_priority_score"] >= ranked[1]["non_size_priority_score"])},
        "authority_boundary": {"portfolio_execution": False, "portfolio_state_mutation": False, "trade_ledger_mutation": False, "valuation_history_mutation": False, "official_pricing_pointer_mutation": False, "historical_output_mutation": False, "report_delivery": False, "email_sent": False},
    }
    en, nl = render(evidence)
    evidence["surfaces"] = {"english_filename": "portfolio_close_first_execution_review_en.md", "dutch_filename": "portfolio_close_first_execution_review_nl.md"}
    return evidence, en, nl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--portfolio-state", default="output/etf_portfolio_state.json")
    parser.add_argument("--scorecard", default="output/etf_recommendation_scorecard.csv")
    parser.add_argument("--lane-assessment", default="output/lane_reviews/etf_lane_assessment_260716.json")
    parser.add_argument("--requested-close-date", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    state = read_json(Path(args.portfolio_state))
    scorecard = read_scorecard(Path(args.scorecard))
    lanes = read_lane_scores(Path(args.lane_assessment))
    close_date = date.fromisoformat(args.requested_close_date)
    snapshot = fetch_market_snapshot([row["ticker"] for row in active_positions(state)], close_date)
    evidence, en, nl = build_evidence(state, scorecard, lanes, snapshot)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "portfolio_close_first_execution_review_evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    (output_dir / "portfolio_close_first_execution_review_en.md").write_text(en, encoding="utf-8")
    (output_dir / "portfolio_close_first_execution_review_nl.md").write_text(nl, encoding="utf-8")
    print("ETF_CLOSE_FIRST_REVIEW_OK | " f"close_date={close_date.isoformat()} | freshness={snapshot['freshness_status']} | conclusion={evidence['decision']['conclusion']} | source={evidence['decision']['selected_source'] or 'none'} | projected_count={evidence['decision']['transition']['projected_count']} | portfolio_mutation=false | email_sent=false")


if __name__ == "__main__":
    main()
