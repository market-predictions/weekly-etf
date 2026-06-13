from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tools.validate_deterministic_regime_client_surface import validate_surface_payload

FIXTURE = Path("fixtures/deterministic_regime_client_surface/safe_surface_fixture.json")


def _payload() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_safe_surface_fixture_passes() -> None:
    result = validate_surface_payload(_payload())

    assert result["status"] == "passed"
    assert result["regime_label_en"] == "Risk-on growth"
    assert result["regime_label_nl"] == "Risk-on groei"


def test_rejects_raw_macro_axes_in_surface_text() -> None:
    payload = _payload()
    payload["safe_surface_en"] += " macro_axes are visible here."

    with pytest.raises(RuntimeError, match="raw_macro_axes"):
        validate_surface_payload(payload)


def test_rejects_json_path_in_surface_text() -> None:
    payload = _payload()
    payload["safe_surface_en"] += " See output/macro/latest.json."

    with pytest.raises(RuntimeError, match="source_path"):
        validate_surface_payload(payload)


def test_rejects_numeric_confidence_precision() -> None:
    payload = _payload()
    payload["safe_surface_en"] = payload["safe_surface_en"].replace(
        "Confidence is high but review-only",
        "Confidence 82% is high but review-only",
    )

    with pytest.raises(RuntimeError, match="numeric_confidence"):
        validate_surface_payload(payload)


def test_rejects_positive_authority_field() -> None:
    payload = _payload()
    payload["portfolio_action_authority"] = True

    with pytest.raises(RuntimeError, match="portfolio_action_authority must be false"):
        validate_surface_payload(payload)


def test_rejects_missing_review_only_disclaimer() -> None:
    payload = _payload()
    payload["safe_surface_nl"] = payload["safe_surface_nl"].replace("alleen ter review", "ter informatie")
    payload["confidence_band_nl"] = "hoog maar ter informatie"

    with pytest.raises(RuntimeError, match="alleen ter review"):
        validate_surface_payload(payload)


def test_rejects_full_shadow_payload_field_name() -> None:
    payload = _payload()
    broken = copy.deepcopy(payload)
    broken["safe_surface_en"] += " deterministic_regime_shadow appears here."

    with pytest.raises(RuntimeError, match="raw_shadow_payload"):
        validate_surface_payload(broken)
