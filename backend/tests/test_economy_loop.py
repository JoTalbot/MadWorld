from app.api.economy_loop_routes import _next_action


def test_economy_loop_prioritizes_active_production():
    assert _next_action(1, 10, 10, 10) == "job_in_progress"


def test_economy_loop_prioritizes_contracts_after_production():
    assert _next_action(0, 2, 10, 10) == "review_contracts"


def test_economy_loop_prioritizes_expedition_when_vehicle_is_ready():
    assert _next_action(0, 0, 1, 10) == "prepare_expedition"


def test_economy_loop_falls_back_to_market_then_gathering():
    assert _next_action(0, 0, 0, 5) == "review_market"
    assert _next_action(0, 0, 0, 0) == "gather_resources"
