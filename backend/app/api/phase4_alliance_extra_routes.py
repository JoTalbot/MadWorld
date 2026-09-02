"""Remaining authoritative alliance read/decline operations."""
from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from app.api.dependencies import get_authenticated_player, get_uow
from app.application.ports import UnitOfWork
from app.api.phase4_alliance_routes import _require_manager
router = APIRouter(prefix="/api/v1/social", tags=["social-alliance"])
class InvitationDecision(BaseModel): invitation_id: UUID
@router.post("/alliances/invitations/decline")
def decline_invitation(payload: InvitationDecision, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    row = uow.conn.execute(text("SELECT alliance_id,corporation_id,state,version FROM alliance_invitations WHERE id=:id FOR UPDATE"), {"id": payload.invitation_id}).mappings().first()
    if not row: raise HTTPException(404, "alliance invitation not found")
    corp = UUID(str(row["corporation_id"])); _require_manager(uow, corp, player_id)
    if row["state"] != "OFFERED": raise HTTPException(409, "invitation is no longer actionable")
    uow.conn.execute(text("UPDATE alliance_invitations SET state='DECLINED',version=version+1 WHERE id=:id AND version=:v"), {"id": payload.invitation_id, "v": row["version"]})
    uow.audit.append("alliance.invitation_declined", "alliance", UUID(str(row["alliance_id"])), {"actor_id": str(player_id), "corporation_id": str(corp), "invitation_id": str(payload.invitation_id)})
    return {"ok": True, "state": "DECLINED", "alliance_id": str(row["alliance_id"]), "corporation_id": str(corp)}
@router.get("/alliances/{alliance_id}")
def alliance_overview(alliance_id: UUID, player_id: UUID = Depends(get_authenticated_player), uow: UnitOfWork = Depends(get_uow)):
    member = uow.conn.execute(text("SELECT corporation_id,role FROM alliance_members WHERE alliance_id=:a AND corporation_id IN (SELECT corporation_id FROM corporation_members WHERE player_id=:p)"), {"a": alliance_id, "p": player_id}).mappings().first()
    if not member: raise HTTPException(403, "alliance membership required")
    alliance = uow.conn.execute(text("SELECT id,name,code,status,version FROM alliances WHERE id=:a"), {"a": alliance_id}).mappings().first()
    if not alliance: raise HTTPException(404, "alliance not found")
    members = uow.conn.execute(text("SELECT corporation_id,role,joined_at,version FROM alliance_members WHERE alliance_id=:a ORDER BY joined_at,corporation_id"), {"a": alliance_id}).mappings().all()
    invitations = uow.conn.execute(text("SELECT id,corporation_id,state,expires_at,version FROM alliance_invitations WHERE alliance_id=:a AND state='OFFERED' ORDER BY id"), {"a": alliance_id}).mappings().all()
    return {"alliance": dict(alliance), "viewer_corporation_id": str(member["corporation_id"]), "viewer_role": str(member["role"]), "members": [dict(x) for x in members], "pending_invitations": [dict(x) for x in invitations]}
