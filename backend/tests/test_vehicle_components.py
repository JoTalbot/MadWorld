from uuid import uuid4

import pytest

from app.domain.primitives import DamageType, InvalidTransition, Vehicle


def test_damage_respects_component_armor_and_damage_type() -> None:
    vehicle = Vehicle.create(uuid4(), "test-vehicle", "light_runner")
    applied = vehicle.apply_damage("hull", 40, DamageType.KINETIC)
    assert applied == 30
    assert vehicle.components["hull"].condition == 70
    assert vehicle.durability == 92


def test_explosive_damage_is_more_severe() -> None:
    vehicle = Vehicle.create(uuid4(), "test-vehicle", "light_runner")
    applied = vehicle.apply_damage("engine", 40, DamageType.EXPLOSIVE)
    assert applied == 41
    assert vehicle.components["engine"].condition == 59


def test_component_effects_follow_damage() -> None:
    vehicle = Vehicle.create(uuid4(), "test-vehicle", "light_runner")
    vehicle.apply_damage("engine", 50, DamageType.KINETIC)
    vehicle.apply_damage("wheels", 25, DamageType.IMPACT)
    effects = vehicle.component_effects()
    assert effects["engine_power"] == 0.55
    assert effects["mobility"] == 0.8


def test_all_components_destroyed_destroy_vehicle() -> None:
    vehicle = Vehicle.create(uuid4(), "test-vehicle", "light_runner")
    for component in vehicle.components:
        vehicle.components[component].condition = 0
    vehicle._sync_durability()
    vehicle.apply_damage("hull", 1, DamageType.KINETIC) if vehicle.durability > 0 else None
    assert vehicle.durability == 0


def test_destroyed_vehicle_rejects_further_damage() -> None:
    vehicle = Vehicle.create(uuid4(), "test-vehicle", "light_runner")
    vehicle.components["hull"].condition = 0
    vehicle.components["engine"].condition = 0
    vehicle.components["wheels"].condition = 0
    vehicle.components["fuel_system"].condition = 0
    vehicle._sync_durability()
    vehicle.state = vehicle.state.DESTROYED
    with pytest.raises(InvalidTransition):
        vehicle.apply_damage("hull", 10, DamageType.FIRE)


def test_component_repair_restores_durability() -> None:
    vehicle = Vehicle.create(uuid4(), "test-vehicle", "light_runner")
    vehicle.apply_damage("engine", 50, DamageType.KINETIC)
    restored = vehicle.repair_component("engine", 20)
    assert restored == 20
    assert vehicle.components["engine"].condition == 65
    assert vehicle.durability == 91
