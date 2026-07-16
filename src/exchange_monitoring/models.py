"""Domain models shared by exchange adapters and monitoring rules."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class Exchange(StrEnum):
    MEXC = "mexc"
    HYPERLIQUID = "hyperliquid"


@dataclass(frozen=True, slots=True)
class MarketSnapshot:
    """A small exchange-independent view of one market.

    Prices and percentages use ``Decimal`` so test results do not depend on
    binary floating-point rounding. ``symbol`` is a canonical comparison key,
    not a venue-native order symbol: USD, USDT, and USDC quotes are represented
    as ``BASE/USD`` so equivalent markets can be compared across venues.
    """

    exchange: Exchange
    symbol: str
    mark_price: Decimal
    day_open_price: Decimal
    quote_volume_24h: Decimal
    best_bid: Decimal | None = None
    best_ask: Decimal | None = None

    def __post_init__(self) -> None:
        if not self.symbol or "/" not in self.symbol:
            raise ValueError("symbol must use BASE/QUOTE form")
        if self.mark_price <= 0 or self.day_open_price <= 0:
            raise ValueError("prices must be positive")
        if self.quote_volume_24h < 0:
            raise ValueError("quote volume cannot be negative")
        if self.best_bid is not None and self.best_bid <= 0:
            raise ValueError("best bid must be positive")
        if self.best_ask is not None and self.best_ask <= 0:
            raise ValueError("best ask must be positive")
        if (
            self.best_bid is not None
            and self.best_ask is not None
            and self.best_bid > self.best_ask
        ):
            raise ValueError("best bid cannot exceed best ask")

    @property
    def change_pct(self) -> Decimal:
        return (self.mark_price / self.day_open_price - Decimal("1")) * Decimal("100")

    @property
    def spread_bps(self) -> Decimal | None:
        if self.best_bid is None or self.best_ask is None:
            return None
        midpoint = (self.best_bid + self.best_ask) / Decimal("2")
        return (self.best_ask - self.best_bid) / midpoint * Decimal("10000")


@dataclass(frozen=True, slots=True)
class RegimeAssessment:
    is_risk_on: bool
    anchor_symbol: str
    anchor_change_pct: Decimal | None
    positive_breadth_pct: Decimal
    observed_markets: int
    reasons: tuple[str, ...]

