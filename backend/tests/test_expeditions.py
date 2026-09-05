from datetime import UTC, datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.application.expeditions import SALVAGED_WIRE_ID, SCRAP_METAL_ID, ExpeditionService
from app.domain.expeditions import ExpeditionRisk
from app.domain.primitives import Vehicle
from app.infrastructure.memory import InMemoryUnitOfWork


def setup_player():
    uow = InMemoryUnitOfWork()
    player = uuid4(); vehicle = Vehicle.create(player, "test-runner", "light_runner", fuel=100); inventory = uuid4()
    uow.vehicles.save(vehicle)
    return uow, player, vehicle.id, inventory


def test_expedition_is_persistent_and_consumes_fuel():
    uow, player, vehicle_id, inventory_id = setup_player()
    now = datetime(2030, 1, 1, tzinfo=UTC)
    with uow:
        job = ExpeditionService(uow).start(player, vehicle_id, inventory_id, "dust_basin", 100, ExpeditionRisk.HIGH, "exp-1", now)
        assert job.metadata["fuel_cost"] == 16
        assert uow.vehicles.get(vehicle_id).fuel == 84
        assert job.completes_at == now + timedelta(seconds=3000)


def test_expedition_completion_is_time_guarded_and_rewards_inventory():
    uow, player, vehicle_id, inventory_id = setup_player()
    now = datetime(2030, 1, 1, tzinfo=UTC)
    with uow:
        job = ExpeditionService(uow).start(player, vehicle_id, inventory_id, "iron_ruins", 10, ExpeditionRisk.LOW, "exp-2", now)
        with pytest.raises(ValueError):
            ExpeditionService(uow).complete(player, job.id, now + timedelta(seconds=10))
        completed = ExpeditionService(uow).complete(player, job.id, now + timedelta(seconds=300))
        assert completed.metadata["resolved"] is True
        assert completed.state.value == "completed"
        assert uow.inventories.get_stack(inventory_id, SCRAP_METAL_ID) is not None
        assert uow.inventories.get_stack(inventory_id, SALVAGED_WIRE_ID) is not None or completed.metadata["loot_wire"] == 0


def test_expedition_completion_is_idempotent_after_resolution():
    uow, player, vehicle_id, inventory_id = setup_player()
    now = datetime(2030, 1, 1, tzinfo=UTC)
    with uow:
        job = ExpeditionService(uow).start(player, vehicle_id, inventory_id, "salt_coast", 5, ExpeditionRisk.MEDIUM, "exp-3", now)
        first = ExpeditionService(uow).complete(player, job.id, now + timedelta(seconds=300))
        scrap_before = uow.inventories.get_stack(inventory_id, SCRAP_METAL_ID).quantity
        second = ExpeditionService(uow).complete(player, job.id, now + timedelta(seconds=301))
        assert second.id == first.id
        assert uow.inventories.get_stack(inventory_id, SCRAP_METAL_ID).quantity == scrap_before
