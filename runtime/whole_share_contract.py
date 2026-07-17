from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Iterable

WHOLE_SHARE_TOLERANCE = 1e-9


def _text(value: Any, fallback: str = "") -> str:
    raw = str(value or "").strip()
    return raw or fallback


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default


def _ticker(value: Any) -> str:
    return _text(value).upper()


def is_whole_share(value: Any, *, tolerance: float = WHOLE_SHARE_TOLERANCE) -> bool:
    shares = _float(value)
    return shares >= -tolerance and abs(shares - round(shares)) <= tolerance


def floor_whole_shares(value: Any) -> int:
    shares = max(0.0, _float(value))
    return int(math.floor(shares + WHOLE_SHARE_TOLERANCE))


def whole_shares_for_notional(notional_eur: float, price_local: float, currency: str, fx_rate: float) -> int:
    if notional_eur <= 0 or price_local <= 0:
        return 0
    local_notional = notional_eur if currency.upper() == "EUR" else notional_eur * fx_rate
    return int(math.floor(local_notional / price_local + WHOLE_SHARE_TOLERANCE))


def eur_from_local(value_local: float, currency: str, fx_rate: float) -> float:
    return value_local if currency.upper() == "EUR" else value_local / fx_rate


def validate_whole_share_positions(positions: Iterable[dict[str, Any]], *, context: str = "positions") -> list[str]:
    errors: list[str] = []
    for row in positions:
        ticker = _ticker(row.get("ticker")) or "UNKNOWN"
        shares = _float(row.get("shares"))
        if shares < -WHOLE_SHARE_TOLERANCE:
            errors.append(f"{context}:negative_shares:{ticker}:{shares}")
        elif not is_whole_share(shares):
            errors.append(f"{context}:fractional_shares:{ticker}:{shares}")
    return errors


