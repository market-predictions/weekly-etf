#!/usr/bin/env python3
"""Evaluate Stage-2 confirmation for internal thesis candidates.

This evaluator is shadow-only. It does not create portfolio actions, does not
change lane scoring, and does not make report-facing recommendations.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


AUTHORITY = {
    "shadow_only": True,
    "client_facing_authority": False,
    "decision_impact": "none_stage2_confirmation_shadow_only",
    "portfolio_action_authority": False,
    "fundability_authority": False,
    "report_surface_allowed": False,
}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected JSON object in {path}")
    return payload


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected YAML object in {path}")
    return payload


def _price_by_symbol(price_audit: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in price_audit.get("price_results") or []:
        if isinstance(row, dict) and isinstance(row.get("symbol"), str):
            out[row["symbol"]] = row
    return out


def _metrics_by_symbol(relative_strength: dict[str, Any]) -> dict[str, dict[str, Any]]:
    metrics = relative_strength.get("metrics") or {}
    if not isinstance(metrics, dict):
        return {}
    return {str(k): v for k, v in metrics.items() if isinstance(v, dict)}


def _candidate_crowding(candidate: dict[str, Any], universe_by_tag: dict[str, dict[str, Any]]) -> int | None:
    lane = universe_by_tag.get(str(candidate.get("taxonomy_tag")))
    if not lane:
        return None
    value = lane.get("valuation_crowding")
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _universe_by_tag(universe: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lanes = universe.get("lanes") or []
    return {lane["taxonomy_tag"]: lane for lane in lanes if isinstance(lane, dict) and isinstance(lane.get("taxonomy_tag"), str)}


def _rs_confirmed(metrics: dict[str, Any], rules: dict[str, Any]) -> tuple[bool, list[str]]:
    rs_rules = rules.get("relative_strength") or {}
    reasons: list[str] = []
    if not metrics:
        return False, ["missing_relative_strength_metrics"]
    tradability_required = rs_rules.get("require_tradability_status")
    if tradability_required and metrics.get("tradability_status") != tradability_required:
        reasons.append("tradability_status_not_pass")
    if float(metrics.get("rs_vs_spy_1m_pct", -9999)) < float(rs_rules.get("min_rs_vs_spy_1m_pct", 0.0)):
        reasons.append("rs_1m_below_threshold")
    if float(metrics.get("rs_vs_spy_3m_pct", -9999)) < float(rs_rules.get("min_rs_vs_spy_3m_pct", 0.0)):
        reasons.append("rs_3m_below_threshold")
    if float(metrics.get("trend_quality", -9999)) < float(rs_rules.get("min_trend_quality", 3.0)):
        reasons.append("trend_quality_below_threshold")
    return not reasons, reasons


def _valuation_pricing_ok(price_row: dict[str, Any] | None, rules: dict[str, Any]) -> tuple[bool, list[str]]:
    pricing_rules = rules.get("valuation_pricing") or {}
    if not price_row:
        return False, ["missing_pricing_row"]
    reasons: list[str] = []
    if price_row.get("pricing_tier") not in set(pricing_rules.get("accepted_pricing_tiers") or []):
        reasons.append("pricing_tier_not_accepted")
    if price_row.get("status") not in set(pricing_rules.get("accepted_statuses") or []):
        reasons.append("pricing_status_not_accepted")
    if pricing_rules.get("require_selected_close") and price_row.get("selected_close") is None:
        reasons.append("missing_selected_close")
    if pricing_rules.get("require_final_eod_bar") and price_row.get("is_final_eod_bar") is not True:
        reasons.append("not_final_eod_bar")
    return not reasons, reasons


def evaluate(
    thesis_candidates: dict[str, Any],
    relative_strength: dict[str, Any],
    price_audit: dict[str, Any],
    universe: dict[str, Any],
    rules: dict[str, Any],
    *,
    reference_date: str,
    run_id: str,
) -> dict[str, Any]:
    if thesis_candidates.get("authority", {}).get("shadow_only") is not True:
        raise SystemExit("Stage-1 thesis candidates input must be shadow-only")

    metrics_by_symbol = _metrics_by_symbol(relative_strength)
    prices = _price_by_symbol(price_audit)
    universe_by_tag = _universe_by_tag(universe)
    labels = rules.get("status_labels") or {}

    rows: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for candidate in thesis_candidates.get("candidates") or []:
        if not isinstance(candidate, dict):
            continue
        ticker = str(candidate.get("primary_etf") or "")
        metrics = metrics_by_symbol.get(ticker, {})
        price_row = prices.get(ticker)
        rs_ok, rs_reasons = _rs_confirmed(metrics, rules)
        pricing_ok, pricing_reasons = _valuation_pricing_ok(price_row, rules)
        rationale_ok = bool(candidate.get("driver_to_beneficiary_rationale"))
        driver_ok = bool(candidate.get("driver_id"))
        discipline_ok = candidate.get("portfolio_discipline_clearance") is True
        crowding = _candidate_crowding(candidate, universe_by_tag)
        caution = None
        vc_rules = rules.get("valuation_crowding") or {}
        if crowding is not None and crowding >= int(vc_rules.get("caution_threshold", 4)):
            caution = "valuation_or_crowding_caution"

        if not rs_ok:
            stage2_status = labels.get("no_market_confirmation", "stage_1_candidate")
        elif not pricing_ok:
            stage2_status = labels.get("no_valuation_grade_pricing", "stage_2_confirmed_not_fundable")
        elif not discipline_ok:
            stage2_status = labels.get("portfolio_discipline_missing", "stage_2_confirmed_not_fundable")
        elif not rationale_ok or not driver_ok:
            stage2_status = "stage_2_confirmed_not_fundable"
        else:
            stage2_status = labels.get("all_gates_passed", "stage_2_fundable_ready_shadow")

        counts[stage2_status] = counts.get(stage2_status, 0) + 1
        rows.append(
            {
                "driver_id": candidate.get("driver_id"),
                "taxonomy_tag": candidate.get("taxonomy_tag"),
                "lane_name": candidate.get("lane_name"),
                "primary_etf": ticker,
                "stage2_status": stage2_status,
                "active_driver_confirmed": driver_ok,
                "rationale_present": rationale_ok,
                "relative_strength_confirmed": rs_ok,
                "relative_strength_blockers": rs_reasons,
                "valuation_grade_pricing_confirmed": pricing_ok,
                "valuation_pricing_blockers": pricing_reasons,
                "portfolio_discipline_clearance": discipline_ok,
                "valuation_crowding": crowding,
                "caution_flag": caution,
                "portfolio_action": "none",
                "client_facing_authority": False,
                "fundability_authority": False,
            }
        )

    return {
        "schema_version": "1.0",
        "artifact_type": "stage2_thesis_confirmation_shadow",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "reference_date": reference_date,
        "run_id": run_id,
        "authority": AUTHORITY,
        "counts_by_status": counts,
        "evaluations": sorted(rows, key=lambda row: (str(row["driver_id"]), str(row["taxonomy_tag"]))),
        "guardrails": [
            "Stage-2 fundable-ready shadow is not a portfolio action.",
            "No client-facing report wording may use this artifact until a later promotion decision.",
            "Valuation/crowding is a caution flag, not an automatic hard block unless rules explicitly change.",
        ],
    }


def validate_output(payload: dict[str, Any]) -> None:
    authority = payload.get("authority") or {}
    if authority != AUTHORITY:
        raise SystemExit("Unexpected Stage-2 authority block")
    for row in payload.get("evaluations") or []:
        if row.get("portfolio_action") != "none":
            raise SystemExit("Stage-2 row has portfolio action")
        if row.get("client_facing_authority") is not False:
            raise SystemExit("Stage-2 row has client-facing authority")
        if row.get("fundability_authority") is not False:
            raise SystemExit("Stage-2 row has fundability authority")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--thesis-candidates", type=Path, required=True)
    parser.add_argument("--relative-strength", type=Path, required=True)
    parser.add_argument("--price-audit", type=Path, required=True)
    parser.add_argument("--universe", type=Path, default=Path("config/etf_discovery_universe.yml"))
    parser.add_argument("--rules", type=Path, default=Path("config/stage2_confirmation_rules.yml"))
    parser.add_argument("--output-dir", type=Path, default=Path("output/macro"))
    parser.add_argument("--reference-date", default="unknown")
    parser.add_argument("--run-id", default="stage2_shadow")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--expect-status", action="append", default=[])
    args = parser.parse_args()

    payload = evaluate(
        _load_json(args.thesis_candidates),
        _load_json(args.relative_strength),
        _load_json(args.price_audit),
        _load_yaml(args.universe),
        _load_yaml(args.rules),
        reference_date=args.reference_date,
        run_id=args.run_id,
    )
    validate_output(payload)

    missing = [status for status in args.expect_status if payload["counts_by_status"].get(status, 0) == 0]
    if missing:
        raise SystemExit(f"Expected Stage-2 statuses missing: {missing}")

    if not args.validate_only:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        out = args.output_dir / f"stage2_confirmation_{args.reference_date}_{args.run_id}.json"
        latest = args.output_dir / "latest_stage2_confirmation.json"
        text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        out.write_text(text, encoding="utf-8")
        latest.write_text(text, encoding="utf-8")
        print(f"ETF_STAGE2_CONFIRMATION_WRITTEN | path={out} | rows={len(payload['evaluations'])}")

    print(
        "ETF_STAGE2_CONFIRMATION_SHADOW_OK | "
        f"rows={len(payload['evaluations'])} | statuses={payload['counts_by_status']}"
    )


if __name__ == "__main__":
    main()
