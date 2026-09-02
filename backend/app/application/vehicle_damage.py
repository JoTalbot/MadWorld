"""Authoritative component damage and repair use cases."""

from __future__ import annotations

from uuid import UUID

from app.application.errors import NotFound
from app.application.ports import UnitOfWork
from app.domain.primitives import DamageType, Vehicle


class VehicleDamageService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def get(self, vehicle_id: UUID) -> Vehicle:
        vehicle = self.uow.vehicles.get(vehicle_id)
        if vehicle is None:
            raise NotFound("vehicle not found")
        return vehicle

    def apply_damage(self, vehicle_id: UUID, component: str, amount: int, damage_type: DamageType) -> Vehicle:
        vehicle = self.get(vehicle_id)
        applied = vehicle.apply_damage(component, amount, damage_type)
        self.uow.vehicles.save(vehicle)
        self._record("vehicle.component_damaged", vehicle.id, {
            "component": component,
            "raw_amount": amount,
            "applied_amount": applied,
            "damage_type": damage_type.value,
            "durability": vehicle.durability,
            "state": vehicle.state.value,
        })
        return vehicle

    def repair_component(self, vehicle_id: UUID, component: str, amount: int) -> Vehicle:
        vehicle = self.get(vehicle_id)
        restored = vehicle.repair_component(component, amount)
        if restored == 0:
            raise ValueError("vehicle component is already fully repaired")
        self.uow.vehicles.save(vehicle)
        self._record("vehicle.component_repaired", vehicle.id, {
            "component": component,
            "amount": restored,
            "durability": vehicle.durability,
        })
        return vehicle

    def _record(self, event_type: str, vehicle_id: UUID, payload: dict) -> None:
        from app.domain.events import DEFAULT_EVENT_REGISTRY
        event = DEFAULT_EVENT_REGISTRY.create(event_type, "vehicle", vehicle_id, payload)
        self.uow.audit.append(event.event_type, event.aggregate_type, vehicle_id, event.to_dict())
        self.uow.outbox.enqueue(event.event_type, event.aggregate_type, vehicle_id, event.to_dict())
