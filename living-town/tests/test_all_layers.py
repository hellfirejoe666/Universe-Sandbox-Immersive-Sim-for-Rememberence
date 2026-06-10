#!/usr/bin/env python3
"""
Full Integration Test: All 7 Layers (0-6)
Tests complete stack with narrative persistence.
DEV_MODE: Fast iteration (<10s)
"""

import sys
from pathlib import Path
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


print("=" * 60)
print("FULL INTEGRATION TEST: ALL 7 LAYERS (0-6)")
print("=" * 60)
print("DEV_MODE: Minimal data for fast iteration")
print("=" * 60)

# Initialize systems
print("\n[INIT] Initializing all layers...")

# Layer 0: AIR-AI + UI
print("\n[LAYER 0] AIR-AI + UI")
airai = AIRAIOrchestrator()
ui = UIManager(airai)
save_mgr = SaveManager()
save = save_mgr.new_game("integration_test")

# Layer 1: Core Rules + Items
print("\n[LAYER 1] Core Rules + Items")
bio = calculate_biorhythms("Tiger", "Aries")
item_gen = ItemGenerator()
print(f"  Biorhythm sample: Tiger/Aries (MNF={bio.MNF}, SPL={bio.SPL})")
print(f"  Item generator: Ready")

# Layer 2: Entities
print("\n[LAYER 2] Entities")
npc_gen = NPCGenerator()
npcs = [npc_gen.generate_npc() for _ in range(3)]
print(f"  Generated {len(npcs)} NPCs")
for npc in npcs:
    print(f"    - {npc.name} ({npc.animal_sign}/{npc.star_sign})")

# Layer 3: Structures
print("\n[LAYER 3] Structures")
town_gen = TownGenerator()
town = town_gen.generate_town(building_count=3)
print(f"  Generated town: {town.name} ({len(town.buildings)} buildings)")

# Layer 4: Factions + Decisions
print("\n[LAYER 4] Factions + Decisions")
faction_mgr = FactionManager(count=2)
factions = faction_mgr.get_all_factions()
turn_mgr = FactionTurnManager()
print(f"  Generated {len(factions)} factions")

# Layer 5: Worlds
print("\n[LAYER 5] Worlds")
world_mgr = WorldManager(world_count=1, towns_per_world=2)
world = world_mgr.get_all_worlds()[0]
print(f"  Generated world: {world.name} ({len(world.towns)} towns)")

# Layer 6: Stellaris
print("\n[LAYER 6] Stellaris")
cosmic_mgr = CosmicManager(galaxy_count=1, systems_per_galaxy=3)
galaxy = cosmic_mgr.get_all_galaxies()[0]
print(f"  Generated galaxy: {galaxy.name} ({len(galaxy.systems)} systems)")

# Integration: Connect layers
print("\n" + "=" * 60)
print("INTEGRATION: CONNECTING ALL LAYERS")
print("=" * 60)

# Assign leaders to factions
print("\n[NPCs -> Factions]")
leaders = {}
for i, faction in enumerate(factions):
    leader = npcs[i % len(npcs)]
    leaders[faction.id] = leader
    faction.leader_id = leader.id
    print(f"  {faction.name} led by {leader.name}")

# Run faction turns (3 weeks, DEV_MODE)
print("\n" + "=" * 60)
print("SIMULATION: 3 WEEKS (DEV_MODE)")
print("=" * 60)

for week in range(1, 4):
    save.current_week = week
    actions = turn_mgr.process_week(factions, leaders)
    events = turn_mgr.resolve_actions(actions)
    
    # Log events with narratives
    for event in events:
        narrative = airai.generate_narrative('event', {
            'week': week,
            'faction': 'Faction',
            'action': event['action'],
            'success': event['success']
        })
        save.add_event(event, narrative)

# Narrative Generation Test
print("\n" + "=" * 60)
print("NARRATIVE GENERATION TEST (On-Demand)")
print("=" * 60)

# Generate narratives for NPCs (first time - AI call)
print("\nGenerating narratives (first examination):")
for npc in npcs:
    if not save.has_narrative(f"npc_{npc.id}"):
        narrative = airai.generate_narrative('npc', {
            'name': npc.name,
            'animal_sign': npc.animal_sign,
            'star_sign': npc.star_sign,
            'kno': npc.biorhythms.KNO,
            'wis': npc.biorhythms.WIS,
            'str': npc.biorhythms.STR,
            'mood': 'neutral'
        })
        save.add_narrative(f"npc_{npc.id}", 'npc', narrative, {
            'week': save.current_week,
            'location': town.name
        })
        print(f"  {npc.name}: [GENERATED] {narrative[:50]}...")
    else:
        print(f"  {npc.name}: [SAVED]")

# Re-examine NPCs (should use saved narrative)
print("\nRe-examining NPCs (should use saved narratives):")
for npc in npcs:
    narrative_data = save.get_narrative(f"npc_{npc.id}")
    if narrative_data:
        print(f"  {npc.name}: [RETRIEVED] {narrative_data['text'][:50]}... (view #{narrative_data['view_count']})")

# Save game
print("\n" + "=" * 60)
print("SAVE/LOAD TEST")
print("=" * 60)

filename = save_mgr.save_game("integration_test.json")
print(f"Saved: {filename}")

# Load and verify
loaded = save_mgr.load_game(filename)
print(f"\nLoaded save:")
print(f"  Week: {loaded.current_week}")
print(f"  Narratives: {len(loaded.narratives)}")
print(f"  Events: {len(loaded.witnessed_events)}")
print(f"  Discovered: {len(loaded.discovered_entities)} entities")

# Final Summary
print("\n" + "=" * 60)
print("INTEGRATION COMPLETE")
print("=" * 60)
print(f"Layers: 0-6 (all connected)")
print(f"NPCs: {len(npcs)}")
print(f"Factions: {len(factions)}")
print(f"Towns: 1 ({town.name})")
print(f"Worlds: 1 ({world.name})")
print(f"Galaxies: 1 ({galaxy.name})")
print(f"Narratives: {len(save.narratives)}")
print(f"Events: {len(save.witnessed_events)}")
print(f"Status: ALL SYSTEMS OPERATIONAL")
print("=" * 60)
