"""Deterministic, paper-only short-position exit state machine."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum


class ExitAction(StrEnum):
    HOLD = "hold"
    HARD_STOP = "hard_stop"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"
    BREAKEVEN = "breakeven"
    TIMEOUT = "timeout"


@dataclass(frozen=True, slots=True)
class ShortExitPolicy:
    """Illustrative public-demo parameters expressed as decimal ratios."""

    hard_stop: Decimal = Decimal("0.04")
    take_profit: Decimal = Decimal("0.06")
    breakeven_trigger: Decimal = Decimal("0.025")
    trailing_trigger: Decimal = Decimal("0.04")
    trailing_distance: Decimal = Decimal("0.015")
    max_holding: timedelta = timedelta(hours=3)

    def __post_init__(self) -> None:
        ratio_fields = (
            self.hard_stop,
            self.take_profit,
            self.breakeven_trigger,
            self.trailing_trigger,
            self.trailing_distance,
        )
        if any(value <= 0 or value >= 1 for value in ratio_fields):
            raise ValueError("policy ratios must be between zero and one")
        if self.trailing_trigger < self.breakeven_trigger:
            raise ValueError("trailing trigger cannot precede breakeven trigger")
        if self.max_holding <= timedelta(0):
            raise ValueError("max_holding must be positive")


@dataclass(frozen=True, slots=True)
class PaperShortPosition:
    entry_price: Decimal
    opened_at: datetime
    lowest_price_seen: Decimal | None = None
    breakeven_armed: bool = False
    trailing_armed: bool = False

    def __post_init__(self) -> None:
        if self.entry_price <= 0:
            raise ValueError("entry price must be positive")
        if self.opened_at.tzinfo is None:
            raise ValueError("opened_at must include a timezone")
        if self.lowest_price_seen is not None and self.lowest_price_seen <= 0:
            raise ValueError("lowest price must be positive")


@dataclass(frozen=True, slots=True)
class ExitEvaluation:
    action: ExitAction
    reason: str
    pnl_pct: Decimal
    position: PaperShortPosition
    active_stop: Decimal | None = None

    @property
    def should_exit(self) -> bool:
        return self.action is not ExitAction.HOLD


def evaluate_short_exit(
    position: PaperShortPosition,
    current_price: Decimal,
    observed_at: datetime,
    policy: ShortExitPolicy | None = None,
) -> ExitEvaluation:
    """Evaluate one price observation without placing or simulating an order."""

    policy = policy or ShortExitPolicy()
    if current_price <= 0:
        raise ValueError("current price must be positive")
    if observed_at.tzinfo is None:
        raise ValueError("observed_at must include a timezone")
    if observed_at < position.opened_at:
        raise ValueError("observation cannot precede the position")

    lowest = min(position.lowest_price_seen or position.entry_price, current_price)
    favorable_move = (position.entry_price - lowest) / position.entry_price
    breakeven_armed = position.breakeven_armed or favorable_move >= policy.breakeven_trigger
    trailing_armed = position.trailing_armed or favorable_move >= policy.trailing_trigger
    updated = replace(
        position,
        lowest_price_seen=lowest,
        breakeven_armed=breakeven_armed,
        trailing_armed=trailing_armed,
    )
    pnl_pct = (position.entry_price - current_price) / position.entry_price * Decimal("100")

    hard_stop_price = position.entry_price * (Decimal("1") + policy.hard_stop)
    take_profit_price = position.entry_price * (Decimal("1") - policy.take_profit)
    trailing_stop = lowest * (Decimal("1") + policy.trailing_distance)

    if current_price >= hard_stop_price:
        return ExitEvaluation(
            ExitAction.HARD_STOP,
            "paper hard-stop level reached",
            pnl_pct,
            updated,
            hard_stop_price,
        )
    if current_price <= take_profit_price:
        return ExitEvaluation(
            ExitAction.TAKE_PROFIT,
            "paper take-profit level reached",
            pnl_pct,
            updated,
            take_profit_price,
        )
    if trailing_armed and current_price >= trailing_stop:
        return ExitEvaluation(
            ExitAction.TRAILING_STOP,
            "price rebounded from the best paper price",
            pnl_pct,
            updated,
            trailing_stop,
        )
    if breakeven_armed and current_price >= position.entry_price:
        return ExitEvaluation(
            ExitAction.BREAKEVEN,
            "paper breakeven protection reached",
            pnl_pct,
            updated,
            position.entry_price,
        )
    if observed_at - position.opened_at >= policy.max_holding:
        return ExitEvaluation(
            ExitAction.TIMEOUT,
            "maximum paper holding time reached",
            pnl_pct,
            updated,
        )

    active_stop = trailing_stop if trailing_armed else position.entry_price if breakeven_armed else hard_stop_price
    return ExitEvaluation(
        ExitAction.HOLD,
        "no paper exit condition matched",
        pnl_pct,
        updated,
        active_stop,
    )


