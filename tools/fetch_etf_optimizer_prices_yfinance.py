#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any
import pandas as pd
import yfinance as yf

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument('--config-json', default='lab_inputs/etf_optimizer_fetch_config.json')
    p.add_argument('--output-csv', default='lab_inputs/etf_optimizer_prices.csv')
    return p.parse_args()

def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f'Missing fetch config: {path}')
    return json.loads(path.read_text(encoding='utf-8'))

def validate_tickers(tickers: Any) -> list[str]:
    if not isinstance(tickers, list) or not tickers:
        raise RuntimeError("Config key 'tickers' must be a non-empty list")
    clean = [str(t).strip().upper() for t in tickers if str(t).strip()]
    if len(clean) < 2:
        raise RuntimeError('Need at least 2 ETF tickers in fetch config')
    return clean

def extract_price_frame(raw: pd.DataFrame, tickers: list[str], prefer_adjusted_close: bool) -> pd.DataFrame:
    if raw is None or raw.empty:
        raise RuntimeError('yfinance returned no price data')
    field_order = ['Adj Close', 'Close'] if prefer_adjusted_close else ['Close', 'Adj Close']
    series_map: dict[str, pd.Series] = {}
    if isinstance(raw.columns, pd.MultiIndex):
        top_fields = set(raw.columns.get_level_values(0))
        for ticker in tickers:
            chosen = None
            for field in field_order:
                if field in top_fields and ticker in raw[field].columns:
                    chosen = pd.to_numeric(raw[field][ticker], errors='coerce')
                    break
            if chosen is None:
                raise RuntimeError(f'Missing close-like field for ticker {ticker}')
            series_map[ticker] = chosen.rename(ticker)
    else:
        if len(tickers) != 1:
            raise RuntimeError('Unexpected flat-column response for multiple tickers')
        ticker = tickers[0]
        chosen_col = next((f for f in field_order if f in raw.columns), None)
        if chosen_col is None:
            raise RuntimeError(f'Missing close-like field for ticker {ticker}')
        series_map[ticker] = pd.to_numeric(raw[chosen_col], errors='coerce').rename(ticker)
    df = pd.concat(series_map.values(), axis=1)
    df.columns = list(series_map.keys())
    df = df.sort_index().dropna(how='all').ffill().dropna(how='any')
    if df.empty:
        raise RuntimeError('Fetched ETF price history became empty after alignment')
    return df.astype(float)

def main() -> None:
    args = parse_args()
    config_path = Path(args.config_json)
    output_path = Path(args.output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cfg = load_config(config_path)
    tickers = validate_tickers(cfg.get('tickers'))
    period = cfg.get('period')
    start_date = cfg.get('start_date')
    end_date = cfg.get('end_date')
    interval = str(cfg.get('interval') or '1d')
    auto_adjust = bool(cfg.get('auto_adjust', False))
    prefer_adjusted_close = bool(cfg.get('prefer_adjusted_close', True))
    threads = bool(cfg.get('threads', True))
    if not period and not start_date:
        raise RuntimeError("Fetch config must define either 'period' or 'start_date'")
    raw = yf.download(tickers=tickers, start=start_date, end=end_date, period=period, interval=interval, auto_adjust=auto_adjust, group_by='column', threads=threads, progress=False)
    prices = extract_price_frame(raw, tickers, prefer_adjusted_close)
    exported = prices.reset_index().rename(columns={prices.index.name or 'index': 'date'})
    exported['date'] = pd.to_datetime(exported['date']).dt.strftime('%Y-%m-%d')
    exported.to_csv(output_path, index=False)
    print(f'Fetched ETF optimizer prices for {len(tickers)} tickers')
    print(f'Observations written: {len(exported)}')
    print(f'Output CSV: {output_path}')

if __name__ == '__main__':
    main()
