from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from finance_history.infrastructure import SeedRepository


class SeedRepositoryTest(unittest.TestCase):
    def test_loads_seed_data(self) -> None:
        repository = SeedRepository()

        self.assertGreaterEqual(len(repository.load_materials()), 8)
        self.assertGreaterEqual(len(repository.load_assets()), 6)
        self.assertGreaterEqual(len(repository.load_events()), 10)
        self.assertGreaterEqual(len(repository.load_price_points()), 30)

    def test_asset_lookup(self) -> None:
        repository = SeedRepository()

        asset = repository.asset_by_id("gold")

        self.assertEqual(asset.name, "黄金")
        self.assertEqual(asset.unit, "USD/oz")


if __name__ == "__main__":
    unittest.main()

