"""
World State - Central Repository for All Game Data

Single source of truth for all 6 layers:
- Characters
- Items (inventory + equipment)
- NPCs
- Structures
- Factions
- Cosmic (galaxies, systems, worlds)

All entities reference each other by ID only.
Material/Materia is narrative flavor (no mechanical enforcement).
Level gating prevents using items above character level.
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path


# ────────────────────────────────────────────────
# World State
# ────────────────────────────────────────────────

@dataclass
class WorldState:
    """
    Complete world state containing all game data.
    
    Saved/loaded as single JSON file.
    """
    # Metadata
    name: str = "Unnamed World"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_played: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"
    
    # Layer 1: Characters
    characters: Dict[str, Any] = field(default_factory=dict)
    active_character_id: Optional[str] = None
    
    # Layer 2: Items
    items: Dict[str, Any] = field(default_factory=dict)
    
    # Layer 3: NPCs
    npcs: Dict[str, Any] = field(default_factory=dict)
    
    # Layer 4: Structures
    structures: Dict[str, Any] = field(default_factory=dict)
    
    # Layer 5: Factions
    factions: Dict[str, Any] = field(default_factory=dict)
    
    # Layer 6: Cosmic
    galaxies: Dict[str, Any] = field(default_factory=dict)
    
    # Time tracking (layered turns)
    time: Dict[str, int] = field(default_factory=lambda: {
        'hour': 0,
        'day': 0,
        'week': 0,
        'month': 0,
        'year': 0,
        'decade': 0,
    })
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WorldState':
        """Create from dictionary (loaded JSON)."""
        return cls(**data)
    
    def get_active_character(self) -> Optional[Dict]:
        """Get currently active character."""
        if self.active_character_id:
            return self.characters.get(self.active_character_id)
        return None
    
    def set_active_character(self, char_id: str) -> bool:
        """Set active character."""
        if char_id in self.characters:
            self.active_character_id = char_id
            return True
        return False
    
    def add_character(self, char_data: Dict) -> str:
        """Add character to world."""
        char_id = f"char_{len(self.characters) + 1:03d}"
        char_data['id'] = char_id
        char_data['inventory'] = char_data.get('inventory', [])
        char_data['equipment'] = char_data.get('equipment', {
            'Head': None,
            'Body': None,
            'Hands': None,
            'Legs': None,
            'Feet': None,
            'Other': None,
            'Weapon': None,
        })
        self.characters[char_id] = char_data
        
        # Set as active if first character
        if not self.active_character_id:
            self.active_character_id = char_id
        
        return char_id
    
    def add_item(self, item_data: Dict) -> str:
        """Add item to world."""
        item_id = f"item_{len(self.items) + 1:04d}"
        item_data['id'] = item_id
        self.items[item_id] = item_data
        return item_id
    
    def give_item_to_character(self, char_id: str, item_id: str) -> bool:
        """Give item to character's inventory."""
        if char_id not in self.characters:
            return False
        if item_id not in self.items:
            return False
        
        char = self.characters[char_id]
        if 'inventory' not in char:
            char['inventory'] = []
        
        # Check if item already in inventory
        if item_id in char['inventory']:
            return False
        
        char['inventory'].append(item_id)
        return True
    
    def equip_item(self, char_id: str, item_id: str, slot: str) -> bool:
        """
        Equip item to character slot.
        
        Level gating: Can't equip items above character level.
        """
        if char_id not in self.characters:
            return False
        if item_id not in self.items:
            return False
        
        char = self.characters[char_id]
        item = self.items[item_id]
        
        # Valid slots
        valid_slots = ['Head', 'Body', 'Hands', 'Legs', 'Feet', 'Other', 'Weapon']
        if slot not in valid_slots:
            return False
        
        # Level gating (can't equip above character level)
        char_level = char.get('level', 1)
        item_level = item.get('level', 0)
        if item_level > char_level:
            return False  # Level too high
        
        # Remove from inventory if there
        if 'inventory' in char and item_id in char['inventory']:
            char['inventory'].remove(item_id)
        
        # Unequip current item in slot (return to inventory)
        current_equipped = char.get('equipment', {}).get(slot)
        if current_equipped:
            if 'inventory' not in char:
                char['inventory'] = []
            char['inventory'].append(current_equipped)
        
        # Equip new item
        if 'equipment' not in char:
            char['equipment'] = {}
        char['equipment'][slot] = item_id
        
        return True
    
    def unequip_item(self, char_id: str, slot: str) -> bool:
        """Unequip item from slot, return to inventory."""
        if char_id not in self.characters:
            return False
        
        char = self.characters[char_id]
        if 'equipment' not in char:
            return False
        
        equipped_id = char['equipment'].get(slot)
        if not equipped_id:
            return False
        
        # Remove from equipment
        char['equipment'][slot] = None
        
        # Add to inventory
        if 'inventory' not in char:
            char['inventory'] = []
        char['inventory'].append(equipped_id)
        
        return True
    
    def get_character_inventory(self, char_id: str) -> List[Dict]:
        """Get full item data for character's inventory."""
        if char_id not in self.characters:
            return []
        
        char = self.characters[char_id]
        inventory_ids = char.get('inventory', [])
        
        return [
            self.items[item_id] 
            for item_id in inventory_ids 
            if item_id in self.items
        ]
    
    def get_character_equipment(self, char_id: str) -> Dict[str, Optional[Dict]]:
        """Get full item data for character's equipment."""
        if char_id not in self.characters:
            return {}
        
        char = self.characters[char_id]
        equipment = char.get('equipment', {})
        
        result = {}
        for slot, item_id in equipment.items():
            if item_id and item_id in self.items:
                result[slot] = self.items[item_id]
            else:
                result[slot] = None
        
        return result
    
    def advance_time(self, hours: int = 0):
        """Advance world time."""
        self.time['hour'] += hours
        
        # Roll up time units
        while self.time['hour'] >= 24:
            self.time['hour'] -= 24
            self.time['day'] += 1
        
        while self.time['day'] >= 7:
            self.time['day'] -= 7
            self.time['week'] += 1
        
        while self.time['week'] >= 4:
            self.time['week'] -= 4
            self.time['month'] += 1
        
        while self.time['month'] >= 12:
            self.time['month'] -= 12
            self.time['year'] += 1
        
        while self.time['year'] >= 10:
            self.time['year'] -= 10
            self.time['decade'] += 1
        
        self.last_played = datetime.now().isoformat()


