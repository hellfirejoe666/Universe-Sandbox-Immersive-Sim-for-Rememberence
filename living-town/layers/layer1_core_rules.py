"""
Layer 1: Core Rules/Physics

The foundation layer. Biorhythms, dice rolls, and basic procedures.
All higher layers depend on these rules.

Uses canonical data from data_loader.py (JSON files from Project Rememberence).
"""

import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Import data loader for canonical game data
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_loader import get_loader


# ────────────────────────────────────────────────
# Biorhythm Constants
# ────────────────────────────────────────────────

BIO_KEYS = ['MNF', 'SPL', 'BEU', 'STR', 'FND', 'KNO', 'UND', 'WIS', 'VIT', 'SEX', 'DIV', 'EGO']

THOUGHT_PAIRS = {
    'Environment': ('FND', 'EGO'),      # FND - EGO
    'Emotion': ('BEU', 'DIV'),          # BEU - DIV
    'Subconscious': ('SPL', 'UND'),     # SPL - UND
    'Conscious': ('MNF', 'SEX'),        # MNF - SEX
    'Abstraction': ('KNO', 'WIS'),      # KNO - WIS
    'Perception': ('VIT', 'STR')        # VIT - STR
}


# ────────────────────────────────────────────────
# Data Classes
# ────────────────────────────────────────────────

@dataclass
class Biorhythms:
    """12 biorhythm values (1-20 each)."""
    MNF: int = 10
    SPL: int = 10
    BEU: int = 10
    STR: int = 10
    FND: int = 10
    KNO: int = 10
    UND: int = 10
    WIS: int = 10
    VIT: int = 10
    SEX: int = 10
    DIV: int = 10
    EGO: int = 10
    
    def to_dict(self) -> Dict[str, int]:
        return {k: getattr(self, k) for k in BIO_KEYS}
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'Biorhythms':
        return cls(**{k: data.get(k, 10) for k in BIO_KEYS})
    
    def sum(self) -> int:
        return sum(getattr(self, k) for k in BIO_KEYS)


@dataclass
class Thoughts:
    """6 thought parameters derived from biorhythm pairs."""
    Environment: int = 0
    Emotion: int = 0
    Subconscious: int = 0
    Conscious: int = 0
    Abstraction: int = 0
    Perception: int = 0
    State: float = 0.0  # Average of all thoughts
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'Environment': self.Environment,
            'Emotion': self.Emotion,
            'Subconscious': self.Subconscious,
            'Conscious': self.Conscious,
            'Abstraction': self.Abstraction,
            'Perception': self.Perception,
            'State': self.State
        }


# ────────────────────────────────────────────────
# Core Calculations (Using Canonical Data)
# ────────────────────────────────────────────────

def calculate_biorhythms(animal_sign: str, star_sign: str) -> Biorhythms:
    """
    Calculate 12 biorhythms from Animal + Star sign combination.
    
    Uses canonical data from JSON files (Project Rememberence data).
    Falls back to procedural generation if data not found.
    """
    loader = get_loader()
    
    # Get animal sign data
    animal_data = loader.get_animal_sign(animal_sign)
    if not animal_data:
        # Fallback: procedural generation
        return _procedural_biorhythms(animal_sign, star_sign)
    
    # Get star sign data
    star_data = loader.get_star_sign(star_sign)
    if not star_data:
        # Fallback: procedural generation
        return _procedural_biorhythms(animal_sign, star_sign)
    
    # Combine biorhythms from both signs
    animal_bio = animal_data.get('biorhythms', {})
    star_bio = star_data.get('biorhythms', {})
    
    # Add corresponding values
    combined = {}
    for key in BIO_KEYS:
        animal_val = animal_bio.get(key, 10)
        star_val = star_bio.get(key, 10)
        combined[key] = animal_val + star_val
    
    return Biorhythms(**combined)


def _procedural_biorhythms(animal_sign: str, star_sign: str) -> Biorhythms:
    """
    Fallback procedural generation (if JSON data unavailable).
    Seeds based on sign names for consistency.
    """
    seed_str = f"{animal_sign}_{star_sign}"
    seed = sum(ord(c) for c in seed_str)
    random.seed(seed)
    
    bios = {}
    for key in BIO_KEYS:
        # Generate with structure (not pure random)
        base = 5 + (sum(ord(c) for c in key) % 10)
        variation = random.randint(-3, 3)
        bios[key] = max(1, min(20, base + variation))
    
    random.seed()  # Reset seed
    return Biorhythms(**bios)


def generate_thoughts(biorhythms: Biorhythms) -> Thoughts:
    """
    Generate 6 thought parameters from biorhythm pairs.
    
    Each thought is the difference between paired biorhythms.
    Range: approximately -19 to +19
    """
    thoughts = {}
    
    for thought_name, (bio1_key, bio2_key) in THOUGHT_PAIRS.items():
        bio1 = getattr(biorhythms, bio1_key)
        bio2 = getattr(biorhythms, bio2_key)
        thoughts[thought_name] = bio1 - bio2
    
    # Calculate state (average of absolute thought values)
    avg = sum(abs(v) for v in thoughts.values()) / len(thoughts)
    thoughts['State'] = round(avg, 2)
    
    return Thoughts(**thoughts)


# ────────────────────────────────────────────────
# Dice Rolling
# ────────────────────────────────────────────────

