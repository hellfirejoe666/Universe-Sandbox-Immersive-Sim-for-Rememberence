# data_loader.py
# Unified data loader for Rememberence JSON files
# Phase 1: Core data integration layer

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

class RememberenceData:
    """
    Centralized data loader for all Rememberence game data.
    Loads JSON files and provides validated access to game entities.
    """
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Default to workspace data directory
            data_dir = Path(__file__).parent / 'data'
        
        self.data_dir = Path(data_dir)
        self._cache = {}
        self._loaded = False
        
        # Load all data on initialization
        self.load_all()
    
    def load_all(self) -> Dict[str, Any]:
        """Load all JSON data files into memory."""
        files = {
            'animal_signs': 'animal_signs.json',
            'star_signs': 'star_signs.json',
            'species': 'species.json',
            'types': 'types.json',
            'classes': 'classes.json',
            'runes': 'runes.json',
            'narrative_verses': 'narrative_verses.json'
        }
        
        for key, filename in files.items():
            filepath = self.data_dir / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    self._cache[key] = json.load(f)
            else:
                raise FileNotFoundError(f"Required data file not found: {filepath}")
        
        self._loaded = True
        self._validate_all()
        return self._cache
    
    def _validate_all(self):
        """Run validation checks on all loaded data."""
        errors = []
        
        # Validate animal signs (12 expected)
        animals = self._cache['animal_signs'].get('animalSigns', {})
        if len(animals) != 12:
            errors.append(f"Expected 12 animal signs, found {len(animals)}")
        for key, data in animals.items():
            if 'biorhythms' not in data:
                errors.append(f"Animal {key} missing biorhythms")
            elif len(data['biorhythms']) != 12:
                errors.append(f"Animal {key} has {len(data['biorhythms'])} biorhythms (expected 12)")
        
        # Validate star signs (12 expected)
        stars = self._cache['star_signs'].get('starSigns', {})
        if len(stars) != 12:
            errors.append(f"Expected 12 star signs, found {len(stars)}")
        
        # Validate species (36 expected)
        species = self._cache['species'].get('species', {})
        if len(species) != 36:
            errors.append(f"Expected 36 species, found {len(species)}")
        for key, data in species.items():
            required_stats = ['HP', 'ATK', 'DEF', 'SPD', 'MP']
            for stat in required_stats:
                if stat not in data.get('stats', {}):
                    errors.append(f"Species {key} missing stat: {stat}")
            if 'traits' not in data:
                errors.append(f"Species {key} missing traits")
        
        # Validate types (24 expected)
        types = self._cache['types'].get('types', {})
        if len(types) != 24:
            errors.append(f"Expected 24 types, found {len(types)}")
        for key, data in types.items():
            required_mods = ['HP', 'ATK', 'DEF', 'SPD', 'MP']
            for stat in required_mods:
                if stat not in data.get('stat_modifiers', {}):
                    errors.append(f"Type {key} missing stat_modifier: {stat}")
        
        # Validate classes (6 expected, each with 6 skills)
        classes = self._cache['classes'].get('classes', {})
        if len(classes) != 6:
            errors.append(f"Expected 6 classes, found {len(classes)}")
        for class_name, data in classes.items():
            skills = data.get('skills', [])
            if len(skills) != 6:
                errors.append(f"Class {class_name} has {len(skills)} skills (expected 6)")
        
        # Validate runes (76 expected)
        runes = self._cache['runes'].get('runes', {})
        # Filter out intro/cypher keys
        rune_count = len([k for k in runes.keys() if k not in ['intro', 'cypher']])
        if rune_count != 76:
            errors.append(f"Expected 76 runes, found {rune_count}")
        
        if errors:
            raise ValueError(f"Data validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
    
    # === Accessor Methods ===
    
    def get_animal(self, key: str) -> Optional[Dict]:
        """Get animal sign data by key (e.g., 'Rat', 'Dragon')."""
        return self._cache['animal_signs']['animalSigns'].get(key)
    
    def get_star(self, key: str) -> Optional[Dict]:
        """Get star sign data by key (e.g., 'Aries', 'Leo')."""
        return self._cache['star_signs']['starSigns'].get(key)
    
    def get_species(self, key: str) -> Optional[Dict]:
        """Get species data by key (e.g., 'Drakian', 'Wolfin')."""
        return self._cache['species']['species'].get(key)
    
    def get_type(self, key: str) -> Optional[Dict]:
        """Get type data by key (e.g., 'Pyro', 'Thunder')."""
        return self._cache['types']['types'].get(key)
    
    def get_class(self, class_name: str) -> Optional[Dict]:
        """Get class data by name (Melee/Ranged/Magic/Step/Special/Trance)."""
        return self._cache['classes']['classes'].get(class_name)
    
    def get_class_skill(self, class_name: str, skill_index: int) -> Optional[Dict]:
        """Get specific skill from a class (0-indexed)."""
        class_data = self.get_class(class_name)
        if not class_data:
            return None
        skills = class_data.get('skills', [])
        if 0 <= skill_index < len(skills):
            return skills[skill_index]
        return None
    
    def get_rune(self, key: str) -> Optional[Dict]:
        """Get rune data by key (e.g., '1-Cu', '50-Kel')."""
        return self._cache['runes']['runes'].get(key)
    
    def get_narrative_verses(self) -> Dict:
        """Get narrative verses mapping."""
        return self._cache['narrative_verses']
    
    # === Lookup Helpers ===
    
    def list_animals(self) -> List[str]:
        """Return list of all animal sign keys."""
        return list(self._cache['animal_signs']['animalSigns'].keys())
    
    def list_stars(self) -> List[str]:
        """Return list of all star sign keys."""
        return list(self._cache['star_signs']['starSigns'].keys())
    
    def list_species(self) -> List[str]:
        """Return list of all species keys."""
        return list(self._cache['species']['species'].keys())
    
    def list_types(self) -> List[str]:
        """Return list of all type keys."""
        return list(self._cache['types']['types'].keys())
    
    def list_classes(self) -> List[str]:
        """Return list of all class names."""
        return list(self._cache['classes']['classes'].keys())
    
    def list_runes(self) -> List[str]:
        """Return list of all rune keys (excluding intro/cypher)."""
        runes = self._cache['runes']['runes']
        return [k for k in runes.keys() if k not in ['intro', 'cypher']]
    
    # === Validation Helpers ===
    
    def validate_zodiac(self, animal: str, star: str) -> bool:
        """Check if animal and star sign keys are valid."""
        return animal in self.list_animals() and star in self.list_stars()
    
    def validate_species_type(self, species: str, type_: str) -> bool:
        """Check if species and type keys are valid."""
        return species in self.list_species() and type_ in self.list_types()
    
    def validate_class_skill(self, class_name: str, skill_index: int) -> bool:
        """Check if class and skill index are valid."""
        if class_name not in self.list_classes():
            return False
        return 0 <= skill_index <= 5  # 6 skills per class (0-5)
    
    def get_species_affinities(self, animal: str) -> List[str]:
        """Get recommended species for an animal sign."""
        animal_data = self.get_animal(animal)
        if not animal_data:
            return []
        # Parse affinities like "Drakian, ATK + KNO"
        affinities = animal_data.get('species', [])
        return [a.split(',')[0].strip() for a in affinities]
    
    def get_type_affinities(self, star: str) -> List[str]:
        """Get recommended types for a star sign."""
        star_data = self.get_star(star)
        if not star_data:
            return []
        affinities = star_data.get('types', [])
        return [a.split(',')[0].strip() for a in affinities]
    
    def to_dict(self) -> Dict:
        """Return all loaded data as a single dictionary."""
        return self._cache.copy()


# === Singleton Instance ===
# Create a global instance for easy import/use
_data_instance: Optional[RememberenceData] = None

def get_data(data_dir: str = None) -> RememberenceData:
    """Get or create the global data instance."""
    global _data_instance
    if _data_instance is None:
        _data_instance = RememberenceData(data_dir)
    return _data_instance


# === CLI Test ===
if __name__ == '__main__':
    print("Loading Rememberence data...")
    data = RememberenceData()
    
    print(f"\n[OK] Loaded {len(data.list_animals())} animal signs")
    print(f"[OK] Loaded {len(data.list_stars())} star signs")
    print(f"[OK] Loaded {len(data.list_species())} species")
    print(f"[OK] Loaded {len(data.list_types())} types")
    print(f"[OK] Loaded {len(data.list_classes())} classes")
    print(f"[OK] Loaded {len(data.list_runes())} runes")
    
    # Sample lookups
    print("\n--- Sample Data ---")
    dragon = data.get_animal('Dragon')
    print(f"Dragon: {dragon['biorhythms']}")
    
    drakian = data.get_species('Drakian')
    print(f"\nDrakian: HP={drakian['stats']['HP']}, ATK={drakian['stats']['ATK']}, " +
          f"DEF={drakian['stats']['DEF']}, SPD={drakian['stats']['SPD']}, MP={drakian['stats']['MP']}")
    print(f"  Move: {drakian['stats']['Move']}")
    print(f"  Active traits: {len(drakian['traits']['active'])}")
    
    pyro = data.get_type('Pyro')
    print(f"\nPyro: color={pyro.get('color', 'N/A')}, move_pattern={pyro.get('move_pattern', 'N/A')}")
    print(f"  Stat modifiers: {pyro.get('stat_modifiers', {})}")
    
    melee = data.get_class('Melee')
    print(f"\nMelee Class: {len(melee['skills'])} skills")
    for i, skill in enumerate(melee['skills']):
        print(f"  {i+1}. {skill['name']} - ATK+{skill.get('atk_bonus', 0)}, DEF+{skill.get('def_bonus', 0)}, SPD+{skill.get('spd_bonus', 0)}")
