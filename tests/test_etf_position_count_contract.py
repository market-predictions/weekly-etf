from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.position_count_contract import (
    assess_current_positions,
    assess_position_count_transition,
    count_active_positions,
)
from runtime.position_count_report_surface import apply_position_count_surface
from tools.validate_etf_persisted_valuation_state import _position_count_preflight


def _positions(*tickers: str, shares: float = 1.0) -> list[dict]:
    return [{"ticker": ticker, "shares": shares} for ticker in tickers]


def _priced_position(ticker: str, shares: int, price: float = 100.0) -> dict:
    value = float(shares) * price
    return {
        "ticker": ticker,
        "shares": float(shares),
        "currency": "EUR",
        "current_price_local": price,
        "previous_price_local": price,
        "market_value_local": value,
        "previous_market_value_local": value,
        "market_value_eur": value,
        "previous_market_value_eur": value,
        "current_weight_pct": 0.0,
        "previous_weight_pct": 0.0,
        "weight_inherited_pct": 0.0,
        "target_weight_pct": 0.0,
    }


def _pricing(ticker: str, price: float = 100.0) -> dict:
    return {
        "symbol": ticker,
        "selected_close": price,
        "currency": "EUR",
        "status": "fresh_exact_close",
        "pricing_tier": "valuation_grade",
        "selected_close_type": "raw_close",
        "returned_close_date": "2026-07-16",
        "source": "fixture",
    }


def _preflight_fixture(
    tmp_path: Path,
    *,
    current: list[dict],
    source: str,
    destination: str,
    notional_eur: float,
    action_code: str = "replace_partial",
) -> tuple[dict, dict, Path]:
    invested = sum(float(row["previous_market_value_eur"]) for row in current)
    cash = 100.0
    nav = invested + cash
    all_tickers = sorted({str(row["ticker"]) for row in current} | {destination})
    runtime = {
        "run_id": "position-count-fixture",
        "report_date": "2026-07-16",
        "requested_close_date": "2026-07-16",
        "source_files": {"pricing_audit": "fixture", "rotation_plan": "fixture"},
        "fx_basis": {"rate": 1.0},
        "portfolio": {
            "cash_eur": cash,
            "total_portfolio_value_eur": nav,
            "base_currency": "EUR",
        },
        "pricing": [_pricing(ticker) for ticker in all_tickers],
        "positions": current,
        "rotation_plan": {
            "policy": {
                "min_trade_size_pct_nav": 2.0,
                "max_single_source_reduction_pct_nav": 50.0,
                "max_major_rotations_per_run": 1,
                "max_active_positions": 8,
            },
            "trade_intents": [
                {
                    "source_ticker": source,
                    "destination_ticker": destination,
                    "delta_weight_pct": -(notional_eur / nav * 100.0),
                    "destination_delta_weight_pct": notional_eur / nav * 100.0,
                    "estimated_notional_eur": notional_eur,
                    "action_code": action_code,
                    "reason_codes": ["position_count_fixture"],
                }
            ],
        },
    }
    state = {
        "cash_eur": cash,
        "invested_market_value_eur": invested,
        "nav_eur": nav,
        "positions": current,
    }
    state_path = tmp_path / "portfolio.json"
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return runtime, state, state_path


def test_zero_share_positions_do_not_count() -> None:
    positions = _positions("AAA", "BBB") + [{"ticker": "ZERO", "shares": 0}]
    assert count_active_positions(positions) == 2
    assessment = assess_current_positions(positions, max_active_positions=2)
    assert assessment.passed
    assert assessment.status == "compliant"


def test_duplicate_active_ticker_is_invalid() -> None:
    assessment = assess_current_positions(
        [{"ticker": "AAA", "shares": 1}, {"ticker": "AAA", "shares": 2}],
        max_active_positions=8,
    )
    assert not assessment.passed
    assert "official_state:duplicate_active_ticker:AAA" in assessment.errors


def test_at_limit_reduce_to_residual_plus_new_ticker_is_blocked() -> None:
    current = _positions("SRC", "B", "C", "D", "E", "F", "G", "H")
    projected = _positions("SRC", "B", "C", "D", "E", "F", "G", "H", "NEW")
    assessment = assess_position_count_transition(current, projected, max_active_positions=8)
    assert not assessment.passed
    assert assessment.current_count == 8
    assert assessment.projected_count == 9
    assert "NEW" in assessment.opened_tickers
    assert any(error.startswith("post_trade_active_position_count_exceeds_limit") for error in assessment.errors)


def test_at_limit_full_source_close_plus_new_ticker_is_allowed() -> None:
    current = _positions("SRC", "B", "C", "D", "E", "F", "G", "H")
    projected = _positions("NEW", "B", "C", "D", "E", "F", "G", "H")
    assessment = assess_position_count_transition(current, projected, max_active_positions=8)
    assert assessment.passed
    assert assessment.status == "compliant"
    assert assessment.opened_tickers == ("NEW",)
    assert assessment.closed_tickers == ("SRC",)


def test_already_over_limit_cannot_open_another_ticker() -> None:
    current = _positions("A", "B", "C", "D", "E", "F", "G", "H", "I")
    projected = current + [{"ticker": "NEW", "shares": 1}]
    assessment = assess_position_count_transition(current, projected, max_active_positions=8)
    assert not assessment.passed
    assert "close_first_new_ticker_blocked:NEW" in assessment.errors


