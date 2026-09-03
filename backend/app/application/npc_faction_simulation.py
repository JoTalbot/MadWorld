"""Deterministic bounded NPC faction decision engine."""
from __future__ import annotations
from uuid import UUID, uuid4
from sqlalchemy import text

ACTIONS = ("ATTACK","DEFEND","EXPAND","RETREAT","TRADE","RAID","ESCORT","SCOUT","EXPLOIT","BLOCKADE")

def _clamp(v: int, lo: int, hi: int) -> int: return max(lo, min(hi, v))

def observe(conn, faction_id: str, region_id: str) -> dict:
    f=conn.execute(text("SELECT id,name,doctrine,aggression_bps,logistics_bps FROM world_factions WHERE id=:id"),{"id":faction_id}).mappings().one()
    p=conn.execute(text("SELECT resource_type,pressure_bps,trend_bps FROM regional_resource_pressure WHERE region_id=:r ORDER BY pressure_bps DESC"),{"r":region_id}).mappings().all()
    return {"faction":dict(f),"region_id":region_id,"pressure":[dict(x) for x in p]}

def choose_action(conn, faction_id: str, region_id: str, tick: int) -> dict:
    o=observe(conn,faction_id,region_id); f=o["faction"]; pressure=o["pressure"]
    aggression=int(f["aggression_bps"]); logistics=int(f["logistics_bps"]); maxp=max((int(x["pressure_bps"]) for x in pressure),default=0)
    if maxp >= 7000 and logistics < 4000: action="EXPLOIT"
    elif aggression >= 7000 and maxp >= 5000: action="RAID"
    elif aggression >= 6500: action="ATTACK"
    elif logistics >= 7000: action="TRADE"
    elif maxp <= -4000: action="SCOUT"
    else: action="DEFEND"
    priority=_clamp(5000 + (aggression-5000)//2 + (maxp//2),0,10000)
    target=region_id
    aid=uuid4()
    conn.execute(text("INSERT INTO npc_faction_actions(id,faction_id,region_id,action_type,target_region_id,priority,rationale,state,scheduled_tick) VALUES(:id,:f,:r,:a,:t,:p,CAST(:j AS JSONB),'PLANNED',:tick) ON CONFLICT(faction_id,scheduled_tick,action_type,region_id) DO NOTHING"),{"id":aid,"f":faction_id,"r":region_id,"a":action,"t":target,"p":priority,"j":__import__('json').dumps({'aggression_bps':aggression,'logistics_bps':logistics,'pressure_bps':maxp}),'tick':tick})
    row=conn.execute(text("SELECT id,faction_id,region_id,action_type,target_region_id,priority,rationale,state,scheduled_tick FROM npc_faction_actions WHERE faction_id=:f AND region_id=:r AND scheduled_tick=:t ORDER BY id DESC LIMIT 1"),{"f":faction_id,"r":region_id,"t":tick}).mappings().one()
    return dict(row)

def execute_action(conn, action_id: UUID, tick: int) -> dict:
    row=conn.execute(text("SELECT * FROM npc_faction_actions WHERE id=:id FOR UPDATE"),{"id":action_id}).mappings().first()
    if not row: raise ValueError("faction action not found")
    if row["state"]=="EXECUTED": return dict(row)
    if int(row["scheduled_tick"])>tick: raise ValueError("action is not due")
    conn.execute(text("UPDATE npc_faction_actions SET state='EXECUTED',executed_tick=:t,version=version+1,updated_at=now() WHERE id=:id"),{"id":action_id,"t":tick})
    conn.execute(text("INSERT INTO faction_action_events(id,action_id,faction_id,region_id,action_type,tick,payload) VALUES(:id,:a,:f,:r,:t,:tick,:p) ON CONFLICT(action_id) DO NOTHING"),{"id":uuid4(),"a":action_id,"f":row["faction_id"],"r":row["region_id"],"t":row["action_type"],"tick":tick,"p":__import__('json').dumps({'priority':row['priority'],'rationale':row['rationale']})})
    return dict(conn.execute(text("SELECT * FROM npc_faction_actions WHERE id=:id"),{"id":action_id}).mappings().one())
