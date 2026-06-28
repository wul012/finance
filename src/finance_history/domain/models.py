from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class PriceDirection(str, Enum):
    UP = "上涨"
    DOWN = "下跌"
    FLAT = "震荡"


@dataclass(frozen=True)
class MoneyMaterial:
    id: str
    name: str
    category: str
    active_from_year: int
    active_to_year: int | None
    value_basis: str
    strengths: tuple[str, ...]
    limits: tuple[str, ...]


@dataclass(frozen=True)
class Asset:
    id: str
    name: str
    asset_type: str
    quote_currency: str
    unit: str
    description: str
    related_material_ids: tuple[str, ...]


@dataclass(frozen=True)
class MarketEvent:
    id: str
    year: int
    name: str
    summary: str
    direct_reason: str
    deep_reason: str
    affected_assets: tuple[str, ...]
    affected_materials: tuple[str, ...]
    tags: tuple[str, ...]
    source: str


@dataclass(frozen=True)
class PricePoint:
    asset_id: str
    year: int
    price: Decimal
    unit: str
    source: str
    note: str


@dataclass(frozen=True)
class TimelineEntry:
    year: int
    title: str
    kind: str
    summary: str


@dataclass(frozen=True)
class TrendWindow:
    asset_id: str
    start_year: int
    end_year: int
    start_price: Decimal
    end_price: Decimal
    unit: str
    change_pct: Decimal
    direction: PriceDirection
    related_events: tuple[MarketEvent, ...]

