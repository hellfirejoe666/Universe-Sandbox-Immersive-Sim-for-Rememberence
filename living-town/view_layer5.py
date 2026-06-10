#!/usr/bin/env python3
"""
Layer 5 Viewer - Factions
==========================
Watch procedural faction generation and decision-making.
Factions, ideologies, weekly turns, and emergent stories.
"""

import sys
import time
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from layers.layer5_factions import (
    FactionManager, FactionTurnManager, Faction,
    FactionType, CollectiveStructure, ActionCategory
)
from layers.layer3_entities import NPCGenerator


def view_layer5(weeks=8, delay=0.7):
    """
    Watch Layer 5: Factions in action.
    
    Shows:
    - Faction generation (3 procedural factions)
    - Leader assignment (NPCs from Layer 3)
    - Weekly decision turns (Civ-style)
    - Action resolution (success/fail)
    - Emergent story patterns
    """
    
    print("\n" + "=" * 70)
    print("  LAYER 5 VIEWER - Factions")
    print("  Watching procedural factions and weekly decisions")
    print("=" * 70)
    print(f"\nRunning {weeks} weeks of simulation... (delay: {delay}s)\n")
    
    time.sleep(1)
    
    # Initialize systems
    npc_gen = NPCGenerator()
    faction_mgr = FactionManager(count=3)
    turn_mgr = FactionTurnManager()
    
    # Generate factions
    factions = faction_mgr.get_all_factions()
    
    # Generate leaders for each faction
    leaders = {}
    npcs = [npc_gen.generate_npc() for _ in range(3)]
    
    for i, faction in enumerate(factions):
        leader = npcs[i]
        leaders[faction.id] = leader
        faction.leader_id = leader.id
    
    # Track stats
    action_counts = {cat.value: 0 for cat in ActionCategory}
    success_count = 0
    fail_count = 0
    
    # Show initial state
    print("-" * 70)
    print("  INITIAL STATE")
    print("-" * 70)
    
    print(f"\n  Factions ({len(factions)}):")
    for faction in factions:
        leader = leaders[faction.id]
        print(f"\n    {faction.name}")
        print(f"      Leader: {leader.name} ({leader.animal_sign}/{leader.star_sign})")
        print(f"      Type: {faction.faction_type.value}")
        print(f"      Structure: {faction.structure.value}")
        print(f"      Ideology: {faction.ideology}")
        print(f"      Purpose: {faction.purpose}")
        print(f"      Members: ~{faction.member_count}")
    
    print("\n" + "=" * 70)
    print("  SIMULATION RUNNING")
    print("=" * 70)
    
    # Run weekly turns
    try:
        for week in range(1, weeks + 1):
            print(f"\n{'=' * 70}")
            print(f"  WEEK {week:2d}")
            print('=' * 70)
            
            # Process faction turns
            actions = turn_mgr.process_week(factions, leaders)
            events = turn_mgr.resolve_actions(actions)
            
            # Show results
            print(f"\n  Actions Taken:")
            for i, faction in enumerate(factions):
                action = actions[i] if i < len(actions) else None
                result = events[i] if i < len(events) else None
                
                if not action:
                    continue
                
                leader = leaders[faction.id]
                status = "[OK]" if (result and result.get('success')) else "[FAIL]"
                
                if result and result.get('success'):
                    success_count += 1
                else:
                    fail_count += 1
                
                action_counts[action.category.value] += 1
                
                print(f"\n    {faction.name[:35]:<35} | {leader.name[:12]:<12}")
                print(f"      {status} {action.name:<25} [{action.success_chance:.0f}%]")
                print(f"          {action.description}")
            
            # Show event summary
            print(f"\n  Week {week} Events:")
            for event in events:
                sym = "+" if event.get('success') else "-"
                print(f"    [{sym}] {event.get('action', 'Unknown')[:50]}")
            
            # Show emerging patterns every 3 weeks
            if week % 3 == 0:
                print(f"\n  [Pattern Check - Week {week}]")
                
                # Find most active faction
                faction_actions = {}
                for action in turn_mgr.action_log:
                    fname = action.get('faction', 'Unknown')
                    faction_actions[fname] = faction_actions.get(fname, 0) + 1
                
                if faction_actions:
                    most_active = max(faction_actions.items(), key=lambda x: x[1])
                    print(f"    Most Active: {most_active[0]} ({most_active[1]} actions)")
                
                # Find success rate
                total = success_count + fail_count
                if total > 0:
                    rate = (success_count / total) * 100
                    print(f"    Success Rate: {rate:.0f}% ({success_count}/{total})")
            
            time.sleep(delay)
    
    except KeyboardInterrupt:
        print("\n\n  *** Interrupted ***")
    
    # Final summary
    print("\n" + "=" * 70)
    print("  LAYER 5 VIEWER COMPLETE")
    print("=" * 70)
    
    print(f"\n  Simulation Summary:")
    print(f"    Weeks Simulated: {weeks}")
    print(f"    Factions:        {len(factions)}")
    print(f"    Total Actions:   {success_count + fail_count}")
    
    print(f"\n  Action Distribution:")
    for category, count in sorted(action_counts.items()):
        if count > 0:
            pct = (count / (success_count + fail_count)) * 100 if (success_count + fail_count) > 0 else 0
            print(f"    {category:15s}: {count:2d} ({pct:.0f}%)")
    
    print(f"\n  Success/Fail:")
    print(f"    Successful: {success_count}")
    print(f"    Failed:     {fail_count}")
    
    if success_count + fail_count > 0:
        rate = (success_count / (success_count + fail_count)) * 100
        print(f"    Success Rate: {rate:.0f}%")
    
    print(f"\n  Final Faction States:")
    for faction in factions:
        print(f"    {faction.name[:35]:<35} | {faction.purpose[:30]}")
    
    print()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Layer 5: Factions Viewer')
    parser.add_argument('--weeks', type=int, default=6, help='Number of weeks to simulate')
    parser.add_argument('--delay', type=float, default=0.8, help='Delay between weeks')
    parser.add_argument('--fast', action='store_true', help='Fast mode (0.3s delay)')
    
    args = parser.parse_args()
    
    if args.fast:
        args.delay = 0.3
    
    view_layer5(weeks=args.weeks, delay=args.delay)
