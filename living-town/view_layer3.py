#!/usr/bin/env python3
"""
Layer 3 Viewer - Entities (NPCs)
=================================
Watch procedural NPC generation.
Biorhythms, thoughts, schedules, and relationships.
"""

import sys
import time
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from layers.layer3_entities import NPCGenerator, TownManager, NPC, EntityState


def view_layer3(iterations=8, delay=0.6):
    """
    Watch Layer 3: Entities in action.
    
    Shows:
    - NPC generation (12 animals x 12 stars)
    - Biorhythm-based personalities
    - Daily schedules
    - Relationships between NPCs
    - State changes
    """
    
    print("\n" + "=" * 70)
    print("  LAYER 3 VIEWER - Entities (NPCs)")
    print("  Watching procedural NPC generation")
    print("=" * 70)
    print(f"\nRunning {iterations} iterations... (delay: {delay}s)\n")
    
    time.sleep(1)
    
    gen = NPCGenerator()
    manager = TownManager()
    
    # Track stats
    npcs_created = []
    state_counts = {s.value: 0 for s in EntityState}
    
    for i in range(iterations):
        print("-" * 70)
        print(f"Iteration {i+1:2d}")
        print("-" * 70)
        
        # Generate an NPC
        npc = gen.generate_npc()
        npcs_created.append(npc)
        manager.add_npc(npc)
        
        print(f"\n  NPC: {npc.name}")
        print(f"    ID: {npc.id}")
        print(f"    Sign: {npc.animal_sign} / {npc.star_sign}")
        print(f"    Type: {npc.entity_type.value} / {npc.spirit_type.value}")
        print(f"    Level: {npc.level}")
        
        # Show key biorhythms
        bio = npc.biorhythms
        print(f"\n  Key Biorhythms:")
        print(f"    MNF={bio.MNF:2d}  KNO={bio.KNO:2d}  WIS={bio.WIS:2d}")
        print(f"    STR={bio.STR:2d}  VIT={bio.VIT:2d}  EGO={bio.EGO:2d}")
        print(f"    Sum: {bio.sum()}")
        
        # Show thoughts
        thoughts = npc.thoughts
        print(f"\n  Thoughts:")
        print(f"    Environment:   {thoughts.Environment:3d}  (Chaos/Order)")
        print(f"    Emotion:       {thoughts.Emotion:3d}  (Fear/Love)")
        print(f"    State:         {thoughts.State:.1f}")
        
        # Show schedule
        print(f"\n  Daily Schedule:")
        for time_period in ['morning', 'afternoon', 'evening', 'night']:
            activity = npc.schedule.get(time_period, 'idle')
            print(f"    {time_period:10s}: {activity}")
        
        # Show state
        state_counts[npc.state.value] += 1
        print(f"\n  Current State: {npc.state.value}")
        
        # Show current goal
        if npc.current_goal:
            print(f"  Current Goal: {npc.current_goal}")
        
        # Show relationships (if not first NPC)
        if len(npcs_created) > 1:
            print(f"\n  Relationships:")
            for other_npc in npcs_created[:-1]:
                rel = npc.relationships.get(other_npc.id, 0)
                rel_str = f"{rel:+d}" if rel != 0 else "0"
                rel_symbol = "+" if rel > 20 else ("-" if rel < -20 else "o")
                print(f"    [{rel_symbol}] {other_npc.name}: {rel_str}")
        
        # Update state periodically (simulate time passing)
        if i % 2 == 1 and i > 0:
            new_state = random.choice(list(EntityState))
            manager.update_npc_state(npc.id, new_state, f"auto_{new_state.value}")
            print(f"\n  [State Change] -> {new_state.value}")
            state_counts[new_state.value] += 1
        
        print()
        time.sleep(delay)
    
    # Summary
    print("=" * 70)
    print("  Layer 3 Viewer Complete")
    print("=" * 70)
    
    print(f"\n  NPCs Generated: {len(npcs_created)}")
    
    print(f"\n  Sign Distribution:")
    animals = {}
    stars = {}
    for npc in npcs_created:
        animals[npc.animal_sign] = animals.get(npc.animal_sign, 0) + 1
        stars[npc.star_sign] = stars.get(npc.star_sign, 0) + 1
    
    print(f"    Animals: {', '.join(f'{k}({v})' for k, v in sorted(animals.items()))}")
    print(f"    Stars:   {', '.join(f'{k}({v})' for k, v in sorted(stars.items()))}")
    
    print(f"\n  State Distribution:")
    for state, count in state_counts.items():
        if count > 0:
            pct = (count / len(npcs_created)) * 100 if npcs_created else 0
            print(f"    {state:12s}: {count:2d} ({pct:.0f}%)")
    
    # Average biorhythm sum
    if npcs_created:
        avg_sum = sum(npc.biorhythms.sum() for npc in npcs_created) / len(npcs_created)
        print(f"\n  Average Biorhythm Sum: {avg_sum:.1f}")
    
    print()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Layer 3: Entities Viewer')
    parser.add_argument('--iterations', type=int, default=5, help='Number of NPCs to generate')
    parser.add_argument('--delay', type=float, default=0.8, help='Delay between iterations')
    parser.add_argument('--fast', action='store_true', help='Fast mode (0.3s delay)')
    
    args = parser.parse_args()
    
    if args.fast:
        args.delay = 0.3
    
    view_layer3(iterations=args.iterations, delay=args.delay)
