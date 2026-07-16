from decimal import Decimal
import unittest

from exchange_monitoring.models import Exchange
from exchange_monitoring.normalizers import (
    normalize_hyperliquid_snapshot,
    normalize_mexc_snapshot,
)


class NormalizerTests(unittest.TestCase):
    def test_normalizes_mexc_contract_payload_and_derives_open(self) -> None:
        snapshot = normalize_mexc_snapshot(
            {
                "symbol": "BTC_USDT",
                "lastPrice": "102",
                "riseFallRate": "0.02",
                "amount24": "500000",
                "bid1": "101.9",
                "ask1": "102.1",
            }
        )

        self.assertEqual(snapshot.exchange, Exchange.MEXC)
        self.assertEqual(snapshot.symbol, "BTC/USD")
        self.assertEqual(snapshot.day_open_price, Decimal("100"))
        self.assertEqual(snapshot.change_pct, Decimal("2.00"))

    def test_normalizes_hyperliquid_context(self) -> None:
        snapshot = normalize_hyperliquid_snapshot(
            "ETH",
            {
                "markPx": "2100",
                "prevDayPx": "2000",
                "dayNtlVlm": "9000000",
                "impactPxs": ["2099", "2101"],
            },
        )

        self.assertEqual(snapshot.exchange, Exchange.HYPERLIQUID)
        self.assertEqual(snapshot.symbol, "ETH/USD")
        self.assertEqual(snapshot.change_pct, Decimal("5.00"))
        self.assertGreater(snapshot.spread_bps, Decimal("0"))

    def test_rejects_crossed_book(self) -> None:
        with self.assertRaisesRegex(ValueError, "bid cannot exceed"):
            normalize_mexc_snapshot(
                {
                    "symbol": "SOLUSDT",
                    "lastPrice": "100",
                    "openPrice": "99",
                    "quoteVolume": "1000",
                    "bidPrice": "101",
                    "askPrice": "100",
                }
            )

    def test_maps_usdc_and_usdt_to_same_comparison_key(self) -> None:
        usdt = normalize_mexc_snapshot(
            {
                "symbol": "BTCUSDT",
                "lastPrice": "100",
                "openPrice": "99",
                "quoteVolume": "1000",
            }
        )
        usdc = normalize_mexc_snapshot(
            {
                "symbol": "BTCUSDC",
                "lastPrice": "100",
                "openPrice": "99",
                "quoteVolume": "1000",
            }
        )

        self.assertEqual(usdt.symbol, "BTC/USD")
        self.assertEqual(usdc.symbol, "BTC/USD")


if __name__ == "__main__":
    unittest.main()

