from __future__ import annotations

from runtime.delivery_action_status_contract import (
    has_actual_execution,
    install,
)
from runtime import delivery_html_overrides as delivery


def zero_execution_state() -> dict:
    return {
        "positions": [
            {
                "ticker": "SMH",
                "shares_delta_this_run": 0.0,
                "action_executed_this_run": "None",
                "suggested_action": "Hold",
            }
        ],
        "executed_model_changes": [],
        "trade_intents": [],
        "execution_context": {"report_phase": "post_execution"},
        "validation_flags": {"post_execution_report": True},
    }


def executed_state() -> dict:
    return {
        "positions": [
            {
                "ticker": "URNM",
                "shares_delta_this_run": -10.0,
                "action_executed_this_run": "Sell",
                "suggested_action": "Reduce",
            }
        ],
        "executed_model_changes": [
            {"ticker": "URNM", "action": "Sell"}
        ],
        "execution_context": {"report_phase": "post_execution"},
    }


def test_report_phase_alone_is_not_actual_execution() -> None:
    assert has_actual_execution(zero_execution_state()) is False
    assert has_actual_execution(executed_state()) is True


def test_zero_execution_status_is_neutral_and_explicit() -> None:
    install(delivery)
    state = zero_execution_state()

    english = delivery._post_execution_action_snapshot_html(
        delivery, state, "en"
    )
    dutch = delivery._post_execution_action_snapshot_html(
        delivery, state, "nl"
    )

    assert "Portfolio decision status" in english
    assert "No portfolio change was proposed or executed this run" in english
    assert "rotation is already reflected" not in english.lower()
    assert "Status portefeuillebesluit" in dutch
    assert "geen portefeuillewijziging voorgesteld of uitgevoerd" in dutch.lower()
    assert "rotatie is al verwerkt" not in dutch.lower()


def test_actual_execution_preserves_reflected_status() -> None:
    install(delivery)
    state = executed_state()

    english = delivery._post_execution_action_snapshot_html(
        delivery, state, "en"
    )

    assert "Rotation execution status" in english
    assert "already reflected" in english
