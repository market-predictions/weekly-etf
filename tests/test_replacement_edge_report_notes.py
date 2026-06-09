from runtime.replacement_edge_report_notes import (
    MARKER,
    replacement_edge_notes_markdown,
)


def _payload():
    return {
        "diagnostic_only": True,
        "portfolio_action_authority": False,
        "fundability_authority": False,
        "lane_scoring_authority": False,
        "production_recommendation_authority": False,
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
    assert "no allocation, fundability, scoring, recommendation or execution authority" in md
    assert "SPY" in md
    assert "QUAL" in md
    assert "+0.23" in md
    assert "+5.00%" in md


def test_replacement_edge_notes_markdown_is_explicitly_diagnostic_only_nl():
    md = replacement_edge_notes_markdown(_payload(), language="nl")

    assert MARKER in md
    assert "Diagnostisch-only" in md
    assert "geen allocatie-, fundability-, score-, aanbevelings- of uitvoeringsbevoegdheid" in md
    assert "SPY" in md
    assert "QUAL" in md
    assert "+0.23" in md


def test_replacement_edge_notes_empty_state_has_safe_fallback():
    md = replacement_edge_notes_markdown({"edges": []}, language="en")

    assert MARKER in md
    assert "No replacement-edge diagnostics available this run" in md