def test_already_over_limit_count_reducing_close_is_allowed() -> None:
    current = _positions("A", "B", "C", "D", "E", "F", "G", "H", "I")
    projected = _positions("B", "C", "D", "E", "F", "G", "H", "I")
    assessment = assess_position_count_transition(current, projected, max_active_positions=8)
    assert assessment.passed
    assert assessment.current_count == 9
    assert assessment.projected_count == 8
    assert assessment.status == "compliant"


def test_production_preflight_blocks_partial_source_residual_before_mutation(tmp_path: Path) -> None:
    current = [_priced_position("SRC", 4)] + [
        _priced_position(ticker, 1) for ticker in ("B", "C", "D", "E", "F", "G", "H")
    ]
    runtime, state, state_path = _preflight_fixture(
        tmp_path,
        current=current,
        source="SRC",
        destination="NEW",
        notional_eur=300.0,
    )
    before = state_path.read_bytes()
    with pytest.raises(RuntimeError, match="position-count contract blocked guarded execution"):
        _position_count_preflight(runtime, state, state_path)
    assert state_path.read_bytes() == before


def test_production_preflight_allows_full_close_plus_new_ticker(tmp_path: Path) -> None:
    current = [_priced_position("SRC", 4)] + [
        _priced_position(ticker, 1) for ticker in ("B", "C", "D", "E", "F", "G", "H")
    ]
    runtime, state, state_path = _preflight_fixture(
        tmp_path,
        current=current,
        source="SRC",
        destination="NEW",
        notional_eur=400.0,
        action_code="replace_full",
    )
    assessment = _position_count_preflight(runtime, state, state_path)
    assert assessment.passed
    assert assessment.projected_count == 8
    assert assessment.opened_tickers == ("NEW",)
    assert assessment.closed_tickers == ("SRC",)


def test_production_preflight_allows_over_limit_close_into_existing_position(tmp_path: Path) -> None:
    current = [_priced_position("SRC", 4), _priced_position("DEST", 1)] + [
        _priced_position(ticker, 1) for ticker in ("B", "C", "D", "E", "F", "G", "H")
    ]
    runtime, state, state_path = _preflight_fixture(
        tmp_path,
        current=current,
        source="SRC",
        destination="DEST",
        notional_eur=400.0,
        action_code="replace_full",
    )
    assessment = _position_count_preflight(runtime, state, state_path)
    assert assessment.passed
    assert assessment.current_count == 9
    assert assessment.projected_count == 8
    assert assessment.opened_tickers == ()
    assert assessment.closed_tickers == ("SRC",)


def _report(language: str, tickers: tuple[str, ...]) -> str:
    links = "\n".join(
        f"| [{ticker}](https://www.tradingview.com/chart/?symbol={ticker}) | 1 |"
        for ticker in tickers
    )
    if language == "nl":
        return f"""## 15. Huidige posities en cash

| Ticker | Aantal aandelen |
|---|---:|
{links}
| CASH | - |

## 16. Input voor de volgende run

### Randvoorwaarden
- Maximaal aantal posities: 8 zachte doelstelling; het huidige geërfde aantal kan tijdelijk hoger zijn totdat bewaakte rotatie dit verlaagt
"""
    return f"""## 15. Current Portfolio Holdings and Cash

| Ticker | Shares |
|---|---:|
{links}
| CASH | - |

## 16. Continuity Input for Next Run

### Constraints
- Max number of positions: 8 soft target; current inherited count may exceed this until guarded rotation reduces it
"""


def test_english_breach_is_client_safe_and_idempotent() -> None:
    tickers = tuple("ABCDEFGHI")
    positions = _positions(*tickers)
    source = _report("en", tickers)
    cleaned = apply_position_count_surface(source, language="en", official_positions=positions)
    assert "Maximum active positions: 8. Current active positions: 9." in cleaned
    assert "No new position may be opened until the count is restored." in cleaned
    assert "soft target" not in cleaned
    assert apply_position_count_surface(cleaned, language="en", official_positions=positions) == cleaned


def test_dutch_breach_is_client_safe_and_idempotent() -> None:
    tickers = tuple("ABCDEFGHI")
    positions = _positions(*tickers)
    source = _report("nl", tickers)
    cleaned = apply_position_count_surface(source, language="nl", official_positions=positions)
    assert "Maximaal aantal actieve posities: 8. Huidig aantal actieve posities: 9." in cleaned
    assert "Er mag geen nieuwe positie worden geopend totdat het aantal is hersteld." in cleaned
    assert "zachte doelstelling" not in cleaned
    assert apply_position_count_surface(cleaned, language="nl", official_positions=positions) == cleaned


def test_compliant_report_constraint_is_unchanged() -> None:
    tickers = tuple("ABCDEFGH")
    source = _report("en", tickers)
    cleaned = apply_position_count_surface(source, language="en", official_positions=_positions(*tickers))
    assert cleaned == source


def test_historical_report_with_different_tickers_is_unchanged() -> None:
    source = _report("en", tuple("ABCDEFGHIJK"))
    current_positions = _positions(*tuple("ABCDEFGHI"))
    cleaned = apply_position_count_surface(
        source,
        language="en",
        official_positions=current_positions,
    )
    assert cleaned == source