def roll_dice(sides: int = 20, modifier: int = 0, advantage: bool = False, 
              disadvantage: bool = False) -> Tuple[int, List[int], bool, bool]:
    """
    Roll dice with optional modifier and advantage/disadvantage.
    
    Args:
        sides: Number of sides on the die (default 20)
        modifier: Flat modifier to add to result
        advantage: Roll twice, take higher
        disadvantage: Roll twice, take lower
    
    Returns:
        Tuple of (total, rolls_list, is_critical, is_failure)
    """
    rolls = []
    
    if advantage:
        rolls = [random.randint(1, sides) for _ in range(2)]
        result = max(rolls)
    elif disadvantage:
        rolls = [random.randint(1, sides) for _ in range(2)]
        result = min(rolls)
    else:
        rolls = [random.randint(1, sides)]
        result = rolls[0]
    
    total = result + modifier
    is_critical = (result == sides)
    is_failure = (result == 1)
    
    return (total, rolls, is_critical, is_failure)


# ────────────────────────────────────────────────
# Compatibility Calculation
# ────────────────────────────────────────────────

def calculate_compatibility(bio1: Biorhythms, bio2: Biorhythms) -> Dict[str, float]:
    """
    Calculate compatibility between two biorhythm profiles.
    
    Returns:
        Dict with compatibility scores for different aspects
    """
    # Overall compatibility (inverse of total difference)
    total_diff = sum(abs(getattr(bio1, key) - getattr(bio2, key)) for key in BIO_KEYS)
    max_diff = 19 * len(BIO_KEYS)  # Max possible difference
    overall = ((max_diff - total_diff) / max_diff) * 100
    
    # Specific aspects
    mental_compat = 100 - (
        abs(bio1.KNO - bio2.KNO) +
        abs(bio1.WIS - bio2.WIS) +
        abs(bio1.EGO - bio2.EGO)
    ) * 3
    
    physical_compat = 100 - (
        abs(bio1.STR - bio2.STR) +
        abs(bio1.VIT - bio2.VIT) +
        abs(bio1.MNF - bio2.MNF)
    ) * 3
    
    spiritual_compat = 100 - (
        abs(bio1.SPL - bio2.SPL) +
        abs(bio1.UND - bio2.UND) +
        abs(bio1.DIV - bio2.DIV)
    ) * 3
    
    return {
        'overall': max(0, min(100, overall)),
        'mental': max(0, min(100, mental_compat)),
        'physical': max(0, min(100, physical_compat)),
        'spiritual': max(0, min(100, spiritual_compat)),
    }

# Alias for backward compatibility
biorhythm_compatibility = calculate_compatibility


# ────────────────────────────────────────────────
# Data Access Helpers
# ────────────────────────────────────────────────

def get_all_animal_signs() -> Dict:
    """Get all animal signs from canonical data."""
    return get_loader().get_all_animal_signs()


def get_all_star_signs() -> Dict:
    """Get all star signs from canonical data."""
    return get_loader().get_all_star_signs()


def get_canonical_species(name: str) -> Optional[Dict]:
    """Get species data from canonical data."""
    return get_loader().get_species(name)


def get_canonical_type(name: str) -> Optional[Dict]:
    """Get type data from canonical data."""
    return get_loader().get_type(name)


# ────────────────────────────────────────────────
# Test
# ────────────────────────────────────────────────

if __name__ == '__main__':
    print("Testing Layer 1: Core Rules (with canonical data)")
    print("=" * 60)
    
    # Test biorhythm calculation
    print("\nBiorhythm Calculation (Dragon + Scorpio):")
    bio = calculate_biorhythms("Dragon", "Scorpio")
    print(f"  MNF={bio.MNF:2d}  SPL={bio.SPL:2d}  BEU={bio.BEU:2d}")
    print(f"  STR={bio.STR:2d}  FND={bio.FND:2d}  KNO={bio.KNO:2d}")
    print(f"  UND={bio.UND:2d}  WIS={bio.WIS:2d}  VIT={bio.VIT:2d}")
    print(f"  SEX={bio.SEX:2d}  DIV={bio.DIV:2d}  EGO={bio.EGO:2d}")
    print(f"  Sum: {bio.sum()}")
    
    # Test thought generation
    print("\nThought Generation:")
    thoughts = generate_thoughts(bio)
    print(f"  Environment:   {thoughts.Environment:3d}  (Chaos/Order)")
    print(f"  Emotion:       {thoughts.Emotion:3d}  (Fear/Love)")
    print(f"  Subconscious:  {thoughts.Subconscious:3d}  (Reject/Embrace)")
    print(f"  Conscious:     {thoughts.Conscious:3d}  (Passive/Active)")
    print(f"  Abstraction:   {thoughts.Abstraction:3d}  (Lived/Learned)")
    print(f"  Perception:    {thoughts.Perception:3d}  (Negative/Positive)")
    print(f"  State:         {thoughts.State:.1f}")
    
    # Test dice rolling
    print("\nDice Rolling:")
    for mod in [0, 2, 5]:
        total, rolls, crit, fail = roll_dice(20, modifier=mod)
        crit_str = " [CRIT!]" if crit else (" [FAIL]" if fail else "")
        print(f"  d20+{mod}: {rolls[0]:2d} + {mod} = {total:2d}{crit_str}")
    
    # Test compatibility
    print("\nCompatibility (Dragon/Scorpio vs Tiger/Aries):")
    bio2 = calculate_biorhythms("Tiger", "Aries")
    compat = calculate_compatibility(bio, bio2)
    print(f"  Overall:   {compat['overall']:.0f}%")
    print(f"  Mental:    {compat['mental']:.0f}%")
    print(f"  Physical:  {compat['physical']:.0f}%")
    print(f"  Spiritual: {compat['spiritual']:.0f}%")
    
    # Test data access
    print("\nCanonical Data:")
    animals = get_all_animal_signs()
    stars = get_all_star_signs()
    print(f"  Animal signs: {len(animals)}")
    print(f"  Star signs: {len(stars)}")
    print(f"  Total combinations: {len(animals) * len(stars)}")
    
    print("\n" + "=" * 60)
