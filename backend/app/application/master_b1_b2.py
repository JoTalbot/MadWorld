"""B1/B2 integration services.

These services translate authoritative world events into durable domain signals
and deterministic gameplay state transitions. Player-owned assets remain under
explicit player/gameplay commands, not the world simulator.
"""
from __future__ import annotations

import json
from hashlib import sha256
from uuid import UUID

from sqlalchemy import text

from app.application.world_event_consumers import consume_once

ECONOMY_CONSUMER = "economy.world-v1"
TERRITORY_CONSUMER = "territory.world-v1"


def _bps(value: int, low: int, high: int) -> int:
    return max(low, min(high, int(value)))


def apply_economy_signal(conn, event_id: UUID, region_id: str, event_type: str, payload: dict) -> bool:
    """Persist a normalized world→economy signal exactly once."""
    def apply(data: dict) -> None:
        resource = str(data.get("resource_type", "unknown"))[:64]
        pressure = _bps(int(data.get("pressure_bps", 0)), -10000, 10000)
        scarcity = max(0, pressure)
        conn.execute(
            text("""
                INSERT INTO world_economy_signals
                    (world_event_id,region_id,event_type,resource_type,pressure_bps,scarcity_bps,payload)
                VALUES (:id,:r,:e,:rt,:p,:s,CAST(:payload AS JSONB))
                ON CONFLICT (world_event_id) DO UPDATE SET
                    pressure_bps=EXCLUDED.pressure_bps,
                    scarcity_bps=EXCLUDED.scarcity_bps,
                    payload=EXCLUDED.payload
            """),
            {"id": event_id, "r": region_id, "e": event_type, "rt": resource,
             "p": pressure, "s": scarcity, "payload": json.dumps(data)},
        )
        conn.execute(
            text("""
                INSERT INTO world_region_effects(world_region_id,supply_modifier_bps,source_world_event_id,updated_tick)
                SELECT :r, :s, :id, COALESCE((SELECT tick FROM world_events WHERE id=:id),0)
                WHERE EXISTS (SELECT 1 FROM world_regions WHERE id=:r)
                ON CONFLICT (world_region_id) DO UPDATE SET
                    supply_modifier_bps=EXCLUDED.supply_modifier_bps,
                    source_world_event_id=EXCLUDED.source_world_event_id,
                    updated_tick=EXCLUDED.updated_tick,
                    version=world_region_effects.version+1
            """),
            {"r": region_id, "s": _bps(-scarcity // 2, -10000, 0), "id": event_id},
        )
    return consume_once(conn, ECONOMY_CONSUMER, event_id, payload, apply)


def apply_territory_signal(conn, event_id: UUID, region_id: str, event_type: str, payload: dict) -> bool:
    """Translate world hazards into a bounded territory modifier."""
    def apply(data: dict) -> None:
        severity = _bps(int(data.get("severity", 1)), 1, 5)
        disaster = event_type == "disaster"
        # All effect columns are bounded by schema CHECK constraints to
        # [-5000, 5000] bps (see world_region_effects / territory_modifiers).
        # Clamp the computed modifiers to those authoritative limits so a
        # maximum-severity disaster (severity 5 -> raw risk 6000) never violates
        # the database invariant and aborts the whole world tick.
        risk = _bps(severity * 1200 if disaster else 0, -5000, 5000)
        extraction = _bps(-(severity * 1000) if disaster else 0, -5000, 5000)
        travel = _bps(severity * 800 if disaster else 0, -5000, 5000)
        conn.execute(
            text("""
                INSERT INTO territory_modifiers
                    (region_id,source_type,source_id,travel_time_bps,travel_risk_bps,extraction_bps,version)
                SELECT b.world_region_id,'world_event',CAST(:id AS TEXT),:travel,:risk,:extract,0
                FROM world_region_bindings b
                WHERE b.world_region_id=:r
                  AND EXISTS (SELECT 1 FROM world_regions wr WHERE wr.id=b.world_region_id)
                ON CONFLICT (region_id,source_type,source_id) DO NOTHING
            """),
            {"r": region_id, "id": event_id, "travel": travel, "risk": risk, "extract": extraction},
        )
        conn.execute(
            text("""
                INSERT INTO world_region_effects(world_region_id,travel_time_modifier_bps,travel_risk_modifier_bps,extraction_modifier_bps,source_world_event_id,updated_tick)
                SELECT :r,:travel,:risk,:extract,:id,COALESCE((SELECT tick FROM world_events WHERE id=:id),0)
                WHERE EXISTS (SELECT 1 FROM world_regions WHERE id=:r)
                ON CONFLICT (world_region_id) DO UPDATE SET
                    travel_time_modifier_bps=EXCLUDED.travel_time_modifier_bps,
                    travel_risk_modifier_bps=EXCLUDED.travel_risk_modifier_bps,
                    extraction_modifier_bps=EXCLUDED.extraction_modifier_bps,
                    source_world_event_id=EXCLUDED.source_world_event_id,
                    updated_tick=EXCLUDED.updated_tick,
                    version=world_region_effects.version+1
            """),
            {"r": region_id, "travel": travel, "risk": risk, "extract": extraction, "id": event_id},
        )
    return consume_once(conn, TERRITORY_CONSUMER, event_id, payload, apply)


def progress_convoys(conn, current_tick: int) -> int:
    """Advance deterministic convoy lifecycle without touching player assets."""
    rows = conn.execute(text("""
        UPDATE world_convoy_events
        SET state=CASE
            WHEN :tick >= travel_ends_tick AND danger_bps >= 8000 THEN 'LOST'
            WHEN :tick >= travel_ends_tick THEN 'ARRIVED'
            ELSE 'TRAVELLING'
        END,
        resolved_tick=CASE WHEN :tick >= travel_ends_tick THEN :tick ELSE resolved_tick END,
        loss_reason=CASE WHEN :tick >= travel_ends_tick AND danger_bps >= 8000 THEN 'route_hazard' ELSE loss_reason END
        WHERE state IN ('SPAWNED','TRAVELLING') AND travel_ends_tick IS NOT NULL AND travel_ends_tick <= :tick
        RETURNING id
    """), {"tick": current_tick}).all()
    return len(rows)


def expire_world_records(conn, current_tick: int) -> dict[str, int]:
    """Expire discoveries/missions and close expired disasters idempotently."""
    discoveries = conn.execute(text("""
        UPDATE resource_discoveries SET state='EXPIRED'
        WHERE state='AVAILABLE' AND ((expires_tick IS NOT NULL AND expires_tick <= :tick)
          OR (expires_tick IS NULL AND expires_at <= now()))
        RETURNING id
    """), {"tick": current_tick}).all()
    missions = conn.execute(text("""
        UPDATE dynamic_missions SET state='EXPIRED', invalidated_at=COALESCE(invalidated_at,now())
        WHERE state='AVAILABLE' AND ((expires_at IS NOT NULL AND expires_at <= now()))
        RETURNING id
    """), {}).all()
    disasters = conn.execute(text("""
        UPDATE world_disasters SET state='EXPIRED'
        WHERE state='ACTIVE' AND ends_at IS NOT NULL AND ends_at <= now()
        RETURNING id
    """), {}).all()
    return {"discoveries": len(discoveries), "missions": len(missions), "disasters": len(disasters)}


def state_hash(conn, tick: int) -> str:
    """Hash canonical world integration state for deterministic replay audits."""
    rows = conn.execute(text("""
        SELECT region_id,resource_type,pressure_bps,trend_bps,version
        FROM regional_resource_pressure ORDER BY region_id,resource_type
    """), {}).mappings().all()
    payload = json.dumps([dict(r) for r in rows], sort_keys=True, default=str, separators=(",", ":"))
    return sha256(f"{tick}:{payload}".encode()).hexdigest()


def route_risk_bps(conn, region_id: str, base_risk_bps: int) -> int:
    """Return bounded route risk after world and gameplay-territory modifiers."""
    row = conn.execute(text("""
        SELECT COALESCE(w.travel_risk_modifier_bps,0) AS world_risk,
               COALESCE(t.travel_risk_bps,0) AS territory_risk
        FROM world_region_effects w
        LEFT JOIN world_region_bindings b ON b.world_region_id=w.world_region_id
        LEFT JOIN LATERAL (
          SELECT travel_risk_bps
          FROM territory_modifiers
          WHERE region_id=b.world_region_id
          ORDER BY version DESC
          LIMIT 1
        ) t ON TRUE
        WHERE w.world_region_id=:r
    """), {"r": region_id}).mappings().first()
    if not row:
        return _bps(base_risk_bps, 0, 10000)
    return _bps(base_risk_bps + int(row["world_risk"]) + int(row["territory_risk"]), 0, 10000)
