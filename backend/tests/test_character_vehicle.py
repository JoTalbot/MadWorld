from uuid import uuid4

import pytest

from app.application.services import CharacterService, VehicleService
from app.domain.primitives import VehicleState
from app.infrastructure.memory import InMemoryUnitOfWork


def test_character_can_be_created_once_per_player() -> None:
    player_id = uuid4()
    uow = InMemoryUnitOfWork()
    with uow:
        character = CharacterService(uow).create(player_id, "Dust Walker")
        assert character.player_id == player_id
        assert character.level == 1
        assert CharacterService(uow).get_for_player(player_id).name == "Dust Walker"
        with pytest.raises(ValueError, match="already has a character"):
            CharacterService(uow).create(player_id, "Second")


def test_starter_vehicle_has_safe_initial_state_and_is_unique() -> None:
    owner_id = uuid4()
    uow = InMemoryUnitOfWork()
    with uow:
        vehicle = VehicleService(uow).create_starter(owner_id)
        assert vehicle.chassis_code == "light_runner"
        assert vehicle.durability == 100
        assert vehicle.fuel == 25
        assert vehicle.state is VehicleState.ACTIVE
        with pytest.raises(ValueError, match="without vehicles"):
            VehicleService(uow).create_starter(owner_id)


def test_vehicle_repair_and_refuel_are_authoritative() -> None:
    owner_id = uuid4()
    uow = InMemoryUnitOfWork()
    with uow:
        vehicle = VehicleService(uow).create_starter(owner_id)
        vehicle.durability = 60
        uow.vehicles.save(vehicle)
        repaired = VehicleService(uow).repair(vehicle.id, 30)
        refueled = VehicleService(uow).refuel(vehicle.id, 10)
        assert repaired.durability == 90
        assert refueled.fuel == 35
