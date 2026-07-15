from __future__ import annotations

import pytest

from runtime.post_execution_report_surface import (
    action_buckets,
    decision_cockpit_en,
    decision_cockpit_nl,
    main_takeaway_en,
    main_takeaway_nl,
    position_action_label_en,
    position_action_label_nl,
    rotation_plan_table_en,
    rotation_plan_table_nl,
    validate_post_execution_report_consistency,
)
from runtime.render_etf_report_from_state import final_action_table
from runtime.render_etf_report_nl_from_state import final_action_table_nl


def state() -> dict:
    return {
        "positions": [
            {
                "ticker": "SMH",
                "suggested_action": "hold",
                "existing_new": "Existing",
                "weight_inherited_pct": 29.0,
                "target_weight_pct": 29.0,
                "conviction_tier": "Tier 1",
                "total_score": 4.8,
                "portfolio_role": "Growth engine",
                "better_alternative_exists": "No",
                "short_reason": "Core holding.",
            },
            {
                "ticker": "URNM",
                "suggested_action": "hold",
                "rotation_action_code": "replace_partial",
                "existing_new": "Existing",
                "weight_inherited_pct": 7.01,
                "target_weight_pct": 2.01,
                "conviction_tier": "Tier 3",
                "total_score": 3.7,
                "portfolio_role": "Strategic energy",
                "better_alternative_exists": "No",
                "short_reason": "Reduced after failed re-underwriting.",
            },
            {
                "ticker": "XBI",
                "suggested_action": "Add",
                "existing_new": "New",
                "weight_inherited_pct": 0.0,
                "target_weight_pct": 5.0,
                "conviction_tier": "Tier 2",
                "total_score": 4.36,
                "portfolio_role": "Rotation destination",
                "better_alternative_exists": "No",
                "short_reason": "Added as rotation destination.",
            },
        ],
        "executed_model_changes": [
            {
                "ticker": "URNM",
                "action": "Sell",
                "shares_delta": -105.862854,
                "previous_weight_pct": 7.01,
                "new_weight_pct": 2.01,
                "weight_change_pct": -5.0,
                "target_weight_pct": 2.01,
            },
            {
                "ticker": "XBI",
                "action": "Buy",
                "shares_delta": 35.634001,
                "previous_weight_pct": 0.0,
                "new_weight_pct": 5.0,
                "weight_change_pct": 5.0,
                "target_weight_pct": 5.0,
            },
        ],
        "portfolio": {"cash_eur": 1936.52, "total_portfolio_value_eur": 110224.85},
        "execution_context": {"report_phase": "post_execution", "execution_status": "executed"},
        "validation_flags": {"post_execution_report": True},
    }


def _english_report() -> str:
    current = state()
    return f"""## 1. Executive Summary

- **Main takeaway:** **{main_takeaway_en(current)}**

## 2. Portfolio Action Snapshot

### Add — executed
- XBI

### Reduce — executed
- URNM

### Close — executed
- None

### Decision cockpit

{decision_cockpit_en(current)}

## 3. Regime Dashboard

## 12. Portfolio Rotation Plan

{rotation_plan_table_en(current)}

## 13. Final Action Table

{final_action_table(current)}

## 14. Position Changes Reflected in Official State
"""


def _dutch_report() -> str:
    current = state()
    return f"""## 1. Kernsamenvatting

- **Belangrijkste conclusie:** {main_takeaway_nl(current)}

## 2. Portefeuille-acties

| Advies | Tickers / toelichting |
|---|---|
| Toevoegen | XBI |
| Aanhouden | SMH |
| Verlagen | URNM |
| Sluiten | Geen |

{decision_cockpit_nl(current)}

## 3. Regime-dashboard

## 12. Rotatieplan portefeuille

{rotation_plan_table_nl(current)}

## 13. Definitieve actietabel

{final_action_table_nl(current)}

## 14. Positiewijzigingen verwerkt in de officiële portefeuillestaat
"""


def test_action_buckets_exclude_changed_positions_from_hold() -> None:
    buckets = action_buckets(state())
    assert buckets["reduce"] == ["URNM"]
    assert buckets["add"] == ["XBI"]
    assert buckets["hold"] == ["SMH"]


def test_executed_action_labels_override_stale_suggested_action() -> None:
    current = state()
    urnm = next(row for row in current["positions"] if row["ticker"] == "URNM")
    xbi = next(row for row in current["positions"] if row["ticker"] == "XBI")
    assert position_action_label_en(urnm, current) == "Reduce — executed"
    assert position_action_label_en(xbi, current) == "Add — executed"
    assert position_action_label_nl(urnm, current) == "Verlagen — uitgevoerd"
    assert position_action_label_nl(xbi, current) == "Toevoegen — uitgevoerd"


def test_dynamic_takeaway_and_cockpit_describe_execution() -> None:
    current = state()
    assert "reduced URNM" in main_takeaway_en(current)
    assert "added XBI" in main_takeaway_en(current)
    assert "URNM werd verlaagd" in main_takeaway_nl(current)
    assert "XBI werd toegevoegd" in main_takeaway_nl(current)
    assert "executed and persisted" in decision_cockpit_en(current)
    assert "uitgevoerd en verwerkt" in decision_cockpit_nl(current)


def test_final_action_tables_use_executed_labels() -> None:
    current = state()
    english = final_action_table(current)
    dutch = final_action_table_nl(current)
    urnm_en = next(line for line in english.splitlines() if line.startswith("| URNM |"))
    xbi_en = next(line for line in english.splitlines() if line.startswith("| XBI |"))
    urnm_nl = next(line for line in dutch.splitlines() if line.startswith("| URNM |"))
    xbi_nl = next(line for line in dutch.splitlines() if line.startswith("| XBI |"))
    assert "Reduce — executed" in urnm_en
    assert "Add — executed" in xbi_en
    assert "Verlagen — uitgevoerd" in urnm_nl
    assert "Toevoegen — uitgevoerd" in xbi_nl


def test_consistency_validator_accepts_coherent_english_and_dutch() -> None:
    current = state()
    validate_post_execution_report_consistency(_english_report(), current, language="en")
    validate_post_execution_report_consistency(_dutch_report(), current, language="nl")


def test_consistency_validator_rejects_no_action_wording() -> None:
    current = state()
    defective = _english_report().replace(
        "Guarded model rotation executed and persisted", "No portfolio action"
    )
    with pytest.raises(RuntimeError, match="forbidden_no_action_phrase"):
        validate_post_execution_report_consistency(defective, current, language="en")


def test_consistency_validator_rejects_wrong_action_bucket() -> None:
    current = state()
    defective = _dutch_report().replace("| Verlagen | URNM |", "| Verlagen | Geen |")
    with pytest.raises(RuntimeError, match="action_snapshot_mismatch:URNM:reduce"):
        validate_post_execution_report_consistency(defective, current, language="nl")


def test_consistency_validator_accepts_linkified_final_action_tickers() -> None:
    current = state()
    linked = _english_report().replace(
        "| URNM | URNM |",
        "| [URNM](https://www.tradingview.com/chart/?symbol=URNM) | URNM |",
    ).replace(
        "| XBI | XBI |",
        "| [XBI](https://www.tradingview.com/chart/?symbol=XBI) | XBI |",
    )
    validate_post_execution_report_consistency(linked, current, language="en")
