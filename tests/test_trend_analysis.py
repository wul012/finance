from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from finance_history.domain import PriceDirection
from finance_history.infrastructure import SeedRepository
from finance_history.services.trend_analysis import TrendAnalyzer


class TrendAnalyzerTest(unittest.TestCase):
    def test_gold_window_links_nixon_shock(self) -> None:
        repository = SeedRepository()
        analyzer = TrendAnalyzer(repository.load_price_points(), repository.load_events())

        window = analyzer.analyze_asset("gold", start_year=1971, end_year=1980)

        self.assertEqual(window.direction, PriceDirection.UP)
        self.assertGreater(window.change_pct, 1000)
        self.assertIn("nixon_shock", {event.id for event in window.related_events})

    def test_bitcoin_2021_to_2022_is_down(self) -> None:
        repository = SeedRepository()
        analyzer = TrendAnalyzer(repository.load_price_points(), repository.load_events())

        window = analyzer.analyze_asset("bitcoin", start_year=2021, end_year=2022)

        self.assertEqual(window.direction, PriceDirection.DOWN)
        self.assertIn("fed_hikes_2022", {event.id for event in window.related_events})


if __name__ == "__main__":
    unittest.main()

