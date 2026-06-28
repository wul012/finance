from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from finance_history.infrastructure import SeedRepository
from finance_history.services.report import MarkdownReportBuilder


class MarkdownReportBuilderTest(unittest.TestCase):
    def test_report_contains_core_sections(self) -> None:
        report = MarkdownReportBuilder(SeedRepository()).build()

        self.assertIn("# 金融与货币材料发展及涨跌历史第一版报告", report)
        self.assertIn("## 2. 货币材料演变概览", report)
        self.assertIn("## 4. 资产涨跌摘要", report)
        self.assertIn("黄金", report)
        self.assertIn("比特币", report)


if __name__ == "__main__":
    unittest.main()

