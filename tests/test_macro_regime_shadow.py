from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import yaml

from macro_regime.classify import classify_regime_shadow
from tools.replay_macro_regime_shadow_fixtures import replay
from tools.validate_macro_regime_shadow import REQUIRED_FALSE_AUTHORITY_FIELDS, validate_shadow_payload

FIXTURES = Path("fixtures/macro_regime_shadow/regime_shadow_fixtures.json")
THRESHOLDS = Path("config/regime_thresholds.yml")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def test_macro_regime_shadow_fixture_replay_covers_all_threshold_regimes() -> None:
    results = replay(FIXTURES, THRESHOLDS)
    thresholds = _load_yaml(THRESHOLDS)
    expected_regimes = {rule["label"] for rule in thresholds["regime_rules"].values() if "label" in rule}
    covered_regimes = {result["candidate_regime"] for result in results}

    assert expected_regimes <= covered_regimes
    assert len(results) >= len(expected_regimes)


def test_macro_regime_shadow_fixtures_deny_all_production_authority() -> None:
    payload = _load_json(FIXTURES)

    assert payload["status"] == "shadow_only"
    assert payload["decision_impact"] == "none_shadow_comparison_only"
    for field in REQUIRED_FALSE_AUTHORITY_FIELDS:
        assert field in payload
        assert payload[field] is False


def test_macro_regime_shadow_payload_contains_required_no_authority_fields() -> None:
    fixture = _load_json(FIXTURES)["fixtures"][0]
    result = classify_regime_shadow(
        metrics=fixture["metrics"],
        macro_data_audit_summary={"present": False},
        thresholds=_load_yaml(THRESHOLDS),
        legacy_regime="Legacy comparison placeholder",
        legacy_confidence=0.50,
    )

    validated = validate_shadow_payload(result)

    assert validated["candidate_regime"] == fixture["expected_regime"]
    for field in REQUIRED_FALSE_AUTHORITY_FIELDS:
        assert result[field] is False


def test_macro_regime_shadow_validator_rejects_missing_authority_field() -> None:
    fixture = _load_json(FIXTURES)["fixtures"][0]
    result = classify_regime_shadow(
        metrics=fixture["metrics"],
        macro_data_audit_summary={"present": False},
        thresholds=_load_yaml(THRESHOLDS),
        legacy_regime="Legacy comparison placeholder",
        legacy_confidence=0.50,
    )
    broken = copy.deepcopy(result)
    broken.pop("portfolio_action_authority")

    with pytest.raises(RuntimeError, match="portfolio_action_authority"):
        validate_shadow_payload(broken)


def test_macro_regime_shadow_validator_rejects_macro_axes_without_macro_audit_component() -> None:
    fixture = _load_json(FIXTURES)["fixtures"][0]
    result = classify_regime_shadow(
        metrics=fixture["metrics"],
        macro_data_audit_summary={"present": False},
        thresholds=_load_yaml(THRESHOLDS),
        legacy_regime="Legacy comparison placeholder",
        legacy_confidence=0.50,
    )
    broken = copy.deepcopy(result)
    broken["macro_axes"] = {"volatility": "calm"}
    broken["macro_axis_scores"] = {"vix_close": 12.0}

    with pytest.raises(RuntimeError, match="macro_audit_present"):
        validate_shadow_payload(broken)
