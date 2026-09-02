from __future__ import annotations
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException
from app.api.dependencies import get_authenticated_player, get_uow
from app.api.idempotency import replay_or_none, require_key, store_response
from app.api.schemas import ContractResponse
from app.application.contract_service import ContractService
from app.application.ports import UnitOfWork

router=APIRouter(prefix="/api/v1/contracts",tags=["contracts"])
def _response(c): return ContractResponse.model_validate({"id":c.id,"template_id":c.template_id,"player_id":c.player_id,"state":c.state.value,"offered_at":c.offered_at,"accepted_at":c.accepted_at,"deadline_at":c.deadline_at,"progress":c.progress,"reward_granted":c.reward_granted,"version":c.version})
def _owned(c,player):
    if c is None: raise HTTPException(404,"contract not found")
    if c.player_id!=player: raise HTTPException(403,"contract does not belong to player")
    return c

@router.get("",response_model=list[ContractResponse])
def list_contracts(uow:UnitOfWork=Depends(get_uow),player:UUID=Depends(get_authenticated_player)):
    return [_response(c) for c in uow.contracts.list_for_player(player)]

@router.post("/{contract_id}/accept",response_model=ContractResponse)
def accept_contract(contract_id:UUID,idempotency_key:str|None=Header(default=None,alias="Idempotency-Key"),uow:UnitOfWork=Depends(get_uow),player:UUID=Depends(get_authenticated_player)):
    key=require_key(idempotency_key); data={"contract_id":str(contract_id)}; replay=replay_or_none(uow,"contract.accept",key,data)
    if replay is not None:return ContractResponse.model_validate(replay)
    response=_response(ContractService(uow).accept(contract_id,player)); store_response(uow,"contract.accept",key,data,response.model_dump(mode="json"),200,player); return response

@router.post("/{contract_id}/abandon",response_model=ContractResponse)
def abandon_contract(contract_id:UUID,idempotency_key:str|None=Header(default=None,alias="Idempotency-Key"),uow:UnitOfWork=Depends(get_uow),player:UUID=Depends(get_authenticated_player)):
    key=require_key(idempotency_key); data={"contract_id":str(contract_id)}; replay=replay_or_none(uow,"contract.abandon",key,data)
    if replay is not None:return ContractResponse.model_validate(replay)
    response=_response(ContractService(uow).abandon(contract_id,player)); store_response(uow,"contract.abandon",key,data,response.model_dump(mode="json"),200,player); return response
