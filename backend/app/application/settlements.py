"""Settlement application service."""
from __future__ import annotations
from uuid import UUID
from app.application.ports import UnitOfWork
from app.domain.events import DEFAULT_EVENT_REGISTRY
from app.domain.settlements import Settlement

DEFAULT_SETTLEMENT_REGION = "dust_basin"

class SettlementService:
    def __init__(self, uow: UnitOfWork) -> None: self.uow = uow

    def get_or_create(self, player_id: UUID, region: str = DEFAULT_SETTLEMENT_REGION) -> Settlement:
        settlement = self.uow.settlements.get_by_owner(player_id)
        if settlement is not None:
            return settlement
        settlement = Settlement.create(player_id, region)
        self.uow.settlements.save(settlement)
        event = DEFAULT_EVENT_REGISTRY.create("settlement.created", "settlement", settlement.id, {"owner_id": str(player_id), "region": settlement.region, "level": settlement.level, "modules": dict(settlement.modules)})
        self.uow.audit.append(event.event_type, event.aggregate_type, event.aggregate_id, event.to_dict())
        self.uow.outbox.enqueue(event.event_type, event.aggregate_type, event.aggregate_id, event.to_dict())
        return settlement
