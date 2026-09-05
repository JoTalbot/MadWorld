"""Authoritative alliance lifecycle commands for Phase 4."""
from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.api.dependencies import get_authenticated_player, get_uow
from app.application.ports import UnitOfWork

router = APIRouter(prefix="/api/v1/social", tags=["social-alliance"])

class AllianceCreate(BaseModel):
    code: str = Field(min_length=2, max_length=32)
    name: str = Field(min_length=2, max_length=80)

class AllianceInvite(BaseModel):
    alliance_id: UUID
    corporation_id: UUID

class AllianceInvitationDecision(BaseModel):
    invitation_id: UUID


def _role(uow: UnitOfWork, corporation_id: UUID, player_id: UUID) -> str | None:
    row = uow.conn.execute(text("SELECT role FROM corporation_members WHERE corporation_id=:c AND player_id=:p"), {"c": corporation_id, "p": player_id}).first()
    return str(row[0]) if row else None


def _require_member(uow: UnitOfWork, corporation_id: UUID, player_id: UUID) -> str:
    role = _role(uow, corporation_id, player_id)
    if role is None:
        raise HTTPException(403, "corporation membership required")
    return role


def _require_manager(uow: UnitOfWork, corporation_id: UUID, player_id: UUID) -> str:
    role = _require_member(uow, corporation_id, player_id)
    if role not in {"LEADER", "DIRECTOR"}:
        raise HTTPException(403, "alliance management permission required")
    return role


@router.post("/alliances", status_code=201)
def create_alliance(payload: AllianceCreate, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    rows = uow.conn.execute(text("SELECT corporation_id FROM corporation_members WHERE player_id=:p AND role='LEADER'"), {"p": player_id}).first()
    if not rows:
        raise HTTPException(403, "corporation leader required")
    corporation_id = UUID(str(rows[0]))
    alliance_id = uuid4()
    try:
        uow.conn.execute(text("INSERT INTO alliances (id,name,code,status,version) VALUES (:id,:n,:code,'ACTIVE',0)"), {"id": alliance_id, "n": payload.name.strip(), "code": payload.code.strip()})
        uow.conn.execute(text("INSERT INTO alliance_members (alliance_id,corporation_id,role,version) VALUES (:a,:c,'FOUNDER',0)"), {"a": alliance_id, "c": corporation_id})
    except Exception as exc:
        raise HTTPException(409, "alliance code is already in use") from exc
    uow.audit.append("alliance.created", "alliance", alliance_id, {"actor_id": str(player_id), "corporation_id": str(corporation_id)})
    uow.outbox.enqueue("alliance.created", "alliance", alliance_id, {"corporation_id": str(corporation_id)})
    return {"ok": True, "alliance_id": str(alliance_id), "corporation_id": str(corporation_id), "role": "FOUNDER"}


@router.post("/alliances/invite", status_code=201)
def invite_corporation(payload: AllianceInvite, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    source = uow.conn.execute(text("SELECT corporation_id FROM alliance_members WHERE alliance_id=:a AND corporation_id IN (SELECT corporation_id FROM corporation_members WHERE player_id=:p)"), {"a": payload.alliance_id, "p": player_id}).first()
    if source:
        source_corp = UUID(str(source[0]))
    else:
        source_corp_row = uow.conn.execute(text("SELECT corporation_id FROM corporation_members WHERE player_id=:p AND role IN ('LEADER','DIRECTOR') LIMIT 1"), {"p": player_id}).first()
        if not source_corp_row:
            raise HTTPException(403, "alliance manager required")
        source_corp = UUID(str(source_corp_row[0]))
        if uow.conn.execute(text("SELECT 1 FROM alliance_members WHERE alliance_id=:a AND corporation_id=:c"), {"a": payload.alliance_id, "c": source_corp}).first() is None:
            raise HTTPException(403, "source corporation is not an alliance member")
    _require_manager(uow, source_corp, player_id)
    if uow.conn.execute(text("SELECT 1 FROM corporations WHERE id=:c"), {"c": payload.corporation_id}).first() is None:
        raise HTTPException(404, "corporation not found")
    invitation_id = uuid4()
    try:
        uow.conn.execute(text("INSERT INTO alliance_invitations (id,alliance_id,corporation_id,invited_by,state,version) VALUES (:id,:a,:c,:p,'OFFERED',0)"), {"id": invitation_id, "a": payload.alliance_id, "c": payload.corporation_id, "p": player_id})
    except Exception as exc:
        raise HTTPException(409, "an invitation already exists for this corporation") from exc
    uow.audit.append("alliance.invited", "alliance", payload.alliance_id, {"actor_id": str(player_id), "corporation_id": str(payload.corporation_id), "invitation_id": str(invitation_id)})
    return {"ok": True, "invitation_id": str(invitation_id), "state": "OFFERED"}


@router.post("/alliances/invitations/accept")
def accept_invitation(payload: AllianceInvitationDecision, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    row = uow.conn.execute(text("SELECT alliance_id,corporation_id,state,version FROM alliance_invitations WHERE id=:id FOR UPDATE"), {"id": payload.invitation_id}).mappings().first()
    if not row:
        raise HTTPException(404, "alliance invitation not found")
    corporation_id = UUID(str(row["corporation_id"]))
    _require_manager(uow, corporation_id, player_id)
    if row["state"] != "OFFERED":
        raise HTTPException(409, "invitation is no longer actionable")
    uow.conn.execute(text("INSERT INTO alliance_members (alliance_id,corporation_id,role,version) VALUES (:a,:c,'MEMBER',0)"), {"a": row["alliance_id"], "c": corporation_id})
    uow.conn.execute(text("UPDATE alliance_invitations SET state='ACCEPTED',version=version+1 WHERE id=:id AND version=:v"), {"id": payload.invitation_id, "v": row["version"]})
    uow.audit.append("alliance.joined", "alliance", UUID(str(row["alliance_id"])), {"actor_id": str(player_id), "corporation_id": str(corporation_id), "invitation_id": str(payload.invitation_id)})
    return {"ok": True, "state": "ACCEPTED", "alliance_id": str(row["alliance_id"]), "corporation_id": str(corporation_id)}


@router.post("/alliances/leave")
def leave_alliance(alliance_id: UUID, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    corp_row = uow.conn.execute(text("SELECT corporation_id FROM alliance_members WHERE alliance_id=:a AND corporation_id IN (SELECT corporation_id FROM corporation_members WHERE player_id=:p) LIMIT 1"), {"a": alliance_id, "p": player_id}).first()
    if not corp_row:
        raise HTTPException(404, "alliance membership not found")
    corporation_id = UUID(str(corp_row[0]))
    _require_manager(uow, corporation_id, player_id)
    members = uow.conn.execute(text("SELECT COUNT(*) FROM alliance_members WHERE alliance_id=:a"), {"a": alliance_id}).scalar_one()
    if int(members) <= 1:
        uow.conn.execute(text("UPDATE alliances SET status='DISBANDED',version=version+1 WHERE id=:a"), {"a": alliance_id})
    uow.conn.execute(text("DELETE FROM alliance_members WHERE alliance_id=:a AND corporation_id=:c"), {"a": alliance_id, "c": corporation_id})
    uow.audit.append("alliance.left", "alliance", alliance_id, {"actor_id": str(player_id), "corporation_id": str(corporation_id)})
    return {"ok": True, "alliance_id": str(alliance_id), "corporation_id": str(corporation_id)}
