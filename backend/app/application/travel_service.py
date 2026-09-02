"""B2 gameplay command layer for travel, encounters, salvage and recovery."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import text

from app.application.master_b1_b2 import route_risk_bps


def plan_travel(conn, *, player_id: UUID, vehicle_id: UUID, origin_region_id: UUID,
                destination_region_id: UUID, world_region_id: str, duration_seconds: int,
                fuel_reserved: int, cargo_weight: int, base_risk_bps: int,
                idempotency_key: str) -> dict:
    if duration_seconds <= 0 or fuel_reserved < 0 or cargo_weight < 0:
        raise ValueError("invalid travel plan")
    risk = route_risk_bps(conn, world_region_id, base_risk_bps)
    row = conn.execute(text("""
        INSERT INTO player_travel_sessions
          (player_id,vehicle_id,origin_region_id,destination_region_id,state,planned_duration_seconds,
           fuel_reserved,cargo_weight,route_risk_bps,world_region_id,idempotency_key)
        VALUES (:p,:v,:o,:d,'PLANNED',:duration,:fuel,:cargo,:risk,:world,:key)
        ON CONFLICT (idempotency_key) DO UPDATE SET version=player_travel_sessions.version
        RETURNING id,state,route_risk_bps,version
    """), {"p": player_id, "v": vehicle_id, "o": origin_region_id, "d": destination_region_id,
          "duration": duration_seconds, "fuel": fuel_reserved, "cargo": cargo_weight,
          "risk": risk, "world": world_region_id, "key": idempotency_key}).mappings().one()
    return dict(row)


def depart_travel(conn, *, session_id: UUID) -> dict:
    row = conn.execute(text("""
        UPDATE player_travel_sessions
        SET state='TRAVELLING', departure_at=COALESCE(departure_at,now()),
            arrival_at=COALESCE(arrival_at,now()+make_interval(secs => planned_duration_seconds)), version=version+1
        WHERE id=:id AND state='PLANNED'
        RETURNING id,state,departure_at,arrival_at,route_risk_bps,version
    """), {"id": session_id}).mappings().first()
    if not row:
        existing = conn.execute(text("SELECT id,state,departure_at,arrival_at,route_risk_bps,version FROM player_travel_sessions WHERE id=:id"), {"id": session_id}).mappings().first()
        if not existing:
            raise ValueError("travel session not found")
        return dict(existing)
    return dict(row)


def resolve_travel(conn, *, session_id: UUID, outcome: str) -> dict:
    if outcome not in {'ARRIVED','INTERRUPTED','LOST','CANCELLED'}:
        raise ValueError("invalid travel outcome")
    row = conn.execute(text("""
        UPDATE player_travel_sessions
        SET state=:state, arrival_at=COALESCE(arrival_at,now()), version=version+1
        WHERE id=:id AND state IN ('TRAVELLING','PLANNED')
        RETURNING id,state,arrival_at,vehicle_id,player_id
    """), {"id": session_id, "state": outcome}).mappings().first()
    if not row:
        raise ValueError("travel session is not in a resolvable state")
    if outcome == 'LOST':
        conn.execute(text("""
            INSERT INTO salvage_recovery_cases(player_id,vehicle_id,travel_session_id,state,recovery_cost,salvage_value,idempotency_key)
            VALUES (:p,:v,:s,'AVAILABLE',100,250,:key)
            ON CONFLICT (idempotency_key) DO NOTHING
        """), {"p": row['player_id'], "v": row['vehicle_id'], "s": row['id'], "key": f"loss:{row['id']}"})
    return dict(row)


def spawn_encounter(conn, *, session_id: UUID, world_event_id: UUID, encounter_type: str, severity: int) -> UUID:
    if encounter_type not in {'FACTION','CONVOY','DISASTER','AMBUSH','DISCOVERY'}:
        raise ValueError("invalid encounter type")
    if not 1 <= severity <= 5:
        raise ValueError("invalid severity")
    row = conn.execute(text("""
        INSERT INTO travel_encounters(travel_session_id,world_event_id,encounter_type,severity)
        VALUES (:s,:e,:t,:severity)
        ON CONFLICT (travel_session_id,world_event_id) DO UPDATE SET severity=travel_encounters.severity
        RETURNING id
    """), {"s": session_id, "e": world_event_id, "t": encounter_type, "severity": severity}).first()
    return UUID(str(row[0]))


def resolve_encounter(conn, *, encounter_id: UUID, outcome: str) -> dict:
    if outcome not in {'RESOLVED','ESCAPED','DEFEATED','LOST'}:
        raise ValueError("invalid encounter outcome")
    row = conn.execute(text("""
        UPDATE travel_encounters SET state=:state,resolved_at=now()
        WHERE id=:id AND state='PENDING'
        RETURNING id,travel_session_id,state
    """), {"id": encounter_id, "state": outcome}).mappings().first()
    if not row:
        raise ValueError("encounter is not pending")
    return dict(row)


def claim_recovery(conn, *, player_id: UUID, case_id: UUID) -> dict:
    row = conn.execute(text("""
        UPDATE salvage_recovery_cases SET state='CLAIMED',version=version+1
        WHERE id=:id AND player_id=:p AND state='AVAILABLE'
        RETURNING id,vehicle_id,recovery_cost,state,version
    """), {"id": case_id, "p": player_id}).mappings().first()
    if not row:
        raise ValueError("recovery case unavailable")
    return dict(row)
