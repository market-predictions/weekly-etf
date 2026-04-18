from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

PriceStatus = Literal[
    "fresh_close",
    "fresh_fallback_source",
    "carried_forward",
    "unresolved",
]

SymbolKind = Literal[
    "holding",
    "radar_primary",
    "radar_alternative",
    "challenger",
    "fx",
]

Confidence = Literal["high", "medium", "low"]


@dataclass(slots=True)
class HoldingSnapshot:
    ticker: str
    shares: float
    previous_price_local: Optional[float]
    currency: str
    previous_market_value_local: Optional[float]
    previous_market_value_eur: Optional[float]
    previous_weight_pct: Optional[float]


@dataclass(slots=True)
class ShortlistItem:
    symbol: str
    kind: SymbolKind
    priority: int
    note: str = ""


@dataclass(slots=True)
class PriceRequest:
    symbol: str
    requested_close_date: str
    kind: SymbolKind
    currency_hint: str = "USD"


@dataclass(slots=True)
class PriceResult:
    symbol: str
    requested_close_date: str
    returned_close_date: Optional[str]
    price: Optional[float]
    currency: Optional[str]
    source: Optional[str]
    source_detail: Optional[str]
    field_used: Optional[str]
    status: PriceStatus
    confidence: Confidence
    carried_forward: bool = False
    error: Optional[str] = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class FXResult:
    pair: str
    requested_date: str
    returned_date: Optional[str]
    rate: Optional[float]
    source: Optional[str]
    status: PriceStatus
    error: Optional[str] = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class QuotaStatus:
    source: str
    daily_limit: int
    reserve_daily: int
    spent_today: int
    remaining_today: int
    can_spend: bool


@dataclass(slots=True)
class PricingPassResult:
    run_date: str
    requested_close_date: str
    holdings: list[HoldingSnapshot]
    price_results: list[PriceResult]
    unresolved_tickers: list[str]
    holdings_count: int
    fresh_holdings_count: int
    carried_forward_holdings_count: int
    coverage_count_pct: float
    decision: str
