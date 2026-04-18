from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def cache_dir() -> Path:
    return Path(os.environ.get("ETF_PRICING_CACHE_DIR", "output/pricing"))


def _cache_path(run_date: str) -> Path:
    return cache_dir() / f"price_cache_{run_date}.json"


def load_daily_cache(run_date: str) -> dict[str, Any]:
    path = _cache_path(run_date)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_daily_cache(run_date: str, cache: dict[str, Any]) -> None:
    path = _cache_path(run_date)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")


def make_cache_key(symbol: str, requested_date: str, source: str) -> str:
    return f"{source}:{symbol.upper()}:{requested_date}"


def cache_get(cache: dict[str, Any], symbol: str, requested_date: str, source: str):
    return cache.get(make_cache_key(symbol, requested_date, source))


def cache_put(cache: dict[str, Any], result: dict[str, Any]) -> None:
    key = make_cache_key(result["symbol"], result["requested_close_date"], result["source"] or "unknown")
    cache[key] = result
