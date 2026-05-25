from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_PORTFOLIO_STATE = Path("output/etf_portfolio_state.json")
DEFAULT_VALUATION_HISTORY = Path("output/etf_valuation_history.csv")
HISTORY_FIELDS = [
    "date",
    "nav_eur",
    "cash_eur",
    "invested_market_value_eur",
    "daily_return_pct",
    "since_inception_return_pct",
    "drawdown_pct",
    "eurusd_used",
    "comment",
    "source_report",
]

PRICED_STATUSES = {
    "fresh_close",  # legacy
    "fresh_fallback_source",  # legacy
    "fresh_exact_close",
    "fresh_exact_unverified",
    "prior_valid_close",
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return default


def _round(value: Any, digits: int = 2) -> float:
    return round(_float(value), digits)


def _text(value: Any, fallback: str = "") -> str:
    raw = str(value or "").strip()
    return raw or fallback


def _ticker(value: Any) -> str:
    return _text(value).upper()


def _source_report_name(path_value: str | None) -> str:
    if not path_value:
        return ""
    return Path(path_value).name


def _fx_rate(runtime_state: dict[str, Any]) -> float | None:
    raw = (runtime_state.get("fx_basis") or {}).get("rate")
    if raw is None or raw == "":
        return None
    return _round(raw, 4)


def _history_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


def _write_history_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized: list[dict[str, Any]] = []
    for row in rows:
        normalized.append({field: row.get(field, "") for field in HISTORY_FIELDS})
    normalized.sort(key=lambda row: str(row.get("date") or ""))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=HISTORY_FIELDS)
        writer.writeheader()
        writer.writerows(normalized)


def _position_price_map(runtime_state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        _ticker(row.get("symbol")): dict(row)
        for row in runtime_state.get("pricing", []) or []
        if _ticker(row.get("symbol"))
    }


def _runtime_positions(runtime_state: dict[str, Any]) -> list[dict[str, Any]]:
    positions = []
    price_map = _position_price_map(runtime_state)
    for row in runtime_state.get("positions", []) or []:
        ticker = _ticker(row.get("ticker"))
        if not ticker or ticker == "CASH":
            continue
        item = dict(row)
        item["ticker"] = ticker
        if ticker in price_map:
            item["_price_row"] = price_map[ticker]
        positions.append(item)
    return positions


def _compute_nav(runtime_state: dict[str, Any]) -> tuple[float, float, float]:
    cash = _round((runtime_state.get("portfolio") or {}).get("cash_eur"), 2)
    invested = round(sum(_float(row.get("previous_market_value_eur")) for row in _runtime_positions(runtime_state)), 2)
    nav = round(invested + cash, 2)
    runtime_nav = _float((runtime_state.get("portfolio") or {}).get("total_portfolio_value_eur"), nav)
    if abs(runtime_nav - nav) > 0.05:
        raise RuntimeError(f"Runtime NAV mismatch: positions+cash={nav:.2f}, runtime_portfolio={runtime_nav:.2f}")
    return cash, invested, nav


def _update_positions(existing_state: dict[str, Any], runtime_state: dict[str, Any], nav: float) -> list[dict[str, Any]]:
    existing_by_ticker = {
        _ticker(row.get("ticker")): dict(row)
        for row in existing_state.get("positions", []) or []
        if _ticker(row.get("ticker"))
    }
    updated: list[dict[str, Any]] = []
    for row in _runtime_positions(runtime_state):
        ticker = _ticker(row.get("ticker"))
        base = dict(existing_by_ticker.get(ticker, {}))
        base.update({k: v for k, v in row.items() if not k.startswith("_")})

        price_row = row.get("_price_row") or {}
        price = _float(base.get("current_price_local") or base.get("previous_price_local"))
        market_value_local = _float(base.get("market_value_local") or base.get("previous_market_value_local"))
        market_value_eur = _float(base.get("market_value_eur") or base.get("previous_market_value_eur"))
        weight = round((market_value_eur / nav * 100.0), 2) if nav else 0.0

        base["ticker"] = ticker
        base["current_price_local"] = round(price, 4)
        base["continuity_current_price_local"] = round(price, 4)
        base["previous_price_local"] = round(price, 4)
        base["market_value_local"] = round(market_value_local, 2)
        base["previous_market_value_local"] = round(market_value_local, 2)
        base["market_value_eur"] = round(market_value_eur, 2)
        base["previous_market_value_eur"] = round(market_value_eur, 2)
        base["current_weight_pct"] = weight
        base["previous_weight_pct"] = weight
        base["weight_inherited_pct"] = weight
        base["target_weight_pct"] = round(_float(base.get("target_weight_pct"), weight), 2)
        base["pricing_source"] = price_row.get("source") or base.get("pricing_source")
        base["pricing_status"] = price_row.get("status") or base.get("pricing_status")
        base["pricing_close_type"] = price_row.get("selected_close_type") or base.get("pricing_close_type")
        base["pricing_tier"] = price_row.get("pricing_tier") or base.get("pricing_tier")
        base["price_date"] = price_row.get("returned_close_date") or base.get("price_date")
        base["selected_close"] = price_row.get("selected_close") if price_row.get("selected_close") is not None else base.get("selected_close", price)
        base["action_executed_this_run"] = base.get("action_executed_this_run") or "None"
        updated.append(base)
    return updated


