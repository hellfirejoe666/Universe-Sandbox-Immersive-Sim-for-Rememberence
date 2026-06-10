#!/usr/bin/env python3
"""
Living Town Simulation

Main simulation runner that ties together all layers:
- Layer 1: Core Rules (biorhythms, dice)
- Layer 2: Items
- Layer 3: Entities (NPCs)
- Layer 4: Structures (Buildings, Towns)

 NPCs live autonomous lives, interact, and create emergent stories.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from layers.layer1_core_rules import Biorhythms, Thoughts, calculate_biorhythms
from layers.layer2_items import ItemGenerator, Item, ItemType
from layers.layer3_entities import NPCGenerator, TownManager, NPC, EntityState
from layers.layer4_structures import TownGenerator, Town, Building, BuildingType


class LivingTownSimulation:
    """
    Main simulation orchestrator.
    
    DEV_MODE: When True, skips state persistence for fast iteration.
    """
    
    # Development settings
    DEV_MODE = True
    DEV_NPC_COUNT = 5
    DEV_BUILDING_COUNT = 3
    
    def __init__(self, workspace_path: str = None):
        if workspace_path is None:
            workspace_path = "D:/Ollama/OpenClaw/workspace"
        
        self.workspace = Path(workspace_path)
        self.state_dir = self.workspace / "living-town" / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize managers
        self.town_manager = TownManager(self.state_dir)
        self.item_generator = ItemGenerator()
        self.town_generator = TownGenerator()
        
        # Current town
        self.current_town: Town = None
        
        # Simulation state
        self.simulation_time = {
            'day': 1,
            'hour': 8,  # Start at 8 AM
            'minute': 0
        }
        
        # Event log
        self.event_log: List[Dict] = []
        
        print("[Simulation] Living Town initialized")
        print(f"[Simulation] State directory: {self.state_dir}")
    
    # 
    # Initialization
    # 
    
    def initialize_world(self, town_name: str = None, 
                        npc_count: int = None,
                        building_count: int = None):
        """
        Initialize the world with a town, NPCs, and buildings.
        
        DEV_MODE: Uses minimal counts for fast iteration.
        """
        # Apply DEV_MODE overrides
        if self.DEV_MODE:
            if npc_count is None:
                npc_count = self.DEV_NPC_COUNT
            if building_count is None:
                building_count = self.DEV_BUILDING_COUNT
            print(f"[DEV_MODE] NPC count: {npc_count}, Buildings: {building_count}")
        else:
            if npc_count is None:
                npc_count = 10
            if building_count is None:
                building_count = 8
        print("\n" + "=" * 60)
        print("INITIALIZING WORLD")
        print("=" * 60)
        
        # Generate town
        print("\n[1/3] Generating town...")
        self.current_town = self.town_generator.generate_town(
            building_count=building_count
        )
        if town_name:
            self.current_town.name = town_name
        
        print(f"  Town: {self.current_town.name}")
        print(f"  Region: {self.current_town.region}")
        print(f"  Buildings: {len(self.current_town.buildings)}")
        
        # Spawn NPCs
        print(f"\n[2/3] Spawning {npc_count} NPCs...")
        self.town_manager.spawn_initial_population(npc_count)
        print(f"  Population: {len(self.town_manager.get_all_npcs())}")
        
        # Assign NPCs to buildings
        print("\n[3/3] Assigning NPCs to buildings...")
        self._assign_npcs_to_buildings()
        
        # Save initial state (skip in DEV_MODE)
        if not self.DEV_MODE:
            self._save_simulation_state()
        
        print("\n[COMPLETE] World initialization complete!")
        print(f"  Time: Day {self.simulation_time['day']}, {self.simulation_time['hour']:02d}:00")
    
    def _assign_npcs_to_buildings(self):
        """Assign NPCs to appropriate buildings based on their roles."""
        npcs = self.town_manager.get_all_npcs()
        buildings = list(self.current_town.buildings.values())
        
        # Find key buildings
        houses = [b for b in buildings if b.building_type == BuildingType.HOUSE]
        shops = [b for b in buildings if b.building_type == BuildingType.SHOP]
        tavern = next((b for b in buildings if b.building_type == BuildingType.TAVERN), None)
        
        # Assign each NPC to a house
        for i, npc in enumerate(npcs):
            if houses:
                house = houses[i % len(houses)]
                house.occupants.append(npc.id)
                
                # Some NPCs own their homes
                if i < len(houses):
                    house.owner_id = npc.id
            
            # Assign merchants to shops
            if npc.current_goal == 'setup_shop' and shops:
                shop = shops[i % len(shops)]
                shop.owner_id = npc.id
                shop.occupants.append(npc.id)
        
        print(f"  Assigned {len(npcs)} NPCs to {len(buildings)} buildings")
    
    # 
    # Simulation Loop
    # 
    
    def run_simulation_step(self, minutes: int = 60):
        """
        Advance the simulation by a time step.
        
        Args:
            minutes: Minutes to advance (default 1 hour)
        """
        print(f"\n{'=' * 60}")
        print(f"SIMULATION STEP - Day {self.simulation_time['day']}, "
              f"{self.simulation_time['hour']:02d}:{self.simulation_time['minute']:02d}")
        print(f"{'=' * 60}")
        
        # Advance time
        self._advance_time(minutes)
        
        # Update NPC states based on schedule/time
        self._update_npc_states()
        
        # Process NPC interactions
        self._process_interactions()
        
        # Log events
        self._log_simulation_step()
        
        # Save state periodically (skip in DEV_MODE)
        if not self.DEV_MODE and self.simulation_time['hour'] == 0:
            self._save_simulation_state()
    
    def _advance_time(self, minutes: int):
        """Advance simulation time."""
        self.simulation_time['minute'] += minutes
        
        while self.simulation_time['minute'] >= 60:
            self.simulation_time['minute'] -= 60
            self.simulation_time['hour'] += 1
        
        while self.simulation_time['hour'] >= 24:
            self.simulation_time['hour'] -= 24
            self.simulation_time['day'] += 1
    
    def _get_time_of_day(self) -> str:
        """Get current time period."""
        hour = self.simulation_time['hour']
        
        if 5 <= hour < 9:
            return 'morning'
        elif 9 <= hour < 13:
            return 'late_morning'
        elif 13 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'
    
    def _update_npc_states(self):
        """Update NPC states based on time and schedule."""
        time_of_day = self._get_time_of_day()
        npcs = self.town_manager.get_all_npcs()
        
        print(f"\n[Time] {time_of_day.replace('_', ' ').title()}")
        print(f"[NPCs] Updating {len(npcs)} NPCs...")
        
        for npc in npcs:
            # Get scheduled activity for this time
            scheduled = npc.schedule.get(time_of_day, 'idle')
            
            # Determine state from activity
            state_map = {
                'train': EntityState.WORKING,
                'patrol': EntityState.WORKING,
                'setup_shop': EntityState.WORKING,
                'sell': EntityState.WORKING,
                'research': EntityState.WORKING,
                'teach': EntityState.WORKING,
                'tend_crops': EntityState.WORKING,
                'harvest': EntityState.WORKING,
                'tavern': EntityState.SOCIAL,
                'socialize': EntityState.SOCIAL,
                'rest': EntityState.IDLE,
                'wander': EntityState.IDLE,
                'sleep': EntityState.SLEEPING,
            }
            
            new_state = state_map.get(scheduled, EntityState.IDLE)
            
            # Update if changed
            if npc.state != new_state:
                old_state = npc.state
                self.town_manager.update_npc_state(npc.id, new_state, scheduled)
                
                # Log significant changes
                if new_state in [EntityState.SOCIAL, EntityState.SLEEPING]:
                    self._log_event(
                        'npc_state_change',
                        f"{npc.name} went from {old_state.value} to {new_state.value}"
                    )
    
    def _process_interactions(self):
        """Process NPC interactions."""
        npcs = self.town_manager.get_all_npcs()
        
        # Find NPCs that are social
        social_npcs = [n for n in npcs if n.state == EntityState.SOCIAL]
        
        if len(social_npcs) >= 2:
            # Pick two random social NPCs to interact
            npc1 = random.choice(social_npcs)
            npc2 = random.choice([n for n in social_npcs if n.id != npc1.id])
            
            if npc2:
                result = self.town_manager.calculate_interaction(npc1.id, npc2.id)
                
                self._log_event(
                    'npc_interaction',
                    f"{result['npc1']} and {result['npc2']} interacted: {result['outcome']} "
                    f"(compatibility: {result['compatibility']:.2f})"
                )
                
                print(f"  [Interaction] {result['npc1']}  {result['npc2']}: "
                      f"{result['outcome']} ({result['compatibility']:.2f})")
    
    # 
    # Event Logging
    # 
    
    def _log_event(self, event_type: str, description: str, data: Dict = None):
        """Log a simulation event."""
        event = {
            'timestamp': datetime.now().isoformat(),
            'sim_time': self.simulation_time.copy(),
            'type': event_type,
            'description': description,
            'data': data or {}
        }
        
        self.event_log.append(event)
        
        # Keep only last 100 events
        if len(self.event_log) > 100:
            self.event_log = self.event_log[-100:]
    
    def _log_simulation_step(self):
        """Log the current simulation step."""
        npcs = self.town_manager.get_all_npcs()
        
        # Count states
        states = {}
        for npc in npcs:
            state = npc.state.value
            states[state] = states.get(state, 0) + 1
        
        self._log_event(
            'simulation_step',
            f"Day {self.simulation_time['day']}, {self.simulation_time['hour']:02d}:00 - "
            f"{len(npcs)} NPCs active",
            {'npc_states': states}
        )
    
    # 
    # State Persistence
    # 
    
    def _save_simulation_state(self):
        """Save complete simulation state."""
        state = {
            'simulation_time': self.simulation_time,
            'town': self.current_town.to_dict() if self.current_town else None,
            'event_log': self.event_log[-50:],  # Last 50 events
            'saved_at': datetime.now().isoformat()
        }
        
        state_file = self.state_dir / 'simulation_state.json'
        state_file.write_text(json.dumps(state, indent=2))
        
        print(f"\n[Save] Simulation state saved to {state_file}")
    
    def _load_simulation_state(self) -> bool:
        """Load simulation state from file."""
        state_file = self.state_dir / 'simulation_state.json'
        
        if not state_file.exists():
            return False
        
        try:
            data = json.loads(state_file.read_text())
            
            self.simulation_time = data.get('simulation_time', self.simulation_time)
            self.event_log = data.get('event_log', [])
            
            # Town would need to be reconstructed
            print(f"[Load] Loaded simulation state from {state_file}")
            return True
        except Exception as e:
            print(f"[Load] Failed to load state: {e}")
            return False
    
    # 
    # Status & Reporting
    # 
    
    def get_status(self) -> Dict[str, Any]:
        """Get current simulation status."""
        npcs = self.town_manager.get_all_npcs()
        
        states = {}
        for npc in npcs:
            state = npc.state.value
            states[state] = states.get(state, 0) + 1
        
        return {
            'sim_time': self.simulation_time,
            'town': self.current_town.name if self.current_town else None,
            'npc_count': len(npcs),
            'npc_states': states,
            'building_count': len(self.current_town.buildings) if self.current_town else 0,
            'events_logged': len(self.event_log)
        }
    
    def print_status(self):
        """Print current simulation status."""
        status = self.get_status()
        
        print("\n" + "=" * 60)
        print("SIMULATION STATUS")
        print("=" * 60)
        print(f"Town: {status['town']}")
        print(f"Time: Day {status['sim_time']['day']}, "
              f"{status['sim_time']['hour']:02d}:{status['sim_time']['minute']:02d}")
        print(f"Population: {status['npc_count']} NPCs")
        print(f"Buildings: {status['building_count']}")
        print(f"Events Logged: {status['events_logged']}")
        print("\nNPC States:")
        for state, count in status['npc_states'].items():
            print(f"  {state}: {count}")
        print("=" * 60)


# 
# Test/Demo
# 

if __name__ == '__main__':
    import random
    
    print("=" * 60)
    print("LIVING TOWN SIMULATION - TEST RUN")
    print("=" * 60)
    
    # Create simulation
    sim = LivingTownSimulation()
    
    # Initialize world
    sim.initialize_world(
        town_name="Echo's Rest",
        npc_count=8,
        building_count=6
    )
    
    # Show initial status
    sim.print_status()
    
    # Run simulation steps
    print("\n" + "=" * 60)
    print("RUNNING SIMULATION (4 time steps)")
    print("=" * 60)
    
    for step in range(4):
        sim.run_simulation_step(minutes=90)  # 1.5 hour steps
        time.sleep(0.5)  # Brief pause for readability
    
    # Final status
    sim.print_status()
    
    # Show recent events
    print("\n" + "=" * 60)
    print("RECENT EVENTS")
    print("=" * 60)
    
    for event in sim.event_log[-10:]:
        print(f"  [{event['sim_time']['day']}d {event['sim_time']['hour']:02d}:00] "
              f"{event['type']}: {event['description']}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