def _pricing_map(runtime_state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in runtime_state.get("pricing", []) or []:
        if not isinstance(row, dict):
            continue
        ticker = _ticker(row.get("symbol") or row.get("ticker"))
        if ticker:
            out[ticker] = dict(row)
    return out


def _price_for(ticker: str, position: dict[str, Any], pricing: dict[str, dict[str, Any]]) -> float:
    row = pricing.get(ticker, {})
    return _float(
        row.get("selected_close")
        or row.get("price")
        or position.get("current_price_local")
        or position.get("previous_price_local")
    )


def _currency_for(ticker: str, position: dict[str, Any], pricing: dict[str, dict[str, Any]]) -> str:
    row = pricing.get(ticker, {})
    return _text(row.get("currency") or position.get("currency") or "USD").upper()


def _fx_rate(runtime_state: dict[str, Any]) -> float:
    return _float((runtime_state.get("fx_basis") or {}).get("rate"), 1.0) or 1.0


def _market_value(shares: float, price_local: float, currency: str, fx_rate: float) -> tuple[float, float]:
    local = round(max(0.0, shares * price_local), 2)
    eur = round(eur_from_local(local, currency, fx_rate), 2)
    return local, eur


def reconcile_portfolio_state(
    portfolio_state: dict[str, Any],
    runtime_state: dict[str, Any],
    *,
    close_tickers: Iterable[str] = (),
    source_name: str = "runtime_state",
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    """Return a whole-share portfolio state, reconciliation artifact, and ledger rows.

    Long-only legacy fractional remainders are sold down with floor semantics. Explicit
    close_tickers are closed completely. Released value is transferred to EUR cash so
    NAV is preserved on the same price/FX basis, apart from cent rounding.
    """

    pricing = _pricing_map(runtime_state)
    fx_rate = _fx_rate(runtime_state)
    close_set = {_ticker(value) for value in close_tickers if _ticker(value)}
    cash_before = _float(portfolio_state.get("cash_eur") or (runtime_state.get("portfolio") or {}).get("cash_eur"))
    report_date = _text(runtime_state.get("requested_close_date") or runtime_state.get("report_date"), "unknown")
    run_id = _text(runtime_state.get("run_id"), "unknown")

    pre_rows: list[dict[str, Any]] = []
    post_rows: list[dict[str, Any]] = []
    adjustments: list[dict[str, Any]] = []
    pre_invested_eur = 0.0
    post_invested_eur = 0.0
    cash_released_eur = 0.0

    for original in portfolio_state.get("positions", []) or []:
        if not isinstance(original, dict):
            continue
        ticker = _ticker(original.get("ticker"))
        if not ticker:
            continue
        price = _price_for(ticker, original, pricing)
        currency = _currency_for(ticker, original, pricing)
        if price <= 0:
            raise RuntimeError(f"whole-share reconciliation missing positive price for {ticker}")

        shares_before = max(0.0, _float(original.get("shares")))
        shares_after = 0 if ticker in close_set else floor_whole_shares(shares_before)
        pre_local, pre_eur = _market_value(shares_before, price, currency, fx_rate)
        post_local, post_eur = _market_value(float(shares_after), price, currency, fx_rate)
        pre_invested_eur += pre_eur
        post_invested_eur += post_eur

        pre_rows.append({"ticker": ticker, "shares": shares_before, "market_value_eur": pre_eur})
        adjusted = abs(shares_before - shares_after) > WHOLE_SHARE_TOLERANCE
        if adjusted:
            released = round(pre_eur - post_eur, 2)
            cash_released_eur += released
            adjustments.append(
                {
                    "ticker": ticker,
                    "reason": "policy_close" if ticker in close_set else "fractional_remainder",
                    "shares_before": round(shares_before, 6),
                    "shares_after": shares_after,
                    "shares_delta": round(shares_after - shares_before, 6),
                    "price_local": round(price, 6),
                    "currency": currency,
                    "released_to_cash_eur": released,
                }
            )

        if shares_after <= 0:
            continue
        row = dict(original)
        row.update(
            {
                "ticker": ticker,
                "shares": shares_after,
                "currency": currency,
                "current_price_local": round(price, 6),
                "previous_price_local": round(price, 6),
                "continuity_current_price_local": round(price, 6),
                "market_value_local": post_local,
                "previous_market_value_local": post_local,
                "market_value_eur": post_eur,
                "previous_market_value_eur": post_eur,
                "shares_delta_this_run": 0.0,
                "weight_change_pct": 0.0,
                "action_executed_this_run": "None",
                "funding_source_note": "No model trade executed this run.",
            }
        )
        post_rows.append(row)

    nav_before = round(pre_invested_eur + cash_before, 2)
    cash_after = round(cash_before + cash_released_eur, 2)
    nav_after = round(post_invested_eur + cash_after, 2)
    rounding_residual = round(nav_before - nav_after, 2)
    cash_after = round(cash_after + rounding_residual, 2)
    nav_after = round(post_invested_eur + cash_after, 2)

    pre_weights = {
        row["ticker"]: (round(row["market_value_eur"] / nav_before * 100.0, 4) if nav_before else 0.0)
        for row in pre_rows
    }
    post_weights: dict[str, float] = {}
    for row in post_rows:
        weight = round(_float(row.get("market_value_eur")) / nav_after * 100.0, 4) if nav_after else 0.0
        post_weights[_ticker(row.get("ticker"))] = weight
        row["current_weight_pct"] = round(weight, 2)
        row["previous_weight_pct"] = round(weight, 2)
        row["weight_inherited_pct"] = round(weight, 2)
        row["target_weight_pct"] = round(weight, 2)

    ledger_rows: list[dict[str, Any]] = []
    for item in adjustments:
        ticker = item["ticker"]
        new_weight = post_weights.get(ticker, 0.0)
        action = "PolicyClose" if item["reason"] == "policy_close" else "FractionalReconciliation"
        ledger_rows.append(
            {
                "trade_id": f"whole-share-{report_date}-{run_id}-{ticker}",
                "trade_date": report_date,
                "source_report": f"whole_share_reconciliation:{source_name}",
                "ticker": ticker,
                "action": action,
                "shares_delta": f"{item['shares_delta']:.6f}",
                "previous_weight_pct": f"{pre_weights.get(ticker, 0.0):.4f}",
                "new_weight_pct": f"{new_weight:.4f}",
                "weight_change_pct": f"{(new_weight - pre_weights.get(ticker, 0.0)):.4f}",
                "target_weight_pct": f"{new_weight:.4f}",
                "conviction_tier": "",
                "portfolio_role": "State contract reconciliation",
                "funding_source_note": (
                    "Closed because the instrument is prohibited by the current leverage policy."
                    if action == "PolicyClose"
                    else "Legacy fractional remainder converted to cash under the whole-share contract."
                ),
            }
        )

    now = datetime.now(timezone.utc).isoformat()
    reconciled = dict(portfolio_state)
    reconciled.update(
        {
            "cash_eur": cash_after,
            "invested_market_value_eur": round(post_invested_eur, 2),
            "nav_eur": nav_after,
            "peak_nav_eur": max(_float(portfolio_state.get("peak_nav_eur"), nav_after), nav_after),
            "positions": sorted(post_rows, key=lambda row: _ticker(row.get("ticker"))),
            "whole_share_contract": {
                "status": "compliant",
                "reconciled_at_utc": now,
                "runtime_state": source_name,
                "policy_closed_tickers": sorted(close_set),
                "adjusted_position_count": len(adjustments),
                "cash_released_eur": round(cash_released_eur + rounding_residual, 2),
                "nav_before_eur": nav_before,
                "nav_after_eur": nav_after,
            },
        }
    )

    artifact = {
        "schema_version": "1.0",
        "artifact_type": "etf_whole_share_reconciliation",
        "created_at_utc": now,
        "status": "reconciled" if adjustments else "already_compliant",
        "report_date": report_date,
        "run_id": run_id,
        "source_runtime_state": source_name,
        "policy_closed_tickers": sorted(close_set),
        "adjustments": adjustments,
        "adjusted_position_count": len(adjustments),
        "cash_before_eur": round(cash_before, 2),
        "cash_after_eur": cash_after,
        "cash_released_eur": round(cash_released_eur + rounding_residual, 2),
        "invested_before_eur": round(pre_invested_eur, 2),
        "invested_after_eur": round(post_invested_eur, 2),
        "nav_before_eur": nav_before,
        "nav_after_eur": nav_after,
        "nav_drift_eur": round(nav_after - nav_before, 2),
        "whole_share_validation_errors": validate_whole_share_positions(post_rows, context="reconciled_state"),
    }
    return reconciled, artifact, ledger_rows
