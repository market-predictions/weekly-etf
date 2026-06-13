#!/usr/bin/env python3
"""Write repo-native validation evidence for the ETF macro-regime shadow workflow."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.validate_macro_regime_shadow import EXPECTED_DECISION_IMPACT, REQUIRED_FALSE_AUTHORITY_FIELDS, validate_shadow_payload

EXPECTED_MARKERS = [
    "ETF_MACRO_REGIME_FIXTURE_REPLAY_OK",
    "ETF_MACRO_DATA_AUDIT_VALID_OK",
    "ETF_MACRO_AUDIT_AXIS_SHADOW_OK",
    "ETF_MACRO_REGIME_SHADOW_OK",
]


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Input pack not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected top-level JSON object in {path}")
    return payload


def _require_shadow_payload(pack: dict[str, Any]) -> dict[str, Any]:
    shadow = pack.get("deterministic_regime_shadow")
    if not isinstance(shadow, dict):
        raise SystemExit("deterministic_regime_shadow missing or not an object")

    try:
        validate_shadow_payload(shadow)
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc

    macro_axes = shadow.get("macro_axes")
    macro_scores = shadow.get("macro_axis_scores")
    macro_evidence = shadow.get("macro_evidence")
    confidence = shadow.get("confidence_decomposition") or {}
    components = confidence.get("components") or {}

    checks = {
        "shadow_only": shadow.get("shadow_only") is True,
        "decision_impact_shadow_only": shadow.get("decision_impact") == EXPECTED_DECISION_IMPACT,
        "candidate_regime_present": bool(shadow.get("candidate_regime")),
        "candidate_confidence_present": shadow.get("candidate_confidence") is not None,
        "legacy_regime_present": bool(shadow.get("legacy_regime")),
        "axes_present": isinstance(shadow.get("axes"), dict) and bool(shadow.get("axes")),
        "macro_axes_present": isinstance(macro_axes, dict) and bool(macro_axes),
        "macro_axis_scores_present": isinstance(macro_scores, dict) and bool(macro_scores),
        "macro_evidence_present": isinstance(macro_evidence, dict) and bool(macro_evidence),
        "macro_audit_confidence_component_present": components.get("macro_audit_present") is True,
    }
    for field in REQUIRED_FALSE_AUTHORITY_FIELDS:
        checks[f"{field}_false"] = shadow.get(field) is False
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("Shadow payload failed evidence checks: " + ", ".join(failed))
    return shadow


def _safe_token(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value.strip())
    return cleaned or "unknown"


def _authority() -> dict[str, bool | str]:
    return {
        "shadow_only": True,
        "client_facing_authority": False,
        "production_report_narrative_authority": False,
        "decision_impact": EXPECTED_DECISION_IMPACT,
        "production_report_path_changed": False,
        "lane_scoring_authority": False,
        "fundability_authority": False,
        "portfolio_action_authority": False,
        "portfolio_mutation": False,
        "historical_output_mutation": False,
    }


def _build_evidence(args: argparse.Namespace, pack: dict[str, Any], shadow: dict[str, Any]) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    axes = shadow.get("axes") if isinstance(shadow.get("axes"), dict) else {}
    macro_axes = shadow.get("macro_axes") if isinstance(shadow.get("macro_axes"), dict) else {}
    macro_axis_scores = shadow.get("macro_axis_scores") if isinstance(shadow.get("macro_axis_scores"), dict) else {}
    macro_evidence = shadow.get("macro_evidence") if isinstance(shadow.get("macro_evidence"), dict) else {}
    confidence = shadow.get("confidence_decomposition") if isinstance(shadow.get("confidence_decomposition"), dict) else {}
    components = confidence.get("components") if isinstance(confidence.get("components"), dict) else {}

    return {
        "schema_version": "1.0",
        "artifact_type": "macro_regime_shadow_validation_evidence",
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
        "source_pack": str(args.pack),
        "validated_markers": EXPECTED_MARKERS,
        "authority": _authority(),
        "macro_data_audit_summary": pack.get("macro_data_audit_summary") or {},
        "shadow_summary": {
            "method": shadow.get("method"),
            "candidate_regime": shadow.get("candidate_regime"),
            "candidate_confidence": shadow.get("candidate_confidence"),
            "legacy_regime": shadow.get("legacy_regime"),
            "legacy_confidence": shadow.get("legacy_confidence"),
            "differs_from_legacy": shadow.get("differs_from_legacy"),
            "axes": axes,
            "macro_axes": macro_axes,
            "macro_axis_scores": macro_axis_scores,
            "macro_evidence": macro_evidence,
            "confidence_components": components,
        },
        "guardrails": [
            "Evidence artifact is non-production and shadow-only.",
            "Do not use deterministic_regime_shadow for client-facing regime/confidence until promoted by control-layer decision.",
            "Do not use deterministic_regime_shadow, macro_axes, or macro_axis_scores for lane scoring, fundability, or portfolio actions.",
            "Production report workflow remains separate from this validation evidence path.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=Path("output/macro/latest.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("output/macro/validation"))
    parser.add_argument("--workflow-name", default="Validate ETF macro regime shadow")
    parser.add_argument("--workflow-run-id", default="local")
    parser.add_argument("--workflow-run-number", default="local")
    parser.add_argument("--workflow-attempt", default="local")
    parser.add_argument("--commit-sha", default="unknown")
    parser.add_argument("--source-ref", default="unknown")
    args = parser.parse_args()

    pack = _load_json(args.pack)
    shadow = _require_shadow_payload(pack)
    evidence = _build_evidence(args, pack, shadow)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_token = _safe_token(f"{args.workflow_run_id}_{args.workflow_attempt}")
    run_path = args.output_dir / f"macro_regime_shadow_validation_{run_token}.json"
    latest_path = args.output_dir / "latest_macro_regime_shadow_validation.json"

    text = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    run_path.write_text(text, encoding="utf-8")
    latest_path.write_text(text, encoding="utf-8")

    print(
        "ETF_MACRO_REGIME_SHADOW_EVIDENCE_OK | "
        f"status={evidence['status']} | "
        f"run_path={run_path} | latest_path={latest_path} | "
        f"macro_axes={','.join(sorted(evidence['shadow_summary']['macro_axes']))}"
    )


if __name__ == "__main__":
    main()
