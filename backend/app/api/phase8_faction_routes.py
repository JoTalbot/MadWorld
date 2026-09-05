"""B4 NPC faction observation, planning and execution API."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.api.dependencies import get_authenticated_player, get_uow
from app.application.npc_faction_simulation import choose_action, execute_action, observe

router=APIRouter(prefix="/api/v1/factions",tags=["npc-factions"])

@router.get("")
def factions(player:UUID=Depends(get_authenticated_player),uow=Depends(get_uow)):
 rows=uow.conn.execute(text("SELECT id,name,doctrine,aggression_bps,logistics_bps,version FROM world_factions ORDER BY id")).mappings().all()
 return {"authoritative":True,"factions":[dict(x) for x in rows]}

@router.get("/{faction_id}/observe")
def faction_observe(faction_id:str,region_id:str,player:UUID=Depends(get_authenticated_player),uow=Depends(get_uow)):
 return observe(uow.conn,faction_id,region_id)

@router.post("/{faction_id}/plan")
def faction_plan(faction_id:str,region_id:str,tick:int,player:UUID=Depends(get_authenticated_player),uow=Depends(get_uow)):
 if tick<0: raise ValueError("tick must be non-negative")
 with uow.conn.begin_nested(): return choose_action(uow.conn,faction_id,region_id,tick)

@router.post("/actions/{action_id}/execute")
def faction_execute(action_id:UUID,tick:int,player:UUID=Depends(get_authenticated_player),uow=Depends(get_uow)):
 if tick<0: raise ValueError("tick must be non-negative")
 return execute_action(uow.conn,action_id,tick)

@router.get("/{faction_id}/diplomacy")
def diplomacy(faction_id:str,player:UUID=Depends(get_authenticated_player),uow=Depends(get_uow)):
 rows=uow.conn.execute(text("SELECT other_faction_id,relation_bps,state,version,updated_at FROM faction_diplomacy WHERE faction_id=:f ORDER BY other_faction_id"),{"f":faction_id}).mappings().all()
 return [dict(x) for x in rows]

@router.get("/actions")
def faction_actions(state:str|None=None,player:UUID=Depends(get_authenticated_player),uow=Depends(get_uow)):
 if state:
  rows=uow.conn.execute(text("SELECT * FROM npc_faction_actions WHERE state=:s ORDER BY scheduled_tick,priority DESC"),{"s":state}).mappings().all()
 else:
  rows=uow.conn.execute(text("SELECT * FROM npc_faction_actions ORDER BY scheduled_tick DESC,priority DESC LIMIT 100")).mappings().all()
 return [dict(x) for x in rows]
