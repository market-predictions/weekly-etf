from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
import yfinance as yf

OUTPUT_DIR = Path("output/market_history")


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def discovery_tickers(config: dict[str, Any]) -> list[str]:
    tickers: set[str] = {"SPY"}
    for lane in config.get("lanes", []) or []:
        for key in ("primary_etf", "alternative_etf"):
            raw = str(lane.get(key, "")).strip().upper()
            if not raw:
                continue
            for ticker in raw.replace("/", " ").replace(",", " ").split():
                if ticker and ticker != "CASH":
                    tickers.add(ticker)
    return sorted(tickers)


def extract_close_frame(raw: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    if raw is None or raw.empty:
        raise RuntimeError("yfinance returned no data for relative-strength fetch")
    if isinstance(raw.columns, pd.MultiIndex):
        field = "Adj Close" if "Adj Close" in raw.columns.get_level_values(0) else "Close"
        data = raw[field].copy()
    else:
        data = raw.copy()
        if "Adj Close" in data.columns:
            data = data[["Adj Close"]]
        elif "Close" in data.columns:
            data = data[["Close"]]
        if len(tickers) == 1:
            data.columns = tickers
    data = data[[c for c in data.columns if str(c).upper() in set(tickers)]].copy()
    data.columns = [str(c).upper() for c in data.columns]
    data = data.sort_index().dropna(how="all").ffill()
    return data


def last_valid(series: pd.Series) -> float | None:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return None
    return float(clean.iloc[-1])


def ret_over_days(series: pd.Series, days: int) -> float | None:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if len(clean) <= days:
        return None
    start = float(clean.iloc[-days - 1])
    end = float(clean.iloc[-1])
    if start == 0:
        return None
    return round((end / start - 1.0) * 100.0, 2)


def trend_quality(series: pd.Series) -> float | None:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if len(clean) < 60:
        return None
    last = float(clean.iloc[-1])
    ma20 = float(clean.iloc[-20:].mean())
    ma50 = float(clean.iloc[-50:].mean())
    score = 0.0
    if last > ma20:
        score += 1.5
    if ma20 > ma50:
        score += 1.5
    if last > ma50:
        score += 1.0
    slope = (ma20 / float(clean.iloc[-40:-20].mean()) - 1.0) if len(clean) >= 40 and float(clean.iloc[-40:-20].mean()) else 0.0
    if slope > 0:
        score += 1.0
    return round(min(score, 5.0), 2)


def max_drawdown_3m(series: pd.Series) -> float | None:
    clean = pd.to_numeric(series, errors="coerce").dropna().iloc[-63:]
    if len(clean) < 20:
        return None
    running_max = clean.cummax()
    dd = clean / running_max - 1.0
    return round(float(dd.min()) * 100.0, 2)


def vol_3m(series: pd.Series) -> float | None:
    clean = pd.to_numeric(series, errors="coerce").dropna().iloc[-64:]
    if len(clean) < 20:
        return None
    returns = clean.pct_change().dropna()
    return round(float(returns.std()) * (252 ** 0.5) * 100.0, 2)


def build_metrics(prices: pd.DataFrame) -> dict[str, Any]:
    spy_ret_1m = ret_over_days(prices["SPY"], 21) if "SPY" in prices.columns else None
    spy_ret_3m = ret_over_days(prices["SPY"], 63) if "SPY" in prices.columns else None
    metrics: dict[str, Any] = {}
    for ticker in prices.columns:
        s = prices[ticker]
        r1 = ret_over_days(s, 21)
        r3 = ret_over_days(s, 63)
        metrics[ticker] = {
            "last_price": last_valid(s),
            "return_1m_pct": r1,
            "return_3m_pct": r3,
            "trend_quality": trend_quality(s),
            "max_drawdown_3m_pct": max_drawdown_3m(s),
            "volatility_3m_pct": vol_3m(s),
            "rs_vs_spy_1m_pct": round(r1 - spy_ret_1m, 2) if r1 is not None and spy_ret_1m is not None else None,
            "rs_vs_spy_3m_pct": round(r3 - spy_ret_3m, 2) if r3 is not None and spy_ret_3m is not None else None,
        }
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/etf_discovery_universe.yml")
    parser.add_argument("--period", default="6mo")
    parser.add_argument("--output-json", default="output/market_history/etf_relative_strength.json")
    args = parser.parse_args()

    config = load_yaml(Path(args.config))
    tickers = discovery_tickers(config)
    raw = yf.download(
        tickers=tickers,
        period=args.period,
        interval="1d",
        auto_adjust=False,
        group_by="column",
        threads=True,
        progress=False,
    )
    prices = extract_close_frame(raw, tickers)
    metrics = build_metrics(prices)

    out_path = Path(args.output_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": "yfinance",
        "period": args.period,
        "tickers_requested": tickers,
        "tickers_returned": sorted(metrics.keys()),
        "metrics": metrics,
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"ETF_RELATIVE_STRENGTH_OK | requested={len(tickers)} | returned={len(metrics)} | output={out_path}")


if __name__ == "__main__":
    main()
