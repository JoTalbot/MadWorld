from pathlib import Path

ROOT=Path(__file__).parents[1]

def test_b4_migration_and_engine_contract():
 sql=(ROOT/'migrations/030_b4_npc_faction_simulation.sql').read_text()
 assert 'npc_faction_actions' in sql
 assert 'faction_diplomacy' in sql
 assert 'faction_action_events' in sql
 assert 'UNIQUE(action_id)' in sql
 code=(ROOT/'app/application/npc_faction_simulation.py').read_text()
 assert 'choose_action' in code and 'execute_action' in code
 assert 'ACTIONS' in code

def test_b5_migration_and_warfare_contract():
 sql=(ROOT/'migrations/031_b5_territory_warfare.sql').read_text()
 for token in ('territory_checkpoints','territory_supply_lines','territory_warfare_operations','territory_warfare_events'):
  assert token in sql
 assert 'condition_bps' in sql
 assert 'disruption_bps' in sql
 code=(ROOT/'app/application/territory_warfare.py').read_text()
 assert 'damage_infrastructure' in code and 'repair_infrastructure' in code
 assert 'resolve_operation' in code

def test_b4_b5_api_surfaces_are_registered():
 main=(ROOT/'app/main.py').read_text()
 assert 'phase8_faction_router' in main
 assert 'phase9_warfare_router' in main
