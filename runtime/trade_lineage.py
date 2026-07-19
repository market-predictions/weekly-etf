from __future__ import annotations

from typing import Any, Iterable

SHARE_TOLERANCE = 1e-6
MATERIAL_WEIGHT_CHANGE_PCT = 0.10
CLIENT_WEIGHT_DECIMALS = 1
EXECUTED_ACTIONS = {
    "buy",
    "sell",
    "add",
    "added",
    "increase",
    "increased",
    "reduce",
    "reduced",
    "close",
    "closed",
    "shadow buy",
    "shadow reduce",
}


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper() or "UNKNOWN"


def is_executed_trade(row: dict[str, Any]) -> bool:
    action = str(row.get("action_executed_this_run") or row.get("action") or "").strip().lower()
    return abs(_float(row.get("shares_delta_this_run", row.get("shares_delta")))) > SHARE_TOLERANCE or action in EXECUTED_ACTIONS


def _ledger_map(rows: Iterable[dict[str, Any]] | None) -> dict[str, dict[str, Any]]:
    return {
        _ticker(row.get("ticker")): dict(row)
        for row in (rows or [])
        if isinstance(row, dict) and _ticker(row.get("ticker")) != "UNKNOWN"
    }


def _derive_pre_trade_values(item: dict[str, Any], pre_trade_shares: float) -> None:
    """Populate explicit immutable values without changing legacy current-value fields.

    The report stack historically uses ``previous_market_value_*`` as the latest/current
    valuation fallback. Reusing those fields for trade lineage would corrupt NAV and
    Section 15. Explicit ``pre_trade_*`` fields therefore carry the immutable snapshot.
    """

    current_shares = _float(item.get("shares"))
    if current_shares <= SHARE_TOLERANCE:
        return
    for current_key, pre_trade_key in (
        ("market_value_local", "pre_trade_market_value_local"),
        ("market_value_eur", "pre_trade_market_value_eur"),
    ):
        current_value = _float(item.get(current_key))
        if current_value >= 0:
            item[pre_trade_key] = round(current_value / current_shares * pre_trade_shares, 2)


