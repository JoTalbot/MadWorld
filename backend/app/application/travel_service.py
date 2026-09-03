"""B2 authoritative travel/gameplay API for travel, encounters, salvage and recovery."""
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
    fuel_row = conn.execute(text("""
        UPDATE vehicles v
        SET fuel = v.fuel - s.fuel_reserved
        FROM player_travel_sessions s
        WHERE s.id=:id
          AND s.state='PLANNED'
          AND v.id=s.vehicle_id
          AND v.owner_id=s.player_id
          AND v.fuel >= s.fuel_reserved
        RETURNING v.id, v.fuel AS fuel_remaining
    """), {"id": session_id}).mappings().first()
    if not fuel_row:
        existing = conn.execute(text("""
            SELECT s.id,s.state,s.departure_at,s.arrival_at,s.route_risk_bps,s.version,
                   s.fuel_reserved,v.fuel AS fuel_remaining
            FROM player_travel_sessions s
            JOIN vehicles v ON v.id=s.vehicle_id
            WHERE s.id=:id
        """), {"id": session_id}).mappings().first()
        if not existing:
            raise ValueError("travel session not found")
        if existing["state"] != "PLANNED":
            return dict(existing)
        raise ValueError("insufficient vehicle fuel")

    row = conn.execute(text("""
        UPDATE player_travel_sessions
        SET state='TRAVELLING', departure_at=COALESCE(departure_at,now()),
            arrival_at=COALESCE(arrival_at,now()+make_interval(secs => planned_duration_seconds)),
            version=version+1
        WHERE id=:id AND state='PLANNED'
        RETURNING id,state,departure_at,arrival_at,route_risk_bps,version,fuel_reserved
    """), {"id": session_id}).mappings().first()
    if not row:
        raise ValueError("travel session is no longer planned")
    result = dict(row)
    result["fuel_remaining"] = fuel_row["fuel_remaining"]
    return result


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
        existing = conn.execute(text("""
            SELECT id,state,arrival_at,vehicle_id,player_id
            FROM player_travel_sessions
            WHERE id=:id
        """), {"id": session_id}).mappings().first()
        if existing and existing["state"] == outcome:
            return dict(existing)
        raise ValueError("travel session is not in a resolvable state")
    if outcome == 'LOST':
        conn.execute(text("""
            UPDATE vehicles
            SET state='destroyed', durability=0, version=version+1
            WHERE id=:v AND owner_id=:p
        """), {"v": row['vehicle_id'], "p": row['player_id']})
        conn.execute(text("""
            UPDATE vehicle_components SET condition=0 WHERE vehicle_id=:v
        """), {"v": row['vehicle_id']})
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
        existing = conn.execute(text("""
            SELECT id,travel_session_id,state
            FROM travel_encounters
            WHERE id=:id
        """), {"id": encounter_id}).mappings().first()
        if existing and existing["state"] == outcome:
            return dict(existing)
        raise ValueError("encounter is not pending")

    # LOST is the authoritative terminal combat outcome for travel: the encounter
    # resolves the linked travel session through the same DB transaction, which
    # destroys the vehicle and creates the idempotent recovery case.
    if outcome == 'LOST':
        resolve_travel(conn, session_id=row['travel_session_id'], outcome='LOST')
    return dict(row)


def claim_recovery(conn, *, player_id: UUID, case_id: UUID) -> dict:
    case = conn.execute(text("""
        SELECT id,vehicle_id,recovery_cost,state
        FROM salvage_recovery_cases
        WHERE id=:id AND player_id=:p
        FOR UPDATE
    """), {"id": case_id, "p": player_id}).mappings().first()
    if not case:
        raise ValueError("recovery case unavailable")
    if case["state"] == "RECOVERED":
        return dict(case)
    if case["state"] != "AVAILABLE":
        raise ValueError("recovery case unavailable")

    wallet = conn.execute(text("SELECT id FROM wallets WHERE owner_id=:p FOR UPDATE"), {"p": player_id}).mappings().first()
    if not wallet:
        raise ValueError("player wallet not found")

    balance = conn.execute(text("""
        SELECT COALESCE(SUM(amount), 0) AS balance
        FROM ledger_entries
        WHERE wallet_id=:w
    """), {"w": wallet["id"]}).scalar_one()
    cost = int(case["recovery_cost"])
    if balance < cost:
        raise ValueError("insufficient wallet balance for recovery")

    if cost:
        conn.execute(text("""
            INSERT INTO ledger_entries(idempotency_key,wallet_id,amount,reason,actor_id)
            VALUES (:key,:w,:amount,:reason,:actor)
            ON CONFLICT (idempotency_key) DO NOTHING
        """), {
            "key": f"recovery:{case_id}",
            "w": wallet["id"],
            "amount": -cost,
            "reason": "vehicle_recovery",
            "actor": player_id,
        })

    vehicle = conn.execute(text("""
        UPDATE vehicles
        SET state='stored', durability=GREATEST(1,durability), version=version+1
        WHERE id=:v AND owner_id=:p AND state='destroyed'
        RETURNING id
    """), {"v": case["vehicle_id"], "p": player_id}).first()
    if not vehicle:
        raise ValueError("recovery vehicle is not destroyed or is not owned by player")

    conn.execute(text("""
        UPDATE vehicle_components
        SET condition=GREATEST(1,condition)
        WHERE vehicle_id=:v
    """), {"v": case["vehicle_id"]})

    row = conn.execute(text("""
        UPDATE salvage_recovery_cases
        SET state='RECOVERED',version=version+1
        WHERE id=:id AND state='AVAILABLE'
        RETURNING id,vehicle_id,recovery_cost,state,version
    """), {"id": case_id}).mappings().one()
    return dict(row)
