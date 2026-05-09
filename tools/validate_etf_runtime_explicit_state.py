from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from runtime.build_etf_report_state import build_runtime_state


def _num(value: Any, label: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Runtime explicit state validation failed: {label} is not numeric: {value!r}") from exc


def _ticker(value: Any) -> str:
    return str(value or "").strip().upper()


def validate_runtime_state(output_dir: Path) -> None:
    state = build_runtime_state()
    report_date = str(state.get("report_date") or "").strip()
    if not report_date:
        raise RuntimeError("Runtime explicit state validation failed: report_date missing.")

    positions = state.get("positions", []) or []
    if not isinstance(positions, list) or not positions:
        raise RuntimeError("Runtime explicit state validation failed: no positions.")

    portfolio = state.get("portfolio") or {}
    cash = _num(portfolio.get("cash_eur"), "cash_eur")
    nav = _num(portfolio.get("total_portfolio_value_eur"), "total_portfolio_value_eur")
    invested = 0.0
    tickers: list[str] = []

    for position in positions:
        ticker = _ticker(position.get("ticker"))
        if not ticker:
            raise RuntimeError("Runtime explicit state validation failed: position without ticker.")
        if ticker in tickers:
            raise RuntimeError(f"Runtime explicit state validation failed: duplicate position ticker {ticker}.")
        shares = _num(position.get("shares"), f"shares for {ticker}")
        price = _num(position.get("previous_price_local"), f"previous_price_local for {ticker}")
        value_eur = _num(position.get("previous_market_value_eur"), f"previous_market_value_eur for {ticker}")
        if shares <= 0 or price <= 0 or value_eur <= 0:
            raise RuntimeError(f"Runtime explicit state validation failed: invalid values for {ticker}.")
        invested += value_eur
        tickers.append(ticker)

    if cash < 0:
        raise RuntimeError("Runtime explicit state validation failed: cash is negative.")
    if nav <= 0:
        raise RuntimeError("Runtime explicit state validation failed: NAV is not positive.")
    if abs((invested + cash) - nav) > 0.10:
        raise RuntimeError(
            "Runtime explicit state validation failed: invested + cash does not reconcile to NAV "
            f"({invested:.2f} + {cash:.2f} vs {nav:.2f})."
        )

    scorecard = state.get("recommendation_scorecard", []) or []
    if not scorecard:
        raise RuntimeError("Runtime explicit state validation failed: recommendation scorecard missing.")
    scorecard_tickers = {_ticker(row.get("ticker")) for row in scorecard if _ticker(row.get("ticker"))}
    missing_scorecard = [ticker for ticker in tickers if ticker not in scorecard_tickers]
    if missing_scorecard:
        raise RuntimeError(
            "Runtime explicit state validation failed: scorecard missing tickers: "
            + ", ".join(missing_scorecard)
        )

    source_files = state.get("source_files") or {}
    missing_sources = [key for key in ("portfolio_state", "pricing_audit", "lane_assessment", "recommendation_scorecard") if not source_files.get(key)]
    if missing_sources:
        raise RuntimeError(
            "Runtime explicit state validation failed: missing source file pointers: "
            + ", ".join(missing_sources)
        )

    runtime_dir = output_dir / "runtime"
    expected_runtime = runtime_dir / f"etf_report_state_{report_date.replace('-', '')}.json"
    if not expected_runtime.exists():
        raise RuntimeError(f"Runtime explicit state validation failed: expected runtime artifact missing: {expected_runtime}")

    print(
        "ETF_RUNTIME_EXPLICIT_STATE_OK | "
        f"report_date={report_date} | positions={len(tickers)} | invested_eur={invested:.2f} | "
        f"cash_eur={cash:.2f} | nav_eur={nav:.2f} | scorecard_rows={len(scorecard)} | "
        f"runtime_artifact={expected_runtime.name}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    validate_runtime_state(Path(args.output_dir))


if __name__ == "__main__":
    main()
