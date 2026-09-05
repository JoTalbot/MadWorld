"""Persistent player settlement domain model."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Settlement:
    id: UUID
    owner_id: UUID
    region: str
    level: int = 1
    modules: dict[str, int] = field(default_factory=lambda: {
        "garage": 1,
        "warehouse": 1,
        "workshop": 1,
        "contracts": 1,
        "market": 1,
    })
    version: int = 0

    @classmethod
    def create(cls, owner_id: UUID, region: str) -> Settlement:
        if not region.strip():
            raise ValueError("settlement region is required")
        return cls(uuid4(), owner_id, region.strip(), 1)

    def interaction_capabilities(self) -> dict[str, bool]:
        return {name: level > 0 for name, level in self.modules.items()}
