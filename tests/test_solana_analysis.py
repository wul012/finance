from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from finance_history.domain import (
    SolanaMarketSnapshot,
    SolanaPricePoint,
    SolanaResearchProfile,
)
from finance_history.services.solana_analysis import SolanaAnalyzer
from finance_history.services.solana_report import SolanaMarkdownReportBuilder


class SolanaAnalyzerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 7, 2, 8, tzinfo=timezone.utc)
        self.snapshot = SolanaMarketSnapshot(
            observed_at=self.now,
            price_usd=Decimal("120"),
            market_cap_usd=Decimal("70000000000"),
            volume_24h_usd=Decimal("4000000000"),
            change_24h_pct=Decimal("8"),
            tvl_usd=Decimal("5000000000"),
            sources=("https://example.com/market",),
        )
        self.history = [
            SolanaPricePoint(
                observed_at=self.now - timedelta(days=99 - index),
                price_usd=Decimal(80 + index) / Decimal("1.5"),
            )
            for index in range(100)
        ]
        self.profile = SolanaResearchProfile(
            overview="测试简介",
            value_mechanisms=(),
            catalysts=(),
            risks=(),
            milestones=(),
        )

    def test_profit_percentage_derives_entry_and_breakeven_drawdown(self) -> None:
        analysis = SolanaAnalyzer().analyze(
            self.snapshot,
            self.history,
            self.profile,
            profit_pct=Decimal("20"),
        )

        position = analysis.position
        self.assertIsNotNone(position)
        assert position is not None
        self.assertEqual(position.entry_price_usd, Decimal("100.00"))
        self.assertEqual(position.return_pct, Decimal("20.00"))
        self.assertEqual(position.breakeven_drawdown_pct, Decimal("16.67"))
        scenario = next(
            item for item in position.scenarios if item.market_move_pct == Decimal("-10")
        )
        self.assertEqual(scenario.resulting_return_pct, Decimal("8.00"))

    def test_market_metrics_cover_multiple_horizons(self) -> None:
        analysis = SolanaAnalyzer().analyze(
            self.snapshot, self.history, self.profile
        )

        self.assertEqual(
            {item.days for item in analysis.metrics.returns}, {7, 30, 90}
        )
        self.assertEqual(analysis.metrics.trend, "短期偏强")
        self.assertGreater(analysis.metrics.annualized_volatility_pct, 0)

    def test_report_keeps_market_and_position_metrics_separate(self) -> None:
        analysis = SolanaAnalyzer().analyze(
            self.snapshot,
            self.history,
            self.profile,
            profit_pct=Decimal("20"),
        )

        report = SolanaMarkdownReportBuilder().build(analysis)

        self.assertIn("24 小时涨跌：8.00%", report)
        self.assertIn("当前收益率：20.00%", report)
        self.assertIn("回撤 16.67%", report)

    def test_rejects_quantity_without_cost_basis(self) -> None:
        with self.assertRaisesRegex(ValueError, "quantity requires"):
            SolanaAnalyzer().analyze(
                self.snapshot,
                self.history,
                self.profile,
                quantity=Decimal("10"),
            )


if __name__ == "__main__":
    unittest.main()
