from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_RELEASE_ID = "weekly_etf_shared_contract_v1_0_0"
EXPECTED_VERSION = "1.0.0"
EXPECTED_ARTIFACTS = {
    "shared_strategy_state": {
        "schema_version": "etf_shared_strategy_state_v1",
        "artifact_type": "etf_shared_strategy_decision_state",
    },
    "shared_portfolio_target": {
        "schema_version": "etf_shared_portfolio_target_v1",
        "artifact_type": "etf_shared_exposure_portfolio_target",
    },
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def text(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(f"Release component is missing: {path}")
    return path.read_text(encoding="utf-8")


def validate(manifest: dict[str, Any], repository_root: Path) -> list[str]:
    blockers: list[str] = []

    if manifest.get("schema_version") != "etf_shared_contract_release_manifest_v1":
        blockers.append("unexpected release-manifest schema_version")
    if manifest.get("contract_release_id") != EXPECTED_RELEASE_ID:
        blockers.append("unexpected contract_release_id")
    if manifest.get("semantic_version") != EXPECTED_VERSION:
        blockers.append("unexpected semantic_version")
    if manifest.get("promotion_status") != "stable_on_merge":
        blockers.append("promotion_status must be stable_on_merge")
    if manifest.get("source_repository") != "market-predictions/weekly-etf":
        blockers.append("unexpected source_repository")
    if manifest.get("stable_branch") != "main":
        blockers.append("stable_branch must be main")
    if manifest.get("promotion_pull_request") != 113:
        blockers.append("promotion pull request must be recorded")

    policy_path = repository_root / str(manifest.get("policy_path") or "")
    if not policy_path.is_file():
        blockers.append("promotion policy is missing")

    consumer = manifest.get("consumer_contract") if isinstance(manifest.get("consumer_contract"), dict) else {}
    if consumer.get("pinning_required") is not True:
        blockers.append("consumer pinning must be required")
    if consumer.get("mutable_feature_branch_allowed") is not False:
        blockers.append("mutable feature branches must be prohibited")
    allowed_refs = set(consumer.get("allowed_refs") or [])
    if allowed_refs != {"immutable_merge_commit_sha", "tag_resolving_to_accepted_commit"}:
        blockers.append("allowed consumer refs do not match the promotion policy")
    validated_consumer = consumer.get("validated_shadow_consumer") if isinstance(consumer.get("validated_shadow_consumer"), dict) else {}
    if validated_consumer.get("repository") != "market-predictions/weekly-etf-eu" or validated_consumer.get("pull_request") != 66:
        blockers.append("validated downstream shadow consumer is not recorded")

    authority = manifest.get("authority") if isinstance(manifest.get("authority"), dict) else {}
    if authority.get("strategy_research_authority") is not True:
        blockers.append("strategy research authority is missing")
    if authority.get("portfolio_reference_authority") is not True:
        blockers.append("portfolio reference authority is missing")
    for key in (
        "portfolio_mutation",
        "funding_authority",
        "execution_authority",
        "broker_execution_authority",
        "production_delivery_authority",
    ):
        if authority.get(key) is not False:
            blockers.append(f"{key} must be false")

    artifacts = manifest.get("artifacts") if isinstance(manifest.get("artifacts"), dict) else {}
    if set(artifacts) != set(EXPECTED_ARTIFACTS):
        blockers.append("release artifact inventory is incomplete or unexpected")
    for artifact_id, expected in EXPECTED_ARTIFACTS.items():
        row = artifacts.get(artifact_id) if isinstance(artifacts.get(artifact_id), dict) else {}
        if row.get("schema_version") != expected["schema_version"]:
            blockers.append(f"{artifact_id} schema version mismatch")
        if row.get("artifact_type") != expected["artifact_type"]:
            blockers.append(f"{artifact_id} artifact type mismatch")
        try:
            schema_path = repository_root / str(row.get("schema_path") or "")
            builder_path = repository_root / str(row.get("builder_path") or "")
            validator_path = repository_root / str(row.get("validator_path") or "")
            schema = load_json(schema_path)
            builder_text = text(builder_path)
            validator_text = text(validator_path)
        except Exception as exc:
            blockers.append(str(exc))
            continue
        schema_const = ((schema.get("properties") or {}).get("schema_version") or {}).get("const")
        artifact_const = ((schema.get("properties") or {}).get("artifact_type") or {}).get("const")
        if schema_const != expected["schema_version"]:
            blockers.append(f"{artifact_id} schema const does not match release manifest")
        if artifact_const != expected["artifact_type"]:
            blockers.append(f"{artifact_id} artifact const does not match release manifest")
        if expected["schema_version"] not in builder_text:
            blockers.append(f"{artifact_id} builder does not emit the released schema version")
        if expected["artifact_type"] not in builder_text:
            blockers.append(f"{artifact_id} builder does not emit the released artifact type")
        if expected["schema_version"] not in validator_text:
            blockers.append(f"{artifact_id} validator does not enforce the released schema version")

    compatibility = manifest.get("compatibility") if isinstance(manifest.get("compatibility"), dict) else {}
    if compatibility.get("major") != 1 or compatibility.get("consumer_must_reject_unknown_major") is not True:
        blockers.append("major-version compatibility policy is incomplete")

    gates = manifest.get("promotion_gates") if isinstance(manifest.get("promotion_gates"), dict) else {}
    required_true = (
        "deterministic_builds_required",
        "artifact_validation_required",
        "release_manifest_validation_required",
        "downstream_shadow_validation_required",
        "required_ci_green",
    )
    for key in required_true:
        if gates.get(key) is not True:
            blockers.append(f"promotion gate {key} must be true")
    if gates.get("official_portfolio_mutation_allowed") is not False:
        blockers.append("promotion must not allow official portfolio mutation")

    rollback = manifest.get("rollback") if isinstance(manifest.get("rollback"), dict) else {}
    if rollback.get("automatic_portfolio_mutation") is not False or rollback.get("automatic_trade_reversal") is not False:
        blockers.append("rollback authority boundary is invalid")

    return blockers


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the shared ETF contract release manifest")
    parser.add_argument(
        "manifest",
        type=Path,
        nargs="?",
        default=Path("control/releases/ETF_SHARED_CONTRACT_RELEASE_1_0_0.json"),
    )
    args = parser.parse_args()
    repository_root = Path(__file__).resolve().parents[1]
    manifest = load_json(args.manifest)
    blockers = validate(manifest, repository_root)
    print(json.dumps({
        "artifact_type": "etf_shared_contract_release_validation",
        "contract_release_id": manifest.get("contract_release_id"),
        "semantic_version": manifest.get("semantic_version"),
        "valid": not blockers,
        "blockers": blockers,
    }, indent=2))
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
