from uuid import uuid4

import pytest

from app.application.phase4_operations import Phase4Operations
from app.application.phase4_social import SocialPolicy


def test_corporation_creation_normalizes_code_and_validates_tax():
    owner=uuid4(); corp=SocialPolicy.create_corporation(owner,"  dustco ","Dust Co",250)
    assert corp.owner_id==owner and corp.code=="DUSTCO" and corp.tax_bps==250

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
    issuer=uuid4(); contract=SocialPolicy.create_contract(issuer,"FLEET_ESCORT",{"price":100},counterparty_player_id=uuid4())
    assert contract.state=="OFFERED"
    with pytest.raises(ValueError): SocialPolicy.create_contract(issuer,"TRADE",{},counterparty_player_id=uuid4(),counterparty_corporation_id=uuid4())
    with pytest.raises(ValueError): SocialPolicy.create_contract(issuer,"TRADE",{})

def test_contract_lifecycle_is_forward_only():
    assert Phase4Operations.transition_contract("OFFERED","ACCEPTED").new_state=="ACCEPTED"
    assert Phase4Operations.transition_contract("ACCEPTED","COMPLETED").new_state=="COMPLETED"
    with pytest.raises(ValueError): Phase4Operations.transition_contract("COMPLETED","ACCEPTED")
    with pytest.raises(ValueError): Phase4Operations.transition_contract("OFFERED","COMPLETED")

def test_reputation_delta_requires_one_subject_and_nonzero_delta():
    player=uuid4(); r=Phase4Operations.reputation_delta(player,None,"settlement","dust",25,"completed contract")
    assert r.delta==25 and r.subject_player_id==player
    with pytest.raises(ValueError): Phase4Operations.reputation_delta(None,None,"settlement","dust",1,"x")
    with pytest.raises(ValueError): Phase4Operations.reputation_delta(player,None,"settlement","dust",0,"x")

def test_escrow_and_invitation_states_are_closed_sets():
    Phase4Operations.validate_escrow_state("LOCKED"); Phase4Operations.validate_invitation_state("OFFERED")
    with pytest.raises(ValueError): Phase4Operations.validate_escrow_state("MINTED")
    with pytest.raises(ValueError): Phase4Operations.validate_invitation_state("APPROVED")