def _numeric_history(rows: list[dict[str, Any]]) -> list[tuple[str, float]]:
    out: list[tuple[str, float]] = []
    for row in rows:
        date = _text(row.get("date"))
        nav = _float(row.get("nav_eur"), default=-1.0)
        if date and nav >= 0:
            out.append((date, nav))
    return sorted(out, key=lambda item: item[0])


def _build_history_row(
    existing_rows_without_current: list[dict[str, Any]],
    runtime_state: dict[str, Any],
    source_report: str,
    cash: float,
    invested: float,
    nav: float,
) -> dict[str, Any]:
    report_date = _text(runtime_state.get("requested_close_date") or runtime_state.get("report_date"))
    if not report_date:
        raise RuntimeError("Runtime state has no requested_close_date/report_date for valuation-history persistence.")

    numeric = _numeric_history(existing_rows_without_current)
    previous_nav = numeric[-1][1] if numeric else nav
    starting_nav = numeric[0][1] if numeric else 100000.0
    previous_peak = max([value for _date, value in numeric] + [nav]) if numeric else nav
    peak = max(previous_peak, nav)
    daily_return_pct = 0.0 if previous_nav == 0 else round((nav / previous_nav - 1.0) * 100.0, 4)
    since_inception_pct = 0.0 if starting_nav == 0 else round((nav / starting_nav - 1.0) * 100.0, 4)
    drawdown_pct = 0.0 if peak == 0 else round((nav / peak - 1.0) * 100.0, 4)
    eurusd = _fx_rate(runtime_state)

    return {
        "date": report_date,
        "nav_eur": round(nav, 2),
        "cash_eur": round(cash, 2),
        "invested_market_value_eur": round(invested, 2),
        "daily_return_pct": daily_return_pct,
        "since_inception_return_pct": since_inception_pct,
        "drawdown_pct": drawdown_pct,
        "eurusd_used": "" if eurusd is None else eurusd,
        "comment": "Runtime valuation from immutable pricing audit and explicit portfolio state",
        "source_report": source_report,
    }


