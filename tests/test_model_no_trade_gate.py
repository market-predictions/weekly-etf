from __future__ import annotations

from tools.validate_etf_model_execution import _is_shadow_no_trade


def test_shadow_no_trade_helper_accepts_only_shadow_no_trade() -> None:
    assert _is_shadow_no_trade(
        {"execution_mode": "shadow", "execution_status": "no_trade_intents"},
        "shadow",
    )
    assert not _is_shadow_no_trade(
        {"execution_mode": "shadow", "execution_status": "shadow_ready"},
        "shadow",
    )
    assert not _is_shadow_no_trade(
        {"execution_mode": "guarded_auto", "execution_status": "no_trade_intents"},
        "guarded_auto",
    )
