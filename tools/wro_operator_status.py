"""Read-only WRO operator projection; never grants delivery or execution authority."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.etf_release_assurance import (
    REQUIRED_CHECKS, evaluate_release_assurance, load_json, report_assets,
    sha256_file, validate_release_assurance,
)
from runtime.report_freshness_contract import validate_report_freshness
from runtime.trade_lineage import validate_trade_lineage_rows
from tools.validate_etf_pricing_lineage_contract import _validate_price_rows, _validate_runtime_vs_audit


WRO_MISSING_PROOF = {
    "lineage_and_freshness": "Complete material-claim lineage and source-specific freshness are not bound by legacy assurance",
    "no_material_evidence_conflicts": "Pricing/runtime checks do not cover every material research claim",
    "deterministic_qa": "Legacy numeric/format QA does not prove the full WRO evidence-quality contract",
    "canonical_bilingual_state": "Matching table numbers do not establish common canonical NL/EN claim lineage",
    "recommendations_not_executions": "Runtime trade checks do not bind every rendered execution claim to the ledger",
    "exact_candidate_independent_assurance": "Separated role labels do not provide an independent exact-package review receipt",
    "no_unresolved_blockers": "Every applicable WRO prerequisite must be proven for this exact package",
}


def _wro_evidence(record: dict, paths: dict, package: dict) -> dict:
    """Use existing pure validators; passing partial checks never certifies WRO."""
    evidence = {gate: {"status": "UNPROVEN", "checks": [], "missing_proof": missing}
                for gate, missing in WRO_MISSING_PROOF.items()}

    def observe(gates, check_id, failure):
        for gate in gates:
            evidence[gate]["checks"].append({"id": check_id, "passed": failure is None, "failure": failure})
            if failure is not None:
                evidence[gate]["status"] = "FAIL"

    for check in record["checks"]:
        observe(("deterministic_qa",), check["id"], None if check["passed"] else check["evidence"])
        if check["id"] == "bilingual_table_numeric_parity":
            observe(("canonical_bilingual_state",), check["id"], None if check["passed"] else check["evidence"])
    runtime = load_json(paths["runtime_state"])
    pricing = load_json(paths["pricing_audit"])
    for language, key in (("en", "english_report"), ("nl", "dutch_report")):
        failure = None
        try:
            validate_report_freshness(paths[key].read_text(encoding="utf-8"), runtime, language)
        except (RuntimeError, ValueError, TypeError, KeyError) as exc:
            failure = str(exc)
        observe(("lineage_and_freshness", "no_material_evidence_conflicts", "deterministic_qa"),
                "existing_report_freshness_" + language, failure)
    if pricing.get("price_results") or pricing.get("prices"):
        failure = None
        try:
            _validate_price_rows(pricing)
            _validate_runtime_vs_audit(runtime, pricing, price_tolerance=0.02, value_tolerance=0.75)
        except (RuntimeError, ValueError, TypeError, KeyError) as exc:
            failure = str(exc)
        observe(("lineage_and_freshness", "no_material_evidence_conflicts"), "existing_pricing_runtime_lineage", failure)
    failures = validate_trade_lineage_rows(runtime.get("positions", []), context="wro_exact_package")
    observe(("recommendations_not_executions",), "existing_runtime_trade_lineage", failures or None)
    unresolved = package["blockers"] + [gate for gate, item in evidence.items() if item["status"] == "FAIL"]
    if unresolved:
        evidence["no_unresolved_blockers"]["status"] = "FAIL"
        evidence["no_unresolved_blockers"]["checks"] = [{"id": "current_package_blockers", "passed": False, "failure": unresolved}]
    return evidence


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
    result["wro_gate_evidence"] = {
        gate: {"status": "UNPROVEN", "checks": [], "missing_proof": missing}
        for gate, missing in WRO_MISSING_PROOF.items()
    }
    blockers = result["blockers"]
    try:
        observed = load_json(assurance)
        if isinstance(observed, dict):
            result["quality_checks"] = observed.get("checks", [])
            result["artifact_hashes"] = observed.get("artifact_hashes", {})
        record = validate_release_assurance(
            assurance, expected_source_sha=source_sha, expected_run_id=run_id,
            expected_close_date=close_date, expected_report_token=report_token,
            require_pass=False)
        if record.get("contract_id") != "ETF_RELEASE_ASSURANCE_CONTRACT_V1":
            raise ValueError("release assurance contract mismatch")
        result["quality_checks"] = record["checks"]
        source_checks = [
            check for check in record["checks"]
            if check.get("id") == "source_identity_bound"
        ]
        if (
            len(source_checks) != 1
            or not isinstance(source_checks[0].get("evidence"), dict)
            or source_checks[0]["evidence"].get("source_sha") != source_sha
        ):
            blockers.append("Assurance source SHA contradicts source identity evidence")
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
        if blockers:
            for gate in ("lineage_and_freshness", "deterministic_qa"):
                result["wro_gate_evidence"][gate]["status"] = "FAIL"
                result["wro_gate_evidence"][gate]["checks"] = [
                    {"id": "exact_package_binding", "passed": False, "failure": list(blockers)}]
        else:
            paths = {key: Path(item["path"]) for key, item in hashes.items()}
            current = evaluate_release_assurance(
                source_sha=source_sha, github_run_id=record["identity"]["github_run_id"],
                run_id=run_id, requested_close_date=close_date, report_token=report_token,
                **{key: paths[key] for key in ("pricing_audit", "runtime_state", "run_manifest",
                                               "portfolio_state", "trade_ledger", "english_report", "dutch_report")})
            result["quality_checks"] = current["checks"]
            for check in current["checks"]:
                if check["passed"] is not True:
                    blockers.append("Existing package QA failed: " + check["id"])
            recorded = {check["id"]: check["passed"] for check in record["checks"]}
            observed = {check["id"]: check["passed"] for check in current["checks"]}
            if recorded != observed:
                blockers.append("Recorded assurance checks contradict current exact-package validation")
            if record["blockers"]:
                blockers.extend("Recorded assurance blocker: " + str(item) for item in record["blockers"])
            result["wro_gate_evidence"] = _wro_evidence(current, paths, result)
    except (OSError, ValueError, RuntimeError, TypeError, KeyError, AttributeError) as exc:
        blockers.append(f"Assurance unavailable or invalid: {exc}")
    # Existing ETF numeric/identity assurance is narrower than the WRO contract.
    # Do not invent a second evidence store or certify the missing scope ourselves.
    if blockers:
        result["wro_gate_evidence"]["no_unresolved_blockers"]["status"] = "FAIL"
    result["wro_gates"] = {key: item["status"] for key, item in result["wro_gate_evidence"].items()}
    for key, item in result["wro_gate_evidence"].items():
        blockers.append(f"WRO gate {item['status'].lower()}: {key}: {item['missing_proof']}")
    blockers.append(result["authorization"]["reason"])
    return result


def format_text(result: dict) -> str:
    """Summarize the existing projection without making new readiness claims."""
    identity = result["identity"]
    lines = [
        f"Weekly ETF: {result['status']}",
        f"Source commit: {identity['source_sha']}",
        f"Run: {identity['run_id']}",
        f"Close date: {identity['requested_close_date']}",
        f"Report token: {identity['report_token']}",
        f"Assurance: {result['assurance']}",
        f"Delivery authorization: {result['authorization']['status']}",
        f"Delivery evidence: {result['delivery_status']}",
    ]
    hashes = result["artifact_hashes"]
    if isinstance(hashes, dict) and hashes:
        lines.extend(("", "Recorded artifact hashes (SHA-256):"))
        for name, artifact in sorted(hashes.items()):
            if isinstance(artifact, dict) and isinstance(artifact.get("sha256"), str):
                lines.append(f"- {name}: {artifact['sha256']}")
    lines.extend(("", "WRO prerequisite gates:"))
    lines.extend(f"- {gate}: {status}" for gate, status in result["wro_gates"].items())
    lines.extend(("", "Blockers:"))
    lines.extend(f"- {blocker}" for blocker in result["blockers"])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assurance", type=Path, required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--close-date", required=True)
    parser.add_argument("--report-token", required=True)
    parser.add_argument("--format", choices=("json", "text"), default="json",
                        help="Output format (default: json)")
    args = vars(parser.parse_args())
    output_format = args.pop("format")
    result = operator_status(**args)
    print(format_text(result) if output_format == "text"
          else json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(1 if result["status"] == "BLOCKED" else 0)


if __name__ == "__main__":
    main()
