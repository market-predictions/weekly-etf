from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

DEFAULT_TRADE_LEDGER = Path("output/etf_trade_ledger.csv")
DEFAULT_RUNTIME_DIR = Path("output/runtime")

PRICED_VALUATION_STATUSES = {
    "fresh_close",
    "fresh_fallback_source",
    "fresh_exact_close",
    "fresh_exact_unverified",
    "prior_valid_close",
}

SCORECARD_FIELDNAMES = [
    "report_date",
    "ticker",
    "weight_pct",
    "shares",
    "current_price_local",
    "currency",
    "market_value_eur",
    "pnl_pct",
    "total_score",
    "suggested_action",
    "conviction_tier",
    "portfolio_role",
    "fresh_cash_test",
    "would_initiate_today",
    "would_initiate_at_current_weight",
    "thesis_score",
    "implementation_score",
    "replaceable_status",
    "weeks_replaceable",
    "best_alternative",
    "alternative_score",
    "contribution_quality",
    "factor_overlap_flag",
    "hedge_validity_status",
    "cash_policy_flag",
    "required_next_action",
    "override_reason",
    "discipline_flags",
    "source_report",
]


def ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def number(value: Any, default: float | None = None) -> float | None:
    if value in (None, ""):
        return default
    try:
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default


def selected_price(row: dict[str, Any]) -> float | None:
    return number(row.get("selected_close"), number(row.get("price")))


