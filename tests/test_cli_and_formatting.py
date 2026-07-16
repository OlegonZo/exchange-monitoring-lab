import json
from pathlib import Path
import unittest

from exchange_monitoring.cli import run_demo


class DemoTests(unittest.TestCase):
    def test_synthetic_demo_is_paper_only_and_deterministic(self) -> None:
        fixture = Path(__file__).parents[1] / "examples" / "sample_market_data.json"
        payload = json.loads(fixture.read_text(encoding="utf-8"))

        output = run_demo(payload)

        self.assertIn("MARKET REGIME | RISK-ON", output)
        self.assertIn("PAPER SHORT | SYNTH/USD | TRAILING_STOP", output)
        self.assertIn("No order was placed.", output)
        self.assertNotIn("token", output.lower())


if __name__ == "__main__":
    unittest.main()

