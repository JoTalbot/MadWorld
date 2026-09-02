from datetime import timedelta
from uuid import UUID, uuid4

import pytest

from app.application.contracts import ContractService
from app.infrastructure.memory import InMemoryUnitOfWork
from app.domain.primitives import InventoryStack, Wallet, utc_now


SCRAP = UUID("10000000-0000-0000-0000-000000000001")


def test_contract_templates_expose_five_phase_one_contracts() -> None:
    assert len(ContractService.templates()) == 5
    assert {template.code for template in ContractService.templates()} == {
        "scrap-run", "metal-haul", "fuel-supply", "parts-request", "salvage-cache"
    }


def test_contract_accept_is_idempotent() -> None:
    uow = InMemoryUnitOfWork()
    player_id = uuid4(); inventory_id = uuid4(); wallet_id = uuid4()
    uow.inventories.owners[inventory_id] = player_id
    uow.wallets.wallets[wallet_id] = Wallet(wallet_id, 0)
    service = ContractService(uow)
    first = service.accept(player_id, "scrap-run", inventory_id, wallet_id, "contract-1")
    second = service.accept(player_id, "scrap-run", inventory_id, wallet_id, "contract-1")
    assert first.id == second.id
    assert first.state.value == "running"


def test_contract_completion_consumes_cargo_and_pays_reward() -> None:
    uow = InMemoryUnitOfWork()
    player_id = uuid4(); inventory_id = uuid4(); wallet_id = uuid4()
    uow.inventories.owners[inventory_id] = player_id
    uow.wallets.wallets[wallet_id] = Wallet(wallet_id, 0)
    uow.inventories.stacks[(inventory_id, SCRAP)] = InventoryStack(SCRAP, 10)
    service = ContractService(uow)
    contract = service.accept(player_id, "scrap-run", inventory_id, wallet_id, "contract-2")
    completed = service.complete(contract.id, player_id, utc_now() + timedelta(seconds=10))
    assert completed.state.value == "completed"
    assert uow.inventories.stacks[(inventory_id, SCRAP)].quantity == 0 if (inventory_id, SCRAP) in uow.inventories.stacks else True
    assert uow.wallets.ledger["contract-reward:" + str(contract.id)].amount == 120


def test_contract_completion_rejects_insufficient_cargo_without_paying() -> None:
    uow = InMemoryUnitOfWork()
    player_id = uuid4(); inventory_id = uuid4(); wallet_id = uuid4()
    uow.inventories.owners[inventory_id] = player_id
    uow.wallets.wallets[wallet_id] = Wallet(wallet_id, 0)
    uow.inventories.stacks[(inventory_id, SCRAP)] = InventoryStack(SCRAP, 9)
    service = ContractService(uow)
    contract = service.accept(player_id, "scrap-run", inventory_id, wallet_id, "contract-3")
    with pytest.raises(ValueError, match="delivery requirements"):
        service.complete(contract.id, player_id, utc_now() + timedelta(seconds=10))
    assert uow.wallets.ledger == {}
