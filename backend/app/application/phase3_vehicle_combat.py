"""Phase 3 authoritative vehicle fitting, combat, salvage and recovery primitives."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from app.domain.primitives import DamageType, InvalidQuantity, InvalidTransition, Vehicle, VehicleState

@dataclass(frozen=True, slots=True)
class Module:
    id: UUID
    code: str
    slot_type: str
    mass: int = 1
    armor: int = 0
    power: int = 0
    fuel_modifier_bps: int = 0

@dataclass(frozen=True, slots=True)
class Weapon:
    id: UUID
    code: str
    damage: int
    damage_type: DamageType
    range_m: int = 100
    cooldown_seconds: int = 5

@dataclass(frozen=True, slots=True)
class CombatResult:
    action_id: UUID
    applied_damage: int
    target_state: VehicleState
    target_durability: int

class VehicleFittingService:
    def fit(self, vehicle: Vehicle, slot: int, module: Module, slots: int = 4) -> None:
        if slot < 0 or slot >= slots: raise InvalidQuantity("invalid fitting slot")
        if module.mass <= 0: raise InvalidQuantity("module mass must be positive")
        vehicle.metadata = getattr(vehicle, "metadata", {})
        vehicle.metadata[f"module:{slot}"] = module.code

class CombatService:
    def attack(self, attacker: Vehicle, target: Vehicle, weapon: Weapon, component: str, distance_m: int, idempotency_key: str) -> CombatResult:
        if attacker.state is VehicleState.DESTROYED: raise InvalidTransition("destroyed attacker cannot attack")
        if target.state is VehicleState.DESTROYED: raise InvalidTransition("destroyed target cannot be attacked")
        if distance_m < 0 or distance_m > weapon.range_m: raise InvalidTransition("target is out of weapon range")
        applied = target.apply_damage(component, weapon.damage, weapon.damage_type)
        return CombatResult(uuid4(), applied, target.state, target.durability)

class SalvageService:
    def recover_percent(self, vehicle: Vehicle) -> int:
        if vehicle.state is not VehicleState.DESTROYED: raise InvalidTransition("only destroyed vehicles can be salvaged")
        return 50

class RecoveryService:
    def start(self, vehicle: Vehicle, now: datetime, duration: timedelta, cost: int = 0) -> tuple[datetime, int]:
        if vehicle.state is not VehicleState.DESTROYED: raise InvalidTransition("only destroyed vehicles can be recovered")
        if duration.total_seconds() <= 0: raise InvalidQuantity("recovery duration must be positive")
        if cost < 0: raise InvalidQuantity("recovery cost must not be negative")
        return now + duration, cost
    def complete(self, vehicle: Vehicle, now: datetime) -> None:
        if vehicle.state is not VehicleState.DESTROYED: raise InvalidTransition("vehicle is not awaiting recovery")
        vehicle.state = VehicleState.STORED
        for component in vehicle.components.values():
            component.condition = max(1, component.condition)
        vehicle.durability = max(1, vehicle.durability)
