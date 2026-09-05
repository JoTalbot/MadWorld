from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_authenticated_player, get_uow
from app.application.ports import UnitOfWork
from app.application.settlements import SettlementService

router = APIRouter(prefix="/api/v1/settlement", tags=["settlement"])

class SettlementResponse(BaseModel):
    id: UUID
    owner_id: UUID
    region: str
    level: int
    modules: dict[str, int]
    capabilities: dict[str, bool]
    version: int


def response(settlement) -> SettlementResponse:
    return SettlementResponse(id=settlement.id, owner_id=settlement.owner_id, region=settlement.region, level=settlement.level, modules=settlement.modules, capabilities=settlement.interaction_capabilities(), version=settlement.version)

@router.get("", response_model=SettlementResponse)
def get_settlement(uow: UnitOfWork = Depends(get_uow), player: UUID = Depends(get_authenticated_player)):
    return response(SettlementService(uow).get_or_create(player))
