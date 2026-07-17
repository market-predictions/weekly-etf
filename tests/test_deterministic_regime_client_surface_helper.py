from __future__ import annotations

import json
from pathlib import Path

from runtime.deterministic_regime_client_surface import (
    build_deterministic_regime_client_surface,
    confidence_band_en,
    confidence_band_nl,
    render_deterministic_regime_surface_en,
    render_deterministic_regime_surface_nl,
)
from tools.validate_deterministic_regime_client_surface import validate_surface_payload

VALIDATION = Path("output/macro/validation/latest_macro_regime_shadow_validation.json")
COMPARISON = Path("output/macro/validation/latest_macro_regime_shadow_comparison.json")

RAW_BLOCKED_KEYS = {
    "deterministic_regime_shadow",
    "macro_axes",
    "macro_axis_scores",
    "macro_evidence",
    "confidence_decomposition",
    "confidence_components",
    "workflow",
    "workflow_run_id",
    "workflow_run_number",
    "commit_sha",
}


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _dto() -> dict:
    return build_deterministic_regime_client_surface(
        validation_evidence=_json(VALIDATION),
        comparison_evidence=_json(COMPARISON),
        source_evidence_path=str(VALIDATION),
        source_comparison_path=str(COMPARISON),
    )


def test_confidence_band_boundaries() -> None:
    assert confidence_band_en(0.54) == "low"
    assert confidence_band_en(0.55) == "moderate"
    assert confidence_band_en(0.71) == "moderate"
    assert confidence_band_en(0.72) == "high"
    assert confidence_band_nl(0.54) == "laag"
    assert confidence_band_nl(0.55) == "gemiddeld"
    assert confidence_band_nl(0.72) == "hoog"


def test_build_surface_from_latest_shadow_evidence_passes_validator() -> None:
    dto = _dto()
    result = validate_surface_payload(dto)

    assert result["status"] == "passed"
    assert dto["surface_mode"] == "helper_only"
    assert dto["regime_label_en"] == "Risk-on growth"
    assert dto["regime_label_nl"] == "Risk-on groei"


def test_helper_does_not_copy_raw_shadow_fields_into_dto() -> None:
    dto = _dto()

    for key in RAW_BLOCKED_KEYS:
        assert key not in dto


def test_helper_does_not_leak_raw_or_internal_terms_into_safe_text() -> None:
    dto = _dto()
    text = dto["safe_surface_en"] + "\n" + dto["safe_surface_nl"]

    for term in [
        "macro_axes",
        "macro_axis_scores",
        "macro_evidence",
        "confidence_decomposition",
        "output/macro",
        ".json",
        "shadow engine",
        "shadow-engine",
        "review-only",
        "alleen ter review",
        "legacy regime read",
    ]:
        assert term not in text.lower()


def test_render_functions_are_deterministic_for_same_dto() -> None:
    dto = _dto()

    assert render_deterministic_regime_surface_en(dto) == dto["safe_surface_en"]
    assert render_deterministic_regime_surface_nl(dto) == dto["safe_surface_nl"]
    assert render_deterministic_regime_surface_en(dto) == render_deterministic_regime_surface_en(dto)
    assert render_deterministic_regime_surface_nl(dto) == render_deterministic_regime_surface_nl(dto)


def test_authority_fields_remain_false() -> None:
    dto = _dto()

    assert dto["client_facing_authority"] is False
    assert dto["production_report_narrative_authority"] is False
    assert dto["portfolio_action_authority"] is False
    assert dto["lane_scoring_authority"] is False
    assert dto["fundability_authority"] is False
    assert dto["portfolio_mutation"] is False
