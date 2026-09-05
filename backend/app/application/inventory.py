"""Deterministic inventory use cases."""

from __future__ import annotations

from uuid import UUID

from app.application.errors import NotFound
from app.application.ports import UnitOfWork
from app.domain.primitives import InvalidQuantity, InventoryStack


class InventoryService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def add(self, inventory_id: UUID, item_definition_id: UUID, quantity: int, condition: int = 100) -> InventoryStack:
        if quantity <= 0:
            raise InvalidQuantity("inventory quantity must be positive")
        stack = self.uow.inventories.get_stack(inventory_id, item_definition_id)
        if stack is None:
            stack = InventoryStack(item_definition_id, quantity, condition)
        else:
            stack.quantity += quantity
            stack.condition = min(stack.condition, condition)
        self.uow.inventories.save_stack(inventory_id, stack)
        self._record("inventory.stack_added", inventory_id, {"item_definition_id": str(item_definition_id), "quantity": quantity})
        self.uow.commit()
        return stack

    def remove(self, inventory_id: UUID, item_definition_id: UUID, quantity: int) -> InventoryStack | None:
        if quantity <= 0:
            raise InvalidQuantity("inventory quantity must be positive")
        stack = self.uow.inventories.get_stack(inventory_id, item_definition_id)
        if stack is None or stack.quantity < quantity:
            raise NotFound("inventory stack does not contain enough items")
        stack.quantity -= quantity
        if stack.quantity == 0:
            self.uow.inventories.delete_stack(inventory_id, item_definition_id)
            result = None
        else:
            self.uow.inventories.save_stack(inventory_id, stack)
            result = stack
        self._record("inventory.stack_removed", inventory_id, {"item_definition_id": str(item_definition_id), "quantity": quantity})
        self.uow.commit()
        return result

    def _record(self, event_type: str, aggregate_id: UUID, payload: dict) -> None:
        self.uow.audit.append(event_type, "inventory", aggregate_id, payload)
        self.uow.outbox.enqueue(event_type, "inventory", aggregate_id, payload)
