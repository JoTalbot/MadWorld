from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ExpeditionRisk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass(frozen=True, slots=True)
class ExpeditionPlan:
    region: str
    distance_km: int
    risk: ExpeditionRisk
    duration_seconds: int
    fuel_cost: int


RISK_MULTIPLIER = {
    ExpeditionRisk.LOW: 1.0,
    ExpeditionRisk.MEDIUM: 1.25,
    ExpeditionRisk.HIGH: 1.6,
    ExpeditionRisk.EXTREME: 2.1,
}


def build_plan(region: str, distance_km: int, risk: ExpeditionRisk) -> ExpeditionPlan:
    if not region.strip():
        raise ValueError("expedition region must not be blank")
    if not 1 <= distance_km <= 1000:
        raise ValueError("expedition distance must be between 1 and 1000 km")
    multiplier = RISK_MULTIPLIER[risk]
    fuel_cost = max(1, round(distance_km * multiplier / 10))
    duration_seconds = max(60, distance_km * 30)
    return ExpeditionPlan(region.strip(), distance_km, risk, duration_seconds, fuel_cost)
