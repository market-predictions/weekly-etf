from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PRICED_STATUSES = {"fresh_close", "fresh_fallback_source", "fresh_exact_close", "fresh_exact_unverified", "prior_valid_close"}
DEFAULT_OUTPUT_DIR = Path("output/runtime")
LEDGER_FIELDS = [
    "trade_id",
    "trade_date",
    "source_report",
    "ticker",
    "action",
    "shares_delta",
    "previous_weight_pct",
    "new_weight_pct",
    "weight_change_pct",
    "target_weight_pct",
    "conviction_tier",
    "portfolio_role",
    "funding_source_note",
]
CORE_POSITION_FIELDS = {
    "shares",
    "current_price_local",
    "previous_price_local",
    "continuity_current_price_local",
    "currency",
    "market_value_local",
    "previous_market_value_local",
    "market_value_eur",
    "previous_market_value_eur",
    "current_weight_pct",
    "previous_weight_pct",
    "weight_inherited_pct",
    "target_weight_pct",
}
RUN_FIELD_DEFAULTS = {
    "shares_delta_this_run": 0.0,
    "weight_change_pct": 0.0,
    "action_executed_this_run": "None",
    "funding_source_note": "No model trade executed this run.",
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _text(value: Any, fallback: str = "") -> str:
    raw = str(value or "").strip()
    return raw or fallback


def _ticker(value: Any) -> str:
    return _text(value).upper()


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default


def _clear_run_fields(row: dict[str, Any]) -> dict[str, Any]:
    item = dict(row)
    item.update(RUN_FIELD_DEFAULTS)
    return item


def _pricing_map(runtime_state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {_ticker(row.get("symbol")): dict(row) for row in runtime_state.get("pricing", []) or [] if _ticker(row.get("symbol"))}


def _position_map(runtime_state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {_ticker(row.get("ticker")): dict(row) for row in runtime_state.get("positions", []) or [] if _ticker(row.get("ticker"))}


def _trade_intents(runtime_state: dict[str, Any]) -> list[dict[str, Any]]:
    rows = runtime_state.get("trade_intents") or (runtime_state.get("rotation_plan") or {}).get("trade_intents") or []
    return [dict(row) for row in rows if isinstance(row, dict)]


def _policy(runtime_state: dict[str, Any]) -> dict[str, Any]:
    return dict((runtime_state.get("rotation_plan") or {}).get("policy") or {})


def _nav(runtime_state: dict[str, Any]) -> float:
    return _float((runtime_state.get("portfolio") or {}).get("total_portfolio_value_eur"))


def _fx(runtime_state: dict[str, Any]) -> float:
    return _float((runtime_state.get("fx_basis") or {}).get("rate"), 1.0) or 1.0


def _price_local(ticker: str, row: dict[str, Any], price_map: dict[str, dict[str, Any]]) -> float:
    price_row = price_map.get(_ticker(ticker), {})
    return _float(price_row.get("selected_close") or price_row.get("price") or row.get("current_price_local") or row.get("previous_price_local"))


def _currency(ticker: str, row: dict[str, Any], price_map: dict[str, dict[str, Any]]) -> str:
    price_row = price_map.get(_ticker(ticker), {})
    return _text(price_row.get("currency") or row.get("currency") or "USD").upper()


def _local_from_eur(value_eur: float, currency: str, fx: float) -> float:
    return value_eur if currency == "EUR" else value_eur * fx


def _eur_from_local(value_local: float, currency: str, fx: float) -> float:
    return value_local if currency == "EUR" else value_local / fx


def _market_value_eur(row: dict[str, Any]) -> float:
    return _float(row.get("previous_market_value_eur") if row.get("previous_market_value_eur") not in (None, "") else row.get("market_value_eur"))


def _shares_for_notional(notional_eur: float, price_local: float, currency: str, fx: float) -> float:
    if price_local <= 0:
        return 0.0
    return _local_from_eur(notional_eur, currency, fx) / price_local


def _mark_position(row: dict[str, Any], *, shares: float, price: float, currency: str, nav: float, fx: float) -> dict[str, Any]:
    item = dict(row)
    market_value_local = round(max(0.0, shares * price), 2)
    market_value_eur = round(_eur_from_local(market_value_local, currency, fx), 2)
    weight = round(market_value_eur / nav * 100.0, 2) if nav else 0.0
    item.update({
        "shares": round(max(0.0, shares), 6),
        "currency": currency,
        "current_price_local": round(price, 6),
        "previous_price_local": round(price, 6),
        "continuity_current_price_local": round(price, 6),
        "market_value_local": market_value_local,
        "previous_market_value_local": market_value_local,
        "market_value_eur": market_value_eur,
        "previous_market_value_eur": market_value_eur,
        "current_weight_pct": weight,
        "previous_weight_pct": weight,
        "weight_inherited_pct": weight,
    })
    return item


def _valid_price_row(ticker: str, price_map: dict[str, dict[str, Any]]) -> tuple[bool, str]:
    row = price_map.get(_ticker(ticker), {})
    if not row:
        return False, "missing_price_row"
    if _text(row.get("status")) not in PRICED_STATUSES:
        return False, f"invalid_price_status:{row.get('status')}"
    if row.get("selected_close") is None and row.get("price") is None:
        return False, "missing_selected_close"
    if _text(row.get("pricing_tier")) != "valuation_grade":
        return False, f"not_valuation_grade:{row.get('pricing_tier')}"
    return True, "ok"


def _prepare_runtime_state(runtime_state: dict[str, Any], portfolio_state_path: Path) -> dict[str, Any]:
    """Use official portfolio state as position authority before model execution.

    Report/runtime rows may carry scorecard memory and previous execution metadata.
    The scorecard may inform decisions, but execution quantities and this-run
    change fields must start from official portfolio state plus current pricing.
    """
    if not portfolio_state_path.exists():
        return runtime_state
    portfolio_state = _read_json(portfolio_state_path)
    price_map = _pricing_map(runtime_state)
    fx = _fx(runtime_state)
    runtime_by_ticker = _position_map(runtime_state)
    prepared_positions: list[dict[str, Any]] = []
    total_market_value = 0.0
    official_positions = portfolio_state.get("positions", []) or []
    for official in official_positions:
        ticker = _ticker(official.get("ticker"))
        if not ticker:
            continue
        row = dict(runtime_by_ticker.get(ticker, {}))
        row.update({key: value for key, value in official.items() if key in CORE_POSITION_FIELDS or key not in row})
        row = _clear_run_fields(row)
        row["ticker"] = ticker
        price = _price_local(ticker, official, price_map)
        currency = _currency(ticker, official, price_map)
        shares = _float(official.get("shares"))
        if price > 0 and shares >= 0:
            row = _mark_position(row, shares=shares, price=price, currency=currency, nav=1.0, fx=fx)
        price_row = price_map.get(ticker, {})
        if price_row:
            row.update({
                "pricing_source": price_row.get("source"),
                "pricing_status": price_row.get("status"),
                "pricing_tier": price_row.get("pricing_tier"),
                "pricing_close_type": price_row.get("selected_close_type"),
                "price_date": price_row.get("returned_close_date"),
                "selected_close": price_row.get("selected_close") or price_row.get("price"),
            })
        total_market_value += _market_value_eur(row)
        prepared_positions.append(row)

    cash = _float(portfolio_state.get("cash_eur") or (runtime_state.get("portfolio") or {}).get("cash_eur"))
    nav = round(total_market_value + cash, 2)
    for row in prepared_positions:
        mv = _market_value_eur(row)
        weight = round(mv / nav * 100.0, 2) if nav else 0.0
        row["current_weight_pct"] = weight
        row["previous_weight_pct"] = weight
        row["weight_inherited_pct"] = weight
    prepared = dict(runtime_state)
    prepared["positions"] = prepared_positions
    prepared["portfolio"] = {
        "cash_eur": round(cash, 2),
        "total_portfolio_value_eur": nav,
        "base_currency": "EUR",
    }
    return prepared


def _requested_notional(intent: dict[str, Any], nav: float) -> float:
    requested = abs(_float(intent.get("estimated_notional_eur")))
    if requested <= 0 and nav > 0:
        requested = abs(_float(intent.get("delta_weight_pct"))) / 100.0 * nav
    return round(requested, 2)


def _available_source_value_eur(source_row: dict[str, Any]) -> float:
    return max(0.0, _market_value_eur(source_row))


def _execution_notional(intent: dict[str, Any], source_row: dict[str, Any], runtime_state: dict[str, Any]) -> tuple[float, float, bool, str]:
    nav = _nav(runtime_state)
    requested = _requested_notional(intent, nav)
    available = _available_source_value_eur(source_row)
    policy = _policy(runtime_state)
    max_source_reduction = _float(policy.get("max_single_source_reduction_pct_nav"), 5.0)
    policy_cap = nav * max_source_reduction / 100.0 if nav > 0 and max_source_reduction > 0 else requested
    actual = max(0.0, min(requested, available, policy_cap))
    capped = requested - actual > 1.0
    if capped and policy_cap <= requested and policy_cap <= available:
        cap_reason = "policy"
    elif capped:
        cap_reason = "available_value"
    else:
        cap_reason = ""
    return round(actual, 2), round(requested, 2), capped, cap_reason


def _validate_inputs(runtime_state: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    price_map = _pricing_map(runtime_state)
    position_map = _position_map(runtime_state)
    nav = _nav(runtime_state)
    policy = _policy(runtime_state)
    intents = _trade_intents(runtime_state)
    min_trade = _float(policy.get("min_trade_size_pct_nav"), 2.0)
    max_source_reduction = _float(policy.get("max_single_source_reduction_pct_nav"), 5.0)
    max_major = int(_float(policy.get("max_major_rotations_per_run"), 1.0))

    if nav <= 0:
        errors.append("runtime_nav_missing_or_non_positive")
    if not intents:
        warnings.append("no_trade_intents")
    if len(intents) > max_major:
        errors.append(f"major_rotation_count_exceeds_policy:{len(intents)}>{max_major}")

    for position in runtime_state.get("positions", []) or []:
        ticker = _ticker(position.get("ticker"))
        if not ticker:
            continue
        ok, reason = _valid_price_row(ticker, price_map)
        if not ok:
            errors.append(f"holding_price_invalid:{ticker}:{reason}")

    for intent in intents:
        source = _ticker(intent.get("source_ticker"))
        destination = _ticker(intent.get("destination_ticker"))
        source_delta = _float(intent.get("delta_weight_pct"))
        destination_delta = _float(intent.get("destination_delta_weight_pct"))
        if not source or not destination:
            errors.append("trade_intent_missing_source_or_destination")
            continue
        source_row = position_map.get(source)
        if source_row is None:
            errors.append(f"source_not_in_portfolio:{source}")
            continue
        for ticker in (source, destination):
            ok, reason = _valid_price_row(ticker, price_map)
            if not ok:
                errors.append(f"trade_price_invalid:{ticker}:{reason}")
        if source_delta >= 0:
            errors.append(f"source_delta_not_negative:{source}:{source_delta}")
        if destination_delta <= 0:
            errors.append(f"destination_delta_not_positive:{destination}:{destination_delta}")
        actual_notional, requested_notional, capped, cap_reason = _execution_notional(intent, source_row, runtime_state)
        actual_pct = actual_notional / nav * 100.0 if nav else 0.0
        if capped:
            if cap_reason == "policy":
                warnings.append(f"source_notional_capped_to_policy:{source}:{requested_notional:.2f}->{actual_notional:.2f}")
            else:
                warnings.append(f"source_notional_capped_to_available_value:{source}:{requested_notional:.2f}->{actual_notional:.2f}")
        if actual_notional <= 1.0:
            errors.append(f"source_has_no_executable_value:{source}:{actual_notional:.2f}")
        if actual_pct < min_trade:
            errors.append(f"trade_below_min_size_after_source_cap:{source}:{actual_pct:.2f}<{min_trade:.2f}")
        if actual_pct - max_source_reduction > 0.05:
            errors.append(f"source_reduction_exceeds_policy:{source}:{actual_pct:.2f}>{max_source_reduction:.2f}")
        action = _text(intent.get("action_code"))
        if action not in {"replace_partial", "replace_full", "reduce", "close", "add_from_cash"}:
            errors.append(f"unsupported_action_code:{action}")
    return errors, warnings


def _build_shadow_positions(runtime_state: dict[str, Any]) -> list[dict[str, Any]]:
    price_map = _pricing_map(runtime_state)
    positions = {ticker: _clear_run_fields(dict(row)) for ticker, row in _position_map(runtime_state).items()}
    fx = _fx(runtime_state)
    nav = _nav(runtime_state)
    for intent in _trade_intents(runtime_state):
        source = _ticker(intent.get("source_ticker"))
        destination = _ticker(intent.get("destination_ticker"))
        if not source or not destination or source not in positions:
            continue
        source_row = positions[source]
        executable_notional, requested_notional, capped, cap_reason = _execution_notional(intent, source_row, runtime_state)
        if executable_notional <= 0:
            continue
        actual_delta_pct = round(executable_notional / nav * 100.0, 4) if nav else 0.0

        source_price = _price_local(source, source_row, price_map)
        source_currency = _currency(source, source_row, price_map)
        source_shares_delta = -min(_float(source_row.get("shares")), _shares_for_notional(executable_notional, source_price, source_currency, fx))
        source_row = _mark_position(source_row, shares=_float(source_row.get("shares")) + source_shares_delta, price=source_price, currency=source_currency, nav=nav, fx=fx)
        source_row.update({
            "target_weight_pct": round(max(0.0, _float(source_row.get("current_weight_pct"))), 2),
            "shares_delta_this_run": round(source_shares_delta, 6),
            "weight_change_pct": round(-actual_delta_pct, 4),
            "action_executed_this_run": "Shadow reduce",
            "funding_source_note": "Shadow execution capped to source-reduction policy." if cap_reason == "policy" else "Shadow execution capped to available source value." if capped else "Shadow execution from rotation intent.",
        })
        positions[source] = source_row

        dest_price_row = price_map.get(destination, {})
        dest_price = _float(dest_price_row.get("selected_close") or dest_price_row.get("price"))
        dest_currency = _text(dest_price_row.get("currency") or "USD").upper()
        dest_base = _clear_run_fields(dict(positions.get(destination, {})))
        dest_shares_delta = _shares_for_notional(executable_notional, dest_price, dest_currency, fx)
        dest_base.update({
            "ticker": destination,
            "suggested_action": "Add from rotation",
            "portfolio_role": dest_base.get("portfolio_role") or "Rotation destination",
            "pricing_source": dest_price_row.get("source"),
            "pricing_status": dest_price_row.get("status"),
            "pricing_tier": dest_price_row.get("pricing_tier"),
            "pricing_close_type": dest_price_row.get("selected_close_type"),
            "price_date": dest_price_row.get("returned_close_date"),
            "selected_close": dest_price,
        })
        dest_base = _mark_position(dest_base, shares=_float(dest_base.get("shares")) + dest_shares_delta, price=dest_price, currency=dest_currency, nav=nav, fx=fx)
        dest_base.update({
            "target_weight_pct": round(_float(dest_base.get("current_weight_pct")), 2),
            "shares_delta_this_run": round(dest_shares_delta, 6),
            "weight_change_pct": round(actual_delta_pct, 4),
            "action_executed_this_run": "Shadow buy",
            "funding_source_note": f"Shadow buy funded by {source}.",
        })
        positions[destination] = dest_base
    return sorted(positions.values(), key=lambda row: _ticker(row.get("ticker")))


def _build_ledger_rows(runtime_state: dict[str, Any]) -> list[dict[str, Any]]:
    price_map = _pricing_map(runtime_state)
    position_map = _position_map(runtime_state)
    nav = _nav(runtime_state)
    run_id = _text(runtime_state.get("run_id"), "unknown")
    trade_date = _text(runtime_state.get("requested_close_date") or runtime_state.get("report_date"))
    rows: list[dict[str, Any]] = []
    for index, intent in enumerate(_trade_intents(runtime_state), start=1):
        source = _ticker(intent.get("source_ticker"))
        destination = _ticker(intent.get("destination_ticker"))
        source_row = position_map.get(source, {})
        actual_notional, requested_notional, capped, cap_reason = _execution_notional(intent, source_row, runtime_state) if source_row else (0.0, _requested_notional(intent, nav), False, "")
        source_weight = _float(source_row.get("current_weight_pct") or source_row.get("previous_weight_pct"))
        actual_delta_pct = actual_notional / nav * 100.0 if nav else 0.0
        rows.append({
            "trade_id": f"shadow-{trade_date}-{run_id}-{index:02d}-{source}-{destination}",
            "trade_date": trade_date,
            "execution_mode": "shadow",
            "source_ticker": source,
            "destination_ticker": destination,
            "action": _text(intent.get("action_code"), "unknown"),
            "source_delta_weight_pct": round(-actual_delta_pct, 4),
            "destination_delta_weight_pct": round(actual_delta_pct, 4),
            "estimated_notional_eur": round(actual_notional, 2),
            "requested_notional_eur": round(requested_notional, 2),
            "source_previous_weight_pct": round(source_weight, 4),
            "source_target_weight_pct": round(max(0.0, source_weight - actual_delta_pct), 4),
            "destination_target_weight_pct": round(actual_delta_pct, 4),
            "source_price_status": (price_map.get(source) or {}).get("status"),
            "destination_price_status": (price_map.get(destination) or {}).get("status"),
            "notional_capped": capped,
            "notional_capped_to_source_value": cap_reason == "available_value",
            "notional_cap_reason": cap_reason,
            "reason_codes": intent.get("reason_codes") or [],
        })
    return rows


def _read_ledger_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _write_ledger_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = [{field: row.get(field, "") for field in LEDGER_FIELDS} for row in rows]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS)
        writer.writeheader()
        writer.writerows(normalized)


def _official_ledger_rows(runtime_state: dict[str, Any], shadow_positions: list[dict[str, Any]], runtime_state_path: Path) -> list[dict[str, Any]]:
    original = _position_map(runtime_state)
    shadow = {_ticker(row.get("ticker")): row for row in shadow_positions}
    trade_date = _text(runtime_state.get("requested_close_date") or runtime_state.get("report_date"))
    run_id = _text(runtime_state.get("run_id"), "unknown")
    out: list[dict[str, Any]] = []
    for index, intent in enumerate(_trade_intents(runtime_state), start=1):
        source = _ticker(intent.get("source_ticker"))
        destination = _ticker(intent.get("destination_ticker"))
        for suffix, ticker, action in (("SELL", source, "Sell"), ("BUY", destination, "Buy")):
            before = original.get(ticker, {})
            after = shadow.get(ticker, {})
            if not ticker or not after:
                continue
            share_delta = _float(after.get("shares")) - _float(before.get("shares"))
            if abs(share_delta) <= 0.000001:
                continue
            previous_weight = _float(before.get("current_weight_pct") or before.get("previous_weight_pct"))
            new_weight = _float(after.get("current_weight_pct") or after.get("previous_weight_pct"))
            counterparty = destination if action == "Sell" else source
            note = f"Guarded auto-execution: {'reduce' if action == 'Sell' else 'buy'} {ticker} {'to fund' if action == 'Sell' else 'funded by'} {counterparty}."
            out.append({
                "trade_id": f"model-{trade_date}-{run_id}-{index:02d}-{ticker}-{suffix}",
                "trade_date": trade_date,
                "source_report": f"runtime:{runtime_state_path.name}",
                "ticker": ticker,
                "action": action,
                "shares_delta": f"{share_delta:.6f}",
                "previous_weight_pct": f"{previous_weight:.4f}",
                "new_weight_pct": f"{new_weight:.4f}",
                "weight_change_pct": f"{(new_weight - previous_weight):.4f}",
                "target_weight_pct": f"{_float(after.get('target_weight_pct'), new_weight):.4f}",
                "conviction_tier": _text(after.get("conviction_tier")),
                "portfolio_role": _text(after.get("portfolio_role")),
                "funding_source_note": note,
            })
    return out


def _guarded_positions(shadow_positions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in shadow_positions:
        item = dict(row)
        if item.get("action_executed_this_run") == "Shadow reduce":
            item["action_executed_this_run"] = "Sell"
        elif item.get("action_executed_this_run") == "Shadow buy":
            item["action_executed_this_run"] = "Buy"
        else:
            item = _clear_run_fields(item)
        if _float(item.get("shares")) <= 0.000001 and _market_value_eur(item) <= 1.0:
            continue
        out.append(item)
    return out


def _execute_guarded_auto(runtime_state: dict[str, Any], runtime_state_path: Path, portfolio_state_path: Path, trade_ledger_path: Path, shadow_positions: list[dict[str, Any]]) -> dict[str, Any]:
    if not _trade_intents(runtime_state):
        return {"official_ledger_rows": [], "portfolio_state_written": False, "trade_ledger_written": False}
    existing_state = _read_json(portfolio_state_path) if portfolio_state_path.exists() else {}
    official_positions = _guarded_positions(shadow_positions)
    cash = _float((existing_state.get("cash_eur") if existing_state else None) or (runtime_state.get("portfolio") or {}).get("cash_eur"))
    invested = round(sum(_market_value_eur(row) for row in official_positions), 2)
    nav = round(invested + cash, 2)
    persisted = dict(existing_state)
    persisted.update({
        "schema_version": _text(existing_state.get("schema_version"), "1.1"),
        "portfolio_mode": _text(existing_state.get("portfolio_mode"), "client_long_only_thematic"),
        "base_currency": "EUR",
        "valuation_source": "guarded_model_execution_v1",
        "cash_eur": round(cash, 2),
        "invested_market_value_eur": invested,
        "nav_eur": nav,
        "peak_nav_eur": max(_float(existing_state.get("peak_nav_eur"), nav), nav),
        "positions": official_positions,
        "last_model_execution": {
            "date": _text(runtime_state.get("requested_close_date") or runtime_state.get("report_date")),
            "run_id": runtime_state.get("run_id"),
            "runtime_state": str(runtime_state_path),
            "mode": "guarded_auto",
            "trade_count": len(_trade_intents(runtime_state)),
            "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        },
    })
    official_rows = _official_ledger_rows(runtime_state, shadow_positions, runtime_state_path)
    existing_rows = _read_ledger_rows(trade_ledger_path)
    existing_ids = {row.get("trade_id") for row in existing_rows}
    rows_to_append = [row for row in official_rows if row.get("trade_id") not in existing_ids]
    _write_ledger_rows(trade_ledger_path, existing_rows + rows_to_append)
    _write_json(portfolio_state_path, persisted)
    return {
        "official_ledger_rows": rows_to_append,
        "portfolio_state_written": True,
        "trade_ledger_written": True,
        "post_trade_nav_eur": nav,
        "post_trade_invested_market_value_eur": invested,
        "post_trade_cash_eur": round(cash, 2),
    }


def build_execution_artifact(runtime_state_path: Path, portfolio_state_path: Path, trade_ledger_path: Path, mode: str, output_dir: Path) -> dict[str, Any]:
    runtime_state = _prepare_runtime_state(_read_json(runtime_state_path), portfolio_state_path)
    errors, warnings = _validate_inputs(runtime_state)
    shadow_positions = _build_shadow_positions(runtime_state) if not errors else []
    nav = _nav(runtime_state)
    invested = round(sum(_market_value_eur(row) for row in shadow_positions), 2) if shadow_positions else 0.0
    cash = _float((runtime_state.get("portfolio") or {}).get("cash_eur"))
    intents = _trade_intents(runtime_state)
    status = "no_trade_intents" if not errors and not intents else "shadow_ready" if mode == "shadow" and not errors else "blocked" if errors else "ready_for_guarded_auto"
    artifact = {
        "schema_version": "1.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "execution_mode": mode,
        "execution_status": status,
        "run_id": runtime_state.get("run_id"),
        "report_date": runtime_state.get("report_date"),
        "requested_close_date": runtime_state.get("requested_close_date"),
        "source_files": {
            "runtime_state": str(runtime_state_path),
            "portfolio_state": str(portfolio_state_path),
            "trade_ledger": str(trade_ledger_path),
            "pricing_audit": (runtime_state.get("source_files") or {}).get("pricing_audit"),
            "rotation_plan": (runtime_state.get("source_files") or {}).get("rotation_plan"),
        },
        "policy_checks": {
            "passed": not errors,
            "errors": errors,
            "warnings": warnings,
            "mode_note": "Shadow mode writes no official portfolio-state or trade-ledger changes." if mode == "shadow" else "Guarded auto-execution writes official model trade-ledger and portfolio-state changes when all hard gates pass.",
        },
        "pre_trade_portfolio": runtime_state.get("portfolio"),
        "post_trade_shadow_portfolio": {
            "cash_eur": round(cash, 2),
            "invested_market_value_eur": invested,
            "nav_eur": round(invested + cash, 2) if shadow_positions else None,
            "nav_drift_eur": round((invested + cash) - nav, 2) if shadow_positions else None,
        },
        "proposed_ledger_rows": _build_ledger_rows(runtime_state) if not errors else [],
        "shadow_positions": shadow_positions,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    report_token = _text(runtime_state.get("report_date") or runtime_state.get("requested_close_date"), "unknown").replace("-", "")
    run_id = _text(runtime_state.get("run_id"), "unknown")
    out_path = output_dir / f"etf_model_execution_{report_token}_{run_id}.json"
    artifact["artifact_path"] = str(out_path)
    if mode == "guarded_auto" and not errors and intents:
        result = _execute_guarded_auto(runtime_state, runtime_state_path, portfolio_state_path, trade_ledger_path, shadow_positions)
        artifact["execution_status"] = "executed"
        artifact["guarded_auto_result"] = result
    _write_json(out_path, artifact)
    (output_dir / "latest_etf_model_execution_path.txt").write_text(str(out_path) + "\n", encoding="utf-8")
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(description="Build ETF model execution artifact from rotation trade intents.")
    parser.add_argument("--runtime-state", required=True)
    parser.add_argument("--portfolio-state", default="output/etf_portfolio_state.json")
    parser.add_argument("--trade-ledger", default="output/etf_trade_ledger.csv")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--mode", choices=["shadow", "guarded_auto"], default="shadow")
    args = parser.parse_args()

    artifact = build_execution_artifact(Path(args.runtime_state), Path(args.portfolio_state), Path(args.trade_ledger), args.mode, Path(args.output_dir))
    if artifact["policy_checks"]["errors"]:
        message = "ETF_MODEL_EXECUTION_BLOCKED | artifact=" + artifact["artifact_path"] + " | errors=" + ";".join(artifact["policy_checks"]["errors"])
        print(message)
        print(message, file=sys.stderr)
        raise SystemExit(1)
    print(
        "ETF_MODEL_EXECUTION_OK | "
        f"artifact={artifact['artifact_path']} | "
        f"mode={artifact.get('execution_mode')} | "
        f"trades={len(artifact.get('proposed_ledger_rows', []))} | "
        f"status={artifact.get('execution_status')}"
    )


if __name__ == "__main__":
    main()
