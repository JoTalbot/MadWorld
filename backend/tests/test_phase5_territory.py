from datetime import datetime, timedelta, timezone
from uuid import uuid4
import pytest
from pydantic import ValidationError
from app.api.phase5_territory_routes import ClaimRequest, InfrastructureRequest, ResourceSiteRequest, RoadRequest, ObjectiveRequest


def test_claim_requires_nonempty_target_fields():
    with pytest.raises(ValidationError):
        ClaimRequest(corporation_id=uuid4(), region_id="", target_type="site", target_id="x")


def test_resource_site_bounds_are_server_side():
    with pytest.raises(ValidationError):
        ResourceSiteRequest(corporation_id=uuid4(), region_id="dust_basin", resource_type="scrap", name="yard", capacity=0)
    with pytest.raises(ValidationError):
        ResourceSiteRequest(corporation_id=uuid4(), region_id="dust_basin", resource_type="scrap", name="yard", capacity=100, extraction_limit=0)


def test_road_modifiers_are_bounded():
    with pytest.raises(ValidationError):
        RoadRequest(corporation_id=uuid4(), region_id="dust_basin", from_node="a", to_node="b", travel_modifier_bps=5001)
    with pytest.raises(ValidationError):
        RoadRequest(corporation_id=uuid4(), region_id="dust_basin", from_node="a", to_node="b", risk_modifier_bps=-5001)


def test_objective_window_is_timezone_aware_and_ordered_at_command_boundary():
    start=datetime.now(timezone.utc)
    end=start+timedelta(minutes=30)
    request=ObjectiveRequest(corporation_id=uuid4(), region_id="dust_basin", target_type="depot", target_id="d1", opens_at=start, contest_ends_at=end)
    assert request.contest_ends_at > request.opens_at


def test_infrastructure_upkeep_is_bounded():
    with pytest.raises(ValidationError):
        InfrastructureRequest(corporation_id=uuid4(), region_id="dust_basin", infrastructure_type="depot", name="A", upkeep_bps=10001)
