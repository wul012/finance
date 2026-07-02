from __future__ import annotations

import math
import statistics
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from finance_history.domain import (
    HorizonReturn,
    PositionScenario,
    SolanaAnalysis,
    SolanaMarketMetrics,
    SolanaMarketSnapshot,
    SolanaPositionAnalysis,
    SolanaPricePoint,
    SolanaResearchProfile,
)


TWO_PLACES = Decimal("0.01")


class SolanaAnalyzer:
    def analyze(
        self,
        snapshot: SolanaMarketSnapshot,
        history: list[SolanaPricePoint],
        profile: SolanaResearchProfile,
        *,
        entry_price_usd: Decimal | None = None,
        profit_pct: Decimal | None = None,
        quantity: Decimal | None = None,
    ) -> SolanaAnalysis:
        points = self._normalized_points(history, snapshot)
        metrics = self._market_metrics(points, snapshot)
        position = self._position(
            current_price=snapshot.price_usd,
            entry_price=entry_price_usd,
            profit_pct=profit_pct,
            quantity=quantity,
        )
        return SolanaAnalysis(
            snapshot=snapshot,
            metrics=metrics,
            profile=profile,
            position=position,
        )

    def _market_metrics(
        self,
        points: list[SolanaPricePoint],
        snapshot: SolanaMarketSnapshot,
    ) -> SolanaMarketMetrics:
        if len(points) < 30:
            raise ValueError("SOL analysis requires at least 30 daily price points")

        returns = tuple(
            HorizonReturn(days=days, change_pct=self._horizon_return(points, days))
            for days in (7, 30, 90)
            if self._has_horizon(points, days)
        )
        prices = [point.price_usd for point in points]
        recent_20 = prices[-20:]
        recent_30 = prices[-30:]
        sma_20 = sum(recent_20) / Decimal(len(recent_20))
        volatility = self._annualized_volatility(prices)
        max_drawdown = self._max_drawdown(prices)
        return_7d = next(
            (item.change_pct for item in returns if item.days == 7), Decimal("0")
        )

        return SolanaMarketMetrics(
            returns=returns,
            sma_20_usd=_round(sma_20),
            annualized_volatility_pct=_round(volatility),
            max_drawdown_pct=_round(max_drawdown),
            range_30d_low_usd=_round(min(recent_30)),
            range_30d_high_usd=_round(max(recent_30)),
            trend=self._trend(snapshot.price_usd, sma_20, return_7d),
        )

    def _position(
        self,
        *,
        current_price: Decimal,
        entry_price: Decimal | None,
        profit_pct: Decimal | None,
        quantity: Decimal | None,
    ) -> SolanaPositionAnalysis | None:
        if entry_price is not None and profit_pct is not None:
            raise ValueError("entry price and profit percentage cannot be used together")
        if profit_pct is not None:
            if profit_pct <= Decimal("-100"):
                raise ValueError("profit percentage must be greater than -100")
            entry_price = current_price / (Decimal("1") + profit_pct / Decimal("100"))
        if entry_price is None:
            if quantity is not None:
                raise ValueError("quantity requires entry price or profit percentage")
            return None
        if entry_price <= 0:
            raise ValueError("entry price must be positive")
        if quantity is not None and quantity <= 0:
            raise ValueError("quantity must be positive")

        actual_return = (current_price / entry_price - Decimal("1")) * Decimal("100")
        breakeven_drawdown = (
            (current_price - entry_price) / current_price * Decimal("100")
        )
        scenarios = tuple(
            PositionScenario(
                market_move_pct=move,
                resulting_return_pct=_round(
                    current_price
                    * (Decimal("1") + move / Decimal("100"))
                    / entry_price
                    * Decimal("100")
                    - Decimal("100")
                ),
            )
            for move in map(Decimal, ("-5", "-10", "-15", "-20", "5", "10"))
        )
        cost = entry_price * quantity if quantity is not None else None
        market_value = current_price * quantity if quantity is not None else None
        pnl = market_value - cost if market_value is not None and cost is not None else None

        return SolanaPositionAnalysis(
            entry_price_usd=_round(entry_price),
            current_price_usd=_round(current_price),
            return_pct=_round(actual_return),
            breakeven_drawdown_pct=_round(breakeven_drawdown),
            quantity=quantity,
            cost_usd=_round(cost) if cost is not None else None,
            market_value_usd=_round(market_value) if market_value is not None else None,
            unrealized_pnl_usd=_round(pnl) if pnl is not None else None,
            scenarios=scenarios,
        )

    @staticmethod
    def _normalized_points(
        history: list[SolanaPricePoint], snapshot: SolanaMarketSnapshot
    ) -> list[SolanaPricePoint]:
        by_date = {point.observed_at.date(): point for point in history}
        by_date[snapshot.observed_at.date()] = SolanaPricePoint(
            observed_at=snapshot.observed_at,
            price_usd=snapshot.price_usd,
        )
        return sorted(by_date.values(), key=lambda point: point.observed_at)

    @staticmethod
    def _has_horizon(points: list[SolanaPricePoint], days: int) -> bool:
        # Daily APIs can start several hours inside the requested window.
        tolerance = timedelta(days=1)
        return points[0].observed_at <= points[-1].observed_at - timedelta(days=days) + tolerance

    @staticmethod
    def _horizon_return(points: list[SolanaPricePoint], days: int) -> Decimal:
        cutoff = points[-1].observed_at.date() - timedelta(days=days)
        start = min(points, key=lambda point: abs((point.observed_at.date() - cutoff).days))
        return _round((points[-1].price_usd / start.price_usd - 1) * Decimal("100"))

    @staticmethod
    def _annualized_volatility(prices: list[Decimal]) -> Decimal:
        log_returns = [
            math.log(float(current / previous))
            for previous, current in zip(prices, prices[1:])
            if previous > 0 and current > 0
        ]
        if len(log_returns) < 2:
            return Decimal("0")
        return Decimal(str(statistics.stdev(log_returns) * math.sqrt(365) * 100))

    @staticmethod
    def _max_drawdown(prices: list[Decimal]) -> Decimal:
        peak = prices[0]
        worst = Decimal("0")
        for price in prices:
            peak = max(peak, price)
            drawdown = (price / peak - Decimal("1")) * Decimal("100")
            worst = min(worst, drawdown)
        return worst

    @staticmethod
    def _trend(current: Decimal, sma_20: Decimal, return_7d: Decimal) -> str:
        if current > sma_20 and return_7d > 0:
            return "短期偏强"
        if current < sma_20 and return_7d < 0:
            return "短期偏弱"
        return "方向分化"


def _round(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
