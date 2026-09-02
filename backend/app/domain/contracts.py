"""Authoritative contract templates and immutable terms."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class ContractType(StrEnum):
    DELIVERY = "delivery"
    GATHERING = "gathering"
    CRAFTING = "crafting"
    SALVAGE = "salvage"
    EXPLORATION = "exploration"


@dataclass(frozen=True, slots=True)
class ContractTemplate:
    code: str
    title: str
    description: str
    contract_type: ContractType
    item_definition_id: UUID
    required_quantity: int
    reward: int
    duration_seconds: int = 3600
    penalty: int = 0

    def __post_init__(self) -> None:
        if not self.code.strip() or not self.title.strip():
            raise ValueError("contract code and title must not be blank")
        if self.required_quantity <= 0 or self.reward <= 0:
            raise ValueError("contract quantity and reward must be positive")
        if self.duration_seconds <= 0 or self.penalty < 0:
            raise ValueError("contract duration must be positive and penalty non-negative")


# Stable definitions. Item UUIDs are deliberately explicit so templates remain deterministic.
CONTRACT_TEMPLATES: tuple[ContractTemplate, ...] = (
    ContractTemplate("scrap-run", "Scrap Run", "Deliver recovered scrap to the settlement depot.", ContractType.DELIVERY, UUID("10000000-0000-0000-0000-000000000001"), 10, 120),
    ContractTemplate("metal-haul", "Metal Haul", "Deliver processed metal for workshop production.", ContractType.DELIVERY, UUID("10000000-0000-0000-0000-000000000002"), 8, 180),
    ContractTemplate("fuel-supply", "Fuel Supply", "Deliver fuel cells to the frontier garage.", ContractType.DELIVERY, UUID("10000000-0000-0000-0000-000000000003"), 5, 220),
    ContractTemplate("parts-request", "Parts Request", "Deliver mechanical parts to keep local vehicles operational.", ContractType.DELIVERY, UUID("10000000-0000-0000-0000-000000000004"), 6, 260),
    ContractTemplate("salvage-cache", "Salvage Cache", "Recover a cache of valuable components and return it to the depot.", ContractType.SALVAGE, UUID("10000000-0000-0000-0000-000000000005"), 3, 350),
)

TEMPLATES_BY_CODE = {template.code: template for template in CONTRACT_TEMPLATES}
