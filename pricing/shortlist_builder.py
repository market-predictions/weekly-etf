from __future__ import annotations

from .models import ShortlistItem


def build_holdings_shortlist(holdings: list[str]) -> list[ShortlistItem]:
    return [ShortlistItem(symbol=s, kind="holding", priority=10) for s in holdings]


def merge_and_deduplicate(items: list[ShortlistItem]) -> list[ShortlistItem]:
    seen = set()
    result: list[ShortlistItem] = []
    for item in sorted(items, key=lambda x: (-x.priority, x.symbol)):
        key = item.symbol.upper()
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result
