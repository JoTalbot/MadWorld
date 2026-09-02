from uuid import uuid4
import pytest
from app.api.phase4_completion_routes import EscrowContractCreate, ContractSettle, ManufacturerCreate

def test_escrow_contract_requires_one_counterparty():
    with pytest.raises(ValueError):
        EscrowContractCreate(issuer_corporation_id=uuid4(), contract_type="ESCORT", amount=100)
    with pytest.raises(ValueError):
        EscrowContractCreate(issuer_corporation_id=uuid4(), contract_type="ESCORT", amount=100, counterparty_player_id=uuid4(), counterparty_corporation_id=uuid4())

def test_escrow_amount_is_positive():
    with pytest.raises(ValueError):
        EscrowContractCreate(issuer_corporation_id=uuid4(), contract_type="ESCORT", amount=0, counterparty_player_id=uuid4())

def test_contract_settlement_requires_target_state():
    payload = ContractSettle(contract_id=uuid4(), new_state="COMPLETED")
    assert payload.new_state == "COMPLETED"

def test_manufacturer_quality_is_bounded():
    with pytest.raises(ValueError):
        ManufacturerCreate(corporation_id=uuid4(), brand_name="Brand", quality_rating=10001)
