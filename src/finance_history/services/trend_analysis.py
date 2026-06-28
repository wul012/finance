from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from finance_history.domain import MarketEvent, PriceDirection, PricePoint, TrendWindow


class TrendAnalyzer:
    def __init__(
        self,
        price_points: list[PricePoint],
        events: list[MarketEvent],
        threshold_pct: Decimal = Decimal("5"),
    ) -> None:
        self.price_points = price_points
        self.events = events
        self.threshold_pct = threshold_pct

    def analyze_asset(
        self,
        asset_id: str,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> TrendWindow:
        points = self._points_for_asset(asset_id)
        if start_year is not None:
            points = [point for point in points if point.year >= start_year]
        if end_year is not None:
            points = [point for point in points if point.year <= end_year]
        if len(points) < 2:
            raise ValueError(f"{asset_id} 至少需要两个价格观察点才能分析")

        start = points[0]
        end = points[-1]
        change_pct = ((end.price - start.price) / start.price * Decimal("100")).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        return TrendWindow(
            asset_id=asset_id,
            start_year=start.year,
            end_year=end.year,
            start_price=start.price,
            end_price=end.price,
            unit=end.unit,
            change_pct=change_pct,
            direction=self._direction(change_pct),
            related_events=self._events_for_asset(asset_id, start.year, end.year),
        )

    def adjacent_windows(self, asset_id: str) -> list[TrendWindow]:
        points = self._points_for_asset(asset_id)
        return [
            self.analyze_asset(asset_id, start_year=start.year, end_year=end.year)
            for start, end in zip(points, points[1:])
        ]

    def _points_for_asset(self, asset_id: str) -> list[PricePoint]:
        points = [point for point in self.price_points if point.asset_id == asset_id]
        if not points:
            raise ValueError(f"没有找到资产价格观察点：{asset_id}")
        return sorted(points, key=lambda point: point.year)

    def _events_for_asset(
        self,
        asset_id: str,
        start_year: int,
        end_year: int,
    ) -> tuple[MarketEvent, ...]:
        matched = [
            event
            for event in self.events
            if start_year <= event.year <= end_year
            and (asset_id in event.affected_assets or "*" in event.affected_assets)
        ]
        return tuple(sorted(matched, key=lambda event: event.year))

    def _direction(self, change_pct: Decimal) -> PriceDirection:
        if change_pct > self.threshold_pct:
            return PriceDirection.UP
        if change_pct < -self.threshold_pct:
            return PriceDirection.DOWN
        return PriceDirection.FLAT


def format_decimal(value: Decimal) -> str:
    normalized = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{normalized:,.2f}"

