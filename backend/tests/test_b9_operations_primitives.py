import pytest

from app.application.operations import liveops_enabled, make_analytics_event, make_push_payload


def test_analytics_event_is_versioned_and_copies_properties():
    props = {"screen": "market"}
    event = make_analytics_event("screen_view", props, "player-1")
    props["screen"] = "changed"
    assert event.event_version == 1
    assert event.properties["screen"] == "market"
    assert event.player_id == "player-1"


def test_push_payload_is_provider_neutral():
    assert make_push_payload("Alert", "Convoy arrived", {"route": "dust"})["data"]["route"] == "dust"


def test_operations_validate_inputs():
    with pytest.raises(ValueError):
        make_analytics_event("", {})
    with pytest.raises(ValueError):
        make_analytics_event("event", [])
    with pytest.raises(ValueError):
        make_push_payload("", "body")
    assert liveops_enabled({"enabled": True})
    assert not liveops_enabled({"enabled": False})
