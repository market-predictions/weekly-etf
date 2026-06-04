#!/usr/bin/env python3
"""Write repo-native validation evidence for Stage-1 thesis candidates.

This evidence is shadow-only. It must not promote thesis candidates to client-facing,
lane-scoring, fundability, or portfolio-action authority.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_DECISION_IMPACT = "none_stage1_thesis_candidates_only"
EXPECTED_MARKERS = [
    "ETF_THESIS_CANDIDATES_SHADOW_OK",
]


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Input artifact not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected JSON object in {path}")
    return payload


def _require_shadow_artifact(payload: dict[str, Any]) -> None:
    authority = payload.get("authority") or {}
    checks = {
        "artifact_type": payload.get("artifact_type") == "stage_1_thesis_candidates_shadow",
        "authority_shadow_only": authority.get("shadow_only") is True,
        "authority_client_facing_false": authority.get("client_facing_authority") is False,
        "authority_decision_impact": authority.get("decision_impact") == EXPECTED_DECISION_IMPACT,
        "authority_portfolio_action_false": authority.get("portfolio_action_authority") is False,
        "authority_fundability_false": authority.get("fundability_authority") is False,
        "authority_report_surface_false": authority.get("report_surface_allowed") is False,
        "drivers_list_present": isinstance(payload.get("drivers"), list),
        "candidates_list_present": isinstance(payload.get("candidates"), list),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("Thesis candidate artifact failed authority checks: " + ", ".join(failed))

    for candidate in payload.get("candidates") or []:
        if candidate.get("client_facing_authority") is not False:
            raise SystemExit("Candidate has client-facing authority")
        if candidate.get("fundability_status") != "not_fundable_stage_1_only":
            raise SystemExit("Candidate is not marked stage-1-only / not fundable")
        if candidate.get("portfolio_action") != "none":
            raise SystemExit("Candidate has portfolio action")
        if candidate.get("requires_stage_2_confirmation") is not True:
            raise SystemExit("Candidate does not require Stage-2 confirmation")


def _safe_token(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value.strip())
    return cleaned or "unknown"


def _build_evidence(args: argparse.Namespace, payload: dict[str, Any]) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    drivers = payload.get("drivers") if isinstance(payload.get("drivers"), list) else []
    candidates = payload.get("candidates") if isinstance(payload.get("candidates"), list) else []
    active_driver_ids = payload.get("active_driver_ids") if isinstance(payload.get("active_driver_ids"), list) else []

    return {
        "schema_version": "1.0",
        "artifact_type": "stage_1_thesis_candidates_validation_evidence",
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
        "source_artifact": str(args.artifact),
        "validated_markers": EXPECTED_MARKERS,
        "authority": {
            "shadow_only": True,
            "client_facing_authority": False,
            "decision_impact": EXPECTED_DECISION_IMPACT,
            "production_report_path_changed": False,
            "lane_scoring_authority": False,
            "fundability_authority": False,
            "portfolio_action_authority": False,
            "report_surface_allowed": False,
        },
        "summary": {
            "reference_date": payload.get("reference_date"),
            "run_id": payload.get("run_id"),
            "active_driver_count": len(active_driver_ids),
            "active_driver_ids": active_driver_ids,
            "driver_count": len(drivers),
            "candidate_count": len(candidates),
            "candidate_taxonomy_tags": sorted({str(c.get("taxonomy_tag")) for c in candidates if c.get("taxonomy_tag")}),
        },
        "guardrails": [
            "Stage-1 thesis candidates are internal only.",
            "No candidate is fundable without Stage-2 confirmation, valuation-grade pricing, and portfolio discipline gates.",
            "Do not surface this artifact in English or Dutch reports.",
            "Do not feed Stage-1 thesis candidates into lane scoring, fundability, portfolio actions, or recommendations until explicitly promoted.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=Path("output/macro/latest_thesis_candidates.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("output/macro/validation"))
    parser.add_argument("--workflow-name", default="Validate ETF thesis candidates shadow")
    parser.add_argument("--workflow-run-id", default="local")
    parser.add_argument("--workflow-run-number", default="local")
    parser.add_argument("--workflow-attempt", default="local")
    parser.add_argument("--commit-sha", default="unknown")
    parser.add_argument("--source-ref", default="unknown")
    args = parser.parse_args()

    payload = _load_json(args.artifact)
    _require_shadow_artifact(payload)
    evidence = _build_evidence(args, payload)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_token = _safe_token(f"{args.workflow_run_id}_{args.workflow_attempt}")
    run_path = args.output_dir / f"thesis_candidates_validation_{run_token}.json"
    latest_path = args.output_dir / "latest_thesis_candidates_validation.json"
    text = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    run_path.write_text(text, encoding="utf-8")
    latest_path.write_text(text, encoding="utf-8")

    print(
        "ETF_THESIS_CANDIDATES_EVIDENCE_OK | "
        f"status={evidence['status']} | "
        f"active_drivers={evidence['summary']['active_driver_count']} | "
        f"candidates={evidence['summary']['candidate_count']} | "
        f"run_path={run_path} | latest_path={latest_path}"
    )


if __name__ == "__main__":
    main()
