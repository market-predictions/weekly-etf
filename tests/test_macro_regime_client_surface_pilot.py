from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.render_macro_regime_client_surface_pilot import build_macro_regime_client_surface_pilot
from tools.validate_macro_regime_client_surface_pilot import validate_macro_regime_client_surface_pilot
from tools.validate_macro_narrative_client_surface import validate as validate_wp2_client_surface


def _shadow_payload() -> dict:
    return {
        "schema_version": "macro_regime_shadow_narrative_v1",
        "artifact_type": "macro_regime_shadow_narrative_comparison",
        "run_id": "20260605_000000",
        "report_date": "2026-06-05",
        "current_macro_narrative": {
            "en": {
                "status": "found",
                "language": "en",
                "text": "## 1. Executive Summary\n- **Primary regime:** Risk-on growth\n\n## 3. Regime Dashboard\n- Current regime: Risk-on growth.\n- Confidence: 66%.",
            },
            "nl": {
                "status": "found",
                "language": "nl",
                "text": "## 1. Kernsamenvatting\n- **Primair regime:** Risk-on groei\n\n## 3. Regime-dashboard\n- Huidig regime: Risk-on groei.\n- Vertrouwen: 66%.",
            },
        },
        "deterministic_regime_shadow_narrative_candidate": {
            "en": "The deterministic shadow candidate classifies the regime as **Risk-on narrow leadership** with confidence **72%.",
            "nl": "De deterministische shadow-kandidaat classificeert het regime als **Risk-on narrow leadership** met vertrouwen **72%.",
        },
    }


def _write_payload(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "pilot.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def test_builds_required_non_authoritative_pilot_fields() -> None:
    payload = build_macro_regime_client_surface_pilot(
        shadow_payload=_shadow_payload(),
        shadow_narrative_artifact_path="output/macro/shadow_narrative/macro_regime_shadow_narrative_20260605_000000.json",
        created_at_utc="2026-06-05T00:00:00Z",
    )

    assert payload["current_macro_narrative_en"]
    assert payload["current_macro_narrative_nl"]
    assert payload["deterministic_macro_candidate_en"]
    assert payload["deterministic_macro_candidate_nl"]
    assert payload["wp2_validation_status"] == "passed"
    assert payload["wp3_promotion_status"] == "not_promoted"
    assert payload["client_surface_pilot"] is True
    assert payload["production_report_narrative_authority"] is False
    assert payload["portfolio_action_authority"] is False
    assert payload["lane_scoring_authority"] is False
    assert payload["fundability_authority"] is False
    assert payload["funding_authority"] is False
    assert payload["portfolio_mutation"] is False


def test_pilot_passes_pilot_validator_and_wp2_client_surface_gate(tmp_path: Path) -> None:
    payload = build_macro_regime_client_surface_pilot(
        shadow_payload=_shadow_payload(),
        shadow_narrative_artifact_path="output/macro/shadow_narrative/macro_regime_shadow_narrative_20260605_000000.json",
        created_at_utc="2026-06-05T00:00:00Z",
    )
    path = _write_payload(tmp_path, payload)

    validate_macro_regime_client_surface_pilot(path)
    validate_wp2_client_surface(path)


@pytest.mark.parametrize(
    ("field", "value", "expected_error"),
    [
        ("wp3_promotion_status", "promoted_to_report_narrative_authority", "wp3_promotion_status"),
        ("production_report_narrative_authority", True, "production_report_narrative_authority"),
        ("portfolio_action_authority", True, "portfolio_action_authority"),
        ("lane_scoring_authority", True, "lane_scoring_authority"),
        ("fundability_authority", True, "fundability_authority"),
        ("funding_authority", True, "funding_authority"),
        ("portfolio_mutation", True, "portfolio_mutation"),
    ],
)
def test_pilot_rejects_any_authority_promotion(tmp_path: Path, field: str, value: object, expected_error: str) -> None:
    payload = build_macro_regime_client_surface_pilot(
        shadow_payload=_shadow_payload(),
        shadow_narrative_artifact_path="output/macro/shadow_narrative/macro_regime_shadow_narrative_20260605_000000.json",
        created_at_utc="2026-06-05T00:00:00Z",
    )
    payload[field] = value
    path = _write_payload(tmp_path, payload)

    with pytest.raises(RuntimeError, match=expected_error):
        validate_macro_regime_client_surface_pilot(path)


def test_pilot_rejects_missing_wp1_input_path(tmp_path: Path) -> None:
    payload = build_macro_regime_client_surface_pilot(
        shadow_payload=_shadow_payload(),
        shadow_narrative_artifact_path="output/macro/shadow_narrative/macro_regime_shadow_narrative_20260605_000000.json",
        created_at_utc="2026-06-05T00:00:00Z",
    )
    payload["inputs"]["wp1_shadow_narrative_artifact_path"] = ""
    path = _write_payload(tmp_path, payload)

    with pytest.raises(RuntimeError, match="wp1_shadow_narrative_artifact_path"):
        validate_macro_regime_client_surface_pilot(path)
