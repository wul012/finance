from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from finance_history.infrastructure import SeedRepository
from finance_history.services.timeline import TimelineService, format_year


class TimelineServiceTest(unittest.TestCase):
    def test_builds_sorted_timeline(self) -> None:
        repository = SeedRepository()
        entries = TimelineService().build(
            materials=repository.load_materials(),
            events=repository.load_events(),
        )

        self.assertEqual(entries, sorted(entries, key=lambda entry: (entry.year, entry.kind, entry.title)))
        self.assertIn("公元前600年", format_year(-600))


if __name__ == "__main__":
    unittest.main()

