"""Post-simulation B1 integration pipeline.

The pipeline is transactional with the world tick. It converts world output into
stable economy/territory signals, advances NPC world state, progresses generated
records, and writes replay/lag telemetry. Player-owned resources remain outside
this transaction boundary.
"""
from __future__ import annotations

import time
from hashlib import sha256
from typing import Any

from sqlalchemy import text

from app.application.master_b1_b2 import (
    apply_economy_signal,
    apply_territory_signal,
    expire_world_records,
    progress_convoys,
    state_hash,
)
from app.application.phase6_world import simulate_tick


def _event_payload(conn, tick: int) -> list[dict[str, Any]]:
    rows = conn.execute(text("""
        SELECT id,region_id,event_type,severity,payload,faction_id,state
        FROM world_events WHERE tick=:t ORDER BY id
    """), {"t": tick}).mappings().all()
    return [dict(r) for r in rows]


def _faction_dynamics(conn, tick: int, seed: str) -> int:
    """Move faction influence/hostility/supply in bounded deterministic steps."""
    rows = conn.execute(text("""
        SELECT fr.faction_id,fr.region_id,fr.influence_bps,fr.hostility_bps,fr.supply_bps,
               f.aggression_bps,f.logistics_bps
        FROM world_faction_regions fr
        JOIN world_factions f ON f.id=fr.faction_id
        ORDER BY fr.faction_id,fr.region_id
    """)).mappings().all()
    changed = 0
    for row in rows:
        key = f"{seed}:{row['faction_id']}:{row['region_id']}"
        score = int(sha256(key.encode()).hexdigest()[:8], 16) % 101 - 50
        influence = max(0, min(10000, int(row['influence_bps']) + score))
        hostility = max(-10000, min(10000, int(row['hostility_bps']) + score // 2 + (int(row['aggression_bps']) - 5000) // 200))
        supply = max(0, min(10000, int(row['supply_bps']) + score + (int(row['logistics_bps']) - 5000) // 200))
        conn.execute(text("""
            UPDATE world_faction_regions
            SET influence_bps=:i,hostility_bps=:h,supply_bps=:s,version=version+1
            WHERE faction_id=:f AND region_id=:r
        """), {"i": influence, "h": hostility, "s": supply, "f": row['faction_id'], "r": row['region_id']})
        changed += 1
    return changed


def _mission_grammar(conn, tick: int, events: list[dict[str, Any]]) -> int:
    created = 0
    for event in events:
        event_id = event['id']
        region = event['region_id']
        etype = event['event_type']
        payload = event['payload'] or {}
        if not region:
            continue
        if etype == 'convoy_event':
            mission_type, title, reward, risk = 'ESCORT', 'Escort a world convoy', 900, int(payload.get('danger_bps', 3000))
        elif etype == 'resource_discovery':
            mission_type, title, reward, risk = 'RECOVER', 'Recover newly discovered resources', 700, 1800
        elif etype == 'disaster':
            severity = int(payload.get('severity', event['severity']))
            mission_type, title, reward, risk = 'DISASTER_RESPONSE', 'Respond to regional catastrophe', 1000 + severity * 500, min(9500, severity * 1600)
        elif etype == 'regional_shortage':
            mission_type, title, reward, risk = 'SUPPLY', 'Relieve regional shortage', 750, 2500
        else:
            continue
        result = conn.execute(text("""
            INSERT INTO dynamic_missions(world_event_id,source_event_id,region_id,mission_type,title,reward_credits,risk_bps,expires_at)
            VALUES (:id,:id,:r,:mt,:title,:reward,:risk,now()+interval '24 hours')
            ON CONFLICT (source_event_id) DO NOTHING RETURNING id
        """), {"id": event_id, "r": region, "mt": mission_type, "title": title, "reward": reward, "risk": max(0, min(10000, risk))}).first()
        if result:
            created += 1
    return created


def _backfill_generated_lifecycles(conn, tick: int) -> None:
    conn.execute(text("""
        UPDATE world_convoy_events c SET spawn_tick=e.tick,
          travel_ends_tick=e.tick + GREATEST(1, CEIL(c.danger_bps / 2500.0)::BIGINT),
          state=CASE WHEN c.state='SPAWNED' THEN 'TRAVELLING' ELSE c.state END
        FROM world_events e
        WHERE c.world_event_id=e.id AND c.spawn_tick IS NULL
    """), {})
    conn.execute(text("""
        UPDATE resource_discoveries d SET discovered_tick=e.tick,
          expires_tick=e.tick + 48
        FROM world_events e
        WHERE d.world_event_id=e.id AND d.discovered_tick IS NULL
    """), {})
    conn.execute(text("""
        UPDATE dynamic_missions SET source_event_id=world_event_id
        WHERE source_event_id IS NULL
    """), {})


def run_world_tick(conn, expected_tick: int | None = None) -> dict:
    started = time.monotonic()
    result = simulate_tick(conn, expected_tick=expected_tick)
    tick = int(result['tick'])
    events = _event_payload(conn, tick)
    _backfill_generated_lifecycles(conn, tick)
    economy = territory = 0
    for event in events:
        payload = event['payload'] or {}
        if event['region_id']:
            if apply_economy_signal(conn, event['id'], event['region_id'], event['event_type'], payload):
                economy += 1
            if apply_territory_signal(conn, event['id'], event['region_id'], event['event_type'], payload):
                territory += 1
    faction = _faction_dynamics(conn, tick, str(result['seed']))
    missions = _mission_grammar(conn, tick, events)
    progressed = progress_convoys(conn, tick)
    expired = expire_world_records(conn, tick)
    shash = state_hash(conn, tick)
    event_json = __import__('json').dumps(events, sort_keys=True, default=str, separators=(',', ':'))
    ehash = sha256(event_json.encode()).hexdigest()
    duration_ms = int((time.monotonic() - started) * 1000)
    conn.execute(text("""
        UPDATE world_simulation_ticks SET state_hash=:s,event_hash=:e,duration_ms=:d,
          lag_ms=GREATEST(0,EXTRACT(EPOCH FROM (now()-created_at))*1000)::INTEGER
        WHERE tick=:t
    """), {"s": shash, "e": ehash, "d": duration_ms, "t": tick})
    conn.execute(text("""
        INSERT INTO world_replay_checkpoints(tick,state_hash,event_hash)
        VALUES (:t,:s,:e) ON CONFLICT (tick) DO UPDATE SET state_hash=EXCLUDED.state_hash,event_hash=EXCLUDED.event_hash
    """), {"t": tick, "s": shash, "e": ehash})
    telemetry = {
        'economy_signals': economy,
        'territory_signals': territory,
        'faction_updates': faction,
        'mission_grammar': missions,
        'convoys_progressed': progressed,
        **{f'expired_{k}': v for k, v in expired.items()},
        'tick_duration_ms': duration_ms,
    }
    for name, value in telemetry.items():
        conn.execute(text("INSERT INTO world_integration_telemetry(tick,metric_name,metric_value) VALUES (:t,:n,:v)"), {'t': tick, 'n': name, 'v': int(value)})
    return {**result, **telemetry, 'state_hash': shash, 'event_hash': ehash}
