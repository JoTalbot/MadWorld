from datetime import timedelta
from uuid import uuid4

import pytest

from app.application.services import REPAIR_KIT_ID, VehicleService
from app.domain.primitives import InventoryStack
from app.infrastructure.memory import InMemoryUnitOfWork


def test_vehicle_repair_is_a_persistent_idempotent_job() -> None:
    owner_id = uuid4()
    inventory_id = uuid4()
    uow = InMemoryUnitOfWork()
    with uow:
        vehicle = VehicleService(uow).create_starter(owner_id)
        vehicle.durability = 60
        uow.vehicles.save(vehicle)
        uow.inventories.save_stack(inventory_id, InventoryStack(REPAIR_KIT_ID, 3))

        service = VehicleService(uow)
        job = service.start_repair(vehicle.id, inventory_id, 30, "repair-1")
        assert job.job_type == "vehicle_repair"
        assert job.metadata["vehicle_id"] == str(vehicle.id)
        assert job.metadata["kits"] == 2
        assert uow.inventories.get_stack(inventory_id, REPAIR_KIT_ID).quantity == 1
        assert VehicleService(uow).get(vehicle.id).durability == 60

        replay = service.start_repair(vehicle.id, inventory_id, 30, "repair-1")
        assert replay.id == job.id
        assert uow.inventories.get_stack(inventory_id, REPAIR_KIT_ID).quantity == 1

        with pytest.raises(ValueError, match="completion time"):
            service.complete_repair(job.id, job.started_at)

        completed = service.complete_repair(job.id, job.completes_at + timedelta(seconds=1))
        assert completed.state.value == "completed"
        assert VehicleService(uow).get(vehicle.id).durability == 90

        completed_again = service.complete_repair(job.id, job.completes_at + timedelta(seconds=2))
        assert completed_again.id == job.id
        assert VehicleService(uow).get(vehicle.id).durability == 90
