from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tools.validate_macro_data_audit import validate


FIXTURE = Path("tests/fixtures/macro_data_audit_fixture.json")


def _payload() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "macro_data_audit.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_wp18_macro_data_audit_fixture_passes_hardened_validator(tmp_path) -> None:
    path = _write(tmp_path, _payload())

    result = validate(path)

    assert result["mode"] == "fixture"
    assert result["observations"] == 4
    assert result["groups"] == ["ecb", "fred", "treasury_fiscaldata", "volatility"]


def test_wp18_macro_data_audit_requires_source_group_status(tmp_path) -> None:
    payload = _payload()
    payload["source_group_status"] = {"fred": "present"}
    path = _write(tmp_path, payload)

    with pytest.raises(RuntimeError, match="source_group_status"):
        validate(path)


def test_wp18_macro_data_audit_requires_live_source_url(tmp_path) -> None:
    payload = copy.deepcopy(_payload())
    payload["mode"] = "live"
    payload["observations"][0].pop("source_url", None)
    path = _write(tmp_path, payload)

    with pytest.raises(RuntimeError, match="source_url"):
        validate(path)


def test_wp18_macro_data_audit_requires_shadow_authority_wording(tmp_path) -> None:
    payload = _payload()
    payload["authority"]["decision_framework"] = "macro data can drive allocation authority"
    path = _write(tmp_path, payload)

    with pytest.raises(RuntimeError, match="allocation authority"):
        validate(path)
