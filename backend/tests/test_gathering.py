from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from app.application.gathering import GatheringService, ResourceNode
from app.infrastructure.memory import InMemoryUnitOfWork


PLAYER = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
INVENTORY = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
NODE = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
REGION = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
ITEM = UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")


class FakeResourceNodes:
    def __init__(self, node):
        self.node = node

    def get_for_update(self, node_id):
        return self.node if node_id == self.node.id else None

    def save(self, node):
        self.node = node


def make_uow():
    uow = InMemoryUnitOfWork()
    uow.resource_nodes = FakeResourceNodes(ResourceNode(NODE, REGION, ITEM, 20, 5, 30, 0))
    uow.inventories.owners = {INVENTORY: PLAYER}
    return uow


def test_gather_consumes_node_and_adds_inventory():
    uow = make_uow()
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)

    with uow:
        node, amount = GatheringService(uow).gather(PLAYER, INVENTORY, NODE, now)

    assert amount == 5
    assert node.quantity == 15
    assert uow.inventories.get_stack(INVENTORY, ITEM).quantity == 5
    assert uow.outbox.events[-1]["event_type"] == "resource.gathered"


def test_gather_rejects_cooldown_without_mutating_inventory():
    uow = make_uow()
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    uow.resource_nodes.node = ResourceNode(NODE, REGION, ITEM, 20, 5, 30, 0, now)

    with pytest.raises(ValueError, match="cooldown"):
        with uow:
            GatheringService(uow).gather(PLAYER, INVENTORY, NODE, now + timedelta(seconds=29))

    assert uow.inventories.get_stack(INVENTORY, ITEM) is None
    assert uow.resource_nodes.node.quantity == 20


def test_gather_caps_final_extraction_to_remaining_quantity():
    uow = make_uow()
    uow.resource_nodes.node = ResourceNode(NODE, REGION, ITEM, 3, 5, 30, 0)
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)

    with uow:
        node, amount = GatheringService(uow).gather(PLAYER, INVENTORY, NODE, now)

    assert amount == 3
    assert node.quantity == 0
    assert uow.inventories.get_stack(INVENTORY, ITEM).quantity == 3