# ────────────────────────────────────────────────
# World Manager (Singleton)
# ────────────────────────────────────────────────

class WorldManager:
    """
    Manages world state with save/load functionality.
    
    Singleton pattern - only one active world at a time.
    """
    
    _instance = None
    _current_world: Optional[WorldState] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def world(self) -> Optional[WorldState]:
        """Get current world."""
        return self._current_world
    
    def create_world(self, name: str) -> WorldState:
        """Create new world."""
        self._current_world = WorldState(name=name)
        return self._current_world
    
    def load_world(self, save_path: str) -> bool:
        """Load world from save file."""
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._current_world = WorldState.from_dict(data)
            return True
        except Exception as e:
            print(f"Error loading world: {e}")
            return False
    
    def save_world(self, save_path: str) -> bool:
        """Save current world to file."""
        if not self._current_world:
            return False
        
        try:
            # Ensure directory exists
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self._current_world.to_dict(), f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving world: {e}")
            return False
    
    def delete_world(self, save_path: str) -> bool:
        """Delete world save file."""
        try:
            path = Path(save_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting world: {e}")
            return False
    
    def list_worlds(self, saves_dir: str) -> List[Dict]:
        """List all saved worlds."""
        saves_path = Path(saves_dir)
        if not saves_path.exists():
            return []
        
        worlds = []
        for save_file in saves_path.glob('world_*.json'):
            try:
                with open(save_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                worlds.append({
                    'name': data.get('name', 'Unknown'),
                    'filename': save_file.name,
                    'path': str(save_file),
                    'created_at': data.get('created_at', 'Unknown'),
                    'last_played': data.get('last_played', 'Unknown'),
                    'characters': len(data.get('characters', {})),
                })
            except Exception as e:
                print(f"Error reading {save_file}: {e}")
        
        return sorted(worlds, key=lambda w: w['last_played'], reverse=True)
    
    def clear_world(self):
        """Clear current world from memory."""
        self._current_world = None


# ────────────────────────────────────────────────
# Test
# ────────────────────────────────────────────────

if __name__ == '__main__':
    print("Testing World State System")
    print("=" * 60)
    
    # Create world manager
    manager = WorldManager()
    
    # Create new world
    print("\n1. Creating new world...")
    world = manager.create_world("Test World")
    print(f"   World: {world.name}")
    
    # Add character
    print("\n2. Adding character...")
    char_data = {
        'name': 'Test Hero',
        'level': 10,
        'material': 'Human',
        'materia': 'Warrior',
    }
    char_id = world.add_character(char_data)
    print(f"   Character ID: {char_id}")
    print(f"   Active: {world.active_character_id}")
    
    # Add items
    print("\n3. Adding items...")
    item1 = {'name': 'Iron Sword', 'level': 5, 'type': 'Weapon'}
    item2 = {'name': 'Steel Armor', 'level': 10, 'type': 'Armor'}
    item3 = {'name': 'Dragon Blade', 'level': 50, 'type': 'Weapon'}  # Too high level
    
    item1_id = world.add_item(item1)
    item2_id = world.add_item(item2)
    item3_id = world.add_item(item3)
    
    print(f"   Items: {item1_id}, {item2_id}, {item3_id}")
    
    # Give items to character
    print("\n4. Giving items to character...")
    world.give_item_to_character(char_id, item1_id)
    world.give_item_to_character(char_id, item2_id)
    world.give_item_to_character(char_id, item3_id)
    
    inventory = world.get_character_inventory(char_id)
    print(f"   Inventory ({len(inventory)} items):")
    for item in inventory:
        print(f"      - {item['name']} (Lvl {item['level']})")
    
    # Equip items
    print("\n5. Equipping items...")
    success = world.equip_item(char_id, item1_id, 'Weapon')
    print(f"   Equip Iron Sword: {success}")
    
    success = world.equip_item(char_id, item2_id, 'Body')
    print(f"   Equip Steel Armor: {success}")
    
    # Try to equip too-high level item
    success = world.equip_item(char_id, item3_id, 'Weapon')
    print(f"   Equip Dragon Blade (Lvl 50, char is Lvl 10): {success} (should be False)")
    
    # Show equipment
    print("\n6. Character Equipment:")
    equipment = world.get_character_equipment(char_id)
    for slot, item in equipment.items():
        if item:
            print(f"   {slot}: {item['name']} (Lvl {item['level']})")
        else:
            print(f"   {slot}: (empty)")
    
    # Save world
    print("\n7. Saving world...")
    save_path = "D:\\Ollama\\OpenClaw\\workspace\\living-town\\saves\\world_test.json"
    success = manager.save_world(save_path)
    print(f"   Save successful: {success}")
    print(f"   Saved to: {save_path}")
    
    # Clear and reload
    print("\n8. Clearing and reloading world...")
    manager.clear_world()
    manager.load_world(save_path)
    
    reloaded = manager.world
    print(f"   Reloaded world: {reloaded.name}")
    print(f"   Characters: {len(reloaded.characters)}")
    print(f"   Items: {len(reloaded.items)}")
    
    # List worlds
    print("\n9. Listing worlds...")
    saves_dir = "D:\\Ollama\\OpenClaw\\workspace\\living-town\\saves"
    worlds = manager.list_worlds(saves_dir)
    for w in worlds:
        print(f"   - {w['name']} ({w['characters']} chars, last: {w['last_played'][:10]})")
    
    print("\n" + "=" * 60)
    print("World State System Test Complete!")