def index_price_results(pricing_audit: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = pricing_audit.get("price_results", []) or pricing_audit.get("prices", []) or []
    return {ticker(row.get("symbol")): row for row in rows if ticker(row.get("symbol"))}


def fx_rate(pricing_audit: dict[str, Any]) -> float | None:
    return number((pricing_audit.get("fx_basis") or {}).get("rate"))


def recompute_pnl_pct(current_price: Any, avg_entry: Any) -> float | None:
    current = number(current_price)
    entry = number(avg_entry)
    if current is None or entry is None or entry <= 0:
        return None
    return round((current / entry - 1.0) * 100.0, 2)


def _execution_artifact_path(source_report: str, runtime_dir: Path) -> Path | None:
    raw = str(source_report or "").strip()
    if not raw.startswith("runtime:"):
        return None
    source_name = Path(raw.removeprefix("runtime:")).name
    if not source_name.startswith("etf_report_state_"):
        return None
    return runtime_dir / source_name.replace(
        "etf_report_state_", "etf_model_execution_", 1
    )


def _execution_positions(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in ("executed_positions", "shadow_positions", "positions"):
        value = payload.get(key)
        if isinstance(value, list):
            rows.extend(row for row in value if isinstance(row, dict))
    for key in ("post_trade_portfolio", "post_trade_shadow_portfolio", "result"):
        nested = payload.get(key)
        if not isinstance(nested, dict):
            continue
        value = nested.get("positions")
        if isinstance(value, list):
            rows.extend(row for row in value if isinstance(row, dict))
    return rows


def reconstruct_average_entry_local(
    symbol: str,
    trade_ledger_path: Path = DEFAULT_TRADE_LEDGER,
    runtime_dir: Path = DEFAULT_RUNTIME_DIR,
) -> float | None:
    if not trade_ledger_path.exists():
        return None
    lots: list[tuple[float, float]] = []
    with trade_ledger_path.open("r", encoding="utf-8", newline="") as handle:
        for ledger_row in csv.DictReader(handle):
            if ticker(ledger_row.get("ticker")) != ticker(symbol):
                continue
            shares_delta = number(ledger_row.get("shares_delta"))
            if shares_delta is None or shares_delta <= 0:
                continue
            artifact_path = _execution_artifact_path(
                str(ledger_row.get("source_report") or ""), runtime_dir
            )
            if artifact_path is None or not artifact_path.exists():
                continue
            try:
                payload = json.loads(artifact_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            matching = [
                row
                for row in _execution_positions(payload)
                if ticker(row.get("ticker")) == ticker(symbol)
            ]
            if not matching:
                continue
            positive = [
                row
                for row in matching
                if (number(row.get("shares_delta_this_run"), 0.0) or 0.0) > 0
            ]
            selected = positive[0] if positive else matching[0]
            execution_price = number(
                selected.get("selected_close"),
                number(selected.get("current_price_local")),
            )
            if execution_price is None or execution_price <= 0:
                continue
            lots.append((shares_delta, execution_price))
    total_shares = sum(shares for shares, _ in lots)
    if total_shares <= 0:
        return None
    return round(
        sum(shares * price for shares, price in lots) / total_shares, 6
    )


def build_current_run_valuation_state(
    portfolio_state: dict[str, Any],
    pricing_audit: dict[str, Any],
    *,
    trade_ledger_path: Path = DEFAULT_TRADE_LEDGER,
    runtime_dir: Path = DEFAULT_RUNTIME_DIR,
) -> dict[str, Any]:
    prices = index_price_results(pricing_audit)
    fx = fx_rate(pricing_audit)
    positions: list[dict[str, Any]] = []
    invested = 0.0
    errors: list[str] = []

    for raw in portfolio_state.get("positions", []) or []:
        symbol = ticker(raw.get("ticker"))
        if not symbol:
            continue
        row = dict(raw)
        price_row = prices.get(symbol)
        if not price_row:
            errors.append(f"{symbol}:missing_current_price")
            continue
        status = str(price_row.get("status") or "")
        price = selected_price(price_row)
        if status not in PRICED_VALUATION_STATUSES or price is None:
            errors.append(f"{symbol}:non_valuation_grade_current_price")
            continue
        shares = number(row.get("shares"))
        if shares is None:
            errors.append(f"{symbol}:missing_shares")
            continue

        currency = str(price_row.get("currency") or row.get("currency") or "USD").upper()
        market_value_local = round(shares * price, 2)
        if currency == "EUR":
            market_value_eur = market_value_local
        elif fx and fx > 0:
            market_value_eur = round(market_value_local / fx, 2)
        else:
            errors.append(f"{symbol}:missing_fx_rate")
            continue

        avg_entry = number(row.get("avg_entry_local"))
        avg_entry_source = "portfolio_state"
        if avg_entry is None or avg_entry <= 0:
            avg_entry = reconstruct_average_entry_local(
                symbol,
                trade_ledger_path=trade_ledger_path,
                runtime_dir=runtime_dir,
            )
            avg_entry_source = "model_execution_history"
        if avg_entry is None or avg_entry <= 0:
            errors.append(f"{symbol}:missing_average_entry_authority")
            continue
        pnl = recompute_pnl_pct(price, avg_entry)
        row.update(
            {
                "ticker": symbol,
                "current_price_local": price,
                "previous_price_local": price,
                "continuity_current_price_local": price,
                "currency": currency,
                "market_value_local": market_value_local,
                "previous_market_value_local": market_value_local,
                "market_value_eur": market_value_eur,
                "previous_market_value_eur": market_value_eur,
                "pricing_source": price_row.get("source"),
                "pricing_status": status,
                "pricing_tier": price_row.get("pricing_tier"),
                "pricing_close_type": price_row.get("selected_close_type"),
                "price_date": price_row.get("returned_close_date")
                or pricing_audit.get("requested_close_date"),
                "selected_close": price,
                "avg_entry_local": avg_entry,
                "avg_entry_source": avg_entry_source,
                "pnl_pct": pnl,
                "pnl_basis": "current_close_vs_avg_entry",
            }
        )
        invested += market_value_eur
        positions.append(row)

    if errors:
        raise RuntimeError("ETF current-run valuation authority failed: " + "; ".join(errors))

    cash = number(portfolio_state.get("cash_eur"), 0.0) or 0.0
    nav = round(invested + cash, 2)
    for row in positions:
        mv = number(row.get("market_value_eur"), 0.0) or 0.0
        weight = round(mv / nav * 100.0, 2) if nav else 0.0
        row["current_weight_pct"] = weight
        row["previous_weight_pct"] = weight
        row["weight_inherited_pct"] = weight
        row.setdefault("target_weight_pct", weight)

    report_date = str(
        pricing_audit.get("requested_close_date")
        or portfolio_state.get("last_report", {}).get("date")
        or ""
    )
    return {
        "schema_version": "1.0",
        "report_date": report_date,
        "run_id": pricing_audit.get("run_id"),
        "portfolio": {
            "cash_eur": round(cash, 2),
            "invested_market_value_eur": round(invested, 2),
            "total_portfolio_value_eur": nav,
            "base_currency": "EUR",
        },
        "positions": positions,
        "validation_flags": {
            "current_run_prices_used": True,
            "current_run_weights_recomputed": True,
            "pnl_recomputed_from_avg_entry": True,
            "average_entry_authority_complete": True,
            "prior_persisted_market_values_not_authoritative": True,
        },
    }


def _contribution_quality(pnl: float | None) -> str:
    if pnl is None:
        return "Unresolved"
    if pnl > 10:
        return "Strong positive contributor"
    if pnl > 3:
        return "Positive contributor"
    if pnl >= -3:
        return "Flat / opportunity-cost review"
    if pnl > -10:
        return "Negative contributor"
    return "Material drag"


def _replaceable(position: dict[str, Any], prior: dict[str, Any]) -> bool:
    action = str(position.get("suggested_action") or prior.get("suggested_action") or "").lower()
    fresh = str(position.get("fresh_cash_test") or prior.get("fresh_cash_test") or "").lower()
    better = str(
        position.get("better_alternative_exists")
        or prior.get("better_alternative_exists")
        or ""
    ).lower()
    return (
        "review" in action
        or "reduce" in action
        or "replace" in action
        or "no" in fresh
        or "reduce" in fresh
        or "smaller" in fresh
        or better == "yes"
    )


def _discipline_flags(
    position: dict[str, Any], prior: dict[str, Any], replaceable: bool
) -> str:
    flags = {
        part
        for part in str(prior.get("discipline_flags") or "").split(";")
        if part
    }
    pnl = number(position.get("pnl_pct"))
    if replaceable:
        flags.add("replaceable")
    else:
        flags.discard("replaceable")
    if pnl is not None and pnl < -10:
        flags.add("loss_gt_10pct")
    else:
        flags.discard("loss_gt_10pct")
    if ticker(position.get("ticker")) in {"SPY", "SMH"}:
        flags.add("factor_overlap")
    return ";".join(sorted(flags))


def refresh_scorecard_rows(
    previous_rows: list[dict[str, Any]],
    current_positions: list[dict[str, Any]],
    report_date: str,
    source: str,
) -> list[dict[str, str]]:
    previous = {
        ticker(row.get("ticker")): dict(row)
        for row in previous_rows
        if ticker(row.get("ticker"))
    }
    refreshed: list[dict[str, str]] = []
    for position in current_positions:
        symbol = ticker(position.get("ticker"))
        prior = previous.get(symbol, {})
        row = {name: str(prior.get(name) or "") for name in SCORECARD_FIELDNAMES}
        replaceable = _replaceable(position, prior)
        prior_weeks = int(number(prior.get("weeks_replaceable"), 0.0) or 0)
        same_date = str(prior.get("report_date") or "") == report_date
        weeks = prior_weeks if same_date else (prior_weeks + 1 if replaceable else 0)
        if not replaceable:
            weeks = 0
        pnl = number(position.get("pnl_pct"))
        row.update(
            {
                "report_date": report_date,
                "ticker": symbol,
                "weight_pct": f"{(number(position.get('current_weight_pct'), 0.0) or 0.0):.2f}",
                "shares": f"{(number(position.get('shares'), 0.0) or 0.0):.6f}",
                "current_price_local": f"{(number(position.get('current_price_local'), 0.0) or 0.0):.6f}",
                "currency": str(
                    position.get("currency") or prior.get("currency") or "USD"
                ),
                "market_value_eur": f"{(number(position.get('market_value_eur'), 0.0) or 0.0):.2f}",
                "pnl_pct": "" if pnl is None else f"{pnl:.2f}",
                "total_score": str(
                    position.get("total_score") or prior.get("total_score") or ""
                ),
                "suggested_action": str(
                    position.get("suggested_action")
                    or prior.get("suggested_action")
                    or ""
                ),
                "conviction_tier": str(
                    position.get("conviction_tier")
                    or prior.get("conviction_tier")
                    or ""
                ),
                "portfolio_role": str(
                    position.get("portfolio_role")
                    or prior.get("portfolio_role")
                    or ""
                ),
                "fresh_cash_test": str(
                    position.get("fresh_cash_test")
                    or prior.get("fresh_cash_test")
                    or ""
                ),
                "thesis_score": str(
                    position.get("thesis_score") or prior.get("thesis_score") or ""
                ),
                "implementation_score": str(
                    position.get("implementation_score")
                    or prior.get("implementation_score")
                    or ""
                ),
                "replaceable_status": "Hold under review" if replaceable else "None",
                "weeks_replaceable": str(weeks),
                "best_alternative": str(
                    position.get("best_alternative")
                    or prior.get("best_alternative")
                    or ""
                ),
                "contribution_quality": _contribution_quality(pnl),
                "factor_overlap_flag": str(
                    position.get("factor_overlap_flag")
                    or prior.get("factor_overlap_flag")
                    or ""
                ),
                "hedge_validity_status": str(
                    position.get("hedge_validity_status")
                    or prior.get("hedge_validity_status")
                    or ""
                ),
                "cash_policy_flag": str(
                    position.get("cash_policy_flag")
                    or prior.get("cash_policy_flag")
                    or ""
                ),
                "required_next_action": str(
                    position.get("required_next_action")
                    or prior.get("required_next_action")
                    or ""
                ),
                "override_reason": str(
                    position.get("override_reason")
                    or prior.get("override_reason")
                    or ""
                ),
                "discipline_flags": _discipline_flags(
                    position, prior, replaceable
                ),
                "source_report": source,
            }
        )
        refreshed.append(row)
    return refreshed


def write_scorecard(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SCORECARD_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def validate_current_run_authority(
    scorecard_rows: list[dict[str, Any]],
    positions: list[dict[str, Any]],
    report_date: str,
    pnl_tolerance_pct: float = 0.05,
) -> dict[str, Any]:
    errors: list[str] = []
    by_ticker = {
        ticker(row.get("ticker")): row
        for row in scorecard_rows
        if ticker(row.get("ticker"))
    }
    for position in positions:
        symbol = ticker(position.get("ticker"))
        row = by_ticker.get(symbol)
        if row is None:
            errors.append(f"{symbol}:missing_scorecard_row")
            continue
        if str(row.get("report_date") or "") != report_date:
            errors.append(f"{symbol}:scorecard_date_mismatch")
        expected_pnl = recompute_pnl_pct(
            position.get("current_price_local"), position.get("avg_entry_local")
        )
        actual_pnl = number(row.get("pnl_pct"))
        if expected_pnl is None:
            errors.append(f"{symbol}:missing_average_entry_authority")
        elif actual_pnl is None or abs(actual_pnl - expected_pnl) > pnl_tolerance_pct:
            errors.append(
                f"{symbol}:pnl_mismatch expected={expected_pnl:.2f} actual={actual_pnl}"
            )
        scorecard_price = number(row.get("current_price_local"))
        current_price = number(position.get("current_price_local"))
        if current_price is not None and (
            scorecard_price is None
            or abs(scorecard_price - current_price) > 0.0001
        ):
            errors.append(f"{symbol}:current_price_mismatch")
    if errors:
        raise RuntimeError(
            "ETF rotation state authority validation failed: " + "; ".join(errors)
        )
    return {
        "scorecard_date_aligned": True,
        "pnl_consistent_with_current_close_and_avg_entry": True,
        "average_entry_authority_complete": True,
        "current_price_consistent": True,
        "validated_holding_count": len(positions),
        "report_date": report_date,
    }
