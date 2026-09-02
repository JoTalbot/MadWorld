"""Authoritative contract domain model for IMP-077."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4

class ContractState(StrEnum):
    OFFERED="offered"; ACTIVE="active"; COMPLETED="completed"; FAILED="failed"; EXPIRED="expired"; CANCELLED="cancelled"
class ContractRisk(StrEnum):
    LOW="low"; MEDIUM="medium"; HIGH="high"; EXTREME="extreme"
@dataclass(frozen=True, slots=True)
class ContractObjective:
    id:str; event_type:str; target:int=1; match:dict=field(default_factory=dict); sequence:int=0
@dataclass(frozen=True, slots=True)
class ContractReward:
    currency:int=0; reputation:int=0; faction_id:str|None=None
@dataclass(slots=True)
class ContractTemplate:
    id:UUID; code:str; title:str; description:str; objectives:tuple[ContractObjective,...]; reward:ContractReward=field(default_factory=ContractReward); deadline_seconds:int|None=None; risk:ContractRisk=ContractRisk.LOW; faction_id:str|None=None; reputation_required:int=0; prerequisites:tuple[UUID,...]=(); chain_next:tuple[UUID,...]=(); enabled:bool=True
@dataclass(slots=True)
class Contract:
    id:UUID; template_id:UUID; player_id:UUID; state:ContractState; offered_at:datetime; accepted_at:datetime|None=None; deadline_at:datetime|None=None; progress:dict[str,int]=field(default_factory=dict); reward_granted:bool=False; version:int=0
    @classmethod
    def offer(cls,template,player_id,now): return cls(uuid4(),template.id,player_id,ContractState.OFFERED,now,progress={o.id:0 for o in template.objectives})
    def accept(self,now,deadline_seconds):
        if self.state is not ContractState.OFFERED: raise ValueError("only offered contracts can be accepted")
        self.state=ContractState.ACTIVE; self.accepted_at=now; self.deadline_at=now+timedelta(seconds=deadline_seconds) if deadline_seconds else None
    def update(self,objective_id,amount):
        if self.state is ContractState.ACTIVE: self.progress[objective_id]=max(0,self.progress.get(objective_id,0)+amount)
    def complete(self):
        if self.state is ContractState.ACTIVE:self.state=ContractState.COMPLETED
    def expire_if_due(self,now):
        if self.state is ContractState.ACTIVE and self.deadline_at is not None and now>=self.deadline_at:self.state=ContractState.EXPIRED
