from __future__ import annotations

import pytest

from runtime.build_etf_report_state import _enrich_positions
from runtime.render_cockpit_front_page import _action_surface
from runtime.render_etf_report_from_state import invested_eur, section15_table, weights
from runtime.trade_lineage import (
    normalize_and_validate_trade_lineage,
    normalize_trade_lineage_rows,
    validate_trade_lineage_rows,
)


def _legacy_rotation_rows() -> list[dict[str, object]]:
    return [
        {
            "ticker": "PAVE",
            "shares": 107.0,
            "shares_delta_this_run": 107.0,
            "action_executed_this_run": "Buy",
            "current_weight_pct": 4.94,
            "previous_weight_pct": 4.94,
            "weight_change_pct": 4.9708,
            "current_price_local": 56.30,
            "previous_price_local": 56.30,
            "market_value_local": 6024.10,
            "previous_market_value_local": 6024.10,
            "market_value_eur": 5266.88,
            "previous_market_value_eur": 5266.88,
        },
        {
            "ticker": "XLU",
            "shares": 14.0,
            "shares_delta_this_run": -134.0,
            "action_executed_this_run": "Sell",
            "current_weight_pct": 0.52,
            "previous_weight_pct": 0.52,
            "weight_change_pct": -4.9708,
            "current_price_local": 45.17,
            "previous_price_local": 45.17,
            "market_value_local": 632.38,
            "previous_market_value_local": 632.38,
            "market_value_eur": 552.89,
            "previous_market_value_eur": 552.89,
        },
    ]


def test_legacy_overwritten_rotation_is_reconstructed() -> None:
    rows = normalize_and_validate_trade_lineage(
        _legacy_rotation_rows(), context="legacy_rotation"
    )
    by_ticker = {row["ticker"]: row for row in rows}

    pave = by_ticker["PAVE"]
    assert pave["previous_shares"] == pytest.approx(0.0)
    assert pave["pre_trade_shares"] == pytest.approx(0.0)
    assert pave["previous_weight_pct"] == pytest.approx(0.0)
    assert pave["pre_trade_weight_pct"] == pytest.approx(0.0)
    assert pave["pre_trade_market_value_eur"] == pytest.approx(0.0)
    assert pave["previous_market_value_eur"] == pytest.approx(5266.88)
    assert pave["trade_lineage_source"] == "derived_from_recorded_delta"

    xlu = by_ticker["XLU"]
    assert xlu["previous_shares"] == pytest.approx(148.0)
    assert xlu["pre_trade_shares"] == pytest.approx(148.0)
    assert xlu["previous_weight_pct"] == pytest.approx(5.4908)
    assert xlu["pre_trade_weight_pct"] == pytest.approx(5.4908)
    assert xlu["pre_trade_market_value_eur"] == pytest.approx(5844.83, abs=0.02)
    assert xlu["previous_market_value_eur"] == pytest.approx(552.89)
    assert xlu["trade_lineage_source"] == "derived_from_recorded_delta"


def test_official_ledger_snapshot_takes_precedence() -> None:
    rows = normalize_and_validate_trade_lineage(
        _legacy_rotation_rows(),
        official_ledger_rows=[
            {
                "ticker": "PAVE",
                "shares_delta": "107.000000",
                "previous_weight_pct": "0.0000",
                "new_weight_pct": "4.9600",
                "weight_change_pct": "4.9600",
            },
            {
                "ticker": "XLU",
                "shares_delta": "-134.000000",
                "previous_weight_pct": "5.4900",
                "new_weight_pct": "0.5200",
                "weight_change_pct": "-4.9700",
            },
        ],
        context="official_rotation",
    )
    by_ticker = {row["ticker"]: row for row in rows}
    assert by_ticker["PAVE"]["previous_weight_pct"] == pytest.approx(0.0)
    assert by_ticker["PAVE"]["pre_trade_weight_pct"] == pytest.approx(0.0)
    assert by_ticker["XLU"]["previous_weight_pct"] == pytest.approx(5.49)
    assert by_ticker["XLU"]["pre_trade_weight_pct"] == pytest.approx(5.49)
    assert by_ticker["PAVE"]["trade_lineage_source"] == "official_trade_ledger"
    assert by_ticker["XLU"]["trade_lineage_source"] == "official_trade_ledger"


