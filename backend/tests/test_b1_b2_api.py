from app.main import app


def test_b2_travel_routes_are_registered():
    # FastAPI 0.141+ may expose included routers as internal wrapper objects
    # in app.routes. The OpenAPI surface is the stable public registration
    # contract and avoids coupling this test to Starlette internals.
    paths = set(app.openapi()["paths"])
    assert {
        "/api/v1/travel/plan",
        "/api/v1/travel/{session_id}/depart",
        "/api/v1/travel/{session_id}/resolve",
        "/api/v1/travel/{session_id}/encounters/{world_event_id}",
        "/api/v1/travel/encounters/{encounter_id}/resolve",
        "/api/v1/travel/recovery/{case_id}/claim",
    } <= paths
