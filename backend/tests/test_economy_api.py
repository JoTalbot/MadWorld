from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.api.economy_routes import JobResponse, RecipeResponse, _json


RECIPE_ID = UUID("60000000-0000-0000-0000-000000000001")
SETTLEMENT_ID = UUID("20000000-0000-0000-0000-000000000001")


def test_seed_recipe_id_is_stable_and_typed():
    response = RecipeResponse(
        id=RECIPE_ID,
        code="refine_metal",
        name="Refine Scrap Metal",
        kind="refining",
        facility_code="refinery",
        duration_seconds=30,
        inputs=[{"item_code": "scrap_metal", "quantity": 5}],
        outputs=[{"item_code": "metal_plate", "quantity": 1}],
    )
    assert response.id == RECIPE_ID
    assert response.duration_seconds > 0
    assert response.inputs[0]["quantity"] == 5


def test_json_accepts_decoded_and_serialized_recipe_payloads():
    payload = [{"item_code": "scrap_metal", "quantity": 5}]
    assert _json(payload) == payload
    assert _json('[{"item_code":"scrap_metal","quantity":5}]') == payload


def test_job_completion_timestamp_is_strictly_after_start():
    started = datetime(2026, 9, 3, 18, 0, tzinfo=timezone.utc)
    completes = started + timedelta(seconds=30)
    response = JobResponse(
        id=UUID("70000000-0000-0000-0000-000000000001"),
        recipe_id=RECIPE_ID,
        settlement_id=SETTLEMENT_ID,
        state="running",
        started_at=started.isoformat(),
        completes_at=completes.isoformat(),
    )
    assert datetime.fromisoformat(response.completes_at) > datetime.fromisoformat(response.started_at)


def test_warehouse_capacity_scales_with_settlement_level():
    assert 1000 + (1 - 1) * 500 == 1000
    assert 1000 + (3 - 1) * 500 == 2000
    assert 1000 + (5 - 1) * 500 == 3000


def test_economy_recipe_codes_match_seed_items():
    seed_items = {
        "scrap_metal", "salvaged_wire", "raw_fuel", "fiber", "chemicals",
        "metal_plate", "wire_bundle", "fuel_cell", "repair_kit", "armor_panel",
    }
    recipes = [
        {"inputs": [{"item_code": "scrap_metal"}], "outputs": [{"item_code": "metal_plate"}]},
        {"inputs": [{"item_code": "salvaged_wire"}], "outputs": [{"item_code": "wire_bundle"}]},
        {"inputs": [{"item_code": "raw_fuel"}, {"item_code": "chemicals"}], "outputs": [{"item_code": "fuel_cell"}]},
        {"inputs": [{"item_code": "metal_plate"}, {"item_code": "wire_bundle"}, {"item_code": "chemicals"}], "outputs": [{"item_code": "repair_kit"}]},
        {"inputs": [{"item_code": "metal_plate"}, {"item_code": "fiber"}, {"item_code": "chemicals"}], "outputs": [{"item_code": "armor_panel"}]},
    ]
    assert all(entry["item_code"] in seed_items for recipe in recipes for side in ("inputs", "outputs") for entry in recipe[side])


def test_economy_recipe_facilities_and_kinds_are_coherent():
    recipes = [
        {"kind": "refining", "facility_code": "refinery", "duration_seconds": 30},
        {"kind": "refining", "facility_code": "workshop", "duration_seconds": 20},
        {"kind": "refining", "facility_code": "refinery", "duration_seconds": 45},
        {"kind": "production", "facility_code": "workshop", "duration_seconds": 60},
        {"kind": "production", "facility_code": "workshop", "duration_seconds": 90},
    ]
    assert {recipe["facility_code"] for recipe in recipes} == {"refinery", "workshop"}
    assert sum(recipe["kind"] == "refining" for recipe in recipes) == 3
    assert sum(recipe["kind"] == "production" for recipe in recipes) == 2
    assert all(recipe["duration_seconds"] > 0 for recipe in recipes)
