from __future__ import annotations
from uuid import UUID
from app.application.errors import NotFound
from app.application.services import WalletService
from app.domain.contracts import Contract, ContractState, ContractTemplate
from app.domain.primitives import utc_now

class ContractService:
    def __init__(self, uow): self.uow=uow; self.repo=uow.contracts
    def create_template(self, template: ContractTemplate):
        if not template.objectives or any(o.target <= 0 for o in template.objectives): raise ValueError("contract objectives must have positive targets")
        self.repo.save_template(template); return template
    def offer(self, template_id: UUID, player_id: UUID, now=None):
        now=now or utc_now(); t=self.repo.get_template(template_id)
        if t is None or not t.enabled: raise NotFound("contract template not found")
        if t.faction_id and self.repo.get_reputation(player_id,t.faction_id) < t.reputation_required: raise ValueError("contract reputation requirement is not met")
        if any(not self.repo.has_completed_template(player_id,p) for p in t.prerequisites): raise ValueError("contract prerequisites are not completed")
        c=Contract.offer(t,player_id,now); self.repo.save(c); return c
    def accept(self, contract_id: UUID, player_id: UUID, now=None):
        now=now or utc_now(); c=self._owned(contract_id,player_id); t=self.repo.get_template(c.template_id)
        if t is None: raise NotFound("contract template not found")
        c.accept(now,t.deadline_seconds); self.repo.save(c); return c
    def abandon(self, contract_id: UUID, player_id: UUID):
        c=self._owned(contract_id,player_id)
        if c.state is not ContractState.ACTIVE: raise ValueError("only active contracts can be abandoned")
        c.state=ContractState.CANCELLED; self.repo.save(c); return c
    def expire(self, player_id: UUID, now=None):
        now=now or utc_now(); out=[]
        for c in self.repo.list_for_player(player_id):
            c.expire_if_due(now)
            if c.state is ContractState.EXPIRED: self.repo.save(c); out.append(c)
        return out
    def apply_event(self, player_id: UUID, event_type: str, payload: dict, now=None):
        now=now or utc_now(); out=[]
        for c in self.repo.list_for_player(player_id):
            if c.state is ContractState.COMPLETED:
                out.append(c)
                continue
            if c.state is not ContractState.ACTIVE: continue
            t=self.repo.get_template(c.template_id)
            if t is None: continue
            c.expire_if_due(now)
            if c.state is ContractState.EXPIRED: self.repo.save(c); out.append(c); continue
            for o in sorted(t.objectives,key=lambda x:x.sequence):
                current=c.progress.get(o.id,0)
                if current>=o.target or any(c.progress.get(p.id,0)<p.target for p in t.objectives if p.sequence<o.sequence): continue
                if o.event_type!=event_type or any(str(payload.get(k))!=str(v) for k,v in o.match.items()): continue
                amount=int(payload.get("quantity",payload.get("amount",1))); c.update(o.id,min(amount,o.target-current))
            if all(c.progress.get(o.id,0)>=o.target for o in t.objectives): c.complete(); self._grant(c,t)
            self.repo.save(c); out.append(c)
        return out
    def _grant(self,c,t):
        if c.reward_granted: return
        r=t.reward
        if r.currency:
            wallet_id=self.repo.wallet_id(c.player_id)
            if wallet_id is None: raise NotFound("player wallet not found")
            WalletService(self.uow).post_entry(wallet_id,r.currency,f"contract:{c.id}:reward",f"contract-reward:{c.id}",c.player_id)
        if r.faction_id and r.reputation: self.repo.add_reputation(c.player_id,r.faction_id,r.reputation)
        c.reward_granted=True
    def _owned(self,contract_id,player_id):
        c=self.repo.get(contract_id)
        if c is None: raise NotFound("contract not found")
        if c.player_id!=player_id: raise PermissionError("contract does not belong to player")
        return c
