import json
from pathlib import Path

import pytest

from runtime.render_macro_regime_shadow_narrative import (
    build_macro_regime_shadow_narrative,
    write_macro_regime_shadow_narrative,
)
from tools.validate_macro_regime_shadow_narrative import validate_macro_regime_shadow_narrative


def _shadow_validation_payload():
    return {
        "artifact_type": "macro_regime_shadow_validation_evidence",
        "shadow_summary": {
            "candidate_regime": "Risk-on narrow leadership",
            "candidate_confidence": 0.72,
            "legacy_regime": "Risk-on growth",
            "legacy_confidence": 0.66,
            "method": "deterministic_axis_classifier_v1_shadow",
            "differs_from_legacy": True,
            "axes": {"equity": "risk_on", "breadth": "narrow"},
            "macro_axes": {"volatility": "calm", "policy_rate": "restrictive"},
            "macro_axis_scores": {"vix_close": 14.8, "fed_funds_effective": 5.33},
            "what_changed": ["Semiconductor leadership is strong, but breadth remains narrow."],
        },
    }


def test_macro_regime_shadow_narrative_artifact_is_valid(tmp_path: Path):
    current_en = """# Weekly ETF Pro Review

## 1. Executive Summary
- **Primary regime:** Risk-on growth

## 3. Regime Dashboard
### Macro regime
- Current regime: Risk-on growth.
- Confidence: 66%.

## 4. Other
Text.
"""
    current_nl = """# Wekelijkse ETF-review

## 1. Kernsamenvatting
- **Primair regime:** Risk-on groei

## 3. Regime-dashboard
### Regimesamenvatting
- Huidig regime: Risk-on groei.
- Vertrouwen: 66%.

## 4. Overig
Tekst.
"""
    artifact = build_macro_regime_shadow_narrative(
        run_id="20260605_000000",
        report_date="2026-06-05",
        current_report_en_text=current_en,
        current_report_nl_text=current_nl,
        macro_regime_payload=_shadow_validation_payload(),
        created_at_utc="2026-06-05T00:00:00Z",
    )
    path = tmp_path / "macro_regime_shadow_narrative_20260605_000000.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")

    validate_macro_regime_shadow_narrative(path)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "macro_regime_shadow_narrative_v1"
    assert payload["status"] == "shadow_candidate_only"
    assert payload["shadow_only"] is True
    assert payload["client_facing"] is False
    assert payload["production_report"] is False
    assert payload["portfolio_action_authority"] is False
    assert payload["lane_scoring_authority"] is False
    assert payload["fundability_authority"] is False
    assert payload["current_macro_narrative"]["en"]["status"] == "found"
    assert "Risk-on narrow leadership" in payload["deterministic_regime_shadow_narrative_candidate"]["en"]
    assert "SHADOW-ONLY" in payload["comparison_markdown"]


def test_write_macro_regime_shadow_narrative_compares_report_files_and_shadow_file(tmp_path: Path):
    report_en = tmp_path / "weekly_analysis_pro_260605.md"
    report_nl = tmp_path / "weekly_analysis_pro_nl_260605.md"
    shadow = tmp_path / "latest_macro_regime_shadow_validation.json"
    report_en.write_text(
        "## 1. Executive Summary\n- **Primary regime:** Risk-on growth\n\n## 3. Regime Dashboard\n- Current regime: Risk-on growth.\n\n## 4. Other\n",
        encoding="utf-8",
    )
    report_nl.write_text(
        "## 1. Kernsamenvatting\n- **Primair regime:** Risk-on groei\n\n## 3. Regime-dashboard\n- Huidig regime: Risk-on groei.\n\n## 4. Overig\n",
        encoding="utf-8",
    )
    shadow.write_text(json.dumps(_shadow_validation_payload()), encoding="utf-8")

    path = write_macro_regime_shadow_narrative(
        tmp_path / "output",
        run_id="20260605_010203",
        report_date="2026-06-05",
        current_report_en_path=report_en,
        current_report_nl_path=report_nl,
        macro_regime_artifact_path=shadow,
        created_at_utc="2026-06-05T01:02:03Z",
    )

    validate_macro_regime_shadow_narrative(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert path.name == "macro_regime_shadow_narrative_20260605_010203.json"
    assert payload["inputs"]["current_report_en_path"] == str(report_en)
    assert payload["inputs"]["macro_regime_artifact_path"] == str(shadow)
    assert "Risk-on narrow leadership" in payload["deterministic_regime_shadow_narrative_candidate"]["en"]
    assert "Huidig regime" in payload["comparison_markdown"]


def test_macro_regime_shadow_narrative_rejects_authority_escalation(tmp_path: Path):
    artifact = build_macro_regime_shadow_narrative(
        run_id="20260605_000000",
        report_date="2026-06-05",
        macro_regime_payload=_shadow_validation_payload(),
        created_at_utc="2026-06-05T00:00:00Z",
    )
    artifact["portfolio_action_authority"] = True
    path = tmp_path / "bad_macro_regime_shadow_narrative.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")

    with pytest.raises(RuntimeError, match="portfolio_action_authority must remain false"):
        validate_macro_regime_shadow_narrative(path)


def test_macro_regime_shadow_narrative_rejects_candidate_without_shadow_label(tmp_path: Path):
    artifact = build_macro_regime_shadow_narrative(
        run_id="20260605_000000",
        report_date="2026-06-05",
        macro_regime_payload=_shadow_validation_payload(),
        created_at_utc="2026-06-05T00:00:00Z",
    )
    artifact["deterministic_regime_shadow_narrative_candidate"]["en"] = "Production-ready macro text."
    path = tmp_path / "bad_macro_regime_shadow_narrative.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")

    with pytest.raises(RuntimeError, match="candidate must clearly state SHADOW-ONLY"):
        validate_macro_regime_shadow_narrative(path)
