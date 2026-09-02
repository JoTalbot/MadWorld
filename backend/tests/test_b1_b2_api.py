from fastapi.routing import APIRoute

from app.main import app


def test_b2_travel_routes_are_registered():
    paths = {route.path for route in app.routes if isinstance(route, APIRoute)}
    assert {
        "/api/v1/travel/plan",
        "/api/v1/travel/{session_id}/depart",
        "/api/v1/travel/{session_id}/resolve",
        "/api/v1/travel/{session_id}/encounters/{world_event_id}",
        "/api/v1/travel/encounters/{encounter_id}/resolve",
        "/api/v1/travel/recovery/{case_id}/claim",
    } <= paths
