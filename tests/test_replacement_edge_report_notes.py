from runtime.polish_runtime_reports import polish_dutch, polish_english
from runtime.fix_report_output_contract import action_snapshot_section
from runtime.replacement_edge_report_notes import (
    EN_AUTHORITY_DISCLAIMER,
    MARKER,
    NL_AUTHORITY_DISCLAIMER,
    replacement_edge_notes_markdown,
)


def _payload():
    return {
        "diagnostic_only": True,
        "portfolio_action_authority": False,
        "fundability_authority": False,
        "lane_scoring_authority": False,
        "funding_authority": False,
        "production_recommendation_authority": False,
        "execution_authority": False,
        "portfolio_mutation": False,
        "edges": [
            {
                "current_holding": "SPY",
                "challenger": "QUAL",
                "1m_relative_strength_edge": 3.0,
                "3m_relative_strength_edge": 5.0,
                "drawdown_edge": 2.0,
                "volatility_edge": 2.0,
                "replacement_edge_score": 0.23,
                "diagnostic_only": True,
                "portfolio_action_authority": False,
                "fundability_authority": False,
                "lane_scoring_authority": False,
            }
        ],
    }


def test_replacement_edge_notes_markdown_is_explicitly_diagnostic_only_en():
    md = replacement_edge_notes_markdown(_payload(), language="en")

    assert MARKER in md
    assert "Diagnostic-only" in md
    assert EN_AUTHORITY_DISCLAIMER in md
    assert "allocation authority" in md
    assert "fundability authority" in md
    assert "lane-scoring authority" in md
    assert "production recommendation authority" in md
    assert "execution authority" in md
    assert "portfolio mutation authority" in md
    assert "SPY" in md
    assert "QUAL" in md
    assert "+0.23" in md
    assert "+5.00%" in md


def test_replacement_edge_notes_markdown_is_explicitly_diagnostic_only_nl():
    md = replacement_edge_notes_markdown(_payload(), language="nl")

    assert MARKER in md
    assert "Diagnostisch-only" in md
    assert NL_AUTHORITY_DISCLAIMER in md
    assert "allocatiebevoegdheid" in md
    assert "fundability-bevoegdheid" in md
    assert "lane-scoring-bevoegdheid" in md
    assert "productie-aanbevelingsbevoegdheid" in md
    assert "uitvoeringsbevoegdheid" in md
    assert "portefeuillemutatiebevoegdheid" in md
    assert "SPY" in md
    assert "QUAL" in md
    assert "+0.23" in md


def test_replacement_edge_notes_empty_state_has_safe_fallback():
    md = replacement_edge_notes_markdown({"edges": []}, language="en")

    assert MARKER in md
    assert "No replacement-edge diagnostics available this run" in md


def test_replacement_edge_notes_are_inserted_into_english_polish_output():
    text = """# Weekly ETF Pro Review 2026-06-04

## 11. Best New Opportunities

### Replacement Duel Table v2

| Current holding | Challenger |
|---|---|
| SPY | QUAL |

## 12. Portfolio Rotation Plan

| Close | Hold |
|---|---|
| None | SPY |
"""
    out = polish_english(text, {"source_files": {}, "macro_policy_pack": {}})

    assert MARKER in out
    assert EN_AUTHORITY_DISCLAIMER in out
    assert out.index("Replacement Duel Table") < out.index(MARKER) < out.index("## 12. Portfolio Rotation Plan")


def test_replacement_edge_notes_are_inserted_into_dutch_polish_output():
    text = """# Wekelijkse ETF-review 4 juni 2026

## 11. Beste nieuwe kansen

### Vervangingsanalyse

| Huidige positie | Alternatief |
|---|---|
| SPY | QUAL |

## 12. Rotatieplan portefeuille

| Sluiten | Aanhouden |
|---|---|
| Geen | SPY |
"""
    out = polish_dutch(text, {"source_files": {}, "macro_policy_pack": {}})

    assert MARKER in out
    assert NL_AUTHORITY_DISCLAIMER in out
    assert out.index("### Vervangingsanalyse") < out.index(MARKER) < out.index("## 12. Rotatieplan portefeuille")


def test_output_contract_fix_keeps_english_replacement_edge_notes():
    out = action_snapshot_section({"positions": []})

    assert MARKER in out
    assert EN_AUTHORITY_DISCLAIMER in out
    assert out.index("### Replacement pricing and duel status") < out.index(MARKER)


def test_replacement_edge_notes_do_not_promote_authority_fields():
    payload = _payload()

    assert payload["diagnostic_only"] is True
    assert payload["portfolio_action_authority"] is False
    assert payload["fundability_authority"] is False
    assert payload["lane_scoring_authority"] is False
    assert payload["funding_authority"] is False
    assert payload["production_recommendation_authority"] is False
    assert payload["execution_authority"] is False
    assert payload["portfolio_mutation"] is False
