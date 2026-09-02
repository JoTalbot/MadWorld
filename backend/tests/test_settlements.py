from uuid import uuid4

from app.application.settlements import SettlementService
from app.infrastructure.memory import InMemoryUnitOfWork


def test_settlement_is_created_once_and_exposes_core_interactions() -> None:
    player = uuid4()
    uow = InMemoryUnitOfWork()
    with uow:
        first = SettlementService(uow).get_or_create(player)
    with uow:
        second = SettlementService(uow).get_or_create(player)
    assert first.id == second.id
    assert second.owner_id == player
    assert second.level == 1
    assert second.interaction_capabilities() == {
        "garage": True,
        "warehouse": True,
        "workshop": True,
        "contracts": True,
        "market": True,
    }
    assert len(uow.audit.events) == 1
    assert len(uow.outbox.events) == 1


def test_settlement_creation_rolls_back_with_transaction() -> None:
    player = uuid4()
    uow = InMemoryUnitOfWork()
    try:
        with uow:
            SettlementService(uow).get_or_create(player)
            raise RuntimeError("rollback")
    except RuntimeError:
        pass
    assert uow.settlements.get_by_owner(player) is None
    assert uow.audit.events == []
    assert uow.outbox.events == []
