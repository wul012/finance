from __future__ import annotations

from finance_history.domain import MarketEvent, MoneyMaterial, TimelineEntry


class TimelineService:
    def build(
        self,
        materials: list[MoneyMaterial],
        events: list[MarketEvent],
    ) -> list[TimelineEntry]:
        entries: list[TimelineEntry] = []
        for material in materials:
            entries.append(
                TimelineEntry(
                    year=material.active_from_year,
                    title=f"{material.name}成为货币材料或信用载体",
                    kind="货币材料",
                    summary=f"价值基础：{material.value_basis}",
                )
            )
        for event in events:
            entries.append(
                TimelineEntry(
                    year=event.year,
                    title=event.name,
                    kind="金融事件",
                    summary=event.summary,
                )
            )
        return sorted(entries, key=lambda entry: (entry.year, entry.kind, entry.title))


def format_year(year: int) -> str:
    if year < 0:
        return f"公元前{abs(year)}年"
    return f"{year}年"

