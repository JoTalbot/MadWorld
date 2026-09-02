"""Deterministic Phase 6 world simulation core.

The simulator emits world events and derived mission/discovery records. It never
writes player wallets, inventory, vehicles or market orders directly.
"""
from __future__ import annotations
from hashlib import sha256
from uuid import UUID
from sqlalchemy import text

REGIONS = ("dust_basin", "iron_ruins", "salt_coast")
RESOURCE_TYPES = ("scrap", "fuel", "water")
EVENT_CYCLE = ("SHORTAGE", "CONVOY", "DISCOVERY", "DISASTER")


def _seed(season: int, tick: int) -> str:
    return sha256(f"madworld:{season}:{tick}".encode()).hexdigest()[:32]


def _score(seed: str, key: str) -> int:
    return int(sha256(f"{seed}:{key}".encode()).hexdigest()[:8], 16) % 10000


def simulate_tick(conn, expected_tick: int | None = None) -> dict:
    """Advance exactly one world tick under a row lock.

    Re-running after a committed tick returns the existing result instead of
    generating duplicate events, making scheduler retries safe.
    """
    state = conn.execute(text("SELECT season,tick,version FROM world_simulation_state WHERE id=1 FOR UPDATE")).mappings().one()
    current = int(state["tick"])
    if expected_tick is not None and current != expected_tick:
        raise ValueError(f"stale world tick: expected {expected_tick}, current {current}")
    next_tick = current + 1
    season = int(state["season"])
    seed = _seed(season, next_tick)
    existing = conn.execute(text("SELECT tick,generated_events,generated_missions,seed FROM world_simulation_ticks WHERE tick=:t"), {"t": next_tick}).mappings().first()
    if existing:
        return dict(existing)

    generated_events = 0
    generated_missions = 0
    for index, region in enumerate(REGIONS):
        pressure_rows = conn.execute(text("SELECT resource_type,target_quantity,available_quantity,version FROM regional_resource_pressure WHERE region_id=:r ORDER BY resource_type"), {"r": region}).mappings().all()
        for row in pressure_rows:
            target = int(row["target_quantity"])
            available = int(row["available_quantity"])
            # Pressure is derived from current stock and a small deterministic drift.
            drift = (_score(seed, f"pressure:{region}:{row['resource_type']}") % 101) - 50
            pressure = max(-10000, min(10000, ((target - available) * 10000 // max(target, 1)) + drift))
            conn.execute(text("UPDATE regional_resource_pressure SET pressure_bps=:p,trend_bps=:tr,version=version+1 WHERE region_id=:r AND resource_type=:rt AND version=:v"), {"p": pressure, "tr": drift, "r": region, "rt": row["resource_type"], "v": row["version"]})
            if pressure >= 3000 and (_score(seed, f"shortage:{region}:{row['resource_type']}") % 3 == 0):
                event_type = "regional_shortage"
                payload = {"resource_type": row["resource_type"], "pressure_bps": pressure}
                result = conn.execute(text("INSERT INTO world_events(tick,region_id,event_type,severity,payload) VALUES (:t,:r,:e,:s,CAST(:p AS JSONB)) ON CONFLICT (tick,event_type,region_id,faction_id) DO NOTHING RETURNING id"), {"t": next_tick, "r": region, "e": event_type, "s": min(5, max(1, pressure // 2000)), "p": __import__('json').dumps(payload)}).first()
                if result:
                    generated_events += 1
                    event_id = UUID(str(result[0]))
                    conn.execute(text("INSERT INTO world_simulation_event_log(tick,event_id,event_type,payload) VALUES (:t,:id,:e,CAST(:p AS JSONB)) ON CONFLICT DO NOTHING"), {"t": next_tick, "id": event_id, "e": event_type, "p": __import__('json').dumps(payload)})
                    mission = conn.execute(text("INSERT INTO dynamic_missions(world_event_id,region_id,mission_type,title,reward_credits,risk_bps,expires_at) VALUES (:id,:r,'SUPPLY','Relieve regional shortage',:reward,:risk,now()+interval '24 hours') RETURNING id"), {"id": event_id, "r": region, "reward": 500 + min(4500, pressure), "risk": min(9000, 1500 + pressure // 2)}).first()
                    if mission: generated_missions += 1
        cycle = EVENT_CYCLE[(next_tick + index) % len(EVENT_CYCLE)]
        if cycle == "CONVOY":
            destination = REGIONS[(index + 1) % len(REGIONS)]
            payload = {"origin": region, "destination": destination, "cargo_type": RESOURCE_TYPES[index % len(RESOURCE_TYPES)]}
            event = conn.execute(text("INSERT INTO world_events(tick,region_id,event_type,severity,payload) VALUES (:t,:r,'convoy_event',2,CAST(:p AS JSONB)) ON CONFLICT (tick,event_type,region_id,faction_id) DO NOTHING RETURNING id"), {"t": next_tick, "r": region, "p": __import__('json').dumps(payload)}).first()
            if event:
                generated_events += 1
                eid = UUID(str(event[0]))
                conn.execute(text("INSERT INTO world_convoy_events(world_event_id,origin_region_id,destination_region_id,cargo_type,cargo_quantity,danger_bps) VALUES (:id,:o,:d,:ct,:q,:danger)"), {"id": eid, "o": region, "d": destination, "ct": payload["cargo_type"], "q": 100 + _score(seed, f"cargo:{region}") % 901, "danger": 1000 + _score(seed, f"danger:{region}") % 6001})
                conn.execute(text("INSERT INTO world_simulation_event_log(tick,event_id,event_type,payload) VALUES (:t,:id,'convoy_event',CAST(:p AS JSONB)) ON CONFLICT DO NOTHING"), {"t": next_tick, "id": eid, "p": __import__('json').dumps(payload)})
        elif cycle == "DISCOVERY":
            rtype = RESOURCE_TYPES[_score(seed, f"discovery:{region}") % len(RESOURCE_TYPES)]
            payload = {"resource_type": rtype, "quantity": 250 + _score(seed, f"quantity:{region}") % 751}
            event = conn.execute(text("INSERT INTO world_events(tick,region_id,event_type,severity,payload) VALUES (:t,:r,'resource_discovery',2,CAST(:p AS JSONB)) ON CONFLICT (tick,event_type,region_id,faction_id) DO NOTHING RETURNING id"), {"t": next_tick, "r": region, "p": __import__('json').dumps(payload)}).first()
            if event:
                generated_events += 1
                eid = UUID(str(event[0]))
                conn.execute(text("INSERT INTO resource_discoveries(world_event_id,region_id,resource_type,quantity,expires_at) VALUES (:id,:r,:rt,:q,now()+interval '48 hours')"), {"id": eid, "r": region, "rt": rtype, "q": payload["quantity"]})
                conn.execute(text("INSERT INTO world_simulation_event_log(tick,event_id,event_type,payload) VALUES (:t,:id,'resource_discovery',CAST(:p AS JSONB)) ON CONFLICT DO NOTHING"), {"t": next_tick, "id": eid, "p": __import__('json').dumps(payload)})
        elif cycle == "DISASTER":
            dtype = ("dust_storm", "ash_quake", "toxic_spill")[_score(seed, f"disaster:{region}") % 3]
            severity = 1 + _score(seed, f"severity:{region}") % 5
            payload = {"disaster_type": dtype, "severity": severity}
            event = conn.execute(text("INSERT INTO world_events(tick,region_id,event_type,severity,payload) VALUES (:t,:r,'disaster',:s,CAST(:p AS JSONB)) ON CONFLICT (tick,event_type,region_id,faction_id) DO NOTHING RETURNING id"), {"t": next_tick, "r": region, "s": severity, "p": __import__('json').dumps(payload)}).first()
            if event:
                generated_events += 1
                eid = UUID(str(event[0]))
                disaster = conn.execute(text("INSERT INTO world_disasters(world_event_id,region_id,disaster_type,severity,starts_at,ends_at) VALUES (:id,:r,:dt,:s,now(),now()+interval '12 hours') RETURNING id"), {"id": eid, "r": region, "dt": dtype, "s": severity}).first()
                conn.execute(text("INSERT INTO catastrophe_zones(disaster_id,region_id,hazard_bps,travel_risk_bps,extraction_modifier_bps) VALUES (:d,:r,:h,:risk,:ext)"), {"d": disaster[0], "r": region, "h": severity * 1500, "risk": severity * 1200, "ext": -(severity * 1000)})
                conn.execute(text("INSERT INTO world_simulation_event_log(tick,event_id,event_type,payload) VALUES (:t,:id,'disaster',CAST(:p AS JSONB)) ON CONFLICT DO NOTHING"), {"t": next_tick, "id": eid, "p": __import__('json').dumps(payload)})

    conn.execute(text("INSERT INTO world_simulation_ticks(tick,season,seed,generated_events,generated_missions) VALUES (:t,:s,:seed,:e,:m)"), {"t": next_tick, "s": season, "seed": seed, "e": generated_events, "m": generated_missions})
    conn.execute(text("UPDATE world_simulation_state SET tick=:t,last_tick_at=now(),version=version+1 WHERE id=1"), {"t": next_tick})
    return {"tick": next_tick, "season": season, "seed": seed, "generated_events": generated_events, "generated_missions": generated_missions}
