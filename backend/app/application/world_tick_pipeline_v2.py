"""Hardened B1 world tick pipeline entry point.

This version keeps mission creation conflict-safe with a partial unique index
and delegates the reusable integration operations to the B1/B2 service layer.
"""
from __future__ import annotations

import json
import time
from hashlib import sha256

from sqlalchemy import text

from app.application.master_b1_b2 import (
    apply_economy_signal,
    apply_territory_signal,
    expire_world_records,
    progress_convoys,
    state_hash,
)
from app.application.phase6_world import simulate_tick


def run_world_tick(conn, expected_tick: int | None = None) -> dict:
    started = time.monotonic()
    result = simulate_tick(conn, expected_tick=expected_tick)
    tick = int(result['tick'])
    events = [dict(r) for r in conn.execute(text("""
        SELECT id,region_id,event_type,severity,payload,faction_id,state
        FROM world_events WHERE tick=:t ORDER BY id
    """), {'t': tick}).mappings().all()]

    # Populate lifecycle timing for records emitted by the simulator.
    conn.execute(text("""
        UPDATE world_convoy_events c SET spawn_tick=e.tick,
          travel_ends_tick=e.tick + GREATEST(1, CEIL(c.danger_bps / 2500.0)::BIGINT),
          state=CASE WHEN c.state='SPAWNED' THEN 'TRAVELLING' ELSE c.state END
        FROM world_events e WHERE c.world_event_id=e.id AND c.spawn_tick IS NULL
    """), {})
    conn.execute(text("""
        UPDATE resource_discoveries d SET discovered_tick=e.tick, expires_tick=e.tick+48
        FROM world_events e WHERE d.world_event_id=e.id AND d.discovered_tick IS NULL
    """), {})

    economy = territory = 0
    for event in events:
        if event['region_id']:
            payload = event['payload'] or {}
            economy += int(apply_economy_signal(conn, event['id'], event['region_id'], event['event_type'], payload))
            territory += int(apply_territory_signal(conn, event['id'], event['region_id'], event['event_type'], payload))

    faction_updates = 0
    for row in conn.execute(text("""
        SELECT fr.faction_id,fr.region_id,fr.influence_bps,fr.hostility_bps,fr.supply_bps,
               f.aggression_bps,f.logistics_bps
        FROM world_faction_regions fr JOIN world_factions f ON f.id=fr.faction_id
        ORDER BY fr.faction_id,fr.region_id
    """)).mappings().all():
        score = int(sha256(f"{result['seed']}:{row['faction_id']}:{row['region_id']}".encode()).hexdigest()[:8], 16) % 101 - 50
        conn.execute(text("""
            UPDATE world_faction_regions SET
              influence_bps=GREATEST(0,LEAST(10000,influence_bps+:d)),
              hostility_bps=GREATEST(-10000,LEAST(10000,hostility_bps+:h)),
              supply_bps=GREATEST(0,LEAST(10000,supply_bps+:s)), version=version+1
            WHERE faction_id=:f AND region_id=:r
        """), {'d': score, 'h': score//2 + (int(row['aggression_bps'])-5000)//200,
                's': score + (int(row['logistics_bps'])-5000)//200, 'f': row['faction_id'], 'r': row['region_id']})
        faction_updates += 1

    missions = 0
    for event in events:
        if not event['region_id']:
            continue
        payload = event['payload'] or {}
        kind = event['event_type']
        if kind == 'convoy_event':
            mt, title, reward, risk = 'ESCORT', 'Escort a world convoy', 900, int(payload.get('danger_bps', 3000))
        elif kind == 'resource_discovery':
            mt, title, reward, risk = 'RECOVER', 'Recover newly discovered resources', 700, 1800
        elif kind == 'disaster':
            severity = int(payload.get('severity') or event.get('severity') or 1)
            mt, title, reward, risk = 'DISASTER_RESPONSE', 'Respond to regional catastrophe', 1000 + severity*500, min(9500, severity*1600)
        elif kind == 'regional_shortage':
            mt, title, reward, risk = 'SUPPLY', 'Relieve regional shortage', 750, 2500
        else:
            continue
        inserted = conn.execute(text("""
            INSERT INTO dynamic_missions(world_event_id,source_event_id,region_id,mission_type,title,reward_credits,risk_bps,expires_at)
            SELECT :id,:id,:r,:mt,:title,:reward,:risk,now()+interval '24 hours'
            WHERE NOT EXISTS (SELECT 1 FROM dynamic_missions WHERE source_event_id=:id)
            RETURNING id
        """), {'id': event['id'], 'r': event['region_id'], 'mt': mt, 'title': title,
                'reward': reward, 'risk': max(0, min(10000, risk))}).first()
        missions += int(inserted is not None)

    progressed = progress_convoys(conn, tick)
    expired = expire_world_records(conn, tick)
    shash = state_hash(conn, tick)
    ehash = sha256(json.dumps(events, sort_keys=True, default=str, separators=(',', ':')).encode()).hexdigest()
    duration_ms = int((time.monotonic() - started) * 1000)
    conn.execute(text("""
        UPDATE world_simulation_ticks SET state_hash=:s,event_hash=:e,duration_ms=:d,
          lag_ms=GREATEST(0,EXTRACT(EPOCH FROM (now()-created_at))*1000)::INTEGER WHERE tick=:t
    """), {'s': shash, 'e': ehash, 'd': duration_ms, 't': tick})
    conn.execute(text("""
        INSERT INTO world_replay_checkpoints(tick,state_hash,event_hash) VALUES (:t,:s,:e)
        ON CONFLICT (tick) DO UPDATE SET state_hash=EXCLUDED.state_hash,event_hash=EXCLUDED.event_hash
    """), {'t': tick, 's': shash, 'e': ehash})
    metrics = {'economy_signals': economy, 'territory_signals': territory,
               'faction_updates': faction_updates, 'mission_grammar': missions,
               'convoys_progressed': progressed, **{f'expired_{k}': v for k,v in expired.items()},
               'tick_duration_ms': duration_ms}
    for name, value in metrics.items():
        conn.execute(text("INSERT INTO world_integration_telemetry(tick,metric_name,metric_value) VALUES (:t,:n,:v)"), {'t': tick, 'n': name, 'v': int(value)})
    return {**result, **metrics, 'state_hash': shash, 'event_hash': ehash}
