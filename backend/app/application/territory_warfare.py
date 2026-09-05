"""Authoritative territory warfare commands."""
from uuid import UUID, uuid4

from sqlalchemy import text


def member(conn, corp:UUID, player:UUID)->bool:
 return conn.execute(text("SELECT 1 FROM corporation_members WHERE corporation_id=:c AND player_id=:p"),{"c":corp,"p":player}).first() is not None

def damage_infrastructure(conn, infrastructure_id:UUID, amount:int, actor:UUID, tick:int|None=None)->dict:
 if amount<=0: raise ValueError("damage must be positive")
 row=conn.execute(text("SELECT region_id,controller_corporation_id,condition_bps,version FROM territory_infrastructure WHERE id=:id FOR UPDATE"),{"id":infrastructure_id}).mappings().first()
 if not row: raise ValueError("infrastructure not found")
 new=max(0,int(row['condition_bps'])-amount)
 conn.execute(text("UPDATE territory_infrastructure SET condition_bps=:c,version=version+1 WHERE id=:id AND version=:v"),{"c":new,"id":infrastructure_id,"v":row['version']})
 return {"infrastructure_id":str(infrastructure_id),"region_id":row['region_id'],"condition_bps":new,"damaged_by":str(actor)}

def repair_infrastructure(conn,infrastructure_id:UUID,amount:int,actor:UUID)->dict:
 if amount<=0: raise ValueError("repair must be positive")
 row=conn.execute(text("SELECT region_id,controller_corporation_id,condition_bps,version FROM territory_infrastructure WHERE id=:id FOR UPDATE"),{"id":infrastructure_id}).mappings().first()
 if not row: raise ValueError("infrastructure not found")
 if row['controller_corporation_id'] is None or not member(conn,UUID(str(row['controller_corporation_id'])),actor): raise PermissionError("controller membership required")
 new=min(10000,int(row['condition_bps'])+amount)
 conn.execute(text("UPDATE territory_infrastructure SET condition_bps=:c,version=version+1 WHERE id=:id AND version=:v"),{"c":new,"id":infrastructure_id,"v":row['version']})
 return {"infrastructure_id":str(infrastructure_id),"region_id":row['region_id'],"condition_bps":new}

def create_operation(conn,region_id:str,objective_id:UUID|None,attacker:UUID,defender:UUID|None,kind:str)->dict:
 if kind not in {'SIEGE','DISRUPTION','ASSAULT','REINFORCEMENT'}: raise ValueError('invalid operation type')
 if defender and defender==attacker: raise ValueError('attacker and defender must differ')
 oid=uuid4()
 conn.execute(text("INSERT INTO territory_warfare_operations(id,region_id,objective_id,attacker_corporation_id,defender_corporation_id,operation_type) VALUES(:id,:r,:o,:a,:d,:k)"),{"id":oid,"r":region_id,"o":objective_id,"a":attacker,"d":defender,"k":kind})
 return dict(conn.execute(text("SELECT * FROM territory_warfare_operations WHERE id=:id"),{"id":oid}).mappings().one())

def resolve_operation(conn,operation_id:UUID,winner:UUID|None)->dict:
 row=conn.execute(text("SELECT * FROM territory_warfare_operations WHERE id=:id FOR UPDATE"),{"id":operation_id}).mappings().first()
 if not row: raise ValueError('warfare operation not found')
 if row['state']=='RESOLVED': return dict(row)
 if winner and winner not in {row['attacker_corporation_id'],row['defender_corporation_id']}: raise ValueError('winner must be operation participant')
 state='RESOLVED'; conn.execute(text("UPDATE territory_warfare_operations SET state=:s,resolves_at=now(),version=version+1 WHERE id=:id"),{"s":state,"id":operation_id})
 if winner and row['objective_id']:
  conn.execute(text("UPDATE territory_objectives SET state='RESOLVED',resolved_at=now(),winner_corporation_id=:w,version=version+1 WHERE id=:o AND state IN ('OPEN','CONTESTED')"),{"w":winner,"o":row['objective_id']})
  conn.execute(text("UPDATE territory_control SET controller_corporation_id=:w,controlled_since=now(),version=version+1 WHERE region_id=:r AND target_id=(SELECT target_id FROM territory_objectives WHERE id=:o)"),{"w":winner,"r":row['region_id'],'o':row['objective_id']})
 conn.execute(text("INSERT INTO territory_warfare_events(id,operation_id,event_type,actor_corporation_id,payload) VALUES(:id,:o,'operation.resolved',:w,CAST(:p AS JSONB))"),{"id":uuid4(),'o':operation_id,'w':winner,'p':__import__('json').dumps({'winner':str(winner) if winner else None})})
 return dict(conn.execute(text("SELECT * FROM territory_warfare_operations WHERE id=:id"),{"id":operation_id}).mappings().one())
