"""B5 supply-line, checkpoint and reinforcement commands."""
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.api.dependencies import get_authenticated_player, get_uow
from app.application.territory_warfare import member

router=APIRouter(prefix='/api/v1/territory/warfare',tags=['territory-warfare'])
class SupplyRequest(BaseModel):
 region_id:str=Field(min_length=1,max_length=64);source_target_id:str;destination_target_id:str;owner_corporation_id:UUID;capacity:int=Field(gt=0);current_supply:int=Field(ge=0)
class CheckpointRequest(BaseModel):
 region_id:str;name:str=Field(min_length=1,max_length=128);controller_corporation_id:UUID|None=None;defense_bps:int=Field(default=5000,ge=0,le=10000)
class SupplyAmount(BaseModel): amount:int=Field(gt=0)

def auth(corp,player,uow):
 if not member(uow.conn,corp,player): raise PermissionError('corporation membership required')
@router.post('/supply-lines',status_code=201)
def create_supply(p:SupplyRequest,player:UUID=Depends(get_authenticated_player),uow=Depends(get_uow),idempotency_key:str|None=Header(default=None,alias='Idempotency-Key')):
 if not idempotency_key: raise ValueError('Idempotency-Key header is required')
 auth(p.owner_corporation_id,player,uow)
 if p.current_supply>p.capacity: raise ValueError('current_supply exceeds capacity')
 sid=uuid4();uow.conn.execute(text("INSERT INTO territory_supply_lines(id,region_id,source_target_id,destination_target_id,owner_corporation_id,capacity,current_supply) VALUES(:id,:r,:s,:d,:o,:c,:q)"),p.model_dump()|{'id':sid})
 return dict(uow.conn.execute(text('SELECT * FROM territory_supply_lines WHERE id=:id'),{'id':sid}).mappings().one())
@router.post('/supply-lines/{line_id}/reinforce')
def reinforce(line_id:UUID,p:SupplyAmount,player:UUID=Depends(get_authenticated_player),uow=Depends(get_uow)):
 row=uow.conn.execute(text('SELECT owner_corporation_id,capacity,current_supply,version FROM territory_supply_lines WHERE id=:id FOR UPDATE'),{'id':line_id}).mappings().first()
 if not row: raise ValueError('supply line not found')
 auth(row['owner_corporation_id'],player,uow);new=min(int(row['capacity']),int(row['current_supply'])+p.amount)
 uow.conn.execute(text('UPDATE territory_supply_lines SET current_supply=:q,disruption_bps=GREATEST(0,disruption_bps-:a),version=version+1 WHERE id=:id AND version=:v'),{'q':new,'a':p.amount,'id':line_id,'v':row['version']})
 return {'id':str(line_id),'current_supply':new}
@router.post('/supply-lines/{line_id}/disrupt')
def disrupt(line_id:UUID,p:SupplyAmount,player:UUID=Depends(get_authenticated_player),uow=Depends(get_uow)):
 row=uow.conn.execute(text('SELECT region_id,disruption_bps,current_supply,version FROM territory_supply_lines WHERE id=:id FOR UPDATE'),{'id':line_id}).mappings().first()
 if not row: raise ValueError('supply line not found')
 new=min(10000,int(row['disruption_bps'])+p.amount); supply=max(0,int(row['current_supply'])-p.amount)
 uow.conn.execute(text('UPDATE territory_supply_lines SET disruption_bps=:d,current_supply=:q,version=version+1 WHERE id=:id AND version=:v'),{'d':new,'q':supply,'id':line_id,'v':row['version']})
 return {'id':str(line_id),'disruption_bps':new,'current_supply':supply}
@router.post('/checkpoints',status_code=201)
def checkpoint(p:CheckpointRequest,player:UUID=Depends(get_authenticated_player),uow=Depends(get_uow)):
 if p.controller_corporation_id: auth(p.controller_corporation_id,player,uow)
 cid=uuid4();uow.conn.execute(text("INSERT INTO territory_checkpoints(id,region_id,name,controller_corporation_id,defense_bps) VALUES(:id,:r,:n,:c,:d)"),{'id':cid,**p.model_dump()})
 return dict(uow.conn.execute(text('SELECT * FROM territory_checkpoints WHERE id=:id'),{'id':cid}).mappings().one())
