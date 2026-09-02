"""Authoritative resource gathering use case."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.application.errors import NotFound
from app.application.ports import UnitOfWork
from app.domain.events import DEFAULT_EVENT_REGISTRY


@dataclass(frozen=True, slots=True)
class ResourceNode:
    id: UUID
    region_id: UUID
    resource_item_definition_id: UUID
    quantity: int
    gather_amount: int
    cooldown_seconds: int
    version: int
    last_gathered_at: datetime | None = None


class ResourceNodeRepository:
    """Small protocol-like base used by the gathering service."""

    def get_for_update(self, node_id: UUID) -> ResourceNode | None:  # pragma: no cover
        raise NotImplementedError

    def save(self, node: ResourceNode) -> None:  # pragma: no cover
        raise NotImplementedError


class GatheringService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def gather(self, player_id: UUID, inventory_id: UUID, node_id: UUID, now: datetime | None = None) -> tuple[ResourceNode, int]:
        current = now or datetime.now(timezone.utc)
        node = self.uow.resource_nodes.get_for_update(node_id)
        if node is None:
            raise NotFound("resource node not found")
        if node.quantity <= 0:
            raise ValueError("resource node is depleted")
        if node.last_gathered_at is not None and current < node.last_gathered_at + timedelta(seconds=node.cooldown_seconds):
            raise ValueError("resource node is on cooldown")

        amount = min(node.gather_amount, node.quantity)
        node = ResourceNode(node.id, node.region_id, node.resource_item_definition_id,
                            node.quantity - amount, node.gather_amount, node.cooldown_seconds,
                            node.version, current)
        self.uow.resource_nodes.save(node)
        self.uow.inventories.add_stack(inventory_id, node.resource_item_definition_id, amount, 100)

        event = DEFAULT_EVENT_REGISTRY.create(
            "resource.gathered", "resource_node", node.id,
            {"player_id": str(player_id), "inventory_id": str(inventory_id),
             "item_definition_id": str(node.resource_item_definition_id), "quantity": amount},
        )
        self.uow.audit.append(event.event_type, event.aggregate_type, event.aggregate_id, event.to_dict())
        self.uow.outbox.enqueue(event.event_type, event.aggregate_type, event.aggregate_id, event.to_dict())
        return node, amount
