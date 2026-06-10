"""
Layer 4: Structures (Buildings, Constructions, Places)

All structures are forged from:
- Material (Species) - Construction substance/physical form
- Materia (Type) - Enchantment/purpose/energetic function
- Runes (optional) - Structural enchantments (0-5 slots)

Philosophy: Every structure = Material body + Materia purpose
36 Materials × 24 Materia = 864 base structure types
Plus size, enchantments, and functions = infinite variety

Examples:
  - Drakian + Thunder = Storm fortress, lightning tower
  - Elf + Crystal = Crystal library, moon temple
  - Orc + Warrior = War camp, battle arena
  - Mimic + Beast = Living menagerie, shifting maze
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import sys

# Import data loader
sys.path.insert(0, str(Path(__file__).parent.parent))
from data_loader import get_loader


# ────────────────────────────────────────────────
# Structure Types
# ────────────────────────────────────────────────

class StructureType(Enum):
    DWELLING = "Dwelling"
    COMMERCIAL = "Commercial"
    MILITARY = "Military"
    RELIGIOUS = "Religious"
    ACADEMIC = "Academic"
    INDUSTRIAL = "Industrial"
    MAGICAL = "Magical"
    GOVERNMENT = "Government"
    MONUMENT = "Monument"
    RUIN = "Ruin"


class StructureSize(Enum):
    HUT = "Hut"
    HOUSE = "House"
    HALL = "Hall"
    TOWER = "Tower"
    FORTRESS = "Fortress"
    COMPLEX = "Complex"
    CITADEL = "Citadel"


class StructureCondition(Enum):
    PRISTINE = "Pristine"
    GOOD = "Good"
    WORN = "Worn"
    DAMAGED = "Damaged"
    RUINED = "Ruined"


# ────────────────────────────────────────────────
# Data Classes
# ────────────────────────────────────────────────

@dataclass
class Structure:
    """
    Base structure class (building, construction, place).
    
    Every structure is forged from:
    - Material (Species) = Physical construction
    - Materia (Type) = Purpose/enchantment
    """
    id: str
    name: str
    material: str  # Species (construction material)
    materia: str   # Type (purpose/enchantment)
    
    # Core identity
    structure_type: StructureType = StructureType.DWELLING
    size: StructureSize = StructureSize.HOUSE
    condition: StructureCondition = StructureCondition.GOOD
    level: int = 1
    
    # Stats (defensive, functional, magical)
    stats: Dict[str, int] = field(default_factory=dict)
    
    # Functions (what happens here)
    functions: List[str] = field(default_factory=list)
    
    # Runes (0-5 structural enchantments)
    runes: List[str] = field(default_factory=list)
    
    # Traits from Material/Materia
    traits: List[str] = field(default_factory=list)
    
    # Occupants
    capacity: int = 0
    current_occupants: int = 0
    
    # Economy
    value: int = 0
    production: Dict[str, int] = field(default_factory=dict)  # resource -> amount/turn
    
    # Location
    coordinates: Tuple[int, int] = (0, 0)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'material': self.material,
            'materia': self.materia,
            'structure_type': self.structure_type.value,
            'size': self.size.value,
            'condition': self.condition.value,
            'level': self.level,
            'stats': self.stats,
            'functions': self.functions,
            'runes': self.runes,
            'traits': self.traits,
            'capacity': self.capacity,
            'current_occupants': self.current_occupants,
            'value': self.value,
            'production': self.production,
            'coordinates': self.coordinates,
        }


# ────────────────────────────────────────────────
# Structure Generator
# ────────────────────────────────────────────────

class StructureGenerator:
    """
    Procedural structure generator using Material/Materia ontology.
    
    Every structure = Material (construction) + Materia (purpose)
    """
    
    def __init__(self):
        self.loader = get_loader()
        self.structure_counter = 0
        
        # Structure name components by Material
        self.material_buildings = {
            'Drakian': ['Keep', 'Spire', 'Nest', 'Aerie', 'Roost'],
            'Banshee': ['Crypt', 'Tomb', 'Shrine', 'Sanctum', 'Vault'],
            'Elf': ['Grove', 'Spire', 'Hall', 'Sanctuary', 'Temple'],
            'Orc': ['Stronghold', 'Barracks', 'Fort', 'Camp', 'Arena'],
            'Mimic': ['Labyrinth', 'Menagerie', 'Shifting Hall', 'Living Structure'],
            'Human': ['House', 'Tower', 'Hall', 'Keep', 'Manor'],
        }
        
        # Structure purposes by Materia
        self.materia_purposes = {
            'Thunder': ['Storm Tower', 'Lightning Rod', 'Storm Barracks'],
            'Warrior': ['War Hall', 'Battle Arena', 'Training Grounds'],
            'Pyro': ['Forge', 'Fire Temple', 'Flame Tower'],
            'Aqua': ['Aqueduct', 'Fountain House', 'Tide Temple'],
            'Beast': ['Menagerie', 'Hunting Lodge', 'Beast Den'],
            'Ghost': ['Crypt', 'Spirit Hall', 'Soul Sanctuary'],
            'Crystal': ['Library', 'Crystal Tower', 'Reflection Hall'],
            'Holy': ['Temple', 'Cathedral', 'Sacred Grove'],
        }
        
        # Functions by structure type
        self.type_functions = {
            StructureType.DWELLING: ['Rest', 'Recovery', 'Storage'],
            StructureType.COMMERCIAL: ['Trade', 'Crafting', 'Services'],
            StructureType.MILITARY: ['Training', 'Defense', 'Storage'],
            StructureType.RELIGIOUS: ['Worship', 'Blessing', 'Ritual'],
            StructureType.ACADEMIC: ['Research', 'Teaching', 'Archive'],
            StructureType.INDUSTRIAL: ['Production', 'Refining', 'Crafting'],
            StructureType.MAGICAL: ['Enchantment', 'Summoning', 'Scrying'],
            StructureType.GOVERNMENT: ['Administration', 'Justice', 'Records'],
            StructureType.MONUMENT: ['Commemoration', 'Inspiration', 'Landmark'],
            StructureType.RUIN: ['Exploration', 'Looting', 'Mystery'],
        }
    
    def generate_id(self) -> str:
        self.structure_counter += 1
        return f"structure_{self.structure_counter:04d}"
    
    def generate_structure(self, material: str = None,
                          materia: str = None,
                          structure_type: StructureType = None,
                          level: int = 1) -> Structure:
        """
        Generate a structure from Material + Materia.
        
        Args:
            material: Species (construction material) - random if None
            materia: Type (purpose/enchantment) - random if None
            structure_type: Type of building - random if None
            level: Structure level
        """
        # Get all canonical options
        species_list = list(self.loader.get_all_species().keys())
        types_list = list(self.loader.get_all_types().keys())
        
        # Select or use provided
        if material is None:
            material = random.choice(species_list)
        if materia is None:
            materia = random.choice(types_list)
        if structure_type is None:
            structure_type = random.choice(list(StructureType))
        
        # Get canonical data
        material_data = self.loader.get_species(material)
        materia_data = self.loader.get_type(materia)
        
        # Generate name from Material + Materia
        name = self._generate_name(material, materia, structure_type)
        
        # Determine size based on level
        size = self._determine_size(level, structure_type)
        
        # Determine condition
        condition = self._roll_condition()
        
        # Calculate stats (Material + Materia + level)
        stats = self._calculate_stats(material_data, materia_data, level, structure_type)
        
        # Generate functions
        functions = self._generate_functions(structure_type, materia)
        
        # Get traits from Material
        traits = []
        if material_data and isinstance(material_data, dict):
            traits_data = material_data.get('traits', {})
            traits.extend(traits_data.get('active', [])[:2])
        
        # Get traits from Materia
        if materia_data and isinstance(materia_data, dict):
            traits_data = materia_data.get('traits', {})
            traits.extend(traits_data.get('active', [])[:2])
        
        # Add structural traits
        traits.extend(self._generate_structural_traits(material, materia))
        
        # Calculate capacity
        capacity = self._calculate_capacity(size, structure_type)
        
        # Calculate value
        value = self._calculate_value(material, materia, level, size, condition)
        
        # Generate production (for industrial/magical structures)
        production = self._generate_production(materia, structure_type, level)
        
        # Create structure
        structure = Structure(
            id=self.generate_id(),
            name=name,
            material=material,
            materia=materia,
            structure_type=structure_type,
            size=size,
            condition=condition,
            level=level,
            stats=stats,
            functions=functions,
            traits=traits,
            capacity=capacity,
            current_occupants=random.randint(0, capacity),
            value=value,
            production=production,
            coordinates=(random.randint(-1000, 1000), random.randint(-1000, 1000)),
        )
        
        return structure
    
    def _generate_name(self, material: str, materia: str,
                       structure_type: StructureType) -> str:
        """Generate structure name from Material + Materia + Type."""
        # Get material building style
        mat_buildings = self.material_buildings.get(material, ['Structure'])
        building = random.choice(mat_buildings)
        
        # Get materia purpose
        mat_purposes = self.materia_purposes.get(materia, ['Hall'])
        purpose = random.choice(mat_purposes)
        
        # Combine or choose one
        if random.random() > 0.5:
            return f"{material} {purpose}"
        else:
            return f"{building} of {materia}"
    
    def _determine_size(self, level: int, structure_type: StructureType) -> StructureSize:
        """Determine structure size based on level and type."""
        # Level thresholds
        if level < 5:
            return random.choice([StructureSize.HUT, StructureSize.HOUSE])
        elif level < 15:
            return random.choice([StructureSize.HOUSE, StructureSize.HALL])
        elif level < 30:
            return random.choice([StructureSize.HALL, StructureSize.TOWER])
        elif level < 50:
            return random.choice([StructureSize.TOWER, StructureSize.FORTRESS])
        elif level < 80:
            return random.choice([StructureSize.FORTRESS, StructureSize.COMPLEX])
        else:
            return random.choice([StructureSize.COMPLEX, StructureSize.CITADEL])
    
    def _roll_condition(self) -> StructureCondition:
        """Roll for structure condition."""
        roll = random.random()
        if roll < 0.15:
            return StructureCondition.RUINED
        elif roll < 0.30:
            return StructureCondition.DAMAGED
        elif roll < 0.50:
            return StructureCondition.WORN
        elif roll < 0.80:
            return StructureCondition.GOOD
        else:
            return StructureCondition.PRISTINE
    
    def _calculate_stats(self, material_data: Dict, materia_data: Dict,
                        level: int, structure_type: StructureType) -> Dict[str, int]:
        """Calculate structure stats."""
        # Base stats by structure type
        base_stats = {
            StructureType.DWELLING: {'DEF': 10, 'HP': 50, 'COMFORT': 5},
            StructureType.COMMERCIAL: {'DEF': 5, 'HP': 40, 'TRADE': 10},
            StructureType.MILITARY: {'DEF': 20, 'HP': 100, 'TRAINING': 10},
            StructureType.RELIGIOUS: {'DEF': 10, 'HP': 60, 'FAITH': 15},
            StructureType.ACADEMIC: {'DEF': 8, 'HP': 50, 'RESEARCH': 15},
            StructureType.INDUSTRIAL: {'DEF': 15, 'HP': 80, 'PRODUCTION': 20},
            StructureType.MAGICAL: {'DEF': 10, 'HP': 50, 'MAGIC': 20},
            StructureType.GOVERNMENT: {'DEF': 15, 'HP': 70, 'ORDER': 10},
            StructureType.MONUMENT: {'DEF': 20, 'HP': 100, 'INSPIRATION': 10},
            StructureType.RUIN: {'DEF': 5, 'HP': 30, 'MYSTERY': 20},
        }
        
        stats = dict(base_stats.get(structure_type, {'DEF': 10, 'HP': 50}))
        
        # Scale by level
        tier_mult = (level // 10) + 1
        for stat in stats:
            stats[stat] = stats[stat] * tier_mult
        
        # Material bonuses
        if material_data and isinstance(material_data, dict):
            stats['DEF'] += material_data.get('DEF', 0)
            stats['HP'] += material_data.get('HP', 0)
        
        return stats
    
    def _generate_functions(self, structure_type: StructureType,
                           materia: str) -> List[str]:
        """Generate structure functions."""
        functions = list(self.type_functions.get(structure_type, ['General Use']))
        
        # Add materia-specific functions
        materia_functions = {
            'Thunder': ['Storm channeling', 'Lightning storage'],
            'Warrior': ['Combat training', 'Weapon crafting'],
            'Pyro': ['Metal forging', 'Fire rituals'],
            'Aqua': ['Water purification', 'Healing baths'],
            'Beast': ['Animal taming', 'Beast breeding'],
            'Ghost': ['Spirit communication', 'Soul binding'],
            'Crystal': ['Memory storage', 'Divination'],
        }
        
        if materia in materia_functions:
            functions.extend(materia_functions[materia])
        
        return functions
    
    def _generate_structural_traits(self, material: str, materia: str) -> List[str]:
        """Generate traits specific to structure."""
        traits = []
        
        # Material-based structural traits
        material_traits = {
            'Drakian': 'Fire-resistant construction',
            'Banshee': 'Ethereal architecture',
            'Elf': 'Nature-integrated design',
            'Orc': 'Reinforced fortifications',
            'Mimic': 'Shifting layout',
            'Human': 'Versatile spaces',
        }
        
        if material in material_traits:
            traits.append(f"Material: {material_traits[material]}")
        
        # Materia-based enchantments
        materia_enchantments = {
            'Thunder': 'Lightning ward',
            'Warrior': 'Battle blessing',
            'Pyro': 'Eternal flame',
            'Aqua': 'Flowing water',
            'Beast': 'Wild growth',
            'Ghost': 'Spirit presence',
            'Crystal': 'Memory resonance',
        }
        
        if materia in materia_enchantments:
            traits.append(f"Materia: {materia_enchantments[materia]}")
        
        return traits
    
    def _calculate_capacity(self, size: StructureSize,
                           structure_type: StructureType) -> int:
        """Calculate structure capacity."""
        base_capacity = {
            StructureSize.HUT: 2,
            StructureSize.HOUSE: 5,
            StructureSize.HALL: 20,
            StructureSize.TOWER: 10,
            StructureSize.FORTRESS: 50,
            StructureSize.COMPLEX: 100,
            StructureSize.CITADEL: 500,
        }
        
        base = base_capacity.get(size, 10)
        
        # Type modifiers
        type_mods = {
            StructureType.DWELLING: 1.5,
            StructureType.MILITARY: 2.0,
            StructureType.INDUSTRIAL: 1.2,
        }
        
        mod = type_mods.get(structure_type, 1.0)
        
        return int(base * mod)
    
    def _calculate_value(self, material: str, materia: str,
                        level: int, size: StructureSize,
                        condition: StructureCondition) -> int:
        """Calculate structure value."""
        base_value = {
            StructureSize.HUT: 100,
            StructureSize.HOUSE: 500,
            StructureSize.HALL: 2000,
            StructureSize.TOWER: 5000,
            StructureSize.FORTRESS: 20000,
            StructureSize.COMPLEX: 100000,
            StructureSize.CITADEL: 500000,
        }
        
        value = base_value.get(size, 1000)
        
        # Level multiplier
        value *= ((level // 10) + 1)
        
        # Condition modifier
        condition_mods = {
            StructureCondition.PRISTINE: 1.5,
            StructureCondition.GOOD: 1.0,
            StructureCondition.WORN: 0.7,
            StructureCondition.DAMAGED: 0.4,
            StructureCondition.RUINED: 0.1,
        }
        
        value *= condition_mods.get(condition, 1.0)
        
        return int(value)
    
    def _generate_production(self, materia: str,
                            structure_type: StructureType,
                            level: int) -> Dict[str, int]:
        """Generate production output for industrial/magical structures."""
        production = {}
        
        # Only certain types produce
        if structure_type not in [StructureType.INDUSTRIAL, StructureType.MAGICAL, StructureType.COMMERCIAL]:
            return production
        
        # Materia determines what's produced
        materia_production = {
            'Thunder': {'Lightning Essence': 5},
            'Warrior': {'Weapons': 3, 'Armor': 2},
            'Pyro': {'Forged Items': 5, 'Fire Essence': 3},
            'Aqua': {'Purified Water': 10, 'Healing Potions': 2},
            'Beast': {'Beasts': 1, 'Leather': 5},
            'Ghost': {'Spirit Gems': 1, 'Ectoplasm': 5},
            'Crystal': {'Crystals': 5, 'Memory Shards': 2},
        }
        
        if materia in materia_production:
            for resource, amount in materia_production[materia].items():
                # Scale by level
                production[resource] = amount * ((level // 10) + 1)
        
        return production
    
    def add_runes(self, structure: Structure, num_runes: int = None) -> Structure:
        """Add runes to structure (0-5 slots)."""
        if num_runes is None:
            num_runes = random.randint(0, 5)
        
        runes_data = self.loader.get_all_runes()
        rune_list = list(runes_data.keys())
        
        selected = random.sample(rune_list, min(num_runes, len(rune_list)))
        structure.runes = selected
        
        # Add rune effects to traits
        for rune in selected:
            rune_data = runes_data.get(rune, {})
            effect = rune_data.get('effect', f'{rune} enchantment')
            structure.traits.append(f"Rune ({rune}): {effect}")
        
        return structure


# ────────────────────────────────────────────────
# Test
# ────────────────────────────────────────────────

if __name__ == '__main__':
    print("Testing Layer 4: Structures (Material/Materia Ontology)")
    print("=" * 70)
    
    gen = StructureGenerator()
    
    # Generate specific Material/Materia combinations
    print("\nSTRUCTURES (Material construction + Materia purpose):")
    print("-" * 70)
    
    test_cases = [
        ('Drakian', 'Thunder', StructureType.MILITARY),
        ('Banshee', 'Ghost', StructureType.RELIGIOUS),
        ('Elf', 'Crystal', StructureType.ACADEMIC),
        ('Orc', 'Warrior', StructureType.MILITARY),
        ('Mimic', 'Beast', StructureType.INDUSTRIAL),
    ]
    
    for material, materia, struct_type in test_cases:
        structure = gen.generate_structure(
            material=material,
            materia=materia,
            structure_type=struct_type,
            level=50
        )
        structure = gen.add_runes(structure, num_runes=random.randint(1, 3))
        
        print(f"\n  {structure.name}")
        print(f"    Material (Construction): {structure.material} (Species)")
        print(f"    Materia (Purpose): {structure.materia} (Type)")
        print(f"    Type: {structure.structure_type.value}")
        print(f"    Size: {structure.size.value} | Condition: {structure.condition.value}")
        print(f"    Level: {structure.level}")
        print(f"    Stats: DEF={structure.stats['DEF']}, HP={structure.stats['HP']}")
        print(f"    Capacity: {structure.capacity} ({structure.current_occupants} current)")
        print(f"    Functions: {', '.join(structure.functions)}")
        print(f"    Production: {structure.production if structure.production else 'None'}")
        print(f"    Runes: {', '.join(structure.runes) if structure.runes else 'None'}")
        print(f"    Traits:")
        for trait in structure.traits:
            print(f"      - {trait}")
        print(f"    Value: ${structure.value}")
    
    # Random generation
    print("\n\nRANDOM STRUCTURES (864 base combinations):")
    print("-" * 70)
    
    for i in range(3):
        structure = gen.generate_structure(level=random.randint(1, 100))
        print(f"\n  {i+1}. {structure.name}")
        print(f"     {structure.material} + {structure.materia}")
        print(f"     {structure.structure_type.value} | {structure.size.value}")
        print(f"     Level {structure.level} | {structure.condition.value}")
        print(f"     ${structure.value}")
    
    print("\n" + "=" * 70)
    print("All structures follow Material (Species construction) + Materia (Type purpose) ontology!")
