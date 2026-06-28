from __future__ import annotations

import csv
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from finance_history.domain import Asset, MarketEvent, MoneyMaterial, PricePoint
from finance_history.infrastructure.paths import DEFAULT_SEED_DATA_DIR


class SeedRepository:
    """Loads the versioned offline seed data used by the first release."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_SEED_DATA_DIR

    def load_materials(self) -> list[MoneyMaterial]:
        rows = self._load_json("materials.json")
        return [
            MoneyMaterial(
                id=row["id"],
                name=row["name"],
                category=row["category"],
                active_from_year=int(row["active_from_year"]),
                active_to_year=_optional_int(row.get("active_to_year")),
                value_basis=row["value_basis"],
                strengths=_tuple(row.get("strengths")),
                limits=_tuple(row.get("limits")),
            )
            for row in rows
        ]

    def load_assets(self) -> list[Asset]:
        rows = self._load_json("assets.json")
        return [
            Asset(
                id=row["id"],
                name=row["name"],
                asset_type=row["asset_type"],
                quote_currency=row["quote_currency"],
                unit=row["unit"],
                description=row["description"],
                related_material_ids=_tuple(row.get("related_material_ids")),
            )
            for row in rows
        ]

    def load_events(self) -> list[MarketEvent]:
        rows = self._load_json("events.json")
        events = [
            MarketEvent(
                id=row["id"],
                year=int(row["year"]),
                name=row["name"],
                summary=row["summary"],
                direct_reason=row["direct_reason"],
                deep_reason=row["deep_reason"],
                affected_assets=_tuple(row.get("affected_assets")),
                affected_materials=_tuple(row.get("affected_materials")),
                tags=_tuple(row.get("tags")),
                source=row["source"],
            )
            for row in rows
        ]
        return sorted(events, key=lambda event: event.year)

    def load_price_points(self) -> list[PricePoint]:
        path = self.data_dir / "prices.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            points = [
                PricePoint(
                    asset_id=row["asset_id"],
                    year=int(row["year"]),
                    price=Decimal(row["price"]),
                    unit=row["unit"],
                    source=row["source"],
                    note=row["note"],
                )
                for row in reader
            ]
        return sorted(points, key=lambda point: (point.asset_id, point.year))

    def asset_by_id(self, asset_id: str) -> Asset:
        for asset in self.load_assets():
            if asset.id == asset_id:
                return asset
        raise ValueError(f"unknown asset id: {asset_id}")

    def _load_json(self, filename: str) -> list[dict[str, Any]]:
        path = self.data_dir / filename
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)


def _tuple(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise TypeError(f"expected list or null, got {type(value).__name__}")
    return tuple(str(item) for item in value)


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    return int(value)

