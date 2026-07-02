from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from urllib.request import Request, urlopen

from finance_history.domain import SolanaMarketSnapshot, SolanaPricePoint


COINGECKO_API = "https://api.coingecko.com/api/v3"
DEFILLAMA_API = "https://api.llama.fi"
USER_AGENT = "finance-history-lab/0.2.0"


class SolanaMarketClient:
    """Fetches SOL market data without leaking HTTP concerns into analysis code."""

    def __init__(self, timeout_seconds: float = 15) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch_snapshot(self) -> SolanaMarketSnapshot:
        market_url = (
            f"{COINGECKO_API}/simple/price?ids=solana&vs_currencies=usd"
            "&include_market_cap=true&include_24hr_vol=true"
            "&include_24hr_change=true&include_last_updated_at=true"
        )
        market = self._get_json(market_url)["solana"]
        chains = self._get_json(f"{DEFILLAMA_API}/v2/chains")
        solana = next(chain for chain in chains if chain["name"] == "Solana")

        return SolanaMarketSnapshot(
            observed_at=datetime.fromtimestamp(
                int(market["last_updated_at"]), tz=timezone.utc
            ),
            price_usd=_decimal(market["usd"]),
            market_cap_usd=_decimal(market["usd_market_cap"]),
            volume_24h_usd=_decimal(market["usd_24h_vol"]),
            change_24h_pct=_decimal(market["usd_24h_change"]),
            tvl_usd=_decimal(solana["tvl"]),
            sources=(
                "https://www.coingecko.com/en/coins/solana",
                "https://defillama.com/chain/Solana",
            ),
        )

    def fetch_history(self, days: int = 90) -> list[SolanaPricePoint]:
        if days < 30 or days > 365:
            raise ValueError("history days must be between 30 and 365")
        url = (
            f"{COINGECKO_API}/coins/solana/market_chart"
            f"?vs_currency=usd&days={days}&interval=daily"
        )
        payload = self._get_json(url)
        return [
            SolanaPricePoint(
                observed_at=datetime.fromtimestamp(
                    int(timestamp_ms) / 1000, tz=timezone.utc
                ),
                price_usd=_decimal(price),
            )
            for timestamp_ms, price in payload["prices"]
        ]

    def _get_json(self, url: str) -> Any:
        request = Request(
            url,
            headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        )
        with urlopen(request, timeout=self.timeout_seconds) as response:
            return json.load(response)


def _decimal(value: object) -> Decimal:
    return Decimal(str(value))
