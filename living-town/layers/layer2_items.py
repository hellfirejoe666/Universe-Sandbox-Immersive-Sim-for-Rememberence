"""
Layer 2: Items (Weapons, Armor, Equipment)

All items are forged from:
- Material (Species) - Physical substance
- Materia (Type) - Energetic essence
- Runes (optional) - Additional enchantments

Philosophy: Every item = Material + Materia combination
36 Materials × 24 Materia = 864 base combinations per item type
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import sys

# Import data loader for canonical data
sys.path.insert(0, str(Path(__file__).parent.parent))
from data_loader import get_loader


# ────────────────────────────────────────────────
# Item Types
# ────────────────────────────────────────────────

class ItemType(Enum):
    WEAPON = "Weapon"
    ARMOR = "Armor"
    ACCESSORY = "Accessory"
    CONSUMABLE = "Consumable"
    MATERIAL = "Material"
    QUEST = "Quest Item"


class WeaponType(Enum):
    SWORD = "Sword"
    AXE = "Axe"
    SPEAR = "Spear"
    BOW = "Bow"
    STAFF = "Staff"
    DAGGER = "Dagger"
    HAMMER = "Hammer"
    WHIP = "Whip"
    FISTS = "Fists"
    ORB = "Orb"


class ArmorSlot(Enum):
    HEAD = "Head"
    BODY = "Body"
    HANDS = "Hands"
    LEGS = "Legs"
    FEET = "Feet"
    OTHER = "Other"


class Rarity(Enum):
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    EPIC = "Epic"
    LEGENDARY = "Legendary"
    TRANSCENDENT = "Transcendent"


# ────────────────────────────────────────────────
# Data Classes
# ────────────────────────────────────────────────

@dataclass
class Item:
    """
    Base item class.
    
    Every item is forged from Material + Materia.
    """
    id: str
    name: str
    item_type: ItemType
    material: str  # Species
    materia: str   # Type
    level: int = 1
    rarity: Rarity = Rarity.COMMON
    
    # Stats
    stats: Dict[str, int] = field(default_factory=dict)
    
    # Runes (0-5 slots)
    runes: List[str] = field(default_factory=list)
    
    # Traits from Material/Materia
    traits: List[str] = field(default_factory=list)
    
    # Value
    value: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'type': self.item_type.value,
            'material': self.material,
            'materia': self.materia,
            'level': self.level,
            'rarity': self.rarity.value,
            'stats': self.stats,
            'runes': self.runes,
            'traits': self.traits,
            'value': self.value,
        }


@dataclass
class Weapon(Item):
    """Weapon item."""
    weapon_type: WeaponType = WeaponType.SWORD
    damage: int = 0
    accuracy: int = 0
    speed: int = 0
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data['weapon_type'] = self.weapon_type.value
        data['damage'] = self.damage
        data['accuracy'] = self.accuracy
        data['speed'] = self.speed
        return data


@dataclass
class Armor(Item):
    """Armor item."""
    slot: ArmorSlot = ArmorSlot.BODY
    defense: int = 0
    resistance: int = 0
    weight: int = 0
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data['slot'] = self.slot.value
        data['defense'] = self.defense
        data['resistance'] = self.resistance
        data['weight'] = self.weight
        return data


# ────────────────────────────────────────────────
# Item Generator
# ────────────────────────────────────────────────

class ItemGenerator:
    """
    Procedural item generator using Material/Materia ontology.
    
    All items = Material (Species) + Materia (Type) + optional Runes
    """
    
    def __init__(self):
        self.loader = get_loader()
        self.item_counter = 0
        
        # Weapon name components
        self.material_prefixes = {
            'Drakian': ['Dragon', 'Drake', 'Scale'],
            'Banshee': ['Ghost', 'Spectral', 'Wailing'],
            'Elf': ['Crystal', 'Silver', 'Moon'],
            'Orc': ['Iron', 'Brutal', 'War'],
            'Mimic': ['Shifting', 'Adaptive', 'Living'],
        }
        
        self.materia_suffixes = {
            'Thunder': ['Lightning', 'Storm', 'Shock'],
            'Warrior': ['Battle', 'Strike', 'Blade'],
            'Pyro': ['Flame', 'Ember', 'Inferno'],
            'Aqua': ['Tide', 'Wave', 'Frost'],
            'Beast': ['Feral', 'Predator', 'Hunt'],
            'Ghost': ['Phantom', 'Soul', 'Ethereal'],
        }
    
    def generate_id(self) -> str:
        self.item_counter += 1
        return f"item_{self.item_counter:04d}"
    
    def generate_item(self, item_type: ItemType = None,
                     material: str = None,
                     materia: str = None,
                     level: int = 1,
                     rarity: Rarity = None) -> Item:
        """
        Generate an item from Material + Materia.
        
        Args:
            item_type: Type of item (Weapon, Armor, etc.)
            material: Species (physical substance) - random if None
            materia: Type (energetic essence) - random if None
            level: Item level
            rarity: Rarity tier
        """
        # Get all canonical options
        species_list = list(self.loader.get_all_species().keys())
        types_list = list(self.loader.get_all_types().keys())
        
        # Select or use provided
        if material is None:
            material = random.choice(species_list)
        if materia is None:
            materia = random.choice(types_list)
        if item_type is None:
            item_type = random.choice([ItemType.WEAPON, ItemType.ARMOR, ItemType.ACCESSORY])
        if rarity is None:
            rarity = self._roll_rarity()
        
        # Get canonical data
        material_data = self.loader.get_species(material)
        materia_data = self.loader.get_type(materia)
        
        # Generate base item
        if item_type == ItemType.WEAPON:
            item = self._generate_weapon(material, materia, level, rarity)
        elif item_type == ItemType.ARMOR:
            item = self._generate_armor(material, materia, level, rarity)
        else:
            item = self._generate_accessory(material, materia, level, rarity)
        
        # Add traits from Material (Species)
        if material_data and isinstance(material_data, dict):
            traits = material_data.get('traits', {})
            active_traits = traits.get('active', [])
            if active_traits:
                item.traits.append(f"Material ({material}): {random.choice(active_traits)}")
        
        # Add traits from Materia (Type)
        if materia_data and isinstance(materia_data, dict):
            traits = materia_data.get('traits', {})
            active_traits = traits.get('active', [])
            if active_traits:
                item.traits.append(f"Materia ({materia}): {random.choice(active_traits)}")
        
        # Generate name from Material + Materia
        item.name = self._generate_name(material, materia, item_type)
        
        # Calculate value
        item.value = self._calculate_value(item, rarity, level)
        
        return item
    
    def _generate_weapon(self, material: str, materia: str, 
                        level: int, rarity: Rarity) -> Weapon:
        """Generate a weapon."""
        weapon_type = random.choice(list(WeaponType))
        
        # Scale by level and rarity
        rarity_mult = {
            Rarity.COMMON: 1.0,
            Rarity.UNCOMMON: 1.3,
            Rarity.RARE: 1.6,
            Rarity.EPIC: 2.0,
            Rarity.LEGENDARY: 2.5,
            Rarity.TRANSCENDENT: 3.0,
        }.get(rarity, 1.0)
        
        level_mult = (level // 10) + 1
        
        # Base stats by weapon type
        base_damage = {
            WeaponType.SWORD: 10,
            WeaponType.AXE: 12,
            WeaponType.SPEAR: 9,
            WeaponType.BOW: 8,
            WeaponType.STAFF: 7,
            WeaponType.DAGGER: 6,
            WeaponType.HAMMER: 14,
            WeaponType.WHIP: 5,
            WeaponType.FISTS: 4,
            WeaponType.ORB: 8,
        }.get(weapon_type, 10)
        
        damage = int(base_damage * rarity_mult * level_mult)
        accuracy = int((50 + random.randint(0, 30)) * rarity_mult)
        speed = int((1 + random.randint(0, 4)) * rarity_mult)
        
        return Weapon(
            id=self.generate_id(),
            name="Unnamed Weapon",
            item_type=ItemType.WEAPON,
            material=material,
            materia=materia,
            level=level,
            rarity=rarity,
            weapon_type=weapon_type,
            damage=damage,
            accuracy=accuracy,
            speed=speed,
        )
    
    def _generate_armor(self, material: str, materia: str,
                       level: int, rarity: Rarity) -> Armor:
        """Generate armor."""
        slot = random.choice(list(ArmorSlot))
        
        rarity_mult = {
            Rarity.COMMON: 1.0,
            Rarity.UNCOMMON: 1.3,
            Rarity.RARE: 1.6,
            Rarity.EPIC: 2.0,
            Rarity.LEGENDARY: 2.5,
            Rarity.TRANSCENDENT: 3.0,
        }.get(rarity, 1.0)
        
        level_mult = (level // 10) + 1
        
        # Base stats by slot
        base_defense = {
            ArmorSlot.HEAD: 3,
            ArmorSlot.BODY: 8,
            ArmorSlot.HANDS: 2,
            ArmorSlot.LEGS: 5,
            ArmorSlot.FEET: 3,
            ArmorSlot.OTHER: 4,
        }.get(slot, 5)
        
        defense = int(base_defense * rarity_mult * level_mult)
        resistance = int((2 + random.randint(0, 5)) * rarity_mult)
        weight = int((5 + random.randint(0, 10)) * rarity_mult)
        
        return Armor(
            id=self.generate_id(),
            name="Unnamed Armor",
            item_type=ItemType.ARMOR,
            material=material,
            materia=materia,
            level=level,
            rarity=rarity,
            slot=slot,
            defense=defense,
            resistance=resistance,
            weight=weight,
        )
    
    def _generate_accessory(self, material: str, materia: str,
                           level: int, rarity: Rarity) -> Item:
        """Generate accessory."""
        # Accessories have special effects instead of combat stats
        stats = {
            'power': int((5 + random.randint(0, 10)) * ((level // 10) + 1)),
        }
        
        return Item(
            id=self.generate_id(),
            name="Unnamed Accessory",
            item_type=ItemType.ACCESSORY,
            material=material,
            materia=materia,
            level=level,
            rarity=rarity,
            stats=stats,
        )
    
    def _generate_name(self, material: str, materia: str, 
                       item_type: Item) -> str:
        """Generate item name from Material + Materia."""
        # Get material prefix
        mat_prefixes = self.material_prefixes.get(material, [material[:4]])
        prefix = random.choice(mat_prefixes)
        
        # Get materia suffix
        mat_suffixes = self.materia_suffixes.get(materia, [materia[:4]])
        suffix = random.choice(mat_suffixes)
        
        # Item type name
        type_names = {
            ItemType.WEAPON: ['Blade', 'Weapon', 'Arm'],
            ItemType.ARMOR: ['Guard', 'Armor', 'Shell'],
            ItemType.ACCESSORY: ['Charm', 'Talisman', 'Ring'],
        }
        type_name = random.choice(type_names.get(item_type, ['Item']))
        
        return f"{prefix} {suffix} {type_name}"
    
    def _roll_rarity(self) -> Rarity:
        """Roll for item rarity."""
        roll = random.random()
        if roll < 0.50:
            return Rarity.COMMON
        elif roll < 0.75:
            return Rarity.UNCOMMON
        elif roll < 0.90:
            return Rarity.RARE
        elif roll < 0.96:
            return Rarity.EPIC
        elif roll < 0.99:
            return Rarity.LEGENDARY
        else:
            return Rarity.TRANSCENDENT
    
    def _calculate_value(self, item: Item, rarity: Rarity, level: int) -> int:
        """Calculate item value."""
        base_value = 10
        
        rarity_mult = {
            Rarity.COMMON: 1,
            Rarity.UNCOMMON: 3,
            Rarity.RARE: 10,
            Rarity.EPIC: 30,
            Rarity.LEGENDARY: 100,
            Rarity.TRANSCENDENT: 300,
        }.get(rarity, 1)
        
        level_mult = (level // 10) + 1
        
        # Stats contribution
        stats_value = sum(item.stats.values()) if item.stats else 0
        if isinstance(item, Weapon):
            stats_value = item.damage + item.accuracy + item.speed
        elif isinstance(item, Armor):
            stats_value = item.defense + item.resistance
        
        return base_value * rarity_mult * level_mult + (stats_value * 2)
    
    def add_runes(self, item: Item, num_runes: int = None) -> Item:
        """Add runes to an item (0-5 slots)."""
        if num_runes is None:
            num_runes = random.randint(0, 5)
        
        runes_data = self.loader.get_all_runes()
        rune_list = list(runes_data.keys())
        
        selected = random.sample(rune_list, min(num_runes, len(rune_list)))
        item.runes = selected
        
        # Add rune effects to traits
        for rune in selected:
            rune_data = runes_data.get(rune, {})
            effect = rune_data.get('effect', f'{rune} enchantment')
            item.traits.append(f"Rune ({rune}): {effect}")
        
        return item


# ────────────────────────────────────────────────
# Test
# ────────────────────────────────────────────────

if __name__ == '__main__':
    print("Testing Layer 2: Items (Material/Materia Ontology)")
    print("=" * 70)
    
    gen = ItemGenerator()
    
    # Generate weapons with explicit Material/Materia
    print("\nWEAPONS (Material + Materia):")
    print("-" * 70)
    
    test_cases = [
        ('Drakian', 'Thunder'),
        ('Banshee', 'Ghost'),
        ('Elf', 'Crystal'),
        ('Orc', 'Warrior'),
    ]
    
    for material, materia in test_cases:
        weapon = gen.generate_item(
            item_type=ItemType.WEAPON,
            material=material,
            materia=materia,
            level=50,
            rarity=Rarity.RARE
        )
        weapon = gen.add_runes(weapon, num_runes=random.randint(1, 3))
        
        print(f"\n  {weapon.name}")
        print(f"    Material: {weapon.material} (Species)")
        print(f"    Materia: {weapon.materia} (Type)")
        print(f"    Type: {weapon.weapon_type.value}")
        print(f"    Level: {weapon.level} | Rarity: {weapon.rarity.value}")
        print(f"    Stats: DMG={weapon.damage}, ACC={weapon.accuracy}, SPD={weapon.speed}")
        print(f"    Runes: {', '.join(weapon.runes) if weapon.runes else 'None'}")
        print(f"    Traits:")
        for trait in weapon.traits:
            print(f"      - {trait}")
        print(f"    Value: ${weapon.value}")
    
    # Generate armor
    print("\n\nARMOR (Material + Materia):")
    print("-" * 70)
    
    for material, materia in [('Mimic', 'Beast'), ('Avious', 'Pyro')]:
        armor = gen.generate_item(
            item_type=ItemType.ARMOR,
            material=material,
            materia=materia,
            level=50,
            rarity=Rarity.EPIC
        )
        
        print(f"\n  {armor.name}")
        print(f"    Material: {armor.material} (Species)")
        print(f"    Materia: {armor.materia} (Type)")
        print(f"    Slot: {armor.slot.value}")
        print(f"    Level: {armor.level} | Rarity: {armor.rarity.value}")
        print(f"    Stats: DEF={armor.defense}, RES={armor.resistance}, WGT={armor.weight}")
        print(f"    Traits:")
        for trait in armor.traits:
            print(f"      - {trait}")
        print(f"    Value: ${armor.value}")
    
    # Random generation
    print("\n\nRANDOM ITEMS (864 possible combinations):")
    print("-" * 70)
    
    for i in range(3):
        item = gen.generate_item(level=random.randint(1, 100))
        print(f"\n  {i+1}. {item.name}")
        print(f"     {item.material} + {item.materia} = {item.item_type.value}")
        print(f"     Level {item.level} | {item.rarity.value} | ${item.value}")
    
    print("\n" + "=" * 70)
    print("All items follow Material (Species) + Materia (Type) ontology!")
