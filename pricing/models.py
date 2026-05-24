from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Literal, Optional, Any

PriceStatus = Literal[
    "fresh_close",  # legacy, normalized on load
    "fresh_fallback_source",  # legacy, normalized on load
    "fresh_exact_close",
    "fresh_exact_unverified",
    "prior_valid_close",
    "carried_forward",
    "unresolved",
    "blocked",
]

SymbolKind = Literal[
    "holding",
    "radar_primary",
    "radar_alternative",
    "challenger",
    "fx",
]

Confidence = Literal["high", "medium", "low"]
PricingTier = Literal["valuation_grade", "research_grade"]

EXACT_CLOSE_STATUSES = {"fresh_exact_close", "fresh_exact_unverified"}
PRICED_CLOSE_STATUSES = EXACT_CLOSE_STATUSES | {"prior_valid_close"}
SUCCESS_STATUSES = PRICED_CLOSE_STATUSES
LEGACY_SUCCESS_STATUSES = {"fresh_close", "fresh_fallback_source"}


def _date_or_none(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def normalize_price_status(
    status: str,
    requested_close_date: str | None,
    returned_close_date: str | None,
    has_price: bool,
    carried_forward: bool = False,
) -> PriceStatus:
    """Normalize legacy price statuses into explicit close-date semantics.

    Older clients returned `fresh_close` for an exact date and
    `fresh_fallback_source` for the latest available provider row. The lineage
    contract requires the audit row itself to say whether the selected close is
    an exact requested close or a prior valid close.
    """
    raw = str(status or "unresolved")
    if carried_forward or raw == "carried_forward":
        return "carried_forward"
    if raw in {"unresolved", "blocked"}:
        return raw  # type: ignore[return-value]
    if not has_price:
        return "unresolved"

    requested = _date_or_none(requested_close_date)
    returned = _date_or_none(returned_close_date)
    if raw in LEGACY_SUCCESS_STATUSES or raw in PRICED_CLOSE_STATUSES:
        if requested is not None and returned is not None:
            if returned == requested:
                if raw == "fresh_exact_close":
                    return "fresh_exact_close"
                return "fresh_exact_unverified"
            if returned < requested:
                return "prior_valid_close"
            return "blocked"
        if raw in EXACT_CLOSE_STATUSES:
            return raw  # type: ignore[return-value]
        return "fresh_exact_unverified"
    return "unresolved"


def selected_close_type_from_field(field_used: str | None) -> str | None:
    field = str(field_used or "").lower()
    if not field:
        return None
    if "adj" in field:
        return "adjusted_close"
    if "close" in field:
        return "raw_close"
    return "provider_close"


@dataclass(slots=True)
class HoldingSnapshot:
    ticker: str
    shares: float
    previous_price_local: Optional[float]
    currency: str
    previous_market_value_local: Optional[float]
    previous_market_value_eur: Optional[float]
    previous_weight_pct: Optional[float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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
    provider_symbol: Optional[str] = None
    provider_exchange: Optional[str] = None
    raw_close: Optional[float] = None
    adjusted_close: Optional[float] = None
    selected_close: Optional[float] = None
    selected_close_type: Optional[str] = None
    provider_timestamp: Optional[str] = None
    provider_timezone: Optional[str] = None
    is_final_eod_bar: Optional[bool] = None
    asset_role: Optional[str] = None
    pricing_tier: Optional[PricingTier] = None
    verification: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized = normalize_price_status(
            str(self.status),
            self.requested_close_date,
            self.returned_close_date,
            self.price is not None,
            self.carried_forward,
        )
        object.__setattr__(self, "status", normalized)
        if self.provider_symbol is None:
            object.__setattr__(self, "provider_symbol", self.symbol)
        if self.selected_close is None and self.price is not None:
            object.__setattr__(self, "selected_close", float(self.price))
        if self.raw_close is None and self.price is not None and self.selected_close_type != "adjusted_close":
            object.__setattr__(self, "raw_close", float(self.price))
        if self.selected_close_type is None:
            object.__setattr__(self, "selected_close_type", selected_close_type_from_field(self.field_used))
        if self.is_final_eod_bar is None and self.status in PRICED_CLOSE_STATUSES:
            object.__setattr__(self, "is_final_eod_bar", True)
        if not self.verification:
            object.__setattr__(self, "verification", {"status": "not_checked", "source": None})

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "status",
            normalize_price_status(str(self.status), self.requested_date, self.returned_date, self.rate is not None),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class QuotaStatus:
    source: str
    daily_limit: int
    reserve_daily: int
    spent_today: int
    remaining_today: int
    can_spend: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
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
    holdings: list[HoldingSnapshot] = field(default_factory=list)
    price_results: list[PriceResult] = field(default_factory=list)
    carried_forward_holdings_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        effective_price_results = self.price_results or self.prices
        return {
            "run_date": self.run_date,
            "requested_close_date": self.requested_close_date,
            "holdings_count": self.holdings_count,
            "fresh_holdings_count": self.fresh_holdings_count,
            "carried_forward_holdings_count": self.carried_forward_holdings_count,
            "coverage_count_pct": self.coverage_count_pct,
            "invested_weight_coverage_pct": self.invested_weight_coverage_pct,
            "decision": self.decision,
            "unresolved_tickers": self.unresolved_tickers,
            "fx_basis": None if self.fx_basis is None else self.fx_basis.to_dict(),
            "holdings": [h.to_dict() for h in self.holdings],
            "prices": [p.to_dict() for p in self.prices],
            "price_results": [p.to_dict() for p in effective_price_results],
        }
