from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest

from exchange_monitoring.paper_exit import (
    ExitAction,
    PaperShortPosition,
    ShortExitPolicy,
    evaluate_short_exit,
)


OPENED = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)


class PaperExitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.position = PaperShortPosition(Decimal("100"), OPENED)

    def test_hard_stop(self) -> None:
        result = evaluate_short_exit(self.position, Decimal("104"), OPENED + timedelta(minutes=5))
        self.assertEqual(result.action, ExitAction.HARD_STOP)
        self.assertEqual(result.pnl_pct, Decimal("-4.00"))

    def test_take_profit(self) -> None:
        result = evaluate_short_exit(self.position, Decimal("94"), OPENED + timedelta(minutes=10))
        self.assertEqual(result.action, ExitAction.TAKE_PROFIT)
        self.assertEqual(result.pnl_pct, Decimal("6.00"))

    def test_trailing_stop_keeps_state_between_observations(self) -> None:
        first = evaluate_short_exit(self.position, Decimal("95.5"), OPENED + timedelta(minutes=30))
        self.assertEqual(first.action, ExitAction.HOLD)
        self.assertTrue(first.position.trailing_armed)

        second = evaluate_short_exit(first.position, Decimal("97"), OPENED + timedelta(hours=1))
        self.assertEqual(second.action, ExitAction.TRAILING_STOP)
        self.assertGreater(second.pnl_pct, Decimal("0"))

    def test_timeout(self) -> None:
        policy = ShortExitPolicy(max_holding=timedelta(hours=1))
        result = evaluate_short_exit(
            self.position,
            Decimal("99"),
            OPENED + timedelta(hours=1),
            policy,
        )
        self.assertEqual(result.action, ExitAction.TIMEOUT)

    def test_rejects_naive_timestamp(self) -> None:
        with self.assertRaisesRegex(ValueError, "timezone"):
            evaluate_short_exit(self.position, Decimal("99"), datetime(2026, 1, 1, 13, 0))


if __name__ == "__main__":
    unittest.main()


