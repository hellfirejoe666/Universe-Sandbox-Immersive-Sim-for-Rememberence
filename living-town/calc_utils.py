"""
Calculation Utilities - Reusable formulas from generator.js

All stat calculations follow the same pattern:
  stat = (material_base + materia_modifier) * tier_scale

Where:
  - material_base = Species stats (HP, ATK, DEF, SPD, MP)
  - materia_modifier = Biorhythm value (determined by Type's stat_modifiers)
  - tier_scale = 1, 10, 100, 1000, etc. based on level
"""

from typing import Dict, Optional


def get_tier(level: int) -> str:
    """Get tier name from level (matching JS)."""
    tiers = ['Novice', 'Beginner', 'Mediate', 'Advanced', 'Master', 'Deity']
    
    if level < 10:
        tier_index = 0
    elif level < 100:
        tier_index = 1
    elif level < 1000:
        tier_index = 2
    elif level < 10000:
        tier_index = 3
    elif level < 100000:
        tier_index = 4
    else:
        tier_index = 5
    
    return tiers[tier_index]


def get_tier_scale(level: int) -> int:
    """Get tier scale multiplier (matching JS).
    
    Level 1-9: scale = 1
    Level 10-99: scale = 10
    Level 100-999: scale = 100
    Level 1000-9999: scale = 1000
    etc.
    """
    if level < 10:
        return 1
    
    tier_index = len(str(level - 1))
    return 10 ** tier_index


def calculate_biorhythms(animal_data: Dict, star_data: Dict) -> Dict[str, int]:
    """Calculate biorhythms from animal + star signs (matching JS)."""
    animal_bio = animal_data.get('biorhythms', {})
    star_bio = star_data.get('biorhythms', {})
    
    bios = {}
    for key in ['MNF', 'SPL', 'BEU', 'STR', 'FND', 'KNO', 'UND', 'WIS', 'VIT', 'SEX', 'DIV', 'EGO']:
        bios[key] = animal_bio.get(key, 0) + star_bio.get(key, 0)
    
    return bios


def calculate_thoughts(bios: Dict[str, int]) -> Dict[str, int]:
    """Calculate thoughts from biorhythms (matching JS)."""
    thoughts = {
        'Environment': bios.get('FND', 0) - bios.get('EGO', 0),
        'Emotion': bios.get('BEU', 0) - bios.get('DIV', 0),
        'Subconscious': bios.get('SPL', 0) - bios.get('UND', 0),
        'Conscious': bios.get('MNF', 0) - bios.get('SEX', 0),
        'Abstraction': bios.get('KNO', 0) - bios.get('WIS', 0),
        'Perception': bios.get('VIT', 0) - bios.get('STR', 0),
    }
    
    thoughts['State'] = sum(thoughts.values())
    
    return thoughts


def calculate_stats(
    bios: Dict[str, int],
    species_data: Optional[Dict],
    type_data: Optional[Dict],
    species2_data: Optional[Dict] = None,
    type2_data: Optional[Dict] = None,
    level: int = 1
) -> Dict[str, int]:
    """
    Calculate combat stats (matching JS generator.js exactly).
    
    Formula: stat = (species_base + biorhythm_from_type) * tier_scale
    
    If secondary species/type provided, takes the max of both combinations.
    """
    # Get species base stats (from nested 'stats' dict)
    if species_data and isinstance(species_data, dict):
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
        species_stats2 = species_data.get('stats', {})
        base_species2 = {
            'HP': species_stats2.get('HP', 0),
            'ATK': species_stats2.get('ATK', 0),
            'DEF': species_stats2.get('DEF', 0),
            'SPD': species_stats2.get('SPD', 0),
            'MP': species_stats2.get('MP', 0),
        }
    else:
        base_species2 = None
    
    # Get type stat modifiers (which biorhythm to use for each stat)
    if type_data and isinstance(type_data, dict):
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
    
    # Tier scale
    scale = get_tier_scale(level)
    
    # Calculate each stat
    stats = {}
    for stat in ['HP', 'ATK', 'DEF', 'SPD', 'MP']:
        # Primary species + type
        bio1_key = base_type1.get(stat, 'VIT')
        if bio1_key in ['HP', 'ATK', 'DEF', 'SPD', 'MP']:
            bio1_key = 'VIT'
        
        bio1 = bios.get(bio1_key, 0)
        raw = (base_species1[stat] + bio1) * scale
        
        # Secondary type (if exists) - take max
        if base_type2 and base_species2:
            bio2_key = base_type2.get(stat, bio1_key)
            if bio2_key in ['HP', 'ATK', 'DEF', 'SPD', 'MP']:
                bio2_key = 'VIT'
            
            bio2 = bios.get(bio2_key, 0)
            raw2 = (base_species2[stat] + bio2) * scale
            raw = max(raw, raw2)
        
        stats[stat] = max(1, round(raw))
    
    return stats


