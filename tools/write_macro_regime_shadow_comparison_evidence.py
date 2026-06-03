#!/usr/bin/env python3
"""Write legacy-vs-deterministic macro-regime shadow comparison evidence.

This tool is intentionally non-production authority. It compares the legacy macro
policy pack regime/confidence against the deterministic shadow candidate under
the macro policy-pack authority contract. It must not mutate lane scoring,
fundability, reports, portfolio state, or delivery behavior.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime import build_macro_policy_pack as legacy
from runtime.build_macro_policy_pack_shadow import add_shadow_regime
from tools.validate_macro_policy_pack import _validate_pack
from tools.validate_macro_regime_shadow import validate_shadow_payload

EXPECTED_AUTHORITY = {
    "shadow_only": True,
    "client_facing_authority": False,
    "decision_impact": "none_shadow_comparison_only",
}


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Required JSON input missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected top-level JSON object: {path}")
    return payload


def _safe_token(value: str) -> str:
    token = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value.strip())
    return token or "unknown"


def _resolve_pricing_audit(path_value: str | None) -> Path:
    if path_value:
        path = Path(path_value)
        if not path.exists():
            raise SystemExit(f"Pricing audit not found: {path}")
        return path
    return legacy.latest_file(legacy.PRICING_DIR, "price_audit_*.json")


def _build_shadow_pack(args: argparse.Namespace) -> dict[str, Any]:
    pricing_audit = _resolve_pricing_audit(args.pricing_audit)
    relative_strength = Path(args.relative_strength)
    macro_context = Path(args.macro_context)
    macro_data_audit = Path(args.macro_data_audit) if args.macro_data_audit else None

    if not relative_strength.exists():
        raise SystemExit(f"Relative-strength artifact not found: {relative_strength}")
    if not macro_context.exists():
        raise SystemExit(f"Macro context file not found: {macro_context}")
    if macro_data_audit is not None and not macro_data_audit.exists():
        raise SystemExit(f"Macro data audit not found: {macro_data_audit}")

    base_pack = legacy.build_pack(pricing_audit, relative_strength, macro_context, macro_data_audit)
    shadow_pack = add_shadow_regime(base_pack, relative_strength, macro_data_audit)
    _validate_pack(shadow_pack)
    return shadow_pack


def _require_shadow_authority(shadow: dict[str, Any]) -> dict[str, Any]:
    result = validate_shadow_payload(shadow)
    for key, expected in EXPECTED_AUTHORITY.items():
        actual = shadow.get(key)
        if actual != expected:
            raise SystemExit(f"deterministic_regime_shadow.{key} expected {expected!r}, got {actual!r}")
    if shadow.get("macro_axes") and not isinstance(shadow.get("macro_axes"), dict):
        raise SystemExit("deterministic_regime_shadow.macro_axes must be an object when present")
    print(
        "ETF_MACRO_REGIME_SHADOW_COMPARE_PAYLOAD_OK | "
        f"candidate={result['candidate_regime']} | confidence={result['candidate_confidence']} | "
        f"legacy={result['legacy_regime']} | label_differs={result['regime_label_differs']} | "
        f"confidence_differs={result['confidence_differs']} | confidence_delta={result['confidence_delta']} | "
        f"differs={result['differs_from_legacy']}"
    )
    return result


def _build_evidence(args: argparse.Namespace, pack: dict[str, Any]) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    regime = pack.get("regime") if isinstance(pack.get("regime"), dict) else {}
    shadow = pack.get("deterministic_regime_shadow") if isinstance(pack.get("deterministic_regime_shadow"), dict) else {}
    validation_result = _require_shadow_authority(shadow)
    authority = pack.get("authority") if isinstance(pack.get("authority"), dict) else {}
    field_authority = pack.get("field_authority") if isinstance(pack.get("field_authority"), dict) else {}
    promotion_gates = pack.get("promotion_gates") if isinstance(pack.get("promotion_gates"), dict) else {}

    return {
        "schema_version": "1.1",
        "artifact_type": "macro_regime_legacy_vs_shadow_comparison_evidence",
        "status": "passed",
        "generated_at_utc": generated_at,
        "repository": "market-predictions/weekly-etf",
        "source_inputs": {
            "pricing_audit": str(_resolve_pricing_audit(args.pricing_audit)),
            "relative_strength": args.relative_strength,
            "macro_context": args.macro_context,
            "macro_data_audit": args.macro_data_audit,
            "thresholds": "config/regime_thresholds.yml",
        },
        "workflow": {
            "name": args.workflow_name,
            "run_id": args.workflow_run_id,
            "run_number": args.workflow_run_number,
            "run_attempt": args.workflow_attempt,
            "commit_sha": args.commit_sha,
            "source_ref": args.source_ref,
        },
        "authority": {
            "pack_authority_class": authority.get("authority_class"),
            "pack_decision_authority": authority.get("decision_authority"),
            "promotion_status": promotion_gates.get("status"),
            "shadow_only": True,
            "client_facing_authority": False,
            "decision_impact": "none_shadow_comparison_only",
            "production_report_path_changed": False,
            "lane_scoring_authority": False,
            "fundability_authority": False,
            "portfolio_action_authority": False,
            "field_authority_deterministic_regime_shadow": field_authority.get("deterministic_regime_shadow"),
        },
        "comparison": {
            "legacy_regime": regime.get("current"),
            "legacy_confidence": regime.get("confidence"),
            "legacy_confidence_source": regime.get("confidence_source"),
            "shadow_candidate_regime": shadow.get("candidate_regime"),
            "shadow_candidate_confidence": shadow.get("candidate_confidence"),
            "shadow_method": shadow.get("method"),
            "differs_from_legacy": validation_result.get("differs_from_legacy"),
            "regime_label_differs": validation_result.get("regime_label_differs"),
            "confidence_differs": validation_result.get("confidence_differs"),
            "confidence_delta": validation_result.get("confidence_delta"),
            "confidence_diff_threshold": shadow.get("confidence_diff_threshold"),
            "axes": shadow.get("axes") or {},
            "axis_scores": shadow.get("axis_scores") or {},
            "macro_axes": shadow.get("macro_axes") or {},
            "macro_axis_scores": shadow.get("macro_axis_scores") or {},
            "what_changed": shadow.get("what_changed") or [],
            "confidence_decomposition": shadow.get("confidence_decomposition") or {},
        },
        "guardrails": [
            "Comparison evidence is shadow-only and non-production authority.",
            "Do not use the shadow candidate for client-facing regime labels until explicit control-layer promotion.",
            "Do not use the shadow candidate, macro_axes, or macro_axis_scores for lane scoring, fundability, or portfolio actions.",
            "Legacy macro policy pack decision authority remains legacy_lane_adjustments_only.",
            "differs_from_legacy is retained for backward compatibility and equals regime_label_differs OR confidence_differs.",
        ],
    }


def _write_evidence(args: argparse.Namespace, evidence: dict[str, Any]) -> tuple[Path, Path]:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    token = _safe_token(str(args.run_id or args.workflow_run_id or "local"))
    run_path = output_dir / f"macro_regime_shadow_comparison_{token}.json"
    latest_path = output_dir / "latest_macro_regime_shadow_comparison.json"
    text = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    run_path.write_text(text, encoding="utf-8")
    latest_path.write_text(text, encoding="utf-8")
    return run_path, latest_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pricing-audit", default=None)
    parser.add_argument("--relative-strength", default="output/market_history/etf_relative_strength.json")
    parser.add_argument("--macro-context", default="config/etf_macro_fundamental_context.yml")
    parser.add_argument("--macro-data-audit", default="fixtures/macro_data_audit/macro_audit_fixture_2026-06-02.json")
    parser.add_argument("--output-dir", default="output/macro/validation")
    parser.add_argument("--run-id", default="macro_regime_shadow_comparison")
    parser.add_argument("--workflow-name", default="local")
    parser.add_argument("--workflow-run-id", default="local")
    parser.add_argument("--workflow-run-number", default="local")
    parser.add_argument("--workflow-attempt", default="local")
    parser.add_argument("--commit-sha", default="unknown")
    parser.add_argument("--source-ref", default="unknown")
    args = parser.parse_args()

    pack = _build_shadow_pack(args)
    evidence = _build_evidence(args, pack)
    run_path, latest_path = _write_evidence(args, evidence)
    comparison = evidence["comparison"]
    macro_axes = comparison.get("macro_axes") or {}
    print(
        "ETF_MACRO_REGIME_SHADOW_COMPARISON_OK | "
        f"legacy={comparison.get('legacy_regime')} | "
        f"shadow={comparison.get('shadow_candidate_regime')} | "
        f"legacy_confidence={comparison.get('legacy_confidence')} | "
        f"shadow_confidence={comparison.get('shadow_candidate_confidence')} | "
        f"label_differs={comparison.get('regime_label_differs')} | "
        f"confidence_differs={comparison.get('confidence_differs')} | "
        f"confidence_delta={comparison.get('confidence_delta')} | "
        f"differs={comparison.get('differs_from_legacy')} | "
        f"macro_axes={','.join(sorted(macro_axes)) or 'none'} | "
        f"run_path={run_path} | latest_path={latest_path}"
    )


if __name__ == "__main__":
    main()