def normalize_trade_lineage_rows(
    rows: Iterable[dict[str, Any]],
    *,
    official_ledger_rows: Iterable[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Return rows with an immutable pre-trade quantity/value/weight snapshot.

    Official ledger rows are preferred. Legacy rows whose pre-trade weight was overwritten
    with a post-trade value are repaired deterministically from the recorded share and weight
    deltas. Current valuation compatibility fields are preserved for the existing report stack.
    The function only changes supplied copies; callers decide whether to persist.
    """

    ledger_by_ticker = _ledger_map(official_ledger_rows)
    normalized: list[dict[str, Any]] = []
    for raw in rows:
        item = dict(raw)
        current_shares = max(0.0, _float(item.get("shares")))
        current_weight = max(0.0, _float(item.get("current_weight_pct")))

        if not is_executed_trade(item):
            item["previous_shares"] = current_shares
            item["pre_trade_shares"] = current_shares
            item["previous_weight_pct"] = current_weight
            item["pre_trade_weight_pct"] = current_weight
            item["weight_inherited_pct"] = current_weight
            if item.get("market_value_local") not in (None, ""):
                item["previous_market_value_local"] = item.get("market_value_local")
                item["pre_trade_market_value_local"] = item.get("market_value_local")
            if item.get("market_value_eur") not in (None, ""):
                item["previous_market_value_eur"] = item.get("market_value_eur")
                item["pre_trade_market_value_eur"] = item.get("market_value_eur")
            item["trade_lineage_source"] = "current_snapshot_no_trade"
            normalized.append(item)
            continue

        ticker = _ticker(item.get("ticker"))
        ledger = ledger_by_ticker.get(ticker, {})
        shares_delta = _float(ledger.get("shares_delta"), _float(item.get("shares_delta_this_run")))
        pre_trade_shares = max(0.0, current_shares - shares_delta)
        item["previous_shares"] = round(pre_trade_shares, 6)
        item["pre_trade_shares"] = round(pre_trade_shares, 6)

        recorded_change = _float(
            ledger.get("weight_change_pct"),
            _float(item.get("weight_change_pct")),
        )
        if ledger:
            pre_trade_weight = max(0.0, _float(ledger.get("previous_weight_pct")))
            ledger_new_weight = _float(ledger.get("new_weight_pct"), current_weight)
            item["weight_change_pct"] = round(ledger_new_weight - pre_trade_weight, 4)
            item["trade_lineage_source"] = "official_trade_ledger"
        else:
            existing_previous = _float(item.get("previous_weight_pct"), current_weight)
            overwritten = (
                abs(recorded_change) >= MATERIAL_WEIGHT_CHANGE_PCT
                and abs(existing_previous - current_weight) < 0.005
            )
            pre_trade_weight = max(0.0, current_weight - recorded_change) if overwritten else max(0.0, existing_previous)
            item["trade_lineage_source"] = (
                "derived_from_recorded_delta" if overwritten else "preserved_pre_trade_snapshot"
            )

        item["previous_weight_pct"] = round(pre_trade_weight, 4)
        item["pre_trade_weight_pct"] = round(pre_trade_weight, 4)
        item["weight_inherited_pct"] = round(pre_trade_weight, 4)
        _derive_pre_trade_values(item, pre_trade_shares)
        normalized.append(item)
    return normalized


def validate_trade_lineage_rows(
    rows: Iterable[dict[str, Any]],
    *,
    context: str = "trade_lineage",
    display_decimals: int = CLIENT_WEIGHT_DECIMALS,
) -> list[str]:
    errors: list[str] = []
    for row in rows:
        if not is_executed_trade(row):
            continue
        ticker = _ticker(row.get("ticker"))
        current_shares = _float(row.get("shares"))
        pre_trade_shares = _float(
            row.get("pre_trade_shares", row.get("previous_shares")),
            float("nan"),
        )
        shares_delta = _float(row.get("shares_delta_this_run", row.get("shares_delta")))
        if pre_trade_shares != pre_trade_shares:
            errors.append(f"{context}:missing_pre_trade_shares:{ticker}")
        elif abs((current_shares - pre_trade_shares) - shares_delta) > max(SHARE_TOLERANCE, abs(shares_delta) * 1e-6):
            errors.append(
                f"{context}:share_delta_mismatch:{ticker}:"
                f"{pre_trade_shares:.6f}->{current_shares:.6f}!={shares_delta:.6f}"
            )

        if row.get("previous_weight_pct") in (None, "") or row.get("current_weight_pct") in (None, ""):
            errors.append(f"{context}:missing_weight_snapshot:{ticker}")
            continue
        pre_trade_weight = _float(row.get("pre_trade_weight_pct", row.get("previous_weight_pct")))
        previous_weight = _float(row.get("previous_weight_pct"))
        current_weight = _float(row.get("current_weight_pct"))
        recorded_change = _float(row.get("weight_change_pct"))
        implied_change = current_weight - pre_trade_weight
        material_change = max(abs(recorded_change), abs(implied_change)) >= MATERIAL_WEIGHT_CHANGE_PCT
        if abs(previous_weight - pre_trade_weight) > 0.005:
            errors.append(
                f"{context}:pre_trade_weight_alias_mismatch:{ticker}:"
                f"{previous_weight:.4f}!={pre_trade_weight:.4f}"
            )
        if material_change and abs(implied_change - recorded_change) > 0.15:
            errors.append(
                f"{context}:weight_delta_mismatch:{ticker}:"
                f"{pre_trade_weight:.4f}->{current_weight:.4f}!={recorded_change:.4f}"
            )
        if material_change and round(pre_trade_weight, display_decimals) == round(current_weight, display_decimals):
            errors.append(
                f"{context}:material_trade_identical_display_weight:{ticker}:"
                f"{pre_trade_weight:.4f}->{current_weight:.4f}"
            )
        if current_shares > SHARE_TOLERANCE and row.get("pre_trade_market_value_eur") in (None, ""):
            errors.append(f"{context}:missing_pre_trade_market_value_eur:{ticker}")
        if current_shares > SHARE_TOLERANCE and row.get("market_value_eur") in (None, ""):
            errors.append(f"{context}:missing_current_market_value_eur:{ticker}")
    return errors


def normalize_and_validate_trade_lineage(
    rows: Iterable[dict[str, Any]],
    *,
    official_ledger_rows: Iterable[dict[str, Any]] | None = None,
    context: str = "trade_lineage",
) -> list[dict[str, Any]]:
    normalized = normalize_trade_lineage_rows(rows, official_ledger_rows=official_ledger_rows)
    errors = validate_trade_lineage_rows(normalized, context=context)
    if errors:
        raise RuntimeError("ETF trade-lineage validation failed: " + "; ".join(sorted(set(errors))))
    return normalized