def persist_state(
    runtime_state_path: Path,
    portfolio_state_path: Path,
    valuation_history_path: Path,
    pricing_audit_path: Path | None,
    english_report_path: Path | None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    runtime_state = _read_json(runtime_state_path)
    existing_state = _read_json(portfolio_state_path) if portfolio_state_path.exists() else {}
    report_date = _text(runtime_state.get("requested_close_date") or runtime_state.get("report_date"))
    source_report = _source_report_name(str(english_report_path)) or _source_report_name(runtime_state.get("source_files", {}).get("report"))
    pricing_audit_file = str(pricing_audit_path or runtime_state.get("source_files", {}).get("pricing_audit") or "")

    cash, invested, nav = _compute_nav(runtime_state)
    positions = _update_positions(existing_state, runtime_state, nav)
    if not positions:
        raise RuntimeError("No runtime positions available for portfolio-state persistence.")

    history_rows = _history_rows(valuation_history_path)
    rows_without_current = [row for row in history_rows if _text(row.get("date")) != report_date]
    current_history_row = _build_history_row(rows_without_current, runtime_state, source_report, cash, invested, nav)
    new_history_rows = rows_without_current + [current_history_row]
    numeric_after = _numeric_history(new_history_rows)
    peak_nav = max(value for _date, value in numeric_after) if numeric_after else nav
    max_drawdown = min(_float(row.get("drawdown_pct"), 0.0) for row in new_history_rows) if new_history_rows else 0.0

    persisted = dict(existing_state)
    persisted["schema_version"] = str(existing_state.get("schema_version") or "1.1")
    persisted["portfolio_mode"] = existing_state.get("portfolio_mode") or "client_long_only_thematic"
    persisted["base_currency"] = "EUR"
    persisted["valuation_source"] = "runtime_pricing_lineage_state_v1"
    persisted["pricing_audit_file"] = pricing_audit_file or None
    persisted["trade_ledger_file"] = existing_state.get("trade_ledger_file") or "etf_trade_ledger.csv"
    persisted["recommendation_scorecard_file"] = existing_state.get("recommendation_scorecard_file")
    persisted["inception_date"] = existing_state.get("inception_date") or (numeric_after[0][0] if numeric_after else report_date)
    persisted["starting_capital_eur"] = _round(existing_state.get("starting_capital_eur"), 2) or 100000.0
    persisted["cash_eur"] = round(cash, 2)
    persisted["invested_market_value_eur"] = round(invested, 2)
    persisted["nav_eur"] = round(nav, 2)
    persisted["peak_nav_eur"] = round(peak_nav, 2)
    persisted["max_drawdown_pct"] = round(max_drawdown, 4)
    persisted["positions"] = positions
    persisted["last_report"] = {
        "date": report_date,
        "source_report": source_report,
        "position_count": len(positions),
    }
    persisted["last_valuation"] = {
        "date": report_date,
        "nav_eur": round(nav, 2),
        "invested_market_value_eur": round(invested, 2),
        "cash_eur": round(cash, 2),
        "since_inception_return_pct": current_history_row["since_inception_return_pct"],
        "daily_return_pct": current_history_row["daily_return_pct"],
        "drawdown_pct": current_history_row["drawdown_pct"],
        "eurusd_used": current_history_row["eurusd_used"],
        "equity_curve_state": "New high" if round(nav, 2) >= round(peak_nav, 2) else "Below prior high",
        "valuation_notes": current_history_row["comment"],
    }
    persisted["last_successful_runtime_state_file"] = str(runtime_state_path)
    persisted["last_state_persisted_at_utc"] = datetime.now(timezone.utc).isoformat()

    _write_json(portfolio_state_path, persisted)
    _write_history_rows(valuation_history_path, new_history_rows)
    return persisted, new_history_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Persist successful ETF runtime valuation into canonical state files.")
    parser.add_argument("--runtime-state", required=True)
    parser.add_argument("--pricing-audit", default=None)
    parser.add_argument("--english-report", default=None)
    parser.add_argument("--portfolio-state", default=str(DEFAULT_PORTFOLIO_STATE))
    parser.add_argument("--valuation-history", default=str(DEFAULT_VALUATION_HISTORY))
    args = parser.parse_args()

    runtime_state_path = Path(args.runtime_state)
    pricing_audit_path = Path(args.pricing_audit) if args.pricing_audit else None
    english_report_path = Path(args.english_report) if args.english_report else None
    portfolio_state_path = Path(args.portfolio_state)
    valuation_history_path = Path(args.valuation_history)

    persisted, history_rows = persist_state(
        runtime_state_path=runtime_state_path,
        portfolio_state_path=portfolio_state_path,
        valuation_history_path=valuation_history_path,
        pricing_audit_path=pricing_audit_path,
        english_report_path=english_report_path,
    )
    print(
        "ETF_VALUATION_STATE_PERSISTED | "
        f"date={persisted.get('last_valuation', {}).get('date')} | "
        f"nav={persisted.get('nav_eur')} | "
        f"positions={len(persisted.get('positions', []))} | "
        f"history_rows={len(history_rows)} | "
        f"portfolio_state={portfolio_state_path} | valuation_history={valuation_history_path}"
    )


if __name__ == "__main__":
    main()
