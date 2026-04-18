from __future__ import annotations

from .models import ShortlistItem


def build_holdings_shortlist(holdings: list[str]) -> list[ShortlistItem]:
    return [ShortlistItem(symbol=s, kind="holding", priority=100) for s in holdings]


def build_radar_primary_shortlist(symbols: list[str]) -> list[ShortlistItem]:
    return [ShortlistItem(symbol=s, kind="radar_primary", priority=80) for s in symbols]


def build_radar_alternative_shortlist(symbols: list[str], max_alternatives: int) -> list[ShortlistItem]:
    picked = symbols[:max_alternatives]
    return [ShortlistItem(symbol=s, kind="radar_alternative", priority=60) for s in picked]


def build_challenger_shortlist(symbols: list[str], max_challengers: int) -> list[ShortlistItem]:
    picked = symbols[:max_challengers]
    return [ShortlistItem(symbol=s, kind="challenger", priority=40) for s in picked]


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
