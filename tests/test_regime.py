from decimal import Decimal
import unittest

from exchange_monitoring.models import Exchange, MarketSnapshot
from exchange_monitoring.regime import assess_market_regime


def snapshot(symbol: str, change_pct: str, exchange: Exchange = Exchange.MEXC) -> MarketSnapshot:
    open_price = Decimal("100")
    return MarketSnapshot(
        exchange=exchange,
        symbol=symbol,
        mark_price=open_price * (Decimal("1") + Decimal(change_pct) / Decimal("100")),
        day_open_price=open_price,
        quote_volume_24h=Decimal("1000000"),
    )


class RegimeTests(unittest.TestCase):
    def test_risk_on_when_anchor_and_breadth_pass(self) -> None:
        result = assess_market_regime(
            [
                snapshot("BTC/USD", "2"),
                snapshot("ETH/USD", "1"),
                snapshot("SOL/USD", "-0.5"),
            ]
        )

        self.assertTrue(result.is_risk_on)
        self.assertEqual(result.positive_breadth_pct, Decimal("66.66666666666666666666666667"))

    def test_duplicate_exchange_symbols_receive_one_breadth_vote(self) -> None:
        result = assess_market_regime(
            [
                snapshot("BTC/USD", "2", Exchange.MEXC),
                snapshot("BTC/USD", "4", Exchange.HYPERLIQUID),
                snapshot("ETH/USD", "1"),
                snapshot("SOL/USD", "-1"),
            ]
        )

        self.assertEqual(result.observed_markets, 3)
        self.assertEqual(result.anchor_change_pct, Decimal("3.00"))
        self.assertTrue(result.is_risk_on)

    def test_guarded_when_anchor_is_missing(self) -> None:
        result = assess_market_regime(
            [snapshot("ETH/USD", "3"), snapshot("SOL/USD", "2")],
            min_markets=2,
        )

        self.assertFalse(result.is_risk_on)
        self.assertIn("anchor BTC/USD is missing", result.reasons)


if __name__ == "__main__":
    unittest.main()

