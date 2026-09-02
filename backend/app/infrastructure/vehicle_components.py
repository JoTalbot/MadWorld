"""Persistence adapter for component-aware vehicle state."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import text

from app.domain.primitives import Vehicle, VehicleComponent, default_vehicle_components


class ComponentVehicleRepository:
    """Decorates the existing vehicle repository without changing its contract."""

    def __init__(self, base) -> None:
        self.base = base
        self.conn = base.conn

    def _load_components(self, vehicle: Vehicle) -> Vehicle:
        rows = self.conn.execute(
            text("SELECT component_code, condition, max_condition, armor FROM vehicle_components WHERE vehicle_id = :vehicle_id ORDER BY component_code"),
            {"vehicle_id": vehicle.id},
        ).mappings().all()
        if rows:
            vehicle.components = {
                str(row["component_code"]): VehicleComponent(int(row["condition"]), int(row["max_condition"]), int(row["armor"]))
                for row in rows
            }
        else:
            vehicle.components = default_vehicle_components()
        vehicle._sync_durability()
        return vehicle

    def get(self, vehicle_id: UUID) -> Vehicle | None:
        vehicle = self.base.get(vehicle_id)
        return self._load_components(vehicle) if vehicle else None

    def list_by_owner(self, owner_id: UUID) -> list[Vehicle]:
        return [self._load_components(vehicle) for vehicle in self.base.list_by_owner(owner_id)]

    def save(self, vehicle: Vehicle) -> None:
        self.base.save(vehicle)
        for code, component in vehicle.components.items():
            self.conn.execute(
                text("""INSERT INTO vehicle_components (vehicle_id, component_code, condition, max_condition, armor)
                       VALUES (:vehicle_id, :component_code, :condition, :max_condition, :armor)
                       ON CONFLICT (vehicle_id, component_code) DO UPDATE
                       SET condition = EXCLUDED.condition, max_condition = EXCLUDED.max_condition, armor = EXCLUDED.armor"""),
                {"vehicle_id": vehicle.id, "component_code": code, "condition": component.condition, "max_condition": component.max_condition, "armor": component.armor},
            )
        self.conn.execute(
            text("DELETE FROM vehicle_components WHERE vehicle_id = :vehicle_id AND component_code NOT IN (SELECT unnest(CAST(:codes AS TEXT[])))"),
            {"vehicle_id": vehicle.id, "codes": list(vehicle.components)},
        )
