"""
Character Sheet Generator - Complete Rememberence Format
Uses: calc_utils.py for all calculations (matching generator.js)
"""

import random
from typing import Dict, List, Any, Optional
from data_loader import get_loader
from calc_utils import (
    calculate_biorhythms,
    calculate_thoughts,
    calculate_stats,
    calculate_gear_stats,
    get_tier
)


class CharacterSheetGenerator:
    """Generates complete character sheets matching JS generator."""
    
    def __init__(self):
        self.loader = get_loader()
        self.biorhythm_keys = ['MNF', 'SPL', 'BEU', 'STR', 'FND', 'KNO', 
                                'UND', 'WIS', 'VIT', 'SEX', 'DIV', 'EGO']
    
    def generate_character(self, level: int = 1) -> Dict[str, Any]:
        """Generate complete character with ALL fields from JS generator."""
        
        # Get canonical data
        animals = list(self.loader.get_all_animal_signs().keys())
        stars = list(self.loader.get_all_star_signs().keys())
        species_list = list(self.loader.get_all_species().keys())
        types_list = list(self.loader.get_all_types().keys())
        classes = self.loader.get_all_classes()
        
        # Random selection
        animal = random.choice(animals)
        star = random.choice(stars)
        species = random.choice(species_list)
        species2 = random.choice(species_list) if random.random() > 0.7 else ''
        char_type = random.choice(types_list)
        type2 = random.choice(types_list) if random.random() > 0.7 else ''
        
        # Get canonical data - ensure we get the full data with biorhythms
        animal_data = self.loader.get_animal_sign(animal)
        star_data = self.loader.get_star_sign(star)
        species_data = self.loader.get_species(species)
        species2_data = self.loader.get_species(species2) if species2 else None
        type_data = self.loader.get_type(char_type)
        type2_data = self.loader.get_type(type2) if type2 else None
        
        # Calculate biorhythms
        bios = calculate_biorhythms(animal_data, star_data)
        
        # Calculate thoughts
        thoughts = calculate_thoughts(bios)
        
        # Calculate stats (matching JS exactly)
        stats = calculate_stats(bios, species_data, type_data, species2_data, type2_data, level)
        gear_stats = calculate_gear_stats(stats)
        
        # Select class skills
        skills = self._select_skills(classes)
        
        # Get traits
        species_traits = self._get_traits(species_data, species2_data, 'active')
        type_traits = self._get_traits(type_data, type2_data, 'active')
        species_passive = self._get_traits(species_data, species2_data, 'passive')
        type_passive = self._get_traits(type_data, type2_data, 'passive')
        
        # Generate name
        name = self._gen_name(char_type)
        
        # Get tier
        tier = get_tier(level)
        
        # Description
        desc = f"Offspring of {animal} and {star}, born in the cosmic weave."
        
        return {
            'name': name,
            'level': level,
            'tier': tier,
            'animal': animal,
            'star': star,
            'species': species,
            'species2': species2,
            'type': char_type,
            'type2': type2,
            'biorhythms': bios,  # Changed from 'bios'
            'thoughts': thoughts,
            'stats': stats,
            'gear_stats': gear_stats,
            'skills': skills,
            'species_traits': species_traits,
            'type_traits': type_traits,
            'species_passive': species_passive,
            'type_passive': type_passive,
            'description': desc,
            'weapons': [],
            'gear': {},
            'constructs': [],
            'runes': [],
            'items': [],
        }
    
    def _calc_biorhythms(self, animal_data: Dict, star_data: Dict) -> Dict[str, int]:
        """Calculate biorhythms from animal + star."""
        # Handle nested biorhythms structure
        animal_bio = animal_data.get('biorhythms', {})
        star_bio = star_data.get('biorhythms', {})
        
        # If biorhythms not found at top level, try nested
        if not animal_bio and 'biorhythms' in animal_data:
            animal_bio = animal_data['biorhythms']
        if not star_bio and 'biorhythms' in star_data:
            star_bio = star_data['biorhythms']
        
        bios = {}
        for key in self.biorhythm_keys:
            bios[key] = (animal_bio.get(key, 0) + star_bio.get(key, 0))
        
        return bios
    
    def _calc_thoughts(self, bios: Dict[str, int]) -> Dict[str, int]:
        """Calculate thoughts from biorhythm pairs (matching JS)."""
        thoughts = {}
        
        for thought_name, (bio1_key, bio2_key) in self.thought_pairs.items():
            bio1 = bios.get(bio1_key, 0)
            bio2 = bios.get(bio2_key, 0)
            thoughts[thought_name] = bio1 - bio2
        
        thoughts['State'] = sum(thoughts.values())
        
        return thoughts
    
    def _calc_stats(self, bios: Dict, species_data: Dict, type_data: Dict,
                   species2_data: Optional[Dict], type2_data: Optional[Dict],
                   level: int) -> Dict[str, int]:
        """Calculate stats matching JS generator exactly."""
        
        # Base species stats (from 'stats' nested dict)
        if isinstance(species_data, dict):
            species_stats = species_data.get('stats', {})
            base_species1 = {
                'HP': species_stats.get('HP', 0),
                'ATK': species_stats.get('ATK', 0),
                'DEF': species_stats.get('DEF', 0),
                'SPD': species_stats.get('SPD', 0),
                'MP': species_stats.get('MP', 0),
            }
        else:
            base_species1 = {'HP': 0, 'ATK': 0, 'DEF': 0, 'SPD': 0, 'MP': 0}
        
        if species2_data and isinstance(species2_data, dict):
            species_stats2 = species2_data.get('stats', {})
            base_species2 = {
                'HP': species_stats2.get('HP', 0),
                'ATK': species_stats2.get('ATK', 0),
                'DEF': species_stats2.get('DEF', 0),
                'SPD': species_stats2.get('SPD', 0),
                'MP': species_stats2.get('MP', 0),
            }
        else:
            base_species2 = {'HP': 0, 'ATK': 0, 'DEF': 0, 'SPD': 0, 'MP': 0}
        
        # Type defines WHICH biorhythm to use for each stat (from stat_modifiers)
        if isinstance(type_data, dict):
            stat_mods = type_data.get('stat_modifiers', {})
            base_type1 = {
                'HP': stat_mods.get('HP', 'VIT'),
                'ATK': stat_mods.get('ATK', 'STR'),
                'DEF': stat_mods.get('DEF', 'FND'),
                'SPD': stat_mods.get('SPD', 'SEX'),
                'MP': stat_mods.get('MP', 'WIS'),
            }
        else:
            base_type1 = {'HP': 'VIT', 'ATK': 'STR', 'DEF': 'FND', 'SPD': 'SEX', 'MP': 'WIS'}
        
        if type2_data and isinstance(type2_data, dict):
            stat_mods2 = type2_data.get('stat_modifiers', {})
            base_type2 = {
                'HP': stat_mods2.get('HP', 'VIT'),
                'ATK': stat_mods2.get('ATK', 'STR'),
                'DEF': stat_mods2.get('DEF', 'FND'),
                'SPD': stat_mods2.get('SPD', 'SEX'),
                'MP': stat_mods2.get('MP', 'WIS'),
            }
        else:
            base_type2 = None
        
        # Tier scale (matching JS: level 1-9=1, 10-99=10, 100-999=100, etc.)
        tier_index = 0 if level < 10 else int(str(level - 1).__len__())
        scale = 10 ** tier_index if tier_index > 0 else 1
        
        stats = {}
        for stat in ['HP', 'ATK', 'DEF', 'SPD', 'MP']:
            # Get biorhythm key from type
            bio1_key = base_type1.get(stat, 'VIT')
            # Skip if biorhythm key is invalid
            if bio1_key in ['HP', 'ATK', 'DEF', 'SPD', 'MP']:
                bio1_key = 'VIT'
            
            bio1 = bios.get(bio1_key, 0)
            
            # Calculate: (species_base + biorhythm) * scale
            raw = (base_species1[stat] + bio1) * scale
            
            # If secondary type exists and uses different biorhythm, take max
            if base_type2:
                bio2_key = base_type2.get(stat, bio1_key)
                if bio2_key in ['HP', 'ATK', 'DEF', 'SPD', 'MP']:
                    bio2_key = 'VIT'
                bio2 = bios.get(bio2_key, 0)
                raw2 = (base_species2[stat] + bio2) * scale
                raw = max(raw, raw2)
            
            stats[stat] = max(1, round(raw))
        
        return stats
    
    def _calc_gear_stats(self, base_stats: Dict) -> Dict[str, int]:
        """Calculate gear stats (6 slots x base stats)."""
        slots = 6
        return {stat: round(base_stats[stat] * slots) for stat in base_stats}
    
    def _select_skills(self, classes: Dict) -> Dict[str, str]:
        """Select class skills."""
        skills = {}
        
        for category in ['melee', 'ranged', 'magic', 'step', 'special', 'trance']:
            cat_data = classes.get(category, {})
            if isinstance(cat_data, dict):
                options = list(cat_data.keys())
                skills[category] = random.choice(options) if options else 'None'
            else:
                skills[category] = 'None'
        
        return skills
    
    def _get_traits(self, data1: Dict, data2: Optional[Dict], trait_type: str) -> List[str]:
        """Get traits from species/type data."""
        traits = []
        
        if data1 and isinstance(data1, dict):
            traits_data = data1.get('traits', {})
            traits.extend(traits_data.get(trait_type, []))
        
        if data2 and isinstance(data2, dict):
            traits_data = data2.get('traits', {})
            traits.extend(traits_data.get(trait_type, []))
        
        return list(set(traits))
    
    def _gen_name(self, char_type: str) -> str:
        """Generate name based on type."""
        syllables = {
            'Thunder': ['Zan', 'Thor', 'Ram'],
            'Warrior': ['Krag', 'Gor', 'Tak'],
            'Spellcaster': ['Ael', 'Mir', 'Thal'],
            'Pyro': ['Ign', 'Pyre', 'Flam'],
            'Aqua': ['Mar', 'Aqua', 'Nere'],
            'Beast': ['Fen', 'Wolf', 'Rex'],
        }
        
        type_syllables = syllables.get(char_type, ['Ren', 'Mem', 'Ori'])
        suffixes = ['os', 'ia', 'us', 'a', 'en', 'is']
        
        return random.choice(type_syllables) + random.choice(suffixes)


# Test
if __name__ == '__main__':
    print("Testing Character Sheet Generator")
    print("=" * 60)
    
    gen = CharacterSheetGenerator()
    char = gen.generate_character(level=10)
    
    print(f"\nName: {char['name']}")
    print(f"Level: {char['level']} [{char['tier']}I]")
    print(f"Animal: {char['animal']} / Star: {char['star']}")
    print(f"Species: {char['species']}{('-' + char['species2']) if char['species2'] else ''}")
    print(f"Type: {char['type']}{('-' + char['type2']) if char['type2'] else ''}")
    print(f"\nDescription: {char['description']}")
    
    print("\nStats:")
    for stat, val in char['stats'].items():
        print(f"  {stat}: {val}")
    
    print("\nBiorhythms:")
    for key in gen.biorhythm_keys:
        print(f"  {key}: {char['biorhythms'].get(key, 0)}")
    
    print("\nThoughts:")
    for thought, val in char['thoughts'].items():
        print(f"  {thought}: {val}")
    
    print("\nSkills:")
    for cat, skill in char['skills'].items():
        print(f"  {cat}: {skill}")
    
    print("\n" + "=" * 60)
