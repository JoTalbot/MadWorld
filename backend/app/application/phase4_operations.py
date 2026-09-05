"""Pure Phase 4 lifecycle rules shared by API/application adapters."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

CONTRACT_STATES = {"OFFERED", "ACCEPTED", "COMPLETED", "CANCELLED", "EXPIRED"}
ESCROW_STATES = {"LOCKED", "RELEASED", "REFUNDED"}
INVITATION_STATES = {"OFFERED", "ACCEPTED", "DECLINED", "EXPIRED"}

@dataclass(frozen=True, slots=True)
class ContractTransition:
    old_state: str
    new_state: str

@dataclass(frozen=True, slots=True)
class ReputationDelta:
    subject_player_id: UUID | None
    subject_corporation_id: UUID | None
    target_type: str
    target_id: str
    delta: int
    reason: str

class Phase4Operations:
    @staticmethod
    def transition_contract(old_state: str, new_state: str) -> ContractTransition:
        if old_state not in CONTRACT_STATES or new_state not in CONTRACT_STATES:
            raise ValueError("unknown social contract state")
        allowed = {"OFFERED": {"ACCEPTED", "CANCELLED", "EXPIRED"}, "ACCEPTED": {"COMPLETED", "CANCELLED", "EXPIRED"}, "COMPLETED": set(), "CANCELLED": set(), "EXPIRED": set()}
        if new_state not in allowed[old_state]:
            raise ValueError(f"invalid contract transition: {old_state} -> {new_state}")
        return ContractTransition(old_state, new_state)

    @staticmethod
    def validate_escrow_state(state: str) -> None:
        if state not in ESCROW_STATES:
            raise ValueError("unknown escrow state")

    @staticmethod
    def validate_invitation_state(state: str) -> None:
        if state not in INVITATION_STATES:
            raise ValueError("unknown alliance invitation state")

    @staticmethod
    def reputation_delta(subject_player_id: UUID | None, subject_corporation_id: UUID | None, target_type: str, target_id: str, delta: int, reason: str) -> ReputationDelta:
        if (subject_player_id is None) == (subject_corporation_id is None):
            raise ValueError("exactly one reputation subject is required")
        if not target_type.strip() or not target_id.strip() or not reason.strip():
            raise ValueError("reputation target and reason are required")
        if delta == 0 or not -10_000 <= delta <= 10_000:
            raise ValueError("reputation delta must be non-zero and within bounds")
        return ReputationDelta(subject_player_id, subject_corporation_id, target_type.strip(), target_id.strip(), delta, reason.strip())
