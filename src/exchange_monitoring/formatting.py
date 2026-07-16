"""Plain-text alert formatting suitable for a Telegram transport adapter."""

from __future__ import annotations

from .models import RegimeAssessment
from .paper_exit import ExitEvaluation


def format_regime_alert(assessment: RegimeAssessment) -> str:
    state = "RISK-ON" if assessment.is_risk_on else "GUARDED"
    anchor = (
        "n/a"
        if assessment.anchor_change_pct is None
        else f"{assessment.anchor_change_pct:+.2f}%"
    )
    details = "; ".join(assessment.reasons)
    return (
        f"MARKET REGIME | {state}\n"
        f"Anchor {assessment.anchor_symbol}: {anchor}\n"
        f"Positive breadth: {assessment.positive_breadth_pct:.2f}% "
        f"across {assessment.observed_markets} markets\n"
        f"Reason: {details}\n"
        "Mode: monitoring / paper-only"
    )


def format_exit_alert(symbol: str, evaluation: ExitEvaluation) -> str:
    stop = "n/a" if evaluation.active_stop is None else f"{evaluation.active_stop:.8f}"
    return (
        f"PAPER SHORT | {symbol} | {evaluation.action.value.upper()}\n"
        f"Unrealized PnL: {evaluation.pnl_pct:+.2f}%\n"
        f"Reference stop: {stop}\n"
        f"Reason: {evaluation.reason}\n"
        "No order was placed."
    )


