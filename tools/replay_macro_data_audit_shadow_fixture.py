from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime import build_macro_policy_pack as legacy
from runtime.build_macro_policy_pack_shadow import add_shadow_regime
from tools.validate_macro_data_audit import validate as validate_macro_data_audit
from tools.validate_macro_policy_pack import _validate_pack
from tools.validate_macro_regime_shadow import validate_shadow_payload

DEFAULT_AUDIT = Path("fixtures/macro_data_audit/macro_audit_fixture_2026-06-02.json")
DEFAULT_PRICING_AUDIT = Path("output/pricing/price_audit_2026-05-29_20260531_203900.json")
DEFAULT_RS = Path("output/market_history/etf_relative_strength.json")
DEFAULT_MACRO_CONTEXT = Path("config/etf_macro_fundamental_context.yml")
DEFAULT_OUTPUT_DIR = Path("output/macro")
DEFAULT_VALIDATION_DIR = Path("output/macro/validation")
EXPECTED_MACRO_AXES = {
    "volatility": "calm",
    "real_rates": "restrictive",
    "yield_curve": "inverted",
    "inflation_expectations": "neutral",
    "policy_rate": "restrictive",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _safe_token(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value.strip())
    return cleaned or "unknown"


def _write_policy_pack(pack: dict[str, Any], output_dir: Path, run_id: str) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = str(pack.get("report_date", "unknown")).replace("-", "")
    out_path = output_dir / f"etf_macro_policy_pack_{suffix}_{run_id}.json"
    latest_path = output_dir / "latest.json"
    text = json.dumps(pack, indent=2, sort_keys=True) + "\n"
    out_path.write_text(text, encoding="utf-8")
    latest_path.write_text(text, encoding="utf-8")
    return out_path, latest_path


def _validate_shadow(pack: dict[str, Any], audit_result: dict[str, Any]) -> dict[str, Any]:
    _validate_pack(pack)
    shadow = pack.get("deterministic_regime_shadow") or {}
    validate_shadow_payload(shadow)

    pack_summary = pack.get("macro_data_audit_summary") or {}
    _require(pack_summary.get("present") is True, "macro_data_audit_summary.present must be true")
    _require(pack_summary.get("mode") == "fixture", "macro_data_audit_summary.mode must be fixture")
    _require(pack_summary.get("status") == "passed", "macro_data_audit_summary.status must be passed")

    macro_axes = shadow.get("macro_axes") or {}
    _require(isinstance(macro_axes, dict) and macro_axes, "macro_axes is missing")
    for axis, expected in EXPECTED_MACRO_AXES.items():
        actual = macro_axes.get(axis)
        _require(actual == expected, f"macro axis {axis!r} expected {expected!r}, got {actual!r}")

    macro_scores = shadow.get("macro_axis_scores") or {}
    macro_evidence = shadow.get("macro_evidence") or {}
    _require(isinstance(macro_scores, dict) and macro_scores, "macro_axis_scores is missing")
    _require(macro_evidence.get("macro_audit_mode") == "fixture", "macro_evidence mode mismatch")
    _require(macro_evidence.get("macro_audit_reference_date") == audit_result.get("reference_date"), "macro_evidence date mismatch")

    confidence = shadow.get("confidence_decomposition") or {}
    components = confidence.get("components") or {}
    _require(components.get("macro_audit_present") is True, "macro_audit_present must be true")

    return {
        "candidate_regime": shadow.get("candidate_regime"),
        "candidate_confidence": shadow.get("candidate_confidence"),
        "macro_axes": macro_axes,
        "macro_axis_scores": macro_scores,
        "macro_evidence": macro_evidence,
        "confidence_components": components,
    }


def _write_evidence(args: argparse.Namespace, audit_result: dict[str, Any], pack_path: Path, summary: dict[str, Any]) -> tuple[Path, Path]:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    evidence = {
        "schema_version": "1.0",
        "artifact_type": "macro_audit_axis_shadow_validation_evidence",
        "status": "passed",
        "generated_at_utc": generated_at,
        "repository": "market-predictions/weekly-etf",
        "workflow": {
            "name": args.workflow_name,
            "run_id": args.workflow_run_id,
            "run_number": args.workflow_run_number,
            "run_attempt": args.workflow_attempt,
            "commit_sha": args.commit_sha,
            "source_ref": args.source_ref,
        },
        "source_files": {
            "macro_data_audit_fixture": str(args.audit),
            "pricing_audit": str(args.pricing_audit),
            "relative_strength": str(args.relative_strength),
            "macro_context": str(args.macro_context),
            "shadow_policy_pack": str(pack_path),
        },
        "validated_markers": [
            "ETF_MACRO_DATA_AUDIT_VALID_OK",
            "ETF_MACRO_AUDIT_AXIS_SHADOW_OK",
        ],
        "authority": {
            "shadow_only": True,
            "client_facing_authority": False,
            "decision_impact": "none_shadow_comparison_only",
            "production_report_path_changed": False,
            "lane_scoring_authority": False,
            "fundability_authority": False,
            "portfolio_action_authority": False,
        },
        "macro_data_audit_summary": audit_result,
        "shadow_summary": summary,
    }
    args.validation_output_dir.mkdir(parents=True, exist_ok=True)
    run_token = _safe_token(f"{args.workflow_run_id}_{args.workflow_attempt}_{args.run_id}")
    run_path = args.validation_output_dir / f"macro_audit_axis_shadow_validation_{run_token}.json"
    latest_path = args.validation_output_dir / "latest_macro_audit_axis_shadow_validation.json"
    text = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    run_path.write_text(text, encoding="utf-8")
    latest_path.write_text(text, encoding="utf-8")
    return run_path, latest_path


def replay(args: argparse.Namespace) -> dict[str, Any]:
    audit_result = validate_macro_data_audit(args.audit)
    print(
        "ETF_MACRO_DATA_AUDIT_VALID_OK | "
        f"mode={audit_result['mode']} | reference_date={audit_result['reference_date']} | "
        f"observations={audit_result['observations']} | groups={','.join(audit_result['groups'])}"
    )

    pack = legacy.build_pack(args.pricing_audit, args.relative_strength, args.macro_context, args.audit)
    pack = add_shadow_regime(pack, args.relative_strength, args.audit)
    out_path, latest_path = _write_policy_pack(pack, args.output_dir, args.run_id)

    summary = _validate_shadow(pack, audit_result)
    run_path, evidence_latest_path = _write_evidence(args, audit_result, out_path, summary)

    print(
        "ETF_MACRO_AUDIT_AXIS_SHADOW_OK | "
        f"candidate={summary['candidate_regime']} | "
        f"confidence={summary['candidate_confidence']} | "
        f"macro_axes={json.dumps(summary['macro_axes'], sort_keys=True)} | "
        f"pack={out_path} | latest={latest_path} | "
        f"evidence={run_path} | evidence_latest={evidence_latest_path}"
    )
    return {
        "audit": audit_result,
        "pack": str(out_path),
        "latest": str(latest_path),
        "evidence": str(run_path),
        "evidence_latest": str(evidence_latest_path),
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay macro-data-audit fixture through shadow regime stack.")
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--pricing-audit", type=Path, default=DEFAULT_PRICING_AUDIT)
    parser.add_argument("--relative-strength", type=Path, default=DEFAULT_RS)
    parser.add_argument("--macro-context", type=Path, default=DEFAULT_MACRO_CONTEXT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--validation-output-dir", type=Path, default=DEFAULT_VALIDATION_DIR)
    parser.add_argument("--run-id", default="macro_audit_axis_shadow_validation")
    parser.add_argument("--workflow-name", default="local")
    parser.add_argument("--workflow-run-id", default="local")
    parser.add_argument("--workflow-run-number", default="local")
    parser.add_argument("--workflow-attempt", default="local")
    parser.add_argument("--commit-sha", default="unknown")
    parser.add_argument("--source-ref", default="unknown")
    args = parser.parse_args()
    replay(args)


if __name__ == "__main__":
    main()
