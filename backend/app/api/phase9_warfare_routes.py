"""B5 territory warfare API."""
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.api.dependencies import get_authenticated_player, get_uow
from app.application.territory_warfare import create_operation, damage_infrastructure, member, repair_infrastructure, resolve_operation

router=APIRouter(prefix='/api/v1/territory/warfare',tags=['territory-warfare'])
class OperationRequest(BaseModel):
 region_id:str=Field(min_length=1,max_length=64); objective_id:UUID|None=None; attacker_corporation_id:UUID; defender_corporation_id:UUID|None=None; operation_type:str=Field(min_length=1,max_length=24)
class ResolveRequest(BaseModel): winner_corporation_id:UUID|None=None
class AmountRequest(BaseModel): amount:int=Field(gt=0,le=10000)

def auth(corp,player,uow):
 if not member(uow.conn,corp,player): raise PermissionError('corporation membership required')

@router.get('')
def warfare_state(player:UUID=Depends(get_authenticated_player),uow=Depends(get_uow)):
 ops=uow.conn.execute(text('SELECT * FROM territory_warfare_operations ORDER BY opens_at DESC LIMIT 100')).mappings().all()
 cps=uow.conn.execute(text('SELECT * FROM territory_checkpoints ORDER BY region_id,name')).mappings().all()
 supplies=uow.conn.execute(text('SELECT * FROM territory_supply_lines ORDER BY region_id')).mappings().all()
 return {'authoritative':True,'operations':[dict(x) for x in ops],'checkpoints':[dict(x) for x in cps],'supply_lines':[dict(x) for x in supplies]}

@router.post('/operations',status_code=201)
def start_operation(p:OperationRequest,player:UUID=Depends(get_authenticated_player),uow=Depends(get_uow),idempotency_key:str|None=Header(default=None,alias='Idempotency-Key')):
 if not idempotency_key: raise ValueError('Idempotency-Key header is required')
 auth(p.attacker_corporation_id,player,uow)
 if p.defender_corporation_id and not member(uow.conn,p.defender_corporation_id,player):
  pass
 return create_operation(uow.conn,p.region_id,p.objective_id,p.attacker_corporation_id,p.defender_corporation_id,p.operation_type)

@router.post('/operations/{operation_id}/resolve')
def resolve(operation_id:UUID,p:ResolveRequest,player:UUID=Depends(get_authenticated_player),uow=Depends(get_uow)):
 row=uow.conn.execute(text('SELECT attacker_corporation_id,defender_corporation_id FROM territory_warfare_operations WHERE id=:id'),{'id':operation_id}).mappings().first()
 if not row: raise ValueError('warfare operation not found')
 auth(row['attacker_corporation_id'],player,uow)
 if p.winner_corporation_id and p.winner_corporation_id!=row['attacker_corporation_id'] and row['defender_corporation_id']!=p.winner_corporation_id: raise PermissionError('winner is not an operation participant')
 return resolve_operation(uow.conn,operation_id,p.winner_corporation_id)

@router.post('/infrastructure/{infrastructure_id}/repair')
def repair(infrastructure_id:UUID,p:AmountRequest,player:UUID=Depends(get_authenticated_player),uow=Depends(get_uow)):
 return repair_infrastructure(uow.conn,infrastructure_id,p.amount,player)

@router.post('/operations/{operation_id}/infrastructure/{infrastructure_id}/damage')
def damage(operation_id:UUID,infrastructure_id:UUID,p:AmountRequest,player:UUID=Depends(get_authenticated_player),uow=Depends(get_uow)):
 op=uow.conn.execute(text("SELECT region_id,attacker_corporation_id,state FROM territory_warfare_operations WHERE id=:id FOR UPDATE"),{'id':operation_id}).mappings().first()
 if not op: raise ValueError('warfare operation not found')
 if op['state']!='ACTIVE': raise ValueError('warfare operation is not active')
 auth(op['attacker_corporation_id'],player,uow)
 infra=uow.conn.execute(text('SELECT region_id FROM territory_infrastructure WHERE id=:id'),{'id':infrastructure_id}).mappings().first()
 if not infra: raise ValueError('infrastructure not found')
 if infra['region_id']!=op['region_id']: raise ValueError('infrastructure is outside operation region')
 return damage_infrastructure(uow.conn,infrastructure_id,p.amount,player)

@router.get('/operations/{operation_id}')
def operation(operation_id:UUID,player:UUID=Depends(get_authenticated_player),uow=Depends(get_uow)):
 row=uow.conn.execute(text('SELECT * FROM territory_warfare_operations WHERE id=:id'),{'id':operation_id}).mappings().first()
 if not row: raise ValueError('warfare operation not found')
 return dict(row)
