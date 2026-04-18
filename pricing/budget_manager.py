from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise RuntimeError("PyYAML is required for pricing configs. Install with: pip install pyyaml") from exc


@dataclass
class SourceBudget:
    daily_limit: int
    reserve_daily: int
    local_min_seconds_between_calls: int
    minute_credits: int | None = None
    spent: int = 0
    last_call_ts: float = 0.0


class BudgetManager:
    def __init__(self, rate_limit_file: str | Path):
        cfg = yaml.safe_load(Path(rate_limit_file).read_text(encoding="utf-8"))
        self.policy = cfg["policy"]
        self.budgets = {}
        for name in ("twelve_data", "fmp", "alpha_vantage", "website_fallback"):
            if name in cfg:
                raw = cfg[name]
                self.budgets[name] = SourceBudget(
                    daily_limit=int(raw["daily_limit"]) if "daily_limit" in raw else 999999,
                    reserve_daily=int(raw.get("reserve_daily", 0)),
                    local_min_seconds_between_calls=int(raw.get("local_min_seconds_between_calls", 0)),
                    minute_credits=raw.get("minute_credits"),
                )

    def remaining(self, source: str) -> int:
        budget = self.budgets[source]
        return budget.daily_limit - budget.spent

    def can_spend(self, source: str, kind: str) -> bool:
        budget = self.budgets[source]
        remaining = self.remaining(source)
        reserve = budget.reserve_daily
        if kind == "holding":
            return remaining > max(reserve // 2, 0)
        if kind in {"radar_primary", "radar_alternative"}:
            return remaining > reserve
        return remaining > reserve + 5

    def register_spend(self, source: str, cost: int = 1) -> None:
        budget = self.budgets[source]
        budget.spent += cost
        budget.last_call_ts = time.time()

    def sleep_if_needed(self, source: str) -> None:
        budget = self.budgets[source]
        wait = budget.local_min_seconds_between_calls
        if wait <= 0:
            return
        elapsed = time.time() - budget.last_call_ts
        if elapsed < wait:
            time.sleep(wait - elapsed)
