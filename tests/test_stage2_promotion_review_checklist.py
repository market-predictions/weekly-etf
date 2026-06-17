from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import validate_stage2_promotion_review_checklist as checklist


def _valid_artifact() -> dict:
    return copy.deepcopy(checklist.valid_artifact())


def test_valid_minimal_review_artifact_passes_checklist() -> None:
    status = checklist.validate_checklist(_valid_artifact())

    assert status == "checklist_ready_for_review_not_promoted"


def test_missing_authority_block_fails() -> None:
    payload = _valid_artifact()
    payload.pop("authority")

    with pytest.raises(RuntimeError, match="checklist validation failed"):
        checklist.validate_checklist(payload)


def test_any_authority_field_set_true_fails() -> None:
    payload = _valid_artifact()
    payload["authority"]["delivery_authority"] = True

    with pytest.raises(RuntimeError, match="checklist validation failed"):
        checklist.validate_checklist(payload)


def test_missing_stage2_confirmation_validation_reference_fails() -> None:
    payload = _valid_artifact()
    payload["source_artifacts"].pop("stage2_confirmation_validation")

    with pytest.raises(RuntimeError, match="checklist validation failed"):
        checklist.validate_checklist(payload)


def test_missing_bilingual_alias_source_fails() -> None:
    payload = _valid_artifact()
    payload["source_artifacts"].pop("bilingual_aliases")

    with pytest.raises(RuntimeError, match="checklist validation failed"):
        checklist.validate_checklist(payload)


def test_missing_leakage_validation_reference_fails() -> None:
    payload = _valid_artifact()
    payload["source_artifacts"].pop("leakage_validation")

    with pytest.raises(RuntimeError, match="checklist validation failed"):
        checklist.validate_checklist(payload)


def test_forbidden_promoted_review_status_fails() -> None:
    payload = _valid_artifact()
    payload["review_status"] = "promoted"

    with pytest.raises(RuntimeError, match="checklist validation failed"):
        checklist.validate_checklist(payload)


def test_forbidden_review_text_containing_driver_id_fails() -> None:
    payload = _valid_artifact()
    payload["review_findings"] = [
        {"code": "raw_driver", "severity": "blocker", "summary": "The review text mentions driver_id."}
    ]

    with pytest.raises(RuntimeError, match="checklist validation failed"):
        checklist.validate_checklist(payload)


def test_forbidden_review_text_claiming_fundable_fails() -> None:
    payload = _valid_artifact()
    payload["review_findings"] = [
        {"code": "bad_claim", "severity": "blocker", "summary": "This lane is fundable."}
    ]

    with pytest.raises(RuntimeError, match="checklist validation failed"):
        checklist.validate_checklist(payload)


def test_checklist_success_marker_is_printed_for_valid_artifact(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    artifact_path = tmp_path / "review.json"
    artifact_path.write_text(json.dumps(_valid_artifact(), indent=2, sort_keys=True), encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["validate_stage2_promotion_review_checklist.py", "--artifact", str(artifact_path)])
    checklist.main()

    out = capsys.readouterr().out
    assert "STAGE2_PROMOTION_REVIEW_CHECKLIST_OK" in out
    assert "checklist_ready_for_review_not_promoted" in out


def test_checklist_failure_output_includes_field_bad_value_and_reason(capsys: pytest.CaptureFixture[str]) -> None:
    payload = _valid_artifact()
    payload["review_status"] = "promoted"

    with pytest.raises(RuntimeError, match="checklist validation failed"):
        checklist.validate_checklist(payload)

    out = capsys.readouterr().out
    assert "STAGE2_PROMOTION_REVIEW_CHECKLIST_FINDING" in out
    assert "field=review_status" in out
    assert "value='promoted'" in out
    assert "reason=forbidden promotional status" in out
