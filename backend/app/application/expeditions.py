from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
from uuid import UUID

from app.application.errors import IdempotencyConflict, NotFound
from app.application.ports import UnitOfWork
from app.application.services import InventoryService, JobService
from app.application.vehicle_damage import VehicleDamageService
from app.domain.events import DEFAULT_EVENT_REGISTRY
from app.domain.expeditions import ExpeditionRisk, build_plan
from app.domain.primitives import DamageType, JobState, utc_now

EXPEDITION_JOB_PREFIX = "expedition:"
SCRAP_METAL_ID = UUID("30000000-0000-0000-0000-000000000001")
SALVAGED_WIRE_ID = UUID("30000000-0000-0000-0000-000000000002")


class ExpeditionService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def _inventory_owned(self, inventory_id: UUID, player_id: UUID) -> bool:
        conn = getattr(self.uow, "conn", None)
        if conn is not None:
            from sqlalchemy import text
            return conn.execute(text("SELECT 1 FROM inventories WHERE id=:id AND owner_id=:owner"), {"id": inventory_id, "owner": player_id}).first() is not None
        return True

    def start(self, player_id: UUID, vehicle_id: UUID, inventory_id: UUID, region: str, distance_km: int, risk: ExpeditionRisk, idempotency_key: str, now: datetime | None = None):
        plan = build_plan(region, distance_km, risk)
        existing = self.uow.jobs.get_by_idempotency_key(idempotency_key)
        if existing is not None:
            expected = {
                "vehicle_id": str(vehicle_id), "inventory_id": str(inventory_id), "region": plan.region,
                "distance_km": plan.distance_km, "risk": plan.risk.value,
            }
            actual = {key: existing.metadata.get(key) for key in expected}
            if existing.job_type != f"{EXPEDITION_JOB_PREFIX}{plan.region}" or actual != expected:
                raise IdempotencyConflict("idempotency key already belongs to another expedition")
            return existing
        vehicle = self.uow.vehicles.get(vehicle_id)
        if vehicle is None:
            raise NotFound("vehicle not found")
        if vehicle.owner_id != player_id:
            raise PermissionError("vehicle does not belong to player")
        if not self._inventory_owned(inventory_id, player_id):
            raise PermissionError("inventory does not belong to player")
        if vehicle.state.value == "destroyed":
            raise ValueError("destroyed vehicle cannot start an expedition")
        if vehicle.fuel < plan.fuel_cost:
            raise ValueError("vehicle fuel is insufficient for expedition")
        vehicle.fuel -= plan.fuel_cost
        self.uow.vehicles.save(vehicle)
        started = now or utc_now()
        seed = f"{player_id}:{vehicle_id}:{plan.region}:{plan.distance_km}:{plan.risk.value}:{idempotency_key}".encode()
        digest = hashlib.sha256(seed).digest()
        damage = int(digest[0] % (8 + len(plan.risk.value) * 6))
        loot_scrap = 5 + digest[1] % (6 + plan.distance_km // 20)
        loot_wire = digest[2] % (1 + plan.distance_km // 25)
        component = ("engine", "hull", "wheels", "fuel_system")[digest[3] % 4]
        metadata = {
            "vehicle_id": str(vehicle_id), "inventory_id": str(inventory_id), "player_id": str(player_id),
            "region": plan.region, "distance_km": plan.distance_km, "risk": plan.risk.value,
            "fuel_cost": plan.fuel_cost, "damage": damage, "damage_component": component,
            "damage_type": DamageType.IMPACT.value, "loot_scrap": int(loot_scrap), "loot_wire": int(loot_wire),
            "resolved": False,
        }
        return JobService(self.uow).create(player_id, f"{EXPEDITION_JOB_PREFIX}{plan.region}", started, started + timedelta(seconds=plan.duration_seconds), idempotency_key, metadata)

    def complete(self, player_id: UUID, job_id: UUID, now: datetime | None = None):
        job = self.uow.jobs.get(job_id)
        if job is None or job.owner_id != player_id:
            raise NotFound("expedition not found")
        if not job.job_type.startswith(EXPEDITION_JOB_PREFIX):
            raise ValueError("job is not an expedition")
        if job.state is JobState.CANCELLED:
            raise ValueError("cancelled expedition cannot be completed")
        if job.state is JobState.COMPLETED and job.metadata.get("resolved"):
            return job
        inventory_id = UUID(job.metadata["inventory_id"])
        if not self._inventory_owned(inventory_id, player_id):
            raise PermissionError("inventory does not belong to player")
        completed = JobService(self.uow).complete(job_id, now or utc_now())
        metadata = completed.metadata
        vehicle_id = UUID(metadata["vehicle_id"])
        vehicle = self.uow.vehicles.get(vehicle_id)
        if vehicle is None:
            raise NotFound("expedition vehicle not found")
        damage = int(metadata["damage"])
        if damage > 0:
            VehicleDamageService(self.uow).apply_damage(vehicle_id, metadata["damage_component"], damage, DamageType(metadata["damage_type"]))
        if int(metadata["loot_scrap"]) > 0:
            InventoryService(self.uow).add(inventory_id, SCRAP_METAL_ID, int(metadata["loot_scrap"]), 100)
        if int(metadata["loot_wire"]) > 0:
            InventoryService(self.uow).add(inventory_id, SALVAGED_WIRE_ID, int(metadata["loot_wire"]), 100)
        metadata["resolved"] = True
        self.uow.jobs.save(completed)
        payload = {
            "player_id": str(player_id), "vehicle_id": str(vehicle_id), "inventory_id": str(inventory_id),
            "region": metadata["region"], "risk": metadata["risk"], "distance_km": metadata["distance_km"],
            "loot_scrap": metadata["loot_scrap"], "loot_wire": metadata["loot_wire"],
            "damage": damage, "damage_component": metadata["damage_component"],
        }
        event = DEFAULT_EVENT_REGISTRY.create("expedition.completed", "expedition", job.id, payload)
        self.uow.audit.append(event.event_type, event.aggregate_type, event.aggregate_id, event.to_dict())
        self.uow.outbox.enqueue(event.event_type, event.aggregate_type, event.aggregate_id, event.to_dict())
        if hasattr(self.uow, "contracts"):
            from app.application.contract_service import ContractService
            ContractService(self.uow).apply_event(player_id, event.event_type, payload, now or utc_now())
        return completed