def test_material_trade_with_identical_client_weights_is_rejected() -> None:
    row = {
        "ticker": "PAVE",
        "shares": 107.0,
        "previous_shares": 0.0,
        "pre_trade_shares": 0.0,
        "shares_delta_this_run": 107.0,
        "action_executed_this_run": "Buy",
        "current_weight_pct": 4.94,
        "previous_weight_pct": 4.94,
        "pre_trade_weight_pct": 4.94,
        "weight_change_pct": 4.97,
        "market_value_eur": 5266.88,
        "previous_market_value_eur": 5266.88,
        "pre_trade_market_value_eur": 0.0,
    }
    errors = validate_trade_lineage_rows([row], context="display_gate")
    assert any("material_trade_identical_display_weight:PAVE" in error for error in errors)


def test_no_trade_position_uses_current_snapshot() -> None:
    rows = normalize_trade_lineage_rows(
        [
            {
                "ticker": "SMH",
                "shares": 59.0,
                "shares_delta_this_run": 0.0,
                "action_executed_this_run": "None",
                "current_weight_pct": 26.92,
                "market_value_local": 32835.27,
                "market_value_eur": 28707.93,
            }
        ]
    )
    assert rows[0]["previous_shares"] == pytest.approx(59.0)
    assert rows[0]["pre_trade_shares"] == pytest.approx(59.0)
    assert rows[0]["previous_weight_pct"] == pytest.approx(26.92)
    assert rows[0]["pre_trade_weight_pct"] == pytest.approx(26.92)
    assert rows[0]["previous_market_value_eur"] == pytest.approx(28707.93)
    assert rows[0]["pre_trade_market_value_eur"] == pytest.approx(28707.93)
    assert validate_trade_lineage_rows(rows) == []


def test_report_state_builder_repairs_legacy_rotation_rows() -> None:
    positions = _enrich_positions(
        {
            "cash_eur": 100824.44,
            "positions": _legacy_rotation_rows(),
        },
        {
            "fx_basis": {"rate": 1.14377},
            "price_results": [
                {
                    "symbol": "PAVE",
                    "selected_close": 56.30,
                    "currency": "USD",
                    "status": "fresh_exact_unverified",
                    "pricing_tier": "valuation_grade",
                    "selected_close_type": "raw_close",
                    "returned_close_date": "2026-07-17",
                    "source": "test",
                },
                {
                    "symbol": "XLU",
                    "selected_close": 45.17,
                    "currency": "USD",
                    "status": "fresh_exact_unverified",
                    "pricing_tier": "valuation_grade",
                    "selected_close_type": "raw_close",
                    "returned_close_date": "2026-07-17",
                    "source": "test",
                },
            ],
        },
        [],
        {"assessed_lanes": []},
        {},
    )
    by_ticker = {row["ticker"]: row for row in positions}
    assert by_ticker["PAVE"]["previous_shares"] == pytest.approx(0.0)
    assert by_ticker["PAVE"]["pre_trade_market_value_eur"] == pytest.approx(0.0)
    assert by_ticker["PAVE"]["previous_market_value_eur"] == pytest.approx(5266.88)
    assert by_ticker["PAVE"]["previous_weight_pct"] == pytest.approx(0.0)
    assert by_ticker["XLU"]["previous_shares"] == pytest.approx(148.0)
    assert by_ticker["XLU"]["pre_trade_market_value_eur"] == pytest.approx(5844.83, abs=0.02)
    assert by_ticker["XLU"]["previous_market_value_eur"] == pytest.approx(552.89)
    assert by_ticker["XLU"]["previous_weight_pct"] == pytest.approx(5.4908)


def test_current_report_valuation_remains_current_after_lineage_normalization() -> None:
    positions = normalize_and_validate_trade_lineage(
        _legacy_rotation_rows(), context="current_report_valuation"
    )
    state = {"portfolio": {"cash_eur": 100.0}, "positions": positions}

    assert invested_eur(state) == pytest.approx(5819.77)
    current_weights = weights(state)
    assert current_weights["PAVE"] == pytest.approx(90.5, abs=0.1)
    assert current_weights["XLU"] == pytest.approx(9.5, abs=0.1)

    rendered = section15_table(state)
    assert "| PAVE | 107.00 | 56.30 |" in rendered
    assert "| XLU | 14.00 | 45.17 |" in rendered
    assert "5266.88" in rendered
    assert "552.89" in rendered
    assert "5844.83" not in rendered


def test_cockpit_action_surface_is_intuitive_after_normalization() -> None:
    positions = normalize_and_validate_trade_lineage(
        _legacy_rotation_rows(), context="cockpit_rotation"
    )
    title, note = _action_surface({"positions": positions}, "en")

    assert title == "PAVE added · XLU reduced"
    assert "PAVE 0.0% → 4.9%" in note
    assert "XLU 5.5% → 0.5%" in note
