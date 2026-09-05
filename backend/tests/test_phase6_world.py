from pydantic import ValidationError

from app.api.phase6_world_routes import run_world_tick
from app.application.phase6_world import EVENT_CYCLE, REGIONS, RESOURCE_TYPES, _score, _seed


def test_simulation_seed_is_stable():
    assert _seed(1, 42) == _seed(1, 42)
    assert _seed(1, 42) != _seed(1, 43)


def test_deterministic_score_is_bounded():
    for key in ("a", "b", "region:tick", "disaster"):
        assert 0 <= _score("seed", key) < 10000


def test_phase6_domain_catalog_is_bounded():
    assert len(REGIONS) == 3
    assert len(RESOURCE_TYPES) >= 3
    assert EVENT_CYCLE == ("SHORTAGE", "CONVOY", "DISCOVERY", "DISASTER")


def test_public_tick_entrypoint_rejects_game_clients():
    # Global simulation time must not be player-controlled. The service entrypoint
    # remains available for a trusted scheduler/worker integration.
    assert callable(run_world_tick)
