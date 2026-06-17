from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import build_stage2_promotion_review_decision_dry_run as builder
from tools import validate_stage2_promotion_review_decision_dry_run as dry_validator
from tools import validate_stage2_promotion_review_decision_hardening as hardening
from tools import validate_stage2_promotion_review_decision_sample_gate as sample_gate
from tools import validate_stage2_promotion_review_decision_schema as schema_validator


def _artifact() -> dict:
    return copy.deepcopy(builder.build_dry_run())


def test_dry_run_builder_returns_deterministic_artifact() -> None:
    assert builder.build_dry_run() == builder.build_dry_run()


def test_dry_run_artifact_validates_against_decision_schema() -> None:
    schema_validator.validate_artifact(_artifact(), require_expected_sources=True)


def test_dry_run_artifact_passes_hardening_checks() -> None:
    hardening._validate_hardened_artifact(_artifact())


def test_dry_run_artifact_passes_sample_gate_checks() -> None:
    sample_gate.validate_sample(_artifact())


def test_dry_run_artifact_has_decision_status_not_promoted() -> None:
    assert _artifact()["decision_status"] == "not_promoted"


def test_dry_run_artifact_has_exact_authority_block() -> None:
    assert _artifact()["authority"] == schema_validator.REQUIRED_AUTHORITY


def test_dry_run_artifact_has_exact_source_evidence_references() -> None:
    assert _artifact()["source_evidence"] == schema_validator.EXPECTED_SOURCE_EVIDENCE


def test_dry_run_artifact_has_deterministic_generated_at_utc() -> None:
    assert _artifact()["generated_at_utc"] == "2026-06-17T00:00:00Z"


def test_dry_run_builder_does_not_write_by_default() -> None:
    dry_validator.validate_no_default_write()


@pytest.mark.parametrize("path", [
    "output/dry-run.json",
    "runtime/dry-run.json",
    "portfolio/dry-run.json",
    "reports/dry-run.json",
    "delivery/dry-run.json",
])
def test_dry_run_builder_rejects_blocked_write_roots(path: str) -> None:
    with pytest.raises(ValueError):
        builder.validate_write_path(Path(path))


def test_dry_run_builder_rejects_absolute_write_path() -> None:
    with pytest.raises(ValueError):
        builder.validate_write_path(Path("/tmp/dry-run.json"))


def test_dry_run_builder_rejects_traversal_write_path() -> None:
    with pytest.raises(ValueError):
        builder.validate_write_path(Path("../dry-run.json"))


def test_dry_run_validator_rejects_authority_true() -> None:
    artifact = _artifact()
    artifact["authority"]["delivery_authority"] = True
    with pytest.raises(RuntimeError, match="dry-run validation failed"):
        dry_validator.validate_dry_run_artifact(artifact)


def test_dry_run_validator_rejects_extra_top_level_field() -> None:
    artifact = _artifact()
    artifact["extra"] = True
    with pytest.raises(RuntimeError, match="dry-run validation failed"):
        dry_validator.validate_dry_run_artifact(artifact)


def test_dry_run_validator_rejects_raw_driver_text() -> None:
    artifact = _artifact()
    artifact["decision_rationale"][0]["summary"] = "This text contains driver_id."
    with pytest.raises(RuntimeError, match="dry-run validation failed"):
        dry_validator.validate_dry_run_artifact(artifact)


def test_dry_run_validator_rejects_promotional_text() -> None:
    artifact = _artifact()
    artifact["decision_rationale"][0]["summary"] = "This text says recommended."
    with pytest.raises(RuntimeError, match="dry-run validation failed"):
        dry_validator.validate_dry_run_artifact(artifact)


def test_cli_dry_run_validator_prints_success_marker(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["validate_stage2_promotion_review_decision_dry_run.py"])
    dry_validator.main()
    out = capsys.readouterr().out
    assert "STAGE2_PROMOTION_REVIEW_DECISION_DRY_RUN_OK" in out


def test_allowed_dry_run_write_with_tmp_override(tmp_path: Path) -> None:
    target = tmp_path / "dry-run.json"
    builder.write_dry_run(target, allow_tmp=True)
    assert target.exists()
