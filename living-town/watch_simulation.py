#!/usr/bin/env python3
"""
Multi-Layer Simulation Viewer - Stress Test
============================================
Runs all 6 layers simultaneously at massive scale.

Target Scale:
- 1 Universe
- 10 Galaxies
- 100 Systems
- 1000 Worlds
- 10000 Factions
- 100000 NPCs

100 years of simulation time.
Console stays open at end for evaluation.
"""

import sys
import time
import random
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

# Import all layers
from layers.layer1_core_rules import calculate_biorhythms, generate_thoughts, roll_dice
from layers.layer2_items import ItemGenerator
from layers.layer3_entities import NPCGenerator, TownManager, EntityState
from layers.layer4_structures import TownGenerator, BuildingGenerator
from layers.layer5_factions import FactionManager, FactionTurnManager
from layers.layer6_stellaris import CosmicManager


# ────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────

class SimConfig:
    """Simulation scale configuration."""
    
    # Cosmic scale (Layer 6)
    UNIVERSES = 1
    GALAXIES = 10
    SYSTEMS = 100
    WORLDS = 1000
    
    # Faction scale (Layer 5)
    FACTIONS = 10000
    
    # NPC scale (Layer 3)
    NPCS = 100000
    
    # Time scale
    YEARS = 100
    WEEKS_PER_YEAR = 52
    
    # Display
    TICK_DELAY = 0.0  # No delay for stress test
    SUMMARY_INTERVAL = 10  # Show summary every N years


# ────────────────────────────────────────────────
# Multi-Layer Viewer
# ────────────────────────────────────────────────

