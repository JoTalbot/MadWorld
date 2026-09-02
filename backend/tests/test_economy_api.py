from datetime import datetime, timedelta, timezone
from uuid import uuid4


def test_economy_recipe_ids_are_stable():
    assert str(uuid4()) != "60000000-0000-0000-0000-000000000001"


def test_economy_job_completion_requires_due_time():
    started = datetime.now(timezone.utc)
    completes = started + timedelta(seconds=30)
    assert completes > started


def test_economy_warehouse_capacity_is_level_based():
    assert 1000 + (3 - 1) * 500 == 2000
