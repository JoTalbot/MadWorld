from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import asdict
from uuid import UUID

from sqlalchemy import text

from app.application.errors import ConcurrencyConflict
from app.domain.contracts import Contract, ContractObjective, ContractReward, ContractRisk, ContractState, ContractTemplate


class InMemoryContractRepository:
    def __init__(self): self.templates={}; self.contracts={}; self.reputation={}
    def save_template(self,t): self.templates[t.id]=deepcopy(t)
    def get_template(self,i): return deepcopy(self.templates.get(i))
    def save(self,c):
        old=self.contracts.get(c.id)
        if old and old.version!=c.version: raise ConcurrencyConflict("contract changed since it was read")
        c.version+=1; self.contracts[c.id]=deepcopy(c)
    def get(self,i): return deepcopy(self.contracts.get(i))
    def list_for_player(self,p): return [deepcopy(c) for c in self.contracts.values() if c.player_id==p]
    def has_completed_template(self,p,t): return any(c.player_id==p and c.template_id==t and c.state is ContractState.COMPLETED for c in self.contracts.values())
    def get_reputation(self,p,f): return self.reputation.get((p,f),0)
    def add_reputation(self,p,f,a): self.reputation[(p,f)]=self.get_reputation(p,f)+a
    def wallet_id(self,p):
        owners=getattr(self,"wallet_owners",{})
        return next((wid for wid,owner in owners.items() if owner==p),None)

class PostgresContractRepository:
    def __init__(self,conn): self.conn=conn
    def save_template(self,t):
        self.conn.execute(text("INSERT INTO contract_templates(id,code,title,description,objectives,reward,deadline_seconds,risk,faction_id,reputation_required,prerequisites,chain_next,enabled) VALUES(:id,:code,:title,:description,CAST(:objectives AS JSONB),CAST(:reward AS JSONB),:deadline,:risk,:faction,:rep,CAST(:prereq AS JSONB),CAST(:next AS JSONB),:enabled) ON CONFLICT(id) DO UPDATE SET code=EXCLUDED.code,title=EXCLUDED.title,description=EXCLUDED.description,objectives=EXCLUDED.objectives,reward=EXCLUDED.reward,deadline_seconds=EXCLUDED.deadline_seconds,risk=EXCLUDED.risk,faction_id=EXCLUDED.faction_id,reputation_required=EXCLUDED.reputation_required,prerequisites=EXCLUDED.prerequisites,chain_next=EXCLUDED.chain_next,enabled=EXCLUDED.enabled"),{"id":t.id,"code":t.code,"title":t.title,"description":t.description,"objectives":json.dumps([asdict(o) for o in t.objectives]),"reward":json.dumps(asdict(t.reward)),"deadline":t.deadline_seconds,"risk":t.risk.value,"faction":t.faction_id,"rep":t.reputation_required,"prereq":json.dumps([str(x) for x in t.prerequisites]),"next":json.dumps([str(x) for x in t.chain_next]),"enabled":t.enabled})
    def get_template(self,i):
        r=self.conn.execute(text("SELECT * FROM contract_templates WHERE id=:id"),{"id":i}).mappings().first()
        if not r:return None
        d=dict(r); return ContractTemplate(UUID(str(d["id"])),d["code"],d["title"],d["description"],tuple(ContractObjective(**o) for o in d["objectives"]),ContractReward(**d["reward"]),d["deadline_seconds"],ContractRisk(d["risk"]),d["faction_id"],d["reputation_required"],tuple(UUID(x) for x in d["prerequisites"]),tuple(UUID(x) for x in d["chain_next"]),d["enabled"])
    def save(self,c):
        if c.version==0:
            self.conn.execute(text("INSERT INTO contracts(id,template_id,player_id,state,offered_at,accepted_at,deadline_at,progress,reward_granted,version) VALUES(:id,:template,:player,:state,:offered,:accepted,:deadline,CAST(:progress AS JSONB),:reward,1)"),{"id":c.id,"template":c.template_id,"player":c.player_id,"state":c.state.value,"offered":c.offered_at,"accepted":c.accepted_at,"deadline":c.deadline_at,"progress":json.dumps(c.progress),"reward":c.reward_granted}); c.version=1; return
        r=self.conn.execute(text("UPDATE contracts SET state=:state,accepted_at=:accepted,deadline_at=:deadline,progress=CAST(:progress AS JSONB),reward_granted=:reward,version=version+1 WHERE id=:id AND version=:version"),{"id":c.id,"state":c.state.value,"accepted":c.accepted_at,"deadline":c.deadline_at,"progress":json.dumps(c.progress),"reward":c.reward_granted,"version":c.version})
        if r.rowcount!=1: raise ConcurrencyConflict("contract changed since it was read")
        c.version+=1
    def get(self,i):
        r=self.conn.execute(text("SELECT * FROM contracts WHERE id=:id FOR UPDATE"),{"id":i}).mappings().first(); return self._map(r) if r else None
    def _map(self,r):
        d=dict(r); return Contract(UUID(str(d["id"])),UUID(str(d["template_id"])),UUID(str(d["player_id"])),ContractState(d["state"]),d["offered_at"],d["accepted_at"],d["deadline_at"],dict(d["progress"]),bool(d["reward_granted"]),int(d["version"]))
    def list_for_player(self,p): return [self._map(r) for r in self.conn.execute(text("SELECT * FROM contracts WHERE player_id=:p ORDER BY offered_at,id"),{"p":p}).mappings().all()]
    def has_completed_template(self,p,t): return bool(self.conn.execute(text("SELECT 1 FROM contracts WHERE player_id=:p AND template_id=:t AND state='completed' LIMIT 1"),{"p":p,"t":t}).first())
    def get_reputation(self,p,f): return int(self.conn.execute(text("SELECT reputation FROM faction_reputation WHERE player_id=:p AND faction_id=:f"),{"p":p,"f":f}).scalar() or 0)
    def add_reputation(self,p,f,a): self.conn.execute(text("INSERT INTO faction_reputation(player_id,faction_id,reputation) VALUES(:p,:f,:a) ON CONFLICT(player_id,faction_id) DO UPDATE SET reputation=faction_reputation.reputation+EXCLUDED.reputation"),{"p":p,"f":f,"a":a})
    def wallet_id(self,p): return self.conn.execute(text("SELECT id FROM wallets WHERE owner_id=:p LIMIT 1 FOR UPDATE"),{"p":p}).scalar()
