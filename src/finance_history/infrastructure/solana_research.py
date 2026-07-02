from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from finance_history.domain import (
    SolanaMilestone,
    SolanaResearchItem,
    SolanaResearchProfile,
)
from finance_history.infrastructure.paths import DEFAULT_SEED_DATA_DIR


class SolanaResearchRepository:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_SEED_DATA_DIR

    def load(self) -> SolanaResearchProfile:
        path = self.data_dir / "solana_research.json"
        with path.open("r", encoding="utf-8") as file:
            data: dict[str, Any] = json.load(file)
        return SolanaResearchProfile(
            overview=data["overview"],
            value_mechanisms=_items(data["value_mechanisms"]),
            catalysts=_items(data["catalysts"]),
            risks=_items(data["risks"]),
            milestones=tuple(
                SolanaMilestone(
                    date=row["date"],
                    title=row["title"],
                    impact=row["impact"],
                    source=row["source"],
                )
                for row in data["milestones"]
            ),
        )


def _items(rows: list[dict[str, str]]) -> tuple[SolanaResearchItem, ...]:
    return tuple(
        SolanaResearchItem(
            title=row["title"], detail=row["detail"], source=row["source"]
        )
        for row in rows
    )
