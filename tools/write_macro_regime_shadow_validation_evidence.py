#!/usr/bin/env python3
"""Write repo-native validation evidence for the ETF macro-regime shadow workflow.

This script is intentionally narrow and non-production:
- It reads the already-built shadow macro policy pack.
- It verifies that the deterministic regime payload is present and shadow-only.
- It writes JSON evidence under output/macro/validation/.

The evidence file is for future ChatGPT/repo audits only. It must not be used as
client-facing report authority, lane-scoring authority, or portfolio-action input.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_DECISION_IMPACT = "none_shadow_comparison_only"
EXPECTED_MARKERS = [
    "ETF_MACRO_REGIME_FIXTURE_REPLAY_OK",
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

    checks = {
        "shadow_only": shadow.get("shadow_only") is True,
        "client_facing_authority_false": shadow.get("client_facing_authority") is False,
        "decision_impact_shadow_only": shadow.get("decision_impact") == EXPECTED_DECISION_IMPACT,
        "candidate_regime_present": bool(shadow.get("candidate_regime")),
        "candidate_confidence_present": shadow.get("candidate_confidence") is not None,
        "legacy_regime_present": bool(shadow.get("legacy_regime")),
        "axes_present": isinstance(shadow.get("axes"), dict) and bool(shadow.get("axes")),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("Shadow payload failed evidence checks: " + ", ".join(failed))
    return shadow


def _safe_token(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value.strip())
    return cleaned or "unknown"


def _build_evidence(args: argparse.Namespace, pack: dict[str, Any], shadow: dict[str, Any]) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    axes = shadow.get("axes") if isinstance(shadow.get("axes"), dict) else {}

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
        "authority": {
            "shadow_only": True,
            "client_facing_authority": False,
            "decision_impact": EXPECTED_DECISION_IMPACT,
            "production_report_path_changed": False,
            "lane_scoring_authority": False,
            "fundability_authority": False,
            "portfolio_action_authority": False,
        },
        "shadow_summary": {
            "method": shadow.get("method"),
            "candidate_regime": shadow.get("candidate_regime"),
            "candidate_confidence": shadow.get("candidate_confidence"),
            "legacy_regime": shadow.get("legacy_regime"),
            "legacy_confidence": shadow.get("legacy_confidence"),
            "differs_from_legacy": shadow.get("differs_from_legacy"),
            "axis_labels": {key: value.get("label") for key, value in axes.items() if isinstance(value, dict)},
        },
        "guardrails": [
            "Evidence artifact is non-production and shadow-only.",
            "Do not use deterministic_regime_shadow for client-facing regime/confidence until promoted by control-layer decision.",
            "Do not use deterministic_regime_shadow for lane scoring, fundability, or portfolio actions.",
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
        f"run_path={run_path} | latest_path={latest_path}"
    )


if __name__ == "__main__":
    main()
