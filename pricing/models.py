from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal, Optional, Any

PriceStatus = Literal["fresh_close", "fresh_fallback_source", "carried_forward", "unresolved"]
SymbolKind = Literal["holding", "radar_primary", "radar_alternative", "challenger", "fx"]


@dataclass
class PriceRequest:
    symbol: str
    requested_close_date: str
    kind: SymbolKind
    currency_hint: str = "USD"


@dataclass
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
    confidence: Literal["high", "medium", "low"]
    carried_forward: bool = False
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FXResult:
    pair: str
    requested_date: str
    returned_date: Optional[str]
    rate: Optional[float]
    source: Optional[str]
    status: PriceStatus
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ShortlistItem:
    symbol: str
    kind: SymbolKind
    priority: int
    note: str = ""


@dataclass
class PricingPassResult:
    run_date: str
    requested_close_date: str
    holdings_count: int
    fresh_holdings_count: int
    coverage_count_pct: float
    invested_weight_coverage_pct: float
    decision: str
    unresolved_tickers: list[str]
    fx_basis: Optional[FXResult]
    prices: list[PriceResult]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_date": self.run_date,
            "requested_close_date": self.requested_close_date,
            "holdings_count": self.holdings_count,
            "fresh_holdings_count": self.fresh_holdings_count,
            "coverage_count_pct": self.coverage_count_pct,
            "invested_weight_coverage_pct": self.invested_weight_coverage_pct,
            "decision": self.decision,
            "unresolved_tickers": self.unresolved_tickers,
            "fx_basis": None if self.fx_basis is None else self.fx_basis.to_dict(),
            "prices": [p.to_dict() for p in self.prices],
        }
