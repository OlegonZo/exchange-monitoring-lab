"""Transparent market-regime assessment for monitoring workflows."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from statistics import median
from typing import Iterable

from .models import MarketSnapshot, RegimeAssessment


def assess_market_regime(
    snapshots: Iterable[MarketSnapshot],
    *,
    anchor_symbol: str = "BTC/USD",
    min_anchor_change_pct: Decimal = Decimal("1.0"),
    min_positive_breadth_pct: Decimal = Decimal("55"),
    min_markets: int = 3,
) -> RegimeAssessment:
    """Classify a small cross-exchange snapshot as risk-on or guarded.

    Duplicate symbols from different exchanges are collapsed with a median so
    one listed asset receives one breadth vote. Defaults are illustrative demo
    settings, not production thresholds or investment advice.
    """

    if min_markets < 1:
        raise ValueError("min_markets must be at least one")
    grouped: dict[str, list[Decimal]] = defaultdict(list)
    for snapshot in snapshots:
        grouped[snapshot.symbol].append(snapshot.change_pct)

    changes = {symbol: median(values) for symbol, values in grouped.items()}
    observed = len(changes)
    positive = sum(change > 0 for change in changes.values())
    breadth = (
        Decimal(positive) / Decimal(observed) * Decimal("100")
        if observed
        else Decimal("0")
    )
    anchor_change = changes.get(anchor_symbol)

    reasons: list[str] = []
    if observed < min_markets:
        reasons.append(f"only {observed} unique markets; need {min_markets}")
    if anchor_change is None:
        reasons.append(f"anchor {anchor_symbol} is missing")
    elif anchor_change < min_anchor_change_pct:
        reasons.append(
            f"anchor change {anchor_change:.2f}% is below {min_anchor_change_pct:.2f}%"
        )
    if breadth < min_positive_breadth_pct:
        reasons.append(
            f"positive breadth {breadth:.2f}% is below {min_positive_breadth_pct:.2f}%"
        )

    is_risk_on = not reasons
    if is_risk_on:
        reasons.append("anchor momentum and cross-market breadth both passed")

    return RegimeAssessment(
        is_risk_on=is_risk_on,
        anchor_symbol=anchor_symbol,
        anchor_change_pct=anchor_change,
        positive_breadth_pct=breadth,
        observed_markets=observed,
        reasons=tuple(reasons),
    )

