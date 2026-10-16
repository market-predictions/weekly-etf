"""Read-only WRO operator projection; never grants delivery or execution authority."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.etf_release_assurance import (
    REQUIRED_CHECKS, load_json, report_assets, sha256_file, validate_release_assurance,
)


def operator_status(*, assurance: Path, source_sha: str, run_id: str,
                    close_date: str, report_token: str) -> dict:
    """Inspect one explicitly selected package. Paths resolve from the repository cwd.

    Legacy release assurance does not prove all WRO quality gates or exact-package
    principal authority. Those facts remain unavailable, never inferred from PASS.
    """
    identity = dict(source_sha=source_sha, run_id=run_id,
                    requested_close_date=close_date, report_token=report_token)
    result = dict(status="BLOCKED", identity=identity, assurance=str(assurance),
                  quality_checks=[], artifact_hashes={}, blockers=[],
                  authorization={"status": "BLOCKED", "reason": "No existing exact-package delivery authority binding"},
                  delivery_status="UNPROVEN")
    blockers = result["blockers"]
    try:
        observed = load_json(assurance)
        if isinstance(observed, dict):
            result["quality_checks"] = observed.get("checks", [])
            result["artifact_hashes"] = observed.get("artifact_hashes", {})
        record = validate_release_assurance(
            assurance, expected_source_sha=source_sha, expected_run_id=run_id,
            expected_close_date=close_date, expected_report_token=report_token)
        if record.get("contract_id") != "ETF_RELEASE_ASSURANCE_CONTRACT_V1":
            raise ValueError("release assurance contract mismatch")
        result["quality_checks"] = record["checks"]
        hashes = record["artifact_hashes"]
        result["artifact_hashes"] = hashes
        required = {"pricing_audit", "runtime_state", "run_manifest", "portfolio_state", "trade_ledger"}
        required.update(f"{lang}_{kind}" for lang in ("english", "dutch")
                        for kind in report_assets(Path("report.md")))
        if set(hashes) != required:
            blockers.append("Incomplete or unexpected package artifact inventory")
        ids = [item["id"] for item in record["checks"]]
        if len(ids) != len(set(ids)) or not REQUIRED_CHECKS.issubset(ids):
            blockers.append("Ambiguous or incomplete assurance checks")
        for key, item in hashes.items():
            path = Path(item["path"])
            if not path.is_file() or sha256_file(path) != item["sha256"]:
                blockers.append(f"Artifact missing or changed: {key}")
        manifest = load_json(Path(hashes["run_manifest"]["path"]))
        for key in ("run_id", "requested_close_date", "report_token"):
            if manifest.get(key) != identity[key]:
                blockers.append(f"Manifest identity mismatch: {key}")
        for key in ("pricing_audit", "runtime_state", "english_report", "dutch_report"):
            if manifest.get(f"{key}_path") != hashes[key]["path"]:
                blockers.append(f"Manifest artifact mismatch: {key}")
    except (OSError, ValueError, RuntimeError, TypeError, KeyError, AttributeError) as exc:
        blockers.append(f"Assurance unavailable or invalid: {exc}")
    # Existing ETF numeric/identity assurance is narrower than the WRO contract.
    # Do not invent a second evidence store or certify the missing scope ourselves.
    result["wro_gates"] = {
        "lineage_and_freshness": "UNPROVEN",
        "no_material_evidence_conflicts": "UNPROVEN",
        "deterministic_qa": "UNPROVEN",
        "canonical_bilingual_state": "UNPROVEN",
        "recommendations_not_executions": "UNPROVEN",
        "exact_candidate_independent_assurance": "UNPROVEN",
        "no_unresolved_blockers": "UNPROVEN",
    }
    blockers.extend(f"WRO gate unproven: {key}" for key in result["wro_gates"])
    blockers.append(result["authorization"]["reason"])
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assurance", type=Path, required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--close-date", required=True)
    parser.add_argument("--report-token", required=True)
    result = operator_status(**vars(parser.parse_args()))
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(1 if result["status"] == "BLOCKED" else 0)


if __name__ == "__main__":
    main()
