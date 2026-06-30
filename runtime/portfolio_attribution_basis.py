from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

DEFAULT_TRADE_LEDGER_PATH = Path("output/etf_trade_ledger.csv")


def to_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(str(value).replace(",", "").replace("%", ""))
    except (TypeError, ValueError):
        return None


def position_by_ticker(state: dict[str, Any], ticker: str) -> dict[str, Any] | None:
    ticker = ticker.upper()
    for position in state.get("positions", []) or []:
        if str(position.get("ticker") or "").upper() == ticker:
            return position
    return None


def runtime_state_path(source_report: str) -> Path | None:
    source_report = source_report.strip()
    if not source_report.startswith("runtime:"):
        return None
    raw = source_report.removeprefix("runtime:").strip()
    return Path(raw) if raw else None


def runtime_trade_price(runtime_path: Path, ticker: str) -> tuple[float, str, float | None] | None:
    if not runtime_path.exists():
        return None
    try:
        payload = json.loads(runtime_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    position = position_by_ticker(payload, ticker)
    if not position:
        return None
    price = to_float(position.get("selected_close") or position.get("current_price_local") or position.get("previous_price_local"))
    if price is None:
        return None
    currency = str(position.get("currency") or "USD").upper()
    fx_rate = to_float((payload.get("fx_basis") or {}).get("rate"))
    return price, currency, fx_rate


def local_to_eur(local_value: float, currency: str, fx_rate: float | None) -> float | None:
    if currency.upper() == "EUR":
        return local_value
    if fx_rate is None or fx_rate <= 0:
        return None
    return local_value / fx_rate


def explicit_entry_basis(position: dict[str, Any], state: dict[str, Any]) -> dict[str, float] | None:
    shares = to_float(position.get("shares"))
    avg_entry = to_float(position.get("avg_entry_local"))
    currency = str(position.get("currency") or "USD").upper()
    fx_rate = to_float((state.get("fx_basis") or {}).get("rate"))
    if shares is None or shares <= 0 or avg_entry is None or avg_entry <= 0:
        return None
    local_cost = shares * avg_entry
    eur_cost = local_to_eur(local_cost, currency, fx_rate)
    if eur_cost is None:
        return None
    return {"shares": shares, "cost_basis_eur": round(eur_cost, 6), "avg_entry_local": avg_entry}


def ledger_entry_bases(state: dict[str, Any], ledger_path: Path = DEFAULT_TRADE_LEDGER_PATH) -> dict[str, dict[str, float]]:
    if not ledger_path.exists():
        return {}
    try:
        rows = list(csv.DictReader(ledger_path.read_text(encoding="utf-8").splitlines()))
    except csv.Error:
        return {}

    accumulator: dict[str, dict[str, float]] = {}
    for row in rows:
        ticker = str(row.get("ticker") or "").upper().strip()
        if not ticker or ticker == "NONE":
            continue
        shares_delta = to_float(row.get("shares_delta"))
        if shares_delta is None or abs(shares_delta) <= 1e-12:
            continue
        entry = accumulator.setdefault(ticker, {"shares": 0.0, "cost_basis_eur": 0.0, "cost_basis_local": 0.0, "entries": 0.0})
        if shares_delta > 0:
            runtime_path = runtime_state_path(str(row.get("source_report") or ""))
            if runtime_path is None:
                continue
            price_basis = runtime_trade_price(runtime_path, ticker)
            if price_basis is None:
                continue
            price, currency, fx_rate = price_basis
            local_cost = shares_delta * price
            eur_cost = local_to_eur(local_cost, currency, fx_rate)
            if eur_cost is None:
                continue
            entry["shares"] += shares_delta
            entry["cost_basis_eur"] += eur_cost
            entry["cost_basis_local"] += local_cost
            entry["entries"] += 1.0
            continue

        shares_sold = min(abs(shares_delta), entry["shares"])
        if shares_sold <= 0 or entry["shares"] <= 0:
            continue
        keep_ratio = max((entry["shares"] - shares_sold) / entry["shares"], 0.0)
        entry["shares"] -= shares_sold
        entry["cost_basis_eur"] *= keep_ratio
        entry["cost_basis_local"] *= keep_ratio

    out: dict[str, dict[str, float]] = {}
    for ticker, basis in accumulator.items():
        position = position_by_ticker(state, ticker)
        if not position:
            continue
        current_shares = to_float(position.get("shares"))
        if current_shares is None or current_shares <= 0 or basis["shares"] <= 0 or basis["cost_basis_eur"] <= 0:
            continue
        tolerance = max(0.01, abs(current_shares) * 0.01)
        if abs(basis["shares"] - current_shares) > tolerance:
            continue
        out[ticker] = {
            "shares": round(basis["shares"], 6),
            "cost_basis_eur": round(basis["cost_basis_eur"], 6),
            "avg_entry_local": round(basis["cost_basis_local"] / basis["shares"], 6),
        }
    return out


def entry_basis(position: dict[str, Any], state: dict[str, Any], ledger_bases: dict[str, dict[str, float]]) -> dict[str, float] | None:
    explicit = explicit_entry_basis(position, state)
    if explicit:
        return explicit
    ticker = str(position.get("ticker") or "").upper()
    return ledger_bases.get(ticker)
