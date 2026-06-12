from __future__ import annotations

from tools.validate_etf_model_execution import _is_no_trade_intents


def test_no_trade_helper_accepts_matching_shadow_and_guarded_auto_modes() -> None:
    assert _is_no_trade_intents(
        {"execution_mode": "shadow", "execution_status": "no_trade_intents"},
        "shadow",
    )
    assert _is_no_trade_intents(
        {"execution_mode": "guarded_auto", "execution_status": "no_trade_intents"},
        "guarded_auto",
    )


def test_no_trade_helper_rejects_mismatched_or_ready_status() -> None:
    assert not _is_no_trade_intents(
        {"execution_mode": "shadow", "execution_status": "shadow_ready"},
        "shadow",
    )
    assert not _is_no_trade_intents(
        {"execution_mode": "shadow", "execution_status": "no_trade_intents"},
        "guarded_auto",
    )
