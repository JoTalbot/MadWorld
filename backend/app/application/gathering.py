"""Authoritative resource gathering use case."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.application.errors import NotFound
from app.application.ports import UnitOfWork
from app.application.services import InventoryService
from app.domain.events import DEFAULT_EVENT_REGISTRY


@dataclass(frozen=True, slots=True)
class ResourceNode:
    id: UUID; region_id: UUID; resource_item_definition_id: UUID; quantity: int; gather_amount: int; cooldown_seconds: int; version: int; last_gathered_at: datetime|None=None

class GatheringService:
    def __init__(self,uow: UnitOfWork)->None: self.uow=uow
    def _nodes(self):
        nodes=getattr(self.uow,"resource_nodes",None)
        if nodes is not None:return nodes
        conn=getattr(self.uow,"conn",None)
        if conn is None: raise RuntimeError("resource node repository is not configured")
        from app.infrastructure.resource_nodes import PostgresResourceNodeRepository
        return PostgresResourceNodeRepository(conn)
    def gather(self,player_id:UUID,inventory_id:UUID,node_id:UUID,now:datetime|None=None):
        current=now or datetime.now(UTC); node=self._nodes().get_for_update(node_id)
        if node is None: raise NotFound("resource node not found")
        if node.quantity<=0: raise ValueError("resource node is depleted")
        if node.last_gathered_at is not None and current<node.last_gathered_at+timedelta(seconds=node.cooldown_seconds): raise ValueError("resource node is on cooldown")
        amount=min(node.gather_amount,node.quantity); updated=ResourceNode(node.id,node.region_id,node.resource_item_definition_id,node.quantity-amount,node.gather_amount,node.cooldown_seconds,node.version,current)
        self._nodes().save(updated); InventoryService(self.uow).add(inventory_id,node.resource_item_definition_id,amount,100)
        payload={"player_id":str(player_id),"inventory_id":str(inventory_id),"item_definition_id":str(node.resource_item_definition_id),"quantity":amount}
        event=DEFAULT_EVENT_REGISTRY.create("resource.gathered","resource_node",node.id,payload)
        self.uow.audit.append(event.event_type,event.aggregate_type,event.aggregate_id,event.to_dict()); self.uow.outbox.enqueue(event.event_type,event.aggregate_type,event.aggregate_id,event.to_dict())
        if hasattr(self.uow,"contracts"):
            from app.application.contract_service import ContractService
            ContractService(self.uow).apply_event(player_id,event.event_type,payload,current)
        return updated,amount
