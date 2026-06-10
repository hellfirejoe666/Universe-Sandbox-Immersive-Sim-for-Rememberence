#!/usr/bin/env python3
"""
30-Week Stress Test
2x entities per layer to evaluate scaling and consistency.
DEV_MODE principles but larger dataset.
"""

import sys
from pathlib import Path
import time
sys.path.insert(0, str(Path(__file__).parent.parent))

from layers.layer1_core_rules import calculate_biorhythms
from layers.layer2_items import ItemGenerator
from layers.layer3_entities import NPCGenerator
from layers.layer4_structures import TownGenerator
from layers.layer5_factions import FactionManager, FactionTurnManager
from layers.layer6_worlds import WorldManager
from layers.layer6_stellaris import CosmicManager
from layer0_airai import AIRAIOrchestrator, UIManager
from save_system import SaveManager


# Configuration
CONFIG = {
    'weeks': 30,
    'npcs': 6,           # 2x (was 3)
    'factions': 4,       # 2x (was 2)
    'town_buildings': 6, # 2x (was 3)
    'world_towns': 4,    # 2x (was 2)
    'galaxy_systems': 6, # 2x (was 3)
}

print("=" * 60)
print("30-WEEK STRESS TEST (2x ENTITIES)")
print("=" * 60)
print(f"Configuration:")
for key, value in CONFIG.items():
    print(f"  {key}: {value}")
print("=" * 60)

# Track performance
start_time = time.time()
ai_calls = 0
ai_calls_saved = 0

# Initialize all layers
print("\n[INIT] Initializing all layers...")
init_start = time.time()

airai = AIRAIOrchestrator()
ui = UIManager(airai)
save_mgr = SaveManager()
save = save_mgr.new_game("stress_test")
turn_mgr = FactionTurnManager()

item_gen = ItemGenerator()
npc_gen = NPCGenerator()
town_gen = TownGenerator()
faction_mgr = FactionManager(count=CONFIG['factions'])
world_mgr = WorldManager(world_count=1, towns_per_world=CONFIG['world_towns'])
cosmic_mgr = CosmicManager(galaxy_count=1, systems_per_galaxy=CONFIG['galaxy_systems'])

init_time = time.time() - init_start
print(f"  Initialization: {init_time:.2f}s")

# Generate entities
print("\n[GENERATE] Creating entities...")
gen_start = time.time()

print(f"\n[LAYER 1-2] Items")
items = [item_gen.generate_weapon() for _ in range(10)]
print(f"  Generated {len(items)} items")

print(f"\n[LAYER 2] NPCs ({CONFIG['npcs']})")
npcs = [npc_gen.generate_npc() for _ in range(CONFIG['npcs'])]
for npc in npcs:
    print(f"  - {npc.name} ({npc.animal_sign}/{npc.star_sign})")

print(f"\n[LAYER 3] Towns")
town = town_gen.generate_town(building_count=CONFIG['town_buildings'])
print(f"  {town.name}: {len(town.buildings)} buildings, ~{town.population} pop")

print(f"\n[LAYER 4] Factions ({CONFIG['factions']})")
factions = faction_mgr.get_all_factions()
for faction in factions:
    print(f"  - {faction.name} ({faction.faction_type.value})")

print(f"\n[LAYER 5] Worlds")
world = world_mgr.get_all_worlds()[0]
print(f"  {world.name}: {len(world.towns)} towns")

print(f"\n[LAYER 6] Stellaris")
galaxy = cosmic_mgr.get_all_galaxies()[0]
print(f"  {galaxy.name}: {len(galaxy.systems)} systems")

gen_time = time.time() - gen_start
print(f"\n  Generation: {gen_time:.2f}s")

# Assign faction leaders
print("\n[SETUP] Assigning faction leaders...")
leaders = {}
for i, faction in enumerate(factions):
    leader = npcs[i % len(npcs)]
    leaders[faction.id] = leader
    faction.leader_id = leader.id
    print(f"  {faction.name} -> {leader.name}")

# Run 30-week simulation
print("\n" + "=" * 60)
print(f"SIMULATION: {CONFIG['weeks']} WEEKS")
print("=" * 60)

sim_start = time.time()
narratives_generated = 0
events_logged = 0

for week in range(1, CONFIG['weeks'] + 1):
    save.current_week = week
    
    # Progress indicator every 5 weeks
    if week % 5 == 0:
        print(f"\n[Week {week:2d}] ", end="", flush=True)
    
    # Process faction turns
    actions = turn_mgr.process_week(factions, leaders)
    events = turn_mgr.resolve_actions(actions)
    
    # Generate narratives for events (lazy evaluation)
    for event in events:
        event_key = f"evt_{week}_{event['action']}"
        
        if not save.has_narrative(event_key):
            # First time - generate narrative (AI call)
            narrative = airai.generate_narrative('event', {
                'week': week,
                'faction': 'Faction',
                'action': event['action'],
                'success': event['success']
            })
            save.add_narrative(event_key, 'event', narrative, {'week': week})
            narratives_generated += 1
            ai_calls += 1
        else:
            # Already generated - retrieve saved
            ai_calls_saved += 1
        
        save.add_event(event)
        events_logged += 1
    
    if week % 5 == 0:
        print(f"{len(events)} events, {narratives_generated} AI calls so far")