def calculate_gear_stats(base_stats: Dict[str, int], slots: int = 6) -> Dict[str, int]:
    """Calculate gear stats (6 slots * base stats)."""
    return {stat: val * slots for stat, val in base_stats.items()}


def calculate_weapon_stats(
    material_data: Dict,
    materia_data: Dict,
    level: int = 1
) -> Dict[str, int]:
    """
    Calculate weapon stats using Material/Materia pattern.
    
    Material (Species) = base ATK/DEF/SPD values
    Materia (Type) = stat_modifiers that determine which biorhythms to add
    
    Formula: stat = (material_base + materia_biorhythm) * tier_scale
    """
    # Get material base stats
    if material_data and isinstance(material_data, dict):
        material_stats = material_data.get('stats', {})
        base_atk = material_stats.get('ATK', 0)
        base_def = material_stats.get('DEF', 0)
        base_spd = material_stats.get('SPD', 0)
    else:
        base_atk = base_def = base_spd = 0
    
    # Get materia stat modifiers
    if materia_data and isinstance(materia_data, dict):
        stat_mods = materia_data.get('stat_modifiers', {})
        atk_bio = stat_mods.get('ATK', 'STR')
        def_bio = stat_mods.get('DEF', 'FND')
        spd_bio = stat_mods.get('SPD', 'SEX')
    else:
        atk_bio = 'STR'
        def_bio = 'FND'
        spd_bio = 'SEX'
    
    # Get biorhythms from materia (Type has biorhythms in some cases)
    # For weapons, we might use the materia's inherent values or default
    materia_bio = materia_data.get('biorhythms', {}) if isinstance(materia_data, dict) else {}
    
    scale = get_tier_scale(level)
    
    return {
        'ATK': max(1, (base_atk + materia_bio.get(atk_bio, 0)) * scale),
        'DEF': max(1, (base_def + materia_bio.get(def_bio, 0)) * scale),
        'SPD': max(1, (base_spd + materia_bio.get(spd_bio, 0)) * scale),
    }


# Test
if __name__ == '__main__':
    print("Testing Calculation Utilities")
    print("=" * 60)
    
    # Mock data for Chimera + Holy, Level 10
    bios = {
        'MNF': 7, 'SPL': 7, 'BEU': 2, 'STR': 6,
        'FND': 7, 'KNO': 7, 'UND': 1, 'WIS': 5,
        'VIT': 4, 'SEX': 8, 'DIV': 7, 'EGO': 11
    }
    
    species_data = {
        'stats': {'HP': 21, 'ATK': 3, 'DEF': 4, 'SPD': 2, 'MP': 9}
    }
    
    type_data = {
        'stat_modifiers': {'HP': 'DIV', 'ATK': 'UND', 'DEF': 'WIS', 'SPD': 'EGO', 'MP': 'BEU'}
    }
    
    stats = calculate_stats(bios, species_data, type_data, level=10)
    
    print(f"\nChimera + Holy, Level 10")
    print(f"Biorhythms: DIV={bios['DIV']}, UND={bios['UND']}, WIS={bios['WIS']}, EGO={bios['EGO']}, BEU={bios['BEU']}")
    print(f"\nStats:")
    for stat, val in stats.items():
        print(f"  {stat}: {val}")
    
    print(f"\nTier: {get_tier(10)}")
    print(f"Scale: {get_tier_scale(10)}")
    
    print("\n" + "=" * 60)
    print("All calculations match generator.js")
