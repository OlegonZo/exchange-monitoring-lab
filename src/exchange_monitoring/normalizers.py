"""Adapters from representative MEXC and Hyperliquid payloads."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping, Sequence

from .models import Exchange, MarketSnapshot


def _decimal(value: Any, field: str) -> Decimal:
    if value is None or isinstance(value, bool):
        raise ValueError(f"missing or invalid {field}")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid decimal in {field}: {value!r}") from exc


def _optional_decimal(value: Any, field: str) -> Decimal | None:
    return None if value in (None, "") else _decimal(value, field)


def _first(payload: Mapping[str, Any], *names: str) -> Any:
    for name in names:
        if name in payload and payload[name] not in (None, ""):
            return payload[name]
    return None


def _canonical_symbol(raw: str) -> str:
    symbol = raw.strip().upper().replace("-", "/").replace("_", "/")
    if "/" not in symbol:
        for quote in ("USDT", "USDC", "USD"):
            if symbol.endswith(quote) and len(symbol) > len(quote):
                symbol = f"{symbol[:-len(quote)]}/{quote}"
                break
        else:
            raise ValueError(f"cannot infer quote asset from symbol {raw!r}")
    base, quote = symbol.split("/", 1)
    if not base or not quote:
        raise ValueError(f"invalid symbol {raw!r}")
    if quote in {"USD", "USDT", "USDC"}:
        quote = "USD"
    return f"{base}/{quote}"


def normalize_mexc_snapshot(payload: Mapping[str, Any]) -> MarketSnapshot:
    """Normalize common MEXC spot or contract ticker field names.

    If a payload has no explicit 24-hour open, an open is reconstructed from
    ``riseFallRate``. MEXC contract payloads represent that rate as a ratio
    (for example, ``0.02`` means 2%).
    """

    symbol_raw = _first(payload, "symbol", "contractCode")
    if not isinstance(symbol_raw, str):
        raise ValueError("missing MEXC symbol")

    mark_price = _decimal(_first(payload, "lastPrice", "fairPrice", "price"), "last price")
    open_raw = _first(payload, "openPrice", "openPrice24h")
    if open_raw is None:
        rate = _decimal(_first(payload, "riseFallRate"), "rise/fall rate")
        denominator = Decimal("1") + rate
        if denominator <= 0:
            raise ValueError("rise/fall rate implies an invalid open price")
        day_open = mark_price / denominator
    else:
        day_open = _decimal(open_raw, "open price")

    return MarketSnapshot(
        exchange=Exchange.MEXC,
        symbol=_canonical_symbol(symbol_raw),
        mark_price=mark_price,
        day_open_price=day_open,
        quote_volume_24h=_decimal(
            _first(payload, "quoteVolume", "amount24", "volume24"),
            "24h quote volume",
        ),
        best_bid=_optional_decimal(_first(payload, "bidPrice", "bid1", "bid"), "best bid"),
        best_ask=_optional_decimal(_first(payload, "askPrice", "ask1", "ask"), "best ask"),
    )


def normalize_hyperliquid_snapshot(
    coin: str,
    context: Mapping[str, Any],
) -> MarketSnapshot:
    """Normalize one Hyperliquid ``metaAndAssetCtxs`` asset context."""

    if not coin.strip():
        raise ValueError("missing Hyperliquid coin")
    impact = context.get("impactPxs")
    if impact is not None and (
        not isinstance(impact, Sequence) or isinstance(impact, (str, bytes)) or len(impact) < 2
    ):
        raise ValueError("impactPxs must contain bid and ask")

    bid = impact[0] if impact else None
    ask = impact[1] if impact else None
    return MarketSnapshot(
        exchange=Exchange.HYPERLIQUID,
        symbol=_canonical_symbol(f"{coin}/USDC"),
        mark_price=_decimal(context.get("markPx"), "mark price"),
        day_open_price=_decimal(context.get("prevDayPx"), "previous-day price"),
        quote_volume_24h=_decimal(context.get("dayNtlVlm"), "24h notional volume"),
        best_bid=_optional_decimal(bid, "impact bid"),
        best_ask=_optional_decimal(ask, "impact ask"),
    )

