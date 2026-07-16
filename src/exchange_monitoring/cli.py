"""Command-line demonstration using local, synthetic JSON only."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from .formatting import format_exit_alert, format_regime_alert
from .normalizers import normalize_hyperliquid_snapshot, normalize_mexc_snapshot
from .paper_exit import PaperShortPosition, evaluate_short_exit
from .regime import assess_market_regime


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return parsed


def run_demo(payload: dict[str, Any]) -> str:
    snapshots = [normalize_mexc_snapshot(item) for item in payload.get("mexc", [])]
    snapshots.extend(
        normalize_hyperliquid_snapshot(item["coin"], item["context"])
        for item in payload.get("hyperliquid", [])
    )
    assessment = assess_market_regime(
        snapshots,
        anchor_symbol=payload.get("anchor_symbol", "BTC/USD"),
    )

    lines = ["NORMALIZED SNAPSHOTS"]
    for snapshot in snapshots:
        spread = "n/a" if snapshot.spread_bps is None else f"{snapshot.spread_bps:.2f} bps"
        lines.append(
            f"- {snapshot.exchange.value:11} {snapshot.symbol:10} "
            f"{snapshot.change_pct:+7.2f}% | spread {spread}"
        )
    lines.extend(["", format_regime_alert(assessment)])

    demo_short = payload.get("paper_short")
    if demo_short:
        position = PaperShortPosition(
            entry_price=Decimal(str(demo_short["entry_price"])),
            opened_at=_parse_time(demo_short["opened_at"]),
        )
        evaluation = None
        for point in demo_short.get("price_path", []):
            evaluation = evaluate_short_exit(
                position,
                Decimal(str(point["price"])),
                _parse_time(point["at"]),
            )
            position = evaluation.position
            if evaluation.should_exit:
                break
        if evaluation is not None:
            lines.extend(["", format_exit_alert(demo_short["symbol"], evaluation)])

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a local, synthetic exchange-monitoring demonstration."
    )
    parser.add_argument("input", type=Path, help="path to a synthetic JSON fixture")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    with args.input.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    print(run_demo(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

