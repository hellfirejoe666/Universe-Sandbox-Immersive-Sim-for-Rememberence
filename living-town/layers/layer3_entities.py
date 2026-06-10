"""
Layer 3: Entities (NPCs, Creatures, Characters)

All entities are composed of:
- Material (Species) - Physical body/substance
- Materia (Type) - Soul/essence/energetic nature
- Equipment - Forged from Material + Materia (see Layer 2)
- Runes - Optional enchantments (0-5 slots)

Philosophy: Every entity = Material body + Materia soul
36 Materials × 24 Materia = 864 base entity archetypes
Plus equipment, levels, and runes = infinite variety
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import sys

# Import data loader and item generator
sys.path.insert(0, str(Path(__file__).parent.parent))
from data_loader import get_loader
from layers.layer2_items import ItemGenerator, ItemType, Rarity, Weapon, Armor


# ────────────────────────────────────────────────
# Entity Types
# ────────────────────────────────────────────────

class EntityRole(Enum):
    WARRIOR = "Warrior"
    MAGE = "Mage"
    ROGUE = "Rogue"
    CLERIC = "Cleric"
    RANGER = "Ranger"
    ARTIFICER = "Artificer"
    MERCHANT = "Merchant"
    SCHOLAR = "Scholar"
    LEADER = "Leader"
    GUARDIAN = "Guardian"


class Alignment(Enum):
    LAWFUL = "Lawful"
    NEUTRAL = "Neutral"
    CHAOTIC = "Chaotic"
    GOOD = "Good"
    EVIL = "Evil"


class Disposition(Enum):
    FRIENDLY = "Friendly"
    NEUTRAL = "Neutral"
    HOSTILE = "Hostile"
    UNKNOWN = "Unknown"


# ────────────────────────────────────────────────
# Data Classes
# ────────────────────────────────────────────────

@dataclass
class Entity:
    """
    Base entity class (NPC, creature, character).
    
    Every entity is composed of:
    - Material (Species) = Physical body
    - Materia (Type) = Soul/essence
    """
    id: str
    name: str
    material: str  # Species (physical body)
    materia: str   # Type (soul/essence)
    
    # Core identity
    level: int = 1
    role: EntityRole = EntityRole.WARRIOR
    alignment: Alignment = Alignment.NEUTRAL
    disposition: Disposition = Disposition.NEUTRAL
    
    # Stats (calculated from Material + Materia + level)
    stats: Dict[str, int] = field(default_factory=dict)
    
    # Biorhythms (from animal/star signs)
    animal: str = ""
    star: str = ""
    biorhythms: Dict[str, int] = field(default_factory=dict)
    
    # Equipment (forged from Material + Materia)
    weapons: List[Weapon] = field(default_factory=list)
    armor: Dict[str, Armor] = field(default_factory=dict)  # slot -> Armor
    
    # Runes (0-5 slots)
    runes: List[str] = field(default_factory=list)
    
    # Traits from Material/Materia
    traits: List[str] = field(default_factory=list)
    
    # Behavior
    goals: List[str] = field(default_factory=list)
    dialogue: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'material': self.material,
            'materia': self.materia,
            'level': self.level,
            'role': self.role.value,
            'alignment': self.alignment.value,
            'disposition': self.disposition.value,
            'stats': self.stats,
            'animal': self.animal,
            'star': self.star,
            'biorhythms': self.biorhythms,
            'weapons': [w.to_dict() for w in self.weapons],
            'armor': {k: v.to_dict() for k, v in self.armor.items()},
            'runes': self.runes,
            'traits': self.traits,
            'goals': self.goals,
            'dialogue': self.dialogue,
        }


# ────────────────────────────────────────────────
# Entity Generator
# ────────────────────────────────────────────────

class EntityGenerator:
    """
    Procedural entity generator using Material/Materia ontology.
    
    Every entity = Material (Species body) + Materia (Type soul) + Equipment
    """
    
    def __init__(self):
        self.loader = get_loader()
        self.item_gen = ItemGenerator()
        self.entity_counter = 0
        
        # Name generators by Material/Materia
        self.material_names = {
            'Drakian': ['Drak', 'Scale', 'Flame', 'Wing'],
            'Banshee': ['Whisper', 'Wail', 'Shade', 'Ghost'],
            'Elf': ['Leaf', 'Moon', 'Star', 'Silver'],
            'Orc': ['Gor', 'Krag', 'Iron', 'Bone'],
            'Mimic': ['Shift', 'Change', 'Form', 'Mirror'],
            'Human': ['John', 'Jane', 'Alex', 'Sam'],
        }
        
        self.materia_titles = {
            'Thunder': ['Stormcaller', 'Lightning', 'Thunderer'],
            'Warrior': ['Warbringer', 'Battleborn', 'Warmaster'],
            'Pyro': ['Flameheart', 'Ember', 'Pyromancer'],
            'Aqua': ['Tidewalker', 'Wave', 'Frost'],
            'Beast': ['Beastmaster', 'Predator', 'Hunter'],
            'Ghost': ['Soulkeeper', 'Phantom', 'Spirit'],
            'Crystal': ['Crystalheart', 'Shard', 'Gem'],
        }
        
        # Role descriptions
        self.role_descriptions = {
            EntityRole.WARRIOR: "Skilled in combat and physical prowess",
            EntityRole.MAGE: "Master of arcane energies and spells",
            EntityRole.ROGUE: "Expert in stealth and subterfuge",
            EntityRole.CLERIC: "Healer and protector of the faithful",
            EntityRole.RANGER: "Hunter and guardian of the wilds",
            EntityRole.ARTIFICER: "Creator of magical items and constructs",
            EntityRole.MERCHANT: "Trader and broker of goods",
            EntityRole.SCHOLAR: "Keeper of knowledge and lore",
            EntityRole.LEADER: "Commander and guide of others",
            EntityRole.GUARDIAN: "Protector of sacred places",
        }
    
    def generate_id(self) -> str:
        self.entity_counter += 1
        return f"entity_{self.entity_counter:04d}"
    
    def generate_entity(self, material: str = None,
                       materia: str = None,
                       level: int = 1,
                       role: EntityRole = None) -> Entity:
        """
        Generate an entity from Material + Materia.
        
        Args:
            material: Species (physical body) - random if None
            materia: Type (soul/essence) - random if None
            level: Entity level
            role: Entity role/class
        """
        # Get all canonical options
        species_list = list(self.loader.get_all_species().keys())
        types_list = list(self.loader.get_all_types().keys())
        animals = list(self.loader.get_all_animal_signs().keys())
        stars = list(self.loader.get_all_star_signs().keys())
        
        # Select or use provided
        if material is None:
            material = random.choice(species_list)
        if materia is None:
            materia = random.choice(types_list)
        if role is None:
            role = random.choice(list(EntityRole))
        
        # Get canonical data
        material_data = self.loader.get_species(material)
        materia_data = self.loader.get_type(materia)
        animal = random.choice(animals)
        star = random.choice(stars)
        animal_data = self.loader.get_animal_sign(animal)
        star_data = self.loader.get_star_sign(star)
        
        # Generate name from Material + Materia
        name = self._generate_name(material, materia, role)
        
        # Calculate biorhythms (animal + star)
        biorhythms = self._calculate_biorhythms(animal_data, star_data)
        
        # Calculate stats (Material + Materia + level)
        stats = self._calculate_stats(material_data, materia_data, level, role)
        
        # Generate equipment (forged from Material + Materia)
        weapons = self._generate_equipment(material, materia, level, 'weapon')
        armor = self._generate_equipment(material, materia, level, 'armor')
        
        # Get traits from Material (Species)
        traits = []
        if material_data and isinstance(material_data, dict):
            traits_data = material_data.get('traits', {})
            traits.extend(traits_data.get('active', [])[:2])
        
        # Get traits from Materia (Type)
        if materia_data and isinstance(materia_data, dict):
            traits_data = materia_data.get('traits', {})
            traits.extend(traits_data.get('active', [])[:2])
        
        # Generate goals based on role and Materia
        goals = self._generate_goals(role, materia)
        
        # Generate dialogue snippets
        dialogue = self._generate_dialogue(role, material, materia)
        
        # Select alignment
        alignment = self._roll_alignment(materia)
        
        # Select disposition
        disposition = random.choice(list(Disposition))
        
        # Create entity
        entity = Entity(
            id=self.generate_id(),
            name=name,
            material=material,
            materia=materia,
            level=level,
            role=role,
            alignment=alignment,
            disposition=disposition,
            stats=stats,
            animal=animal,
            star=star,
            biorhythms=biorhythms,
            weapons=weapons,
            armor=armor,
            traits=traits,
            goals=goals,
            dialogue=dialogue,
        )
        
        return entity
    
    def _generate_name(self, material: str, materia: str, 
                       role: EntityRole) -> str:
        """Generate entity name from Material + Materia + Role."""
        # Get material name component
        mat_names = self.material_names.get(material, [material[:4]])
        first = random.choice(mat_names)
        
        # Get materia title
        mat_titles = self.materia_titles.get(materia, [materia[:6]])
        title = random.choice(mat_titles)
        
        # Add role suffix sometimes
        role_suffixes = {
            EntityRole.WARRIOR: ['the Bold', 'the Brave', 'the Mighty'],
            EntityRole.MAGE: ['the Wise', 'the Arcane', 'the Learned'],
            EntityRole.ROGUE: ['the Shadow', 'the Silent', 'the Quick'],
            EntityRole.CLERIC: ['the Pure', 'the Devoted', 'the Sacred'],
            EntityRole.MERCHANT: ['the Rich', 'the Shrewd', 'the Golden'],
            EntityRole.SCHOLAR: ['the Learned', 'the Ancient', 'the Knowing'],
        }
        
        suffix = ""
        if random.random() > 0.5 and role in role_suffixes:
            suffix = " " + random.choice(role_suffixes[role])
        
        return f"{first} {title}{suffix}"
    
    def _calculate_biorhythms(self, animal_data: Dict, star_data: Dict) -> Dict[str, int]:
        """Calculate biorhythms from animal + star signs."""
        bio_keys = ['MNF', 'SPL', 'BEU', 'STR', 'FND', 'KNO', 
                    'UND', 'WIS', 'VIT', 'SEX', 'DIV', 'EGO']
        
        animal_bio = animal_data.get('biorhythms', {})
        star_bio = star_data.get('biorhythms', {})
        
        bios = {}
        for key in bio_keys:
            bios[key] = animal_bio.get(key, 0) + star_bio.get(key, 0)
        
        return bios
    
    def _calculate_stats(self, material_data: Dict, materia_data: Dict,
                        level: int, role: EntityRole) -> Dict[str, int]:
        """Calculate stats from Material + Materia + level + role."""
        # Base stats from Material (Species)
        base_stats = {
            'HP': material_data.get('HP', 10) if isinstance(material_data, dict) else 10,
            'ATK': material_data.get('ATK', 5) if isinstance(material_data, dict) else 5,
            'DEF': material_data.get('DEF', 5) if isinstance(material_data, dict) else 5,
            'SPD': material_data.get('SPD', 5) if isinstance(material_data, dict) else 5,
            'MP': material_data.get('MP', 10) if isinstance(material_data, dict) else 10,
        }
        
        # Role modifiers
        role_mods = {
            EntityRole.WARRIOR: {'ATK': 1.5, 'DEF': 1.3, 'HP': 1.2},
            EntityRole.MAGE: {'MP': 2.0, 'ATK': 0.8, 'DEF': 0.8},
            EntityRole.ROGUE: {'SPD': 1.5, 'ATK': 1.3, 'HP': 0.9},
            EntityRole.CLERIC: {'MP': 1.5, 'HP': 1.3, 'DEF': 1.2},
            EntityRole.RANGER: {'SPD': 1.3, 'ATK': 1.2, 'DEF': 1.1},
            EntityRole.ARTIFICER: {'MP': 1.4, 'DEF': 1.2},
            EntityRole.MERCHANT: {'HP': 1.2, 'SPD': 1.1},
            EntityRole.SCHOLAR: {'MP': 1.5, 'WIS': 1.3},
            EntityRole.LEADER: {'HP': 1.3, 'ATK': 1.2, 'DEF': 1.2},
            EntityRole.GUARDIAN: {'DEF': 1.5, 'HP': 1.4, 'ATK': 1.1},
        }
        
        mods = role_mods.get(role, {})
        for stat, mod in mods.items():
            if stat in base_stats:
                base_stats[stat] = int(base_stats[stat] * mod)
        
        # Scale by level
        tier_mult = (level // 10) + 1
        for stat in base_stats:
            base_stats[stat] = max(1, base_stats[stat] * tier_mult)
        
        return base_stats
    
    def _generate_equipment(self, material: str, materia: str,
                           level: int, equip_type: str) -> Any:
        """Generate equipment for entity."""
        if equip_type == 'weapon':
            # 1-2 weapons
            num_weapons = random.randint(1, 2)
            weapons = []
            for _ in range(num_weapons):
                weapon = self.item_gen.generate_item(
                    item_type=ItemType.WEAPON,
                    material=material,
                    materia=materia,
                    level=level,
                    rarity=self._roll_rarity(level)
                )
                weapons.append(weapon)
            return weapons
        
        elif equip_type == 'armor':
            # Full armor set (6 slots, but maybe not all equipped)
            armor = {}
            slots = ['HEAD', 'BODY', 'HANDS', 'LEGS', 'FEET']
            for slot in slots:
                if random.random() > 0.3:  # 70% chance per slot
                    armor[slot] = self.item_gen.generate_item(
                        item_type=ItemType.ARMOR,
                        material=material,
                        materia=materia,
                        level=level,
                        rarity=self._roll_rarity(level)
                    )
            return armor
        
        return []
    
    def _roll_rarity(self, level: int) -> Rarity:
        """Roll for equipment rarity based on level."""
        # Higher levels = better rarity chances
        base_roll = random.random()
        
        if level >= 50:
            thresholds = [0.30, 0.55, 0.75, 0.90, 0.97]
        elif level >= 20:
            thresholds = [0.40, 0.65, 0.85, 0.95, 0.99]
        else:
            thresholds = [0.50, 0.75, 0.90, 0.96, 0.99]
        
        if base_roll < thresholds[0]:
            return Rarity.COMMON
        elif base_roll < thresholds[1]:
            return Rarity.UNCOMMON
        elif base_roll < thresholds[2]:
            return Rarity.RARE
        elif base_roll < thresholds[3]:
            return Rarity.EPIC
        elif base_roll < thresholds[4]:
            return Rarity.LEGENDARY
        else:
            return Rarity.TRANSCENDENT
    
    def _generate_goals(self, role: EntityRole, materia: str) -> List[str]:
        """Generate entity goals based on role and Materia."""
        base_goals = {
            EntityRole.WARRIOR: ["Prove strength in battle", "Defend the weak", "Seek worthy opponents"],
            EntityRole.MAGE: ["Master ancient spells", "Uncover forbidden knowledge", "Create new magic"],
            EntityRole.ROGUE: ["Accumulate wealth", "Learn all secrets", "Live without chains"],
            EntityRole.CLERIC: ["Spread faith", "Heal the sick", "Purify corruption"],
            EntityRole.RANGER: ["Protect nature", "Hunt dangerous beasts", "Explore wild lands"],
            EntityRole.ARTIFICER: ["Create legendary items", "Master all crafts", "Build automatons"],
            EntityRole.MERCHANT: ["Accumulate wealth", "Control trade routes", "Find rare goods"],
            EntityRole.SCHOLAR: ["Preserve knowledge", "Discover truths", "Teach others"],
            EntityRole.LEADER: ["Unite people", "Build legacy", "Create order"],
            EntityRole.GUARDIAN: ["Protect sacred place", "Maintain balance", "Serve higher purpose"],
        }
        
        materia_influences = {
            'Thunder': ["Harness lightning power", "Become storm incarnate"],
            'Warrior': ["Achieve perfect combat", "Lead armies to glory"],
            'Pyro': ["Master flame essence", "Burn away impurity"],
            'Ghost': ["Understand death", "Transcend mortality"],
            'Beast': ["Embrace primal nature", "Become apex predator"],
        }
        
        goals = list(base_goals.get(role, ["Seek purpose"]))
        
        # Add materia-specific goals
        if materia in materia_influences:
            goals.extend(materia_influences[materia])
        
        # Select 1-3 goals
        return random.sample(goals, min(random.randint(1, 3), len(goals)))
    
    def _generate_dialogue(self, role: EntityRole, material: str, 
                          materia: str) -> List[str]:
        """Generate dialogue snippets."""
        greetings = [
            "Greetings, traveler.",
            "Well met.",
            "What brings you here?",
            "Speak your purpose.",
        ]
        
        role_lines = {
            EntityRole.WARRIOR: ["Strength is everything.", "Prove yourself in battle.", "The weak perish."],
            EntityRole.MAGE: ["Knowledge is power.", "The arcane reveals truth.", "Magic flows through all."],
            EntityRole.MERCHANT: ["Everything has a price.", "Gold speaks all languages.", "What do you seek to buy?"],
            EntityRole.CLERIC: ["The divine guides us.", "Faith strengthens all.", "Purity of soul matters."],
            EntityRole.SCHOLAR: ["Let me share what I know.", "History teaches us.", "Knowledge must be preserved."],
        }
        
        lines = list(greetings)
        lines.extend(role_lines.get(role, ["I have nothing to say."]))
        
        # Add material/materia flavor
        if material == 'Drakian':
            lines.append("Fire runs in my veins.")
        elif material == 'Banshee':
            lines.append("The spirits whisper to me.")
        
        if materia == 'Thunder':
            lines.append("Feel the storm's power.")
        elif materia == 'Ghost':
            lines.append("Death holds no fear for me.")
        
        return lines
    
    def _roll_alignment(self, materia: str) -> Alignment:
        """Roll alignment, influenced by Materia."""
        # Some Materia lean toward certain alignments
        materia_alignments = {
            'Ghost': [Alignment.NEUTRAL, Alignment.CHAOTIC],
            'Warrior': [Alignment.LAWFUL, Alignment.NEUTRAL],
            'Beast': [Alignment.CHAOTIC, Alignment.NEUTRAL],
            'Holy': [Alignment.LAWFUL, Alignment.GOOD],
            'Dark': [Alignment.CHAOTIC, Alignment.EVIL],
        }
        
        options = materia_alignments.get(materia, list(Alignment))
        return random.choice(options)


# ────────────────────────────────────────────────
# Test
# ────────────────────────────────────────────────

if __name__ == '__main__':
    print("Testing Layer 3: Entities (Material/Materia Ontology)")
    print("=" * 70)
    
    gen = EntityGenerator()
    
    # Generate specific Material/Materia combinations
    print("\nENTITIES (Material body + Materia soul):")
    print("-" * 70)
    
    test_cases = [
        ('Drakian', 'Thunder', EntityRole.WARRIOR),
        ('Banshee', 'Ghost', EntityRole.MAGE),
        ('Elf', 'Crystal', EntityRole.SCHOLAR),
        ('Orc', 'Warrior', EntityRole.WARRIOR),
        ('Mimic', 'Beast', EntityRole.ROGUE),
    ]
    
    for material, materia, role in test_cases:
        entity = gen.generate_entity(
            material=material,
            materia=materia,
            level=50,
            role=role
        )
        
        print(f"\n  {entity.name}")
        print(f"    Material (Body): {entity.material} (Species)")
        print(f"    Materia (Soul): {entity.materia} (Type)")
        print(f"    Role: {entity.role.value}")
        print(f"    Level: {entity.level} | Alignment: {entity.alignment.value}")
        print(f"    Zodiac: {entity.animal} + {entity.star}")
        print(f"    Stats: HP={entity.stats['HP']}, ATK={entity.stats['ATK']}, "
              f"DEF={entity.stats['DEF']}, SPD={entity.stats['SPD']}, MP={entity.stats['MP']}")
        print(f"    Weapons: {len(entity.weapons)}")
        for w in entity.weapons:
            print(f"      - {w.name} ({w.material} + {w.materia})")
        print(f"    Armor: {len(entity.armor)} slots equipped")
        print(f"    Traits:")
        for trait in entity.traits:
            print(f"      - {trait}")
        print(f"    Goals:")
        for goal in entity.goals:
            print(f"      - {goal}")
        print(f"    Sample Dialogue: \"{entity.dialogue[0]}\"")
    
    # Random generation
    print("\n\nRANDOM ENTITIES (864 base archetypes):")
    print("-" * 70)
    
    for i in range(3):
        entity = gen.generate_entity(level=random.randint(1, 100))
        print(f"\n  {i+1}. {entity.name}")
        print(f"     {entity.material} (body) + {entity.materia} (soul)")
        print(f"     {entity.role.value} | Level {entity.level} | {entity.alignment.value}")
    
    print("\n" + "=" * 70)
    print("All entities follow Material (Species body) + Materia (Type soul) ontology!")
