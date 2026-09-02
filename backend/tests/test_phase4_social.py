from uuid import uuid4
import pytest
from app.application.phase4_social import SocialPolicy

def test_corporation_creation_normalizes_code_and_validates_tax():
    owner=uuid4()
    corp=SocialPolicy.create_corporation(owner,"  dustco ","Dust Co",250)
    assert corp.owner_id==owner
    assert corp.code=="DUSTCO"
    assert corp.tax_bps==250

def test_roles_and_permissions_are_closed_sets():
    member=SocialPolicy.create_member(uuid4(),uuid4(),"DIPLOMAT")
    assert member.role=="DIPLOMAT"
    with pytest.raises(ValueError): SocialPolicy.create_member(uuid4(),uuid4(),"ADMIN")
    with pytest.raises(ValueError): SocialPolicy.validate_permission("PRINT_MONEY")

def test_diplomacy_disallows_trade_during_hostility():
    with pytest.raises(ValueError): SocialPolicy.set_diplomacy(uuid4(),uuid4(),"WAR",-9000,True,False)
    relation=SocialPolicy.set_diplomacy(uuid4(),uuid4(),"ALLIED",8000,True,True)
    assert relation.trade_allowed and relation.transit_allowed

def test_social_contract_requires_exactly_one_counterparty():
    issuer=uuid4()
    contract=SocialPolicy.create_contract(issuer,"FLEET_ESCORT",{"price":100},counterparty_player_id=uuid4())
    assert contract.state=="OFFERED"
    with pytest.raises(ValueError): SocialPolicy.create_contract(issuer,"TRADE",{},counterparty_player_id=uuid4(),counterparty_corporation_id=uuid4())
    with pytest.raises(ValueError): SocialPolicy.create_contract(issuer,"TRADE",{})
