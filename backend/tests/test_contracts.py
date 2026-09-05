from datetime import UTC, datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.application.contract_service import ContractService
from app.domain.contracts import ContractObjective, ContractReward, ContractRisk, ContractState, ContractTemplate
from app.domain.primitives import Wallet
from app.infrastructure.contracts import InMemoryContractRepository
from app.infrastructure.memory import InMemoryUnitOfWork


def test_contract_progression_deadline_and_deterministic_reward():
    player=uuid4(); wallet_id=uuid4(); template_id=uuid4(); now=datetime(2026,1,1,tzinfo=UTC)
    uow=InMemoryUnitOfWork(); uow.contracts=InMemoryContractRepository(); uow.wallets.wallets[wallet_id]=Wallet(wallet_id,0); uow.contracts.wallet_owners={wallet_id:player}
    template=ContractTemplate(template_id,"gather-iron","Gather iron","Collect iron",(ContractObjective("iron","resource.gathered",3,{"item_definition_id":"iron"}),),ContractReward(currency=50,reputation=5,faction_id="miners"),deadline_seconds=60,risk=ContractRisk.HIGH,faction_id="miners")
    service=ContractService(uow); service.create_template(template); contract=service.offer(template_id,player,now); assert contract.state is ContractState.OFFERED
    contract=service.accept(contract.id,player,now); assert contract.deadline_at==now+timedelta(seconds=60)
    service.apply_event(player,"resource.gathered",{"item_definition_id":"iron","quantity":2},now+timedelta(seconds=10)); assert uow.contracts.get(contract.id).progress["iron"]==2
    service.apply_event(player,"resource.gathered",{"item_definition_id":"iron","quantity":2},now+timedelta(seconds=20)); done=uow.contracts.get(contract.id); assert done.state is ContractState.COMPLETED and done.reward_granted
    assert uow.wallets.get(wallet_id).balance==50; assert service.apply_event(player,"resource.gathered",{"item_definition_id":"iron","quantity":9},now+timedelta(seconds=30))

def test_contract_prerequisite_and_expiry():
    player=uuid4(); a=uuid4(); b=uuid4(); now=datetime(2026,1,1,tzinfo=UTC); uow=InMemoryUnitOfWork(); uow.contracts=InMemoryContractRepository(); service=ContractService(uow)
    first=ContractTemplate(a,"first","First","",(ContractObjective("x","x",1),)); second=ContractTemplate(b,"second","Second","",(ContractObjective("y","y",1),),prerequisites=(a,),deadline_seconds=10)
    service.create_template(first); service.create_template(second)
    with pytest.raises(ValueError,match="prerequisites"): service.offer(b,player,now)
    c=service.offer(a,player,now); service.accept(c.id,player,now); service.apply_event(player,"x",{},now); assert uow.contracts.get(c.id).state is ContractState.COMPLETED
    c2=service.offer(b,player,now); service.accept(c2.id,player,now); service.expire(player,now+timedelta(seconds=10)); assert uow.contracts.get(c2.id).state is ContractState.EXPIRED
