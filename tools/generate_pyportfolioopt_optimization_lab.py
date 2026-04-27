#!/usr/bin/env python3
"""Generate a lab-only ETF optimization bundle using PyPortfolioOpt.

This script is intentionally non-destructive:
- it does not modify the production ETF review flow
- it uses an explicit lab input contract rather than inventing production state
- it writes artifacts only to a separate lab output folder

First iteration scope:
- max Sharpe allocation
- minimum-volatility allocation
- hierarchical risk parity allocation
- optional Black-Litterman max-Sharpe allocation when absolute views are provided
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from pypfopt import EfficientFrontier, HRPOpt, black_litterman, expected_returns, risk_models


@dataclass
class StrategyResult:
    strategy: str
    status: str
    expected_return_pct: float
    volatility_pct: float
    sharpe: float
    notes: str


@dataclass
class OptimizationSummary:
    generated_at_utc: str
    input_prices_csv: str
    constraints_json: str | None
    views_json: str | None
    asset_count: int
    observation_count: int
    strategies_run: list[str]
    best_strategy_by_sharpe: str
    best_strategy_sharpe: float
    note: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate ETF optimization lab artifacts with PyPortfolioOpt")
    parser.add_argument(
        "--prices-csv",
        default="lab_inputs/etf_optimizer_prices.csv",
        help="Wide CSV with date column plus one close-price column per ETF",
    )
    parser.add_argument(
        "--constraints-json",
        default="lab_inputs/etf_optimizer_constraints.json",
        help="Optional JSON file for lab optimization constraints",
    )
    parser.add_argument(
        "--views-json",
        default="lab_inputs/etf_optimizer_views.json",
        help="Optional JSON file for Black-Litterman absolute views",
    )
    parser.add_argument(
        "--artifact-dir",
        default="lab_outputs/optimization",
        help="Directory to write optimization artifacts into",
    )
    return parser.parse_args()


def load_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def load_prices(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing lab input file: {path}. Copy lab_inputs/etf_optimizer_prices_template.csv to lab_inputs/etf_optimizer_prices.csv and populate it first."
        )

    df = pd.read_csv(path)
    if "date" not in df.columns:
        raise RuntimeError("ETF optimizer prices CSV must contain a 'date' column")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).copy()
    df = df.sort_values("date").drop_duplicates(subset=["date"], keep="last")
    df = df.set_index("date")

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")
    df = df.ffill().dropna(axis=0, how="any")

    if df.shape[1] < 2:
        raise RuntimeError("Need at least 2 ETF columns with usable price history")
    if df.shape[0] < 20:
        raise RuntimeError("Need at least 20 price observations for the ETF optimization lab")

    return df.astype(float)


def build_weight_bounds(tickers: list[str], constraints: dict[str, Any]) -> list[tuple[float, float]]:
    default_min = safe_float(constraints.get("default_min_weight"), 0.0)
    default_max = safe_float(constraints.get("default_max_weight"), 0.35)
    per_ticker_bounds = constraints.get("per_ticker_bounds", {}) or {}
    excluded = set(constraints.get("exclude_tickers", []) or [])

    bounds: list[tuple[float, float]] = []
    for ticker in tickers:
        if ticker in excluded:
            bounds.append((0.0, 0.0))
            continue
        custom = per_ticker_bounds.get(ticker)
        if isinstance(custom, dict):
            lower = safe_float(custom.get("min"), default_min)
            upper = safe_float(custom.get("max"), default_max)
        else:
            lower = default_min
            upper = default_max
        bounds.append((lower, upper))
    return bounds


def clean_weight_series(weights: dict[str, float], tickers: list[str]) -> pd.Series:
    series = pd.Series({ticker: safe_float(weights.get(ticker), 0.0) for ticker in tickers}, index=tickers)
    return series.fillna(0.0).astype(float)


def perf_from_weights(weights: pd.Series, mu: pd.Series, cov: pd.DataFrame, risk_free_rate: float = 0.0) -> tuple[float, float, float]:
    w = weights.reindex(mu.index).fillna(0.0).astype(float)
    exp_return = safe_float(np.dot(mu.values, w.values))
    variance = safe_float(np.dot(w.values.T, np.dot(cov.values, w.values)))
    volatility = safe_float(np.sqrt(max(variance, 0.0)))
    sharpe = safe_float((exp_return - risk_free_rate) / volatility) if volatility > 0 else 0.0
    return exp_return * 100.0, volatility * 100.0, sharpe


def strategy_row(strategy: str, weights: pd.Series, mu: pd.Series, cov: pd.DataFrame, notes: str = "") -> tuple[StrategyResult, pd.Series]:
    exp_return_pct, volatility_pct, sharpe = perf_from_weights(weights, mu, cov)
    result = StrategyResult(
        strategy=strategy,
        status="ok",
        expected_return_pct=exp_return_pct,
        volatility_pct=volatility_pct,
        sharpe=sharpe,
        notes=notes,
    )
    return result, weights


def run_max_sharpe(mu: pd.Series, cov: pd.DataFrame, bounds: list[tuple[float, float]]) -> tuple[StrategyResult, pd.Series]:
    ef = EfficientFrontier(mu, cov, weight_bounds=bounds)
    ef.max_sharpe()
    weights = clean_weight_series(ef.clean_weights(), list(mu.index))
    return strategy_row("max_sharpe", weights, mu, cov)


def run_min_vol(mu: pd.Series, cov: pd.DataFrame, bounds: list[tuple[float, float]]) -> tuple[StrategyResult, pd.Series]:
    ef = EfficientFrontier(mu, cov, weight_bounds=bounds)
    ef.min_volatility()
    weights = clean_weight_series(ef.clean_weights(), list(mu.index))
    return strategy_row("min_volatility", weights, mu, cov)


def run_hrp(prices: pd.DataFrame, mu: pd.Series, cov: pd.DataFrame) -> tuple[StrategyResult, pd.Series]:
    returns = expected_returns.returns_from_prices(prices).dropna(how="all")
    hrp = HRPOpt(returns=returns)
    weights = clean_weight_series(hrp.optimize(), list(mu.index))
    return strategy_row("hierarchical_risk_parity", weights, mu, cov)


def run_black_litterman_if_configured(
    tickers: list[str],
    mu: pd.Series,
    cov: pd.DataFrame,
    bounds: list[tuple[float, float]],
    views_cfg: dict[str, Any],
) -> tuple[StrategyResult, pd.Series] | None:
    absolute_views = views_cfg.get("absolute_views") or {}
    if not absolute_views:
        return None

    prior_returns = pd.Series(views_cfg.get("prior_returns") or {}, index=tickers, dtype=float)
    if prior_returns.isna().all():
        prior_returns = mu.copy()
    else:
        prior_returns = prior_returns.fillna(mu)

    bl = black_litterman.BlackLittermanModel(
        cov,
        pi=prior_returns,
        absolute_views=absolute_views,
    )
    posterior_rets = bl.bl_returns()

    ef = EfficientFrontier(posterior_rets, cov, weight_bounds=bounds)
    ef.max_sharpe()
    weights = clean_weight_series(ef.clean_weights(), tickers)
    notes = "Black-Litterman run using absolute views from lab_inputs/etf_optimizer_views.json"
    return strategy_row("black_litterman_max_sharpe", weights, posterior_rets, cov, notes=notes)


def weights_frame(weight_map: dict[str, pd.Series]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for strategy, series in weight_map.items():
        for ticker, weight in series.items():
            rows.append({"strategy": strategy, "ticker": ticker, "weight": safe_float(weight)})
    df = pd.DataFrame(rows)
    return df.sort_values(["strategy", "weight", "ticker"], ascending=[True, False, True]).reset_index(drop=True)


def write_markdown_summary(path: Path, summary: OptimizationSummary, results_df: pd.DataFrame, top_weights: pd.DataFrame) -> None:
    lines = [
        "# ETF optimization lab summary",
        "",
        "## Scope",
        "",
        "This is a lab-only ETF optimization layer using PyPortfolioOpt.",
        "It does not replace the production ETF review methodology or delivery flow.",
        "",
        "## Input overview",
        "",
        f"- Assets in input universe: **{summary.asset_count}**",
        f"- Price observations: **{summary.observation_count}**",
        f"- Strategies run: **{', '.join(summary.strategies_run)}**",
        f"- Best strategy by modeled Sharpe: **{summary.best_strategy_by_sharpe}**",
        f"- Best strategy Sharpe: **{summary.best_strategy_sharpe:.4f}**",
        "",
        "## Strategy comparison",
        "",
        "| Strategy | Expected return (%) | Volatility (%) | Sharpe | Notes |",
        "|---|---:|---:|---:|---|",
    ]
    for _, row in results_df.iterrows():
        lines.append(
            f"| {row['strategy']} | {row['expected_return_pct']:.4f} | {row['volatility_pct']:.4f} | {row['sharpe']:.4f} | {row['notes']} |"
        )

    lines.extend([
        "",
        f"## Top weights — {summary.best_strategy_by_sharpe}",
        "",
        "| Ticker | Weight |",
        "|---|---:|",
    ])
    for _, row in top_weights.iterrows():
        lines.append(f"| {row['ticker']} | {row['weight']:.4f} |")

    lines.extend([
        "",
        "## Note",
        "",
        summary.note,
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    prices_path = Path(args.prices_csv)
    constraints_path = Path(args.constraints_json)
    views_path = Path(args.views_json)
    artifact_dir = Path(args.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    prices = load_prices(prices_path)
    constraints = load_json_if_exists(constraints_path)
    views_cfg = load_json_if_exists(views_path)

    tickers = list(prices.columns)
    mu = expected_returns.mean_historical_return(prices)
    cov = risk_models.sample_cov(prices)
    bounds = build_weight_bounds(tickers, constraints)

    results: list[StrategyResult] = []
    weight_map: dict[str, pd.Series] = {}

    for runner in [
        lambda: run_max_sharpe(mu, cov, bounds),
        lambda: run_min_vol(mu, cov, bounds),
        lambda: run_hrp(prices, mu, cov),
    ]:
        result, weights = runner()
        results.append(result)
        weight_map[result.strategy] = weights

    bl_result = run_black_litterman_if_configured(tickers, mu, cov, bounds, views_cfg)
    if bl_result is not None:
        result, weights = bl_result
        results.append(result)
        weight_map[result.strategy] = weights

    results_df = pd.DataFrame([asdict(r) for r in results]).sort_values("sharpe", ascending=False).reset_index(drop=True)
    weights_df = weights_frame(weight_map)
    best_strategy = str(results_df.iloc[0]["strategy"])
    best_weights = weights_df.loc[weights_df["strategy"] == best_strategy].copy()
    best_weights = best_weights.loc[best_weights["weight"] > 0].sort_values("weight", ascending=False).reset_index(drop=True)

    summary = OptimizationSummary(
        generated_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        input_prices_csv=str(prices_path),
        constraints_json=str(constraints_path) if constraints_path.exists() else None,
        views_json=str(views_path) if views_path.exists() else None,
        asset_count=int(prices.shape[1]),
        observation_count=int(prices.shape[0]),
        strategies_run=results_df["strategy"].tolist(),
        best_strategy_by_sharpe=best_strategy,
        best_strategy_sharpe=safe_float(results_df.iloc[0]["sharpe"]),
        note="This optimization lab is for internal ETF QA and research only. It depends entirely on the supplied lab input universe and should not be treated as a production allocation engine.",
    )

    cleaned_prices_export = artifact_dir / "etf_optimizer_cleaned_prices.csv"
    results_export = artifact_dir / "etf_optimizer_strategy_results.csv"
    weights_export = artifact_dir / "etf_optimizer_weights.csv"
    summary_export = artifact_dir / "etf_optimizer_summary.json"
    summary_md_export = artifact_dir / "etf_optimizer_summary.md"
    manifest_export = artifact_dir / "etf_optimizer_manifest.json"

    cleaned_prices = prices.reset_index().rename(columns={prices.index.name or "index": "date"})
    cleaned_prices.to_csv(cleaned_prices_export, index=False)
    results_df.to_csv(results_export, index=False)
    weights_df.to_csv(weights_export, index=False)
    summary_export.write_text(json.dumps(asdict(summary), indent=2) + "\n", encoding="utf-8")
    write_markdown_summary(summary_md_export, summary, results_df, best_weights)
    manifest_export.write_text(
        json.dumps(
            {
                "generated_at_utc": summary.generated_at_utc,
                "input_files": {
                    "prices_csv": str(prices_path),
                    "constraints_json": str(constraints_path) if constraints_path.exists() else None,
                    "views_json": str(views_path) if views_path.exists() else None,
                },
                "artifacts": {
                    "cleaned_prices_csv": str(cleaned_prices_export),
                    "strategy_results_csv": str(results_export),
                    "weights_csv": str(weights_export),
                    "summary_json": str(summary_export),
                    "summary_markdown": str(summary_md_export),
                },
                "best_strategy_by_sharpe": summary.best_strategy_by_sharpe,
                "strategies_run": summary.strategies_run,
                "asset_count": summary.asset_count,
                "observation_count": summary.observation_count,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"ETF optimization lab artifacts written to: {artifact_dir}")
    print(f"Best strategy by Sharpe: {summary.best_strategy_by_sharpe}")
    print(f"Summary markdown: {summary_md_export}")


if __name__ == "__main__":
    main()
