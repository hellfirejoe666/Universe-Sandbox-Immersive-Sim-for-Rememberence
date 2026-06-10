"""
Save System with Narrative Persistence

Key principle: Narratives generated once, saved forever.
AI only called for new discoveries.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


# ────────────────────────────────────────────────
# Save Data Structure
# ────────────────────────────────────────────────

class SaveData:
    """Complete game save with narrative persistence."""
    
    def __init__(self, player_id: str = "player_001"):
        self.player_id = player_id
        self.playthrough_start = datetime.now().isoformat()
        self.current_week = 0
        
        # Simulation state (from layers 1-6)
        self.npcs: Dict[str, Any] = {}
        self.factions: Dict[str, Any] = {}
        self.towns: Dict[str, Any] = {}
        self.worlds: Dict[str, Any] = {}
        self.systems: Dict[str, Any] = {}
        
        # Narrative persistence (Layer 0)
        self.narratives: Dict[str, Dict] = {}  # entity_id → narrative data
        self.discovered_entities: List[str] = []  # IDs player has seen
        self.witnessed_events: List[Dict] = []  # Events with narratives
        
        # Metadata
        self.last_save = datetime.now().isoformat()
        self.total_play_time = 0  # seconds
    
    def add_narrative(self, entity_id: str, entity_type: str, 
                     text: str, context: Dict[str, Any]):
        """
        Save a generated narrative.
        
        Args:
            entity_id: ID of entity (npc_001, faction_002, etc.)
            entity_type: Type (npc, faction, town, system, event)
            text: AI-generated narrative text
            context: Generation context (week, location, etc.)
        """
        self.narratives[entity_id] = {
            'entity_type': entity_type,
            'text': text,
            'generated_at': datetime.now().isoformat(),
            'context': context,
            'view_count': 0  # Track how many times player viewed this
        }
        
        # Mark as discovered
        if entity_id not in self.discovered_entities:
            self.discovered_entities.append(entity_id)
        
        self.last_save = datetime.now().isoformat()
    
    def get_narrative(self, entity_id: str) -> Optional[Dict]:
        """Retrieve saved narrative."""
        narrative = self.narratives.get(entity_id)
        if narrative:
            narrative['view_count'] = narrative.get('view_count', 0) + 1
        return narrative
    
    def has_narrative(self, entity_id: str) -> bool:
        """Check if narrative exists."""
        return entity_id in self.narratives
    
    def add_event(self, event: Dict, narrative: str = None):
        """Add witnessed event with optional narrative."""
        event_record = {
            'week': self.current_week,
            'timestamp': datetime.now().isoformat(),
            **event
        }
        
        if narrative:
            event_record['narrative'] = narrative
            event_record['narrative_id'] = f"evt_{len(self.witnessed_events):03d}"
        
        self.witnessed_events.append(event_record)
        
        # Keep list manageable
        if len(self.witnessed_events) > 1000:
            self.witnessed_events = self.witnessed_events[-1000:]
    
    def to_dict(self) -> Dict:
        """Convert to serializable dict."""
        return {
            'player_id': self.player_id,
            'playthrough_start': self.playthrough_start,
            'current_week': self.current_week,
            'npcs': self.npcs,
            'factions': self.factions,
            'towns': self.towns,
            'worlds': self.worlds,
            'systems': self.systems,
            'narratives': self.narratives,
            'discovered_entities': self.discovered_entities,
            'witnessed_events': self.witnessed_events,
            'last_save': self.last_save,
            'total_play_time': self.total_play_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SaveData':
        """Load from dict."""
        save = cls()
        save.player_id = data.get('player_id', 'player_001')
        save.playthrough_start = data.get('playthrough_start', '')
        save.current_week = data.get('current_week', 0)
        save.npcs = data.get('npcs', {})
        save.factions = data.get('factions', {})
        save.towns = data.get('towns', {})
        save.worlds = data.get('worlds', {})
        save.systems = data.get('systems', {})
        save.narratives = data.get('narratives', {})
        save.discovered_entities = data.get('discovered_entities', [])
        save.witnessed_events = data.get('witnessed_events', [])
        save.last_save = data.get('last_save', '')
        save.total_play_time = data.get('total_play_time', 0)
        return save
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SaveData':
        """Deserialize from JSON."""
        data = json.loads(json_str)
        return cls.from_dict(data)


# ────────────────────────────────────────────────
# Save Manager
# ────────────────────────────────────────────────

class SaveManager:
    """Manages save/load operations."""
    
    def __init__(self, save_dir: str = None):
        if save_dir is None:
            save_dir = str(Path(__file__).parent / 'saves')
        
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_save: Optional[SaveData] = None
    
    def new_game(self, player_id: str = "player_001") -> SaveData:
        """Start new game."""
        self.current_save = SaveData(player_id)
        print(f"[SaveManager] New game started: {player_id}")
        return self.current_save
    
    def save_game(self, filename: str = None) -> str:
        """Save current game to file."""
        if not self.current_save:
            raise ValueError("No active save")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"save_{timestamp}.json"
        
        filepath = self.save_dir / filename
        
        json_str = self.current_save.to_json()
        filepath.write_text(json_str, encoding='utf-8')
        
        print(f"[SaveManager] Game saved: {filepath.name}")
        return filepath.name
    
    def load_game(self, filename: str) -> SaveData:
        """Load game from file."""
        filepath = self.save_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Save not found: {filename}")
        
        json_str = filepath.read_text(encoding='utf-8')
        self.current_save = SaveData.from_json(json_str)
        
        print(f"[SaveManager] Game loaded: {filename}")
        print(f"  Week: {self.current_save.current_week}")
        print(f"  Narratives: {len(self.current_save.narratives)}")
        print(f"  Discovered: {len(self.current_save.discovered_entities)} entities")
        
        return self.current_save
    
    def get_save_files(self) -> List[str]:
        """List available save files."""
        return sorted([f.name for f in self.save_dir.glob('*.json')])


# ────────────────────────────────────────────────
# Test (Fast, DEV_MODE)
# ────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 60)
    print("SAVE SYSTEM TEST (DEV_MODE)")
    print("=" * 60)
    
    # Initialize save manager
    manager = SaveManager()
    
    # Start new game
    print("\n[1/4] Starting new game...")
    save = manager.new_game("test_player")
    save.current_week = 5
    
    # Add some entities
    print("\n[2/4] Adding entities...")
    save.npcs['npc_001'] = {'name': 'Featherwing', 'type': 'Dragon/Scorpio'}
    save.factions['fct_001'] = {'name': 'Crystal Collective'}
    save.towns['twn_001'] = {'name': 'Crystalhaven', 'population': 500}
    
    # Add narratives (simulating AI generation)
    print("\n[3/4] Adding narratives (simulated AI)...")
    save.add_narrative(
        'npc_001', 'npc',
        'Featherwing is a Dragon/Scorpio whose contemplative nature masks fierce loyalty.',
        {'week': 3, 'location': 'Crystalhaven'}
    )
    
    save.add_narrative(
        'fct_001', 'faction',
        'The Crystal Collective operates from shadows, seeking to perfect selective forgetting.',
        {'week': 5, 'action': 'researching'}
    )
    
    # Add witnessed event
    save.add_event(
        {'faction': 'Crystal Collective', 'action': 'discovered technique', 'success': True},
        'In week 5, the Crystal Collective made a breakthrough in memory technique.'
    )
    
    # Save game
    print("\n[4/4] Saving game...")
    filename = manager.save_game("test_save.json")
    
    # Load game
    print("\n" + "=" * 60)
    print("LOAD TEST")
    print("=" * 60)
    
    loaded = manager.load_game(filename)
    
    # Verify narratives
    print("\nVerifying narratives:")
    for entity_id in ['npc_001', 'fct_001']:
        narrative = loaded.get_narrative(entity_id)
        if narrative:
            print(f"  {entity_id}: {narrative['text'][:60]}...")
            print(f"    Views: {narrative['view_count']}")
    
    # Verify events
    print(f"\nWitnessed events: {len(loaded.witnessed_events)}")
    for event in loaded.witnessed_events:
        print(f"  Week {event['week']}: {event.get('narrative', 'No narrative')[:50]}...")
    
    print("\n" + "=" * 60)
    print("SAVE SYSTEM TEST COMPLETE")
    print("=" * 60)
    print(f"Narratives saved: {len(save.narratives)}")
    print(f"Events logged: {len(save.witnessed_events)}")
    print(f"Save file: {filename}")
