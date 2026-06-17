from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import validate_stage2_promotion_review_decision_fixtures as fixture_validator
from tools import validate_stage2_promotion_review_decision_schema as decision_validator

PRODUCTION_MANIFEST = Path("fixtures/stage2_promotion_review_decision/manifest.json")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _synthetic_root(tmp_path: Path) -> Path:
    return tmp_path / "fixtures" / "stage2_promotion_review_decision"


def _synthetic_manifest(tmp_path: Path, entries: list[dict], *, authority: dict | None = None) -> Path:
    root = _synthetic_root(tmp_path)
    manifest = {
        "schema_version": "1.0",
        "fixture_set": "stage2_promotion_review_decision",
        "authority": authority or dict(fixture_validator.REQUIRED_MANIFEST_AUTHORITY),
        "fixtures": entries,
    }
    path = root / "manifest.json"
    _write_json(path, manifest)
    return path


def _synthetic_pass_fixture(tmp_path: Path, name: str = "pass.json") -> str:
    rel = f"fixtures/stage2_promotion_review_decision/{name}"
    _write_json(tmp_path / rel, decision_validator.valid_artifact())
    return rel


def _synthetic_fail_fixture(tmp_path: Path, name: str = "fail.json") -> str:
    rel = f"fixtures/stage2_promotion_review_decision/{name}"
    payload = decision_validator.valid_artifact()
    payload["decision_status"] = "promoted"
    _write_json(tmp_path / rel, payload)
    return rel


def test_production_fixture_manifest_validates() -> None:
    fixture_validator.validate_manifest_file(PRODUCTION_MANIFEST)


def test_all_production_pass_fixtures_pass() -> None:
    manifest = _load_json(PRODUCTION_MANIFEST)
    for entry in manifest["fixtures"]:
        if entry["expected"] == "pass":
            findings = fixture_validator._validate_pass_fixture(
                Path(entry["path"]), entry["path"], entry["expected_decision_status"]
            )
            assert findings == []


def test_all_production_fail_fixtures_fail_as_expected() -> None:
    manifest = _load_json(PRODUCTION_MANIFEST)
    for entry in manifest["fixtures"]:
        if entry["expected"] == "fail":
            findings = fixture_validator._validate_fail_fixture(
                Path(entry["path"]), entry["path"], entry["expected_failure_contains"]
            )
            assert findings == []


def test_valid_synthetic_manifest_passes(tmp_path: Path) -> None:
    fixture_rel = _synthetic_pass_fixture(tmp_path)
    manifest = _synthetic_manifest(
        tmp_path,
        [{"path": fixture_rel, "expected": "pass", "expected_decision_status": "not_promoted"}],
    )
    fixture_validator.validate_manifest_file(manifest)


def test_manifest_with_duplicate_fixture_path_fails(tmp_path: Path) -> None:
    fixture_rel = _synthetic_pass_fixture(tmp_path)
    manifest = _synthetic_manifest(
        tmp_path,
        [
            {"path": fixture_rel, "expected": "pass", "expected_decision_status": "not_promoted"},
            {"path": fixture_rel, "expected": "pass", "expected_decision_status": "not_promoted"},
        ],
    )
    with pytest.raises(RuntimeError, match="fixture validation failed"):
        fixture_validator.validate_manifest_file(manifest)


def test_manifest_referencing_output_fails(tmp_path: Path) -> None:
    manifest = _synthetic_manifest(
        tmp_path,
        [{"path": "output/stage2_decision.json", "expected": "pass", "expected_decision_status": "not_promoted"}],
    )
    with pytest.raises(RuntimeError, match="fixture validation failed"):
        fixture_validator.validate_manifest_file(manifest)


def test_manifest_with_unknown_expected_value_fails(tmp_path: Path) -> None:
    fixture_rel = _synthetic_pass_fixture(tmp_path)
    manifest = _synthetic_manifest(
        tmp_path,
        [{"path": fixture_rel, "expected": "maybe", "expected_decision_status": "not_promoted"}],
    )
    with pytest.raises(RuntimeError, match="fixture validation failed"):
        fixture_validator.validate_manifest_file(manifest)


def test_pass_fixture_with_wrong_expected_decision_status_fails(tmp_path: Path) -> None:
    fixture_rel = _synthetic_pass_fixture(tmp_path)
    manifest = _synthetic_manifest(
        tmp_path,
        [{"path": fixture_rel, "expected": "pass", "expected_decision_status": "blocked_missing_evidence"}],
    )
    with pytest.raises(RuntimeError, match="fixture validation failed"):
        fixture_validator.validate_manifest_file(manifest)


def test_missing_fixture_file_fails(tmp_path: Path) -> None:
    manifest = _synthetic_manifest(
        tmp_path,
        [{"path": "fixtures/stage2_promotion_review_decision/missing.json", "expected": "pass", "expected_decision_status": "not_promoted"}],
    )
    with pytest.raises(RuntimeError, match="fixture validation failed"):
        fixture_validator.validate_manifest_file(manifest)


def test_manifest_granting_authority_fails(tmp_path: Path) -> None:
    fixture_rel = _synthetic_pass_fixture(tmp_path)
    authority = copy.deepcopy(fixture_validator.REQUIRED_MANIFEST_AUTHORITY)
    authority["delivery_authority"] = True
    manifest = _synthetic_manifest(
        tmp_path,
        [{"path": fixture_rel, "expected": "pass", "expected_decision_status": "not_promoted"}],
        authority=authority,
    )
    with pytest.raises(RuntimeError, match="fixture validation failed"):
        fixture_validator.validate_manifest_file(manifest)


def test_fail_fixture_that_unexpectedly_passes_is_rejected(tmp_path: Path) -> None:
    fixture_rel = _synthetic_pass_fixture(tmp_path)
    manifest = _synthetic_manifest(
        tmp_path,
        [{"path": fixture_rel, "expected": "fail", "expected_failure_contains": "forbidden"}],
    )
    with pytest.raises(RuntimeError, match="fixture validation failed"):
        fixture_validator.validate_manifest_file(manifest)


def test_cli_prints_success_marker(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["validate_stage2_promotion_review_decision_fixtures.py"])
    fixture_validator.main()
    out = capsys.readouterr().out
    assert "STAGE2_PROMOTION_REVIEW_DECISION_FIXTURES_OK" in out
