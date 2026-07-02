from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class SolanaMarketSnapshot:
    observed_at: datetime
    price_usd: Decimal
    market_cap_usd: Decimal
    volume_24h_usd: Decimal
    change_24h_pct: Decimal
    tvl_usd: Decimal
    sources: tuple[str, ...]


@dataclass(frozen=True)
class SolanaPricePoint:
    observed_at: datetime
    price_usd: Decimal


@dataclass(frozen=True)
class HorizonReturn:
    days: int
    change_pct: Decimal


@dataclass(frozen=True)
class SolanaMarketMetrics:
    returns: tuple[HorizonReturn, ...]
    sma_20_usd: Decimal
    annualized_volatility_pct: Decimal
    max_drawdown_pct: Decimal
    range_30d_low_usd: Decimal
    range_30d_high_usd: Decimal
    trend: str


@dataclass(frozen=True)
class PositionScenario:
    market_move_pct: Decimal
    resulting_return_pct: Decimal


@dataclass(frozen=True)
class SolanaPositionAnalysis:
    entry_price_usd: Decimal
    current_price_usd: Decimal
    return_pct: Decimal
    breakeven_drawdown_pct: Decimal
    quantity: Decimal | None
    cost_usd: Decimal | None
    market_value_usd: Decimal | None
    unrealized_pnl_usd: Decimal | None
    scenarios: tuple[PositionScenario, ...]


@dataclass(frozen=True)
class SolanaResearchItem:
    title: str
    detail: str
    source: str


@dataclass(frozen=True)
class SolanaMilestone:
    date: str
    title: str
    impact: str
    source: str


@dataclass(frozen=True)
class SolanaResearchProfile:
    overview: str
    value_mechanisms: tuple[SolanaResearchItem, ...]
    catalysts: tuple[SolanaResearchItem, ...]
    risks: tuple[SolanaResearchItem, ...]
    milestones: tuple[SolanaMilestone, ...]


@dataclass(frozen=True)
class SolanaAnalysis:
    snapshot: SolanaMarketSnapshot
    metrics: SolanaMarketMetrics
    profile: SolanaResearchProfile
    position: SolanaPositionAnalysis | None