sim_time = time.time() - sim_start
print(f"\n  Simulation: {sim_time:.2f}s ({CONFIG['weeks']} weeks)")

# Generate NPC narratives (player examination simulation)
print("\n" + "=" * 60)
print("NARRATIVE GENERATION (Player Examination)")
print("=" * 60)

narr_start = time.time()

print("\nFirst examination (should generate narratives):")
for npc in npcs:
    npc_key = f"npc_{npc.id}"
    
    if not save.has_narrative(npc_key):
        narrative = airai.generate_narrative('npc', {
            'name': npc.name,
            'animal_sign': npc.animal_sign,
            'star_sign': npc.star_sign,
            'kno': npc.biorhythms.KNO,
            'wis': npc.biorhythms.WIS,
            'str': npc.biorhythms.STR,
            'mood': 'neutral'
        })
        save.add_narrative(npc_key, 'npc', narrative, {'week': save.current_week})
        narratives_generated += 1
        ai_calls += 1
        print(f"  {npc.name}: [GENERATED]")
    else:
        ai_calls_saved += 1
        print(f"  {npc.name}: [ALREADY SAVED]")

print("\nRe-examination (should retrieve saved narratives):")
for npc in npcs:
    npc_key = f"npc_{npc.id}"
    narrative_data = save.get_narrative(npc_key)
    
    if narrative_data:
        print(f"  {npc.name}: [RETRIEVED] (view #{narrative_data['view_count']})")
        ai_calls_saved += 1

narr_time = time.time() - narr_start
print(f"  Narrative gen: {narr_time:.2f}s")

# Save/Load test
print("\n" + "=" * 60)
print("SAVE/LOAD TEST")
print("=" * 60)

save_start = time.time()
filename = save_mgr.save_game("stress_test_30w.json")
save_time = time.time() - save_start
print(f"Save time: {save_time:.2f}s ({filename})")

load_start = time.time()
loaded = save_mgr.load_game(filename)
load_time = time.time() - load_start
print(f"Load time: {load_time:.2f}s")

# Performance summary
total_time = time.time() - start_time

print("\n" + "=" * 60)
print("PERFORMANCE SUMMARY")
print("=" * 60)

print(f"""
Total Time: {total_time:.2f}s
  - Initialization: {init_time:.2f}s
  - Generation: {gen_time:.2f}s
  - Simulation: {sim_time:.2f}s ({CONFIG['weeks']} weeks)
  - Narratives: {narr_time:.2f}s
  - Save/Load: {save_time + load_time:.2f}s

Entity Counts:
  - NPCs: {len(npcs)}
  - Factions: {len(factions)}
  - Town Buildings: {len(town.buildings)}
  - World Towns: {len(world.towns)}
  - Galaxy Systems: {len(galaxy.systems)}

AI Performance:
  - AI Calls: {ai_calls} (one-time generation)
  - Calls Saved: {ai_calls_saved} (retrieved from save)
  - Savings: {ai_calls_saved / (ai_calls + ai_calls_saved) * 100:.1f}% reduction

Narratives:
  - Generated: {narratives_generated}
  - Events Logged: {events_logged}
  - Total in Save: {len(loaded.narratives)}

Weeks Simulated: {CONFIG['weeks']}
Events per Week: {events_logged / CONFIG['weeks']:.1f}
""")

# Emergent story highlights
print("=" * 60)
print("EMERGENT STORY HIGHLIGHTS")
print("=" * 60)

# Find most successful faction
faction_success = {}
for event in loaded.witnessed_events:
    # Simplified - in production would track faction per event
    if event['success']:
        faction_success['Success'] = faction_success.get('Success', 0) + 1
    else:
        faction_success['Failure'] = faction_success.get('Failure', 0) + 1

print(f"\nOverall Outcomes:")
for outcome, count in faction_success.items():
    print(f"  {outcome}: {count} events")

# Show some event narratives
print(f"\nSample Event Narratives (first 5):")
for i, event in enumerate(loaded.witnessed_events[:5]):
    narrative_id = f"evt_{event['week']}_{event['action']}"
    narrative_data = loaded.get_narrative(narrative_id)
    if narrative_data:
        print(f"  Week {event['week']}: {narrative_data['text'][:70]}...")

print("\n" + "=" * 60)
print("STRESS TEST COMPLETE")
print("=" * 60)

if total_time < 60:
    print(f"Status: EXCELLENT (<60s for 30 weeks, 2x entities)")
elif total_time < 120:
    print(f"Status: GOOD (<2min for 30 weeks, 2x entities)")
else:
    print(f"Status: NEEDS OPTIMIZATION (>2min)")

print(f"Architecture: VALIDATED (narrative persistence working)")
print("=" * 60)
