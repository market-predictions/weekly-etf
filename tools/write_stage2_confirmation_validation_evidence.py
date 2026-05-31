#!/usr/bin/env python3
"""Write repo-visible evidence for the ETF Stage-2 confirmation shadow workflow.

The evidence file is an audit artifact only. It confirms that the isolated
Stage-2 validation workflow passed, but it does not promote Stage-2 output into
client-facing report, scoring, fundability, or portfolio-action authority.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_MARKER = "ETF_STAGE2_CONFIRMATION_SHADOW_OK"
EXPECTED_DECISION_IMPACT = "none_stage2_confirmation_shadow_only"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Stage-2 artifact not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected JSON object in {path}")
    return payload


def _validate_stage2_payload(payload: dict[str, Any]) -> None:
    if payload.get("artifact_type") != "stage2_thesis_confirmation_shadow":
        raise SystemExit("Unexpected artifact_type for Stage-2 evidence")
    authority = payload.get("authority") or {}
    required = {
        "shadow_only": True,
        "client_facing_authority": False,
        "decision_impact": EXPECTED_DECISION_IMPACT,
        "portfolio_action_authority": False,
        "fundability_authority": False,
        "report_surface_allowed": False,
    }
    for key, expected in required.items():
        if authority.get(key) != expected:
            raise SystemExit(f"Unexpected Stage-2 authority.{key}: {authority.get(key)!r}")
    for row in payload.get("evaluations") or []:
        if row.get("portfolio_action") != "none":
            raise SystemExit("Stage-2 row has portfolio_action other than none")
        if row.get("client_facing_authority") is not False:
            raise SystemExit("Stage-2 row has client-facing authority")
        if row.get("fundability_authority") is not False:
            raise SystemExit("Stage-2 row has fundability authority")


def _safe_token(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value.strip())
    return cleaned or "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage2-artifact", type=Path, default=Path("output/macro/latest_stage2_confirmation.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("output/macro/validation"))
    parser.add_argument("--workflow-name", default="Validate ETF Stage-2 confirmation shadow")
    parser.add_argument("--workflow-run-id", default="local")
    parser.add_argument("--workflow-run-number", default="local")
    parser.add_argument("--workflow-attempt", default="local")
    parser.add_argument("--commit-sha", default="unknown")
    parser.add_argument("--source-ref", default="unknown")
    args = parser.parse_args()

    payload = _load_json(args.stage2_artifact)
    _validate_stage2_payload(payload)

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    evidence: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "stage2_confirmation_shadow_validation_evidence",
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
        "source_artifact": str(args.stage2_artifact),
        "validated_markers": [EXPECTED_MARKER],
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
        "stage2_summary": {
            "reference_date": payload.get("reference_date"),
            "run_id": payload.get("run_id"),
            "counts_by_status": payload.get("counts_by_status") or {},
            "evaluation_count": len(payload.get("evaluations") or []),
        },
        "guardrails": [
            "Stage-2 validation evidence is shadow-only.",
            "Stage-2 fundable-ready shadow is not a portfolio action.",
            "Do not wire Stage-2 artifacts into reports, scoring, fundability, or recommendations without a later control-layer promotion decision.",
        ],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    token = _safe_token(f"{args.workflow_run_id}_{args.workflow_attempt}")
    run_path = args.output_dir / f"stage2_confirmation_validation_{token}.json"
    latest_path = args.output_dir / "latest_stage2_confirmation_validation.json"
    text = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    run_path.write_text(text, encoding="utf-8")
    latest_path.write_text(text, encoding="utf-8")
    print(
        "ETF_STAGE2_CONFIRMATION_EVIDENCE_OK | "
        f"status={evidence['status']} | run_path={run_path} | latest_path={latest_path}"
    )


if __name__ == "__main__":
    main()
