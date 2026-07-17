from __future__ import annotations

import json
from pathlib import Path

from runtime.macro_report_surface import (
    dashboard_en,
    dashboard_nl,
    deterministic_regime_surface_dto,
)
from tools.validate_deterministic_regime_client_surface import validate_surface_payload

VALIDATION = Path("output/macro/validation/latest_macro_regime_shadow_validation.json")
COMPARISON = Path("output/macro/validation/latest_macro_regime_shadow_comparison.json")


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _state() -> dict:
    return {
        "macro_policy_pack": {
            "regime": {
                "current": "Risk-on growth",
                "confidence": 0.66,
                "what_changed": ["AI and semiconductor leadership remains the dominant equity impulse."],
            },
            "regime_memory": {
                "decision_rule": "Macro status informs selectivity; it does not override pricing, risk or portfolio-discipline gates.",
                "report_transfer": {"summary": "Risk-on growth has persisted for 3 run(s); transition state is stable, breadth is mixed, and cross-asset confirmation is mixed."},
            },
            "portfolio_implications": ["Portfolio actions still require pricing, relative strength and position discipline."],
        },
        "deterministic_regime_shadow_validation": _json(VALIDATION),
        "deterministic_regime_shadow_comparison": _json(COMPARISON),
    }


def test_report_surface_includes_client_safe_supplementary_regime_en_and_nl() -> None:
    state = _state()

    en = dashboard_en(state)
    nl = dashboard_nl(state)

    assert "Supplementary regime cross-check" in en
    assert "Aanvullende regimecontrole" in nl
    assert "This supplementary check does not change portfolio actions" in en
    assert "Deze aanvullende controle verandert de portefeuilleacties niet" in nl


def test_report_surface_dto_passes_validator() -> None:
    dto = deterministic_regime_surface_dto(_state())

    assert dto is not None
    result = validate_surface_payload(dto)
    assert result["status"] == "passed"


def test_report_surface_does_not_leak_raw_or_internal_terms() -> None:
    state = _state()
    text = dashboard_en(state) + "\n" + dashboard_nl(state)

    for blocked in [
        "macro_axes",
        "macro_axis_scores",
        "macro_evidence",
        "confidence_decomposition",
        "workflow_run_id",
        "commit_sha",
        "output/macro/validation",
        ".json",
        "shadow engine",
        "shadow-engine",
        "review-only",
        "alleen ter review",
        "legacy regime read",
    ]:
        assert blocked not in text.lower()


def test_deterministic_confidence_is_banded_not_numeric() -> None:
    state = _state()
    dto = deterministic_regime_surface_dto(state)

    assert dto is not None
    assert dto["confidence_band_en"] == "high"
    assert dto["confidence_band_nl"] == "hoog"
    assert "0.72" not in dto["safe_surface_en"]
    assert "72%" not in dto["safe_surface_en"]
    assert "0.72" not in dto["safe_surface_nl"]
    assert "72%" not in dto["safe_surface_nl"]


def test_supplementary_surface_has_clean_client_facing_punctuation() -> None:
    dto = deterministic_regime_surface_dto(_state())

    assert dto is not None
    assert ".;" not in dto["safe_surface_en"]
    assert ".;" not in dto["safe_surface_nl"]
    assert "actions. Pricing, relative strength and position discipline remain decisive." in dto["safe_surface_en"]
    assert "portefeuilleacties niet. Prijsbasis, relatieve sterkte en positiediscipline blijven leidend." in dto["safe_surface_nl"]


def test_primary_macro_regime_remains_present_and_supplementary_surface_is_additive() -> None:
    state = _state()
    en = dashboard_en(state)
    nl = dashboard_nl(state)

    assert "- Current regime: Risk-on growth." in en
    assert "- Confidence: 66%." in en
    assert "- Huidig regime: Risk-on groei." in nl
    assert "- Vertrouwen: 66%." in nl
