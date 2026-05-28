from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "created_at_utc",
    "run_id",
    "report_token",
    "requested_close_date",
    "source_files",
    "policy",
    "incumbent_reviews",
    "candidate_reviews",
    "rotation_decisions",
    "target_weights",
    "trade_intents",
    "validation_flags",
}

REQUIRED_DECISION_FIELDS = {
    "ticker",
    "action_code",
    "current_weight_pct",
    "target_weight_pct",
    "delta_weight_pct",
    "release_score",
    "role_validity",
    "reason_codes",
    "override_status",
}

REQUIRED_TRADE_FIELDS = {
    "source_ticker",
    "destination_ticker",
    "delta_weight_pct",
    "destination_delta_weight_pct",
    "estimated_notional_eur",
    "action_code",
    "reason_codes",
}

VALID_ACTIONS = {"hold", "hold_with_override", "reduce", "replace_partial", "replace_full", "close", "add_from_cash"}
VALID_OVERRIDE_STATUS = {"none", "engine", "operator"}


def _latest_plan(runtime_dir: Path) -> Path:
    pointer = runtime_dir / "latest_etf_rotation_plan_path.txt"
    if pointer.exists():
        raw = pointer.read_text(encoding="utf-8").strip()
        path = Path(raw)
        if path.exists():
            return path
        candidate = runtime_dir / path.name
        if candidate.exists():
            return candidate
    plans = sorted(runtime_dir.glob("etf_rotation_plan_*.json"))
    if not plans:
        raise RuntimeError(f"No etf_rotation_plan_*.json files found in {runtime_dir}")
    return plans[-1]


def _num(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def validate(plan: dict[str, Any], path: Path) -> None:
    failures: list[str] = []
    missing = REQUIRED_TOP_LEVEL - set(plan.keys())
    if missing:
        failures.append("missing top-level fields: " + ", ".join(sorted(missing)))

    decisions = plan.get("rotation_decisions") or []
    if not isinstance(decisions, list) or not decisions:
        failures.append("rotation_decisions must be a non-empty list")
    for idx, decision in enumerate(decisions):
        missing_decision = REQUIRED_DECISION_FIELDS - set(decision.keys())
        if missing_decision:
            failures.append(f"decision[{idx}] missing fields: " + ", ".join(sorted(missing_decision)))
        action = str(decision.get("action_code") or "")
        if action not in VALID_ACTIONS:
            failures.append(f"decision[{idx}] invalid action_code={action!r}")
        override = str(decision.get("override_status") or "")
        if override not in VALID_OVERRIDE_STATUS:
            failures.append(f"decision[{idx}] invalid override_status={override!r}")
        if action == "hold_with_override" and override == "none":
            failures.append(f"decision[{idx}] hold_with_override has override_status=none")
        if override != "none" and not str(decision.get("override_reason_code") or "").strip():
            failures.append(f"decision[{idx}] override missing override_reason_code")

    target_weights = plan.get("target_weights") or []
    tickers = {str(row.get("ticker") or "").upper() for row in target_weights}
    if not target_weights:
        failures.append("target_weights is empty")
    for row in target_weights:
        if not str(row.get("ticker") or "").strip():
            failures.append("target weight row missing ticker")
        weight = _num(row.get("target_weight_pct"))
        if weight < 0:
            failures.append(f"negative target weight for {row.get('ticker')}")

    trades = plan.get("trade_intents") or []
    for idx, trade in enumerate(trades):
        missing_trade = REQUIRED_TRADE_FIELDS - set(trade.keys())
        if missing_trade:
            failures.append(f"trade_intents[{idx}] missing fields: " + ", ".join(sorted(missing_trade)))
        source = str(trade.get("source_ticker") or "").upper()
        dest = str(trade.get("destination_ticker") or "").upper()
        if source and source not in tickers:
            failures.append(f"trade_intents[{idx}] source not in target_weights: {source}")
        if dest and dest not in tickers:
            failures.append(f"trade_intents[{idx}] destination not in target_weights: {dest}")
        if _num(trade.get("estimated_notional_eur")) <= 0:
            failures.append(f"trade_intents[{idx}] non-positive estimated_notional_eur")

    if failures:
        raise RuntimeError("ETF rotation output contract failed: " + " | ".join(failures))

    print(
        "ETF_ROTATION_OUTPUT_CONTRACT_OK | "
        f"plan={path.name} | decisions={len(decisions)} | target_weights={len(target_weights)} | trade_intents={len(trades)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-dir", default="output/runtime")
    parser.add_argument("--plan", default="")
    args = parser.parse_args()
    path = Path(args.plan) if args.plan else _latest_plan(Path(args.runtime_dir))
    validate(json.loads(path.read_text(encoding="utf-8")), path)


if __name__ == "__main__":
    main()
