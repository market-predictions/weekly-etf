from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PRICED_STATUSES = {"fresh_close", "fresh_fallback_source", "fresh_exact_close", "fresh_exact_unverified", "prior_valid_close"}
VALUATION_GRADE = "valuation_grade"
FUNDABLE_STATUS = "funding_candidate_valuation_grade"
NON_FUNDABLE_STATUSES = {
    "research_only_requires_valuation_grade_price",
    "pricing_missing_for_funding_candidate",
    "research_radar_only",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def _latest_file(directory: Path, pattern: str) -> Path:
    files = sorted(directory.glob(pattern))
    if not files:
        raise RuntimeError(f"No files found for {pattern} in {directory}")
    return files[-1]


def _price_map(audit: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in audit.get("prices", []) or audit.get("price_results", []) or []:
        symbol = _ticker(row.get("symbol"))
        if symbol:
            out[symbol] = row
    return out


def _is_valuation_grade(row: dict[str, Any] | None) -> bool:
    if not row:
        return False
    has_price = row.get("selected_close") is not None or row.get("price") is not None
    return has_price and str(row.get("status") or "") in PRICED_STATUSES and str(row.get("pricing_tier") or "") == VALUATION_GRADE


def validate(lane_path: Path, pricing_audit_path: Path) -> None:
    lane_artifact = _load_json(lane_path)
    audit = _load_json(pricing_audit_path)
    prices = _price_map(audit)
    failures: list[str] = []
    warnings: list[str] = []

    lanes = lane_artifact.get("assessed_lanes", []) or []
    for lane in lanes:
        primary = _ticker(lane.get("primary_etf"))
        if not primary:
            continue
        fundability = str(lane.get("fundability_status") or "")
        is_fundable = bool(lane.get("is_fundable_candidate"))
        promoted = bool(lane.get("promoted_to_live_radar"))
        challenger = bool(lane.get("challenger"))
        price_row = prices.get(primary)
        valuation_grade = _is_valuation_grade(price_row)

        if is_fundable and fundability != FUNDABLE_STATUS:
            failures.append(f"{primary}: is_fundable_candidate true but fundability_status={fundability!r}")
        if is_fundable and not valuation_grade:
            failures.append(f"{primary}: fundable without valuation-grade audit row")
        if fundability == FUNDABLE_STATUS and not valuation_grade:
            failures.append(f"{primary}: funding_candidate_valuation_grade but audit row is not valuation-grade")
        if promoted and challenger and not valuation_grade:
            note = str(lane.get("promotion_fundability_note") or "")
            if "valuation-grade" not in note:
                failures.append(f"{primary}: promoted challenger lacks valuation-grade pricing and lacks fundability note")
        if fundability in NON_FUNDABLE_STATUSES and is_fundable:
            failures.append(f"{primary}: non-fundable fundability status but is_fundable_candidate true")
        if challenger and not valuation_grade:
            warnings.append(f"{primary}: challenger remains research/radar only; valuation-grade pricing not available")

    if failures:
        raise RuntimeError("ETF challenger fundability contract failed: " + " | ".join(failures))
    for warning in warnings[:20]:
        print(f"::warning title=ETF Challenger Fundability::{warning}")
    print(
        "ETF_CHALLENGER_FUNDABILITY_CONTRACT_OK | "
        f"lanes={len(lanes)} | warnings={len(warnings)} | lane_artifact={lane_path} | pricing_audit={pricing_audit_path}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane-artifact", default=None)
    parser.add_argument("--pricing-audit", default=None)
    parser.add_argument("--lane-dir", default="output/lane_reviews")
    parser.add_argument("--pricing-dir", default="output/pricing")
    args = parser.parse_args()

    lane_path = Path(args.lane_artifact) if args.lane_artifact else _latest_file(Path(args.lane_dir), "etf_lane_assessment_*.json")
    pricing_path = Path(args.pricing_audit) if args.pricing_audit else _latest_file(Path(args.pricing_dir), "price_audit_*.json")
    validate(lane_path, pricing_path)


if __name__ == "__main__":
    main()
