from app.main import app


def test_b2_travel_routes_are_registered():
    paths = {route.path for route in app.routes}
    assert "/api/v1/travel/plan" in paths
    assert "/api/v1/travel/{session_id}/depart" in paths
    assert "/api/v1/travel/{session_id}/resolve" in paths
    assert "/api/v1/travel/recovery/{case_id}/claim" in paths