class MultiLayerViewer:
    """
    Runs and displays all 6 simulation layers.
    """
    
    def __init__(self):
        self.config = SimConfig()
        
        # Layer instances
        self.item_gen = ItemGenerator()
        self.npc_gen = NPCGenerator()
        self.town_mgr = TownManager()
        self.town_gen = TownGenerator()
        self.building_gen = BuildingGenerator()
        self.faction_mgr = FactionManager(count=self.config.FACTIONS)
        self.turn_mgr = FactionTurnManager()
        self.cosmic_mgr = CosmicManager(
            galaxy_count=self.config.GALAXIES,
            systems_per_galaxy=self.config.SYSTEMS // self.config.GALAXIES
        )
        
        # Tracking
        self.stats = {
            'layer1_rolls': 0,
            'layer2_items': 0,
            'layer3_npcs': 0,
            'layer4_buildings': 0,
            'layer5_actions': 0,
            'layer6_systems': 0,
            'layer6_worlds': 0,
        }
        
        self.start_time = None
        self.factions = None
        self.leaders = {}
        self.npcs = []
    
    def initialize(self):
        """Initialize all layers."""
        print("\n" + "=" * 80)
        print("  MULTI-LAYER SIMULATION - STRESS TEST")
        print("  All 6 Layers Running Simultaneously")
        print("=" * 80)
        
        print(f"\n  Configuration:")
        print(f"    Universes:  {self.config.UNIVERSES}")
        print(f"    Galaxies:   {self.config.GALAXIES}")
        print(f"    Systems:    {self.config.SYSTEMS}")
        print(f"    Worlds:     {self.config.WORLDS}")
        print(f"    Factions:   {self.config.FACTIONS:,}")
        print(f"    NPCs:       {self.config.NPCS:,}")
        print(f"    Years:      {self.config.YEARS}")
        print(f"    Total Weeks: {self.config.YEARS * self.config.WEEKS_PER_YEAR:,}")
        
        print("\n" + "-" * 80)
        print("  INITIALIZING LAYERS...")
        print("-" * 80)
        
        self.start_time = time.time()
        
        # Layer 6: Cosmic
        print("\n  [Layer 6] Generating cosmic scale...")
        galaxies = self.cosmic_mgr.get_all_galaxies()
        total_systems = sum(len(g.systems) for g in galaxies)
        total_worlds = sum(
            len(s.worlds)
            for g in galaxies
            for s in g.systems.values()
        )
        self.stats['layer6_systems'] = total_systems
        self.stats['layer6_worlds'] = total_worlds
        print(f"    Galaxies: {len(galaxies)}")
        print(f"    Systems:  {total_systems}")
        print(f"    Worlds:   {total_worlds}")
        
        # Layer 5: Factions
        print(f"\n  [Layer 5] Generating {self.config.FACTIONS:,} factions...")
        self.factions = self.faction_mgr.get_all_factions()
        print(f"    Factions created: {len(self.factions)}")
        
        # Layer 4: Towns/Buildings
        print(f"\n  [Layer 4] Generating towns and buildings...")
        buildings = 0
        for _ in range(min(1000, self.config.FACTIONS // 10)):
            town = self.town_gen.generate_town(building_count=random.randint(2, 5))
            buildings += len(town.buildings)
        self.stats['layer4_buildings'] = buildings
        print(f"    Buildings: {buildings}")
        
        # Layer 3: NPCs
        print(f"\n  [Layer 3] Generating {self.config.NPCS:,} NPCs...")
        # Generate in batches to avoid memory issues
        batch_size = 10000
        batches = self.config.NPCS // batch_size
        for i in range(batches):
            batch = [self.npc_gen.generate_npc() for _ in range(batch_size)]
            for npc in batch:
                self.town_mgr.add_npc(npc)
            self.npcs.extend(batch)
            if (i + 1) % 2 == 0:
                print(f"      Generated {(i + 1) * batch_size:,} NPCs...")
        self.stats['layer3_npcs'] = len(self.npcs)
        print(f"    NPCs created: {len(self.npcs):,}")
        
        # Assign faction leaders
        print(f"\n  [Layer 5] Assigning faction leaders...")
        for i, faction in enumerate(self.factions[:min(1000, len(self.factions))]):
            leader = self.npcs[i % len(self.npcs)]
            self.leaders[faction.id] = leader
            faction.leader_id = leader.id
        print(f"    Leaders assigned: {len(self.leaders)}")
        
        # Layer 2: Items (sample)
        print(f"\n  [Layer 2] Generating sample items...")
        for _ in range(100):
            self.item_gen.generate_weapon()
            self.item_gen.generate_armor()
        self.stats['layer2_items'] = 200
        print(f"    Items generated: 200 (sample)")
        
        # Layer 1: Biorhythms (calculated during NPC gen)
        self.stats['layer1_rolls'] = self.config.NPCS * 3  # ~3 rolls per NPC
        print(f"\n  [Layer 1] Biorhythms calculated: {self.config.NPCS:,}")
        
        print("\n" + "=" * 80)
        print("  INITIALIZATION COMPLETE")
        print("=" * 80)
        print(f"\n  Total entities: {self.config.NPCS + self.config.FACTIONS + total_worlds:,}")
        print(f"  Ready to begin simulation...\n")
        
        time.sleep(2)
    
    def run_simulation(self):
        """Run the multi-year simulation."""
        
        total_weeks = self.config.YEARS * self.config.WEEKS_PER_YEAR
        faction_sample_size = min(100, len(self.factions))
        faction_sample = self.factions[:faction_sample_size]
        
        print("=" * 80)
        print("  SIMULATION RUNNING")
        print("=" * 80)
        print(f"\n  Running {self.config.YEARS} years ({total_weeks:,} weeks)...")
        print(f"  Sampling {faction_sample_size} factions for detailed tracking")
        print(f"  Press Ctrl+C to stop early\n")
        
        try:
            for year in range(1, self.config.YEARS + 1):
                year_start = time.time()
                
                # Process each week
                for week_in_year in range(1, self.config.WEEKS_PER_YEAR + 1):
                    week = (year - 1) * self.config.WEEKS_PER_YEAR + week_in_year
                    
                    # Layer 5: Faction turns (sample)
                    actions = self.turn_mgr.process_week(faction_sample, self.leaders)
                    events = self.turn_mgr.resolve_actions(actions)
                    self.stats['layer5_actions'] += len(actions)
                    
                    # Layer 1: Random dice rolls (simulating NPC actions)
                    for _ in range(100):
                        roll_dice(20)
                        self.stats['layer1_rolls'] += 1
                    
                    # Layer 3: NPC state updates (sample)
                    if week % 10 == 0:
                        sample_npcs = random.sample(self.npcs, min(1000, len(self.npcs)))
                        for npc in sample_npcs:
                            new_state = random.choice(list(EntityState))
                            self.town_mgr.update_npc_state(npc.id, new_state, f"year_{year}")
                
                # Year summary
                year_time = time.time() - year_start
                weeks_per_sec = self.config.WEEKS_PER_YEAR / year_time
                
                if year % self.config.SUMMARY_INTERVAL == 0 or year == self.config.YEARS:
                    print(f"\n  {'=' * 60}")
                    print(f"  YEAR {year:3d} COMPLETE")
                    print(f"  {'=' * 60}")
                    print(f"    Time elapsed: {year_time:.2f}s")
                    print(f"    Simulation speed: {weeks_per_sec:.1f} weeks/sec")
                    print(f"    Total actions: {self.stats['layer5_actions']:,}")
                    print(f"    Total dice rolls: {self.stats['layer1_rolls']:,}")
                    
                    # Faction status
                    success_count = sum(
                        1 for a in self.turn_mgr.action_log[-1000:]
                        if a.get('success', False)
                    )
                    total_actions = len(self.turn_mgr.action_log[-1000:])
                    if total_actions > 0:
                        success_rate = (success_count / total_actions) * 100
                        print(f"    Faction success rate: {success_rate:.1f}%")
                    
                    # NPC state distribution
                    states = {}
                    for npc in random.sample(self.npcs, min(10000, len(self.npcs))):
                        s = npc.state.value
                        states[s] = states.get(s, 0) + 1
                    print(f"    NPC states (sample):")
                    for state, count in sorted(states.items()):
                        print(f"      {state:15s}: {count:,}")
                
                # Small yield to prevent UI freeze
                if year % 5 == 0:
                    time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("\n\n  *** SIMULATION INTERRUPTED BY USER ***")
            return False
        
        return True
    
    def show_final_summary(self):
        """Show final simulation summary."""
        
        total_time = time.time() - self.start_time
        
        print("\n" + "=" * 80)
        print("  SIMULATION COMPLETE")
        print("=" * 80)
        
        print(f"\n  Duration: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        print(f"  Years simulated: {self.config.YEARS}")
        print(f"  Weeks simulated: {self.config.YEARS * self.config.WEEKS_PER_YEAR:,}")
        
        print(f"\n  Layer Statistics:")
        print(f"    Layer 1 (Core):     {self.stats['layer1_rolls']:,} dice rolls")
        print(f"    Layer 2 (Items):    {self.stats['layer2_items']:,} items generated")
        print(f"    Layer 3 (Entities): {self.stats['layer3_npcs']:,} NPCs")
        print(f"    Layer 4 (Structures): {self.stats['layer4_buildings']:,} buildings")
        print(f"    Layer 5 (Factions): {self.stats['layer5_actions']:,} faction actions")
        print(f"    Layer 6 (Cosmic):   {self.stats['layer6_systems']:,} systems, {self.stats['layer6_worlds']:,} worlds")
        
        total_entities = (
            self.stats['layer3_npcs'] +
            self.stats['layer5_actions'] +
            self.stats['layer6_worlds']
        )
        print(f"\n  Total entity-operations: {total_entities:,}")
        
        if total_time > 0:
            ops_per_sec = total_entities / total_time
            print(f"  Operations/second: {ops_per_sec:,.0f}")
        
        # Final state samples
        print(f"\n  Final State Samples:")
        
        # NPC states
        states = {}
        for npc in random.sample(self.npcs, min(10000, len(self.npcs))):
            s = npc.state.value
            states[s] = states.get(s, 0) + 1
        print(f"\n    NPC States:")
        for state, count in sorted(states.items()):
            pct = (count / 10000) * 100
            print(f"      {state:15s}: {count:6,} ({pct:.1f}%)")
        
        # Faction purposes
        print(f"\n    Faction Purposes (sample):")
        for faction in self.factions[:10]:
            print(f"      {faction.name[:30]:30s}: {faction.purpose[:40]}")
        
        # Cosmic summary
        galaxies = self.cosmic_mgr.get_all_galaxies()
        print(f"\n    Cosmic Scale:")
        print(f"      Galaxies: {len(galaxies)}")
        total_sys = sum(len(g.systems) for g in galaxies)
        total_wld = sum(len(s.worlds) for g in galaxies for s in g.systems.values())
        print(f"      Systems:  {total_sys:,}")
        print(f"      Worlds:   {total_wld:,}")
        
        print("\n" + "=" * 80)
        print("  END OF SIMULATION")
        print("=" * 80)
        print("\n  Console will remain open for evaluation.")
        print("  Close manually or press Ctrl+C to exit.\n")


def main():
    """Main entry point."""
    
    viewer = MultiLayerViewer()
    
    # Initialize all layers
    viewer.initialize()
    
    # Run simulation
    completed = viewer.run_simulation()
    
    # Show final summary
    if completed:
        viewer.show_final_summary()
    
    # Keep console open
    print("\n" + "-" * 80)
    print("  SIMULATION ENDED - CONSOLE REMAINING OPEN")
    print("-" * 80)
    print("\n  You can now:")
    print("    - Review the output above")
    print("    - Scroll through the logs")
    print("    - Copy/paste data for analysis")
    print("\n  Press Ctrl+C when ready to close.\n")
    
    # Wait indefinitely
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n  Console closed by user.")
        sys.exit(0)


if __name__ == '__main__':
    main()
