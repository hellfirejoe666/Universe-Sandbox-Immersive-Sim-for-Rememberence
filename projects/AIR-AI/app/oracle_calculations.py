"""
oracle_calculations.py
DEPRECATED: This file is kept for backward compatibility.
All calculations now use rememberence_core.logic.biorhythm_calculator.py as the single source of truth.
"""

# Re-export from canonical source
import sys
import os
# Add workspace root to path
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from rememberence_core.logic.biorhythm_calculator import (
    BIORHYTHM_KEYS,
    ANIMAL_SIGNS,
    STAR_SIGNS,
    SPECIES_BASE,
    TYPE_MODIFIERS,
    TIER_MULTIPLIERS,
    calculate_biorhythms,
    generate_thoughts,
    calculate_combat_stats,
    roll_dice,
    generate_character_payload
)

# ────────────────────────────────────────────────
# Biorhythm Data (12 stats)
# ────────────────────────────────────────────────

BIORHYTHM_KEYS = ['MNF', 'SPL', 'BEU', 'STR', 'FND', 'KNO', 
                  'UND', 'WIS', 'VIT', 'SEX', 'DIV', 'EGO']

# Animal Signs with biorhythm bonuses
ANIMAL_SIGNS = {
    'Rat': {'MNF': 3, 'SPL': 2, 'BEU': 1, 'STR': 0, 'FND': 1, 'KNO': 2, 
            'UND': 1, 'WIS': 2, 'VIT': 3, 'SEX': 2, 'DIV': 1, 'EGO': 2},
    'Ox': {'MNF': 2, 'SPL': 1, 'BEU': 2, 'STR': 3, 'FND': 3, 'KNO': 1, 
           'UND': 2, 'WIS': 2, 'VIT': 1, 'SEX': 1, 'DIV': 2, 'EGO': 3},
    'Tiger': {'MNF': 3, 'SPL': 2, 'BEU': 2, 'STR': 3, 'FND': 1, 'KNO': 1, 
              'UND': 2, 'WIS': 1, 'VIT': 3, 'SEX': 3, 'DIV': 1, 'EGO': 3},
    'Rabbit': {'MNF': 2, 'SPL': 3, 'BEU': 2, 'STR': 1, 'FND': 2, 'KNO': 2, 
               'UND': 3, 'WIS': 2, 'VIT': 2, 'SEX': 2, 'DIV': 2, 'EGO': 1},
    'Dragon': {'MNF': 4, 'SPL': 2, 'BEU': 2, 'STR': 3, 'FND': 2, 'KNO': 2, 
               'UND': 2, 'WIS': 3, 'VIT': 3, 'SEX': 2, 'DIV': 3, 'EGO': 4},
    'Snake': {'MNF': 3, 'SPL': 2, 'BEU': 2, 'STR': 2, 'FND': 2, 'KNO': 3, 
              'UND': 3, 'WIS': 3, 'VIT': 2, 'SEX': 2, 'DIV': 2, 'EGO': 2},
    'Horse': {'MNF': 3, 'SPL': 2, 'BEU': 3, 'STR': 2, 'FND': 2, 'KNO': 2, 
              'UND': 1, 'WIS': 2, 'VIT': 3, 'SEX': 3, 'DIV': 2, 'EGO': 2},
    'Goat': {'MNF': 2, 'SPL': 2, 'BEU': 2, 'STR': 1, 'FND': 3, 'KNO': 2, 
             'UND': 2, 'WIS': 3, 'VIT': 2, 'SEX': 2, 'DIV': 2, 'EGO': 2},
    'Monkey': {'MNF': 3, 'SPL': 3, 'BEU': 2, 'STR': 2, 'FND': 1, 'KNO': 3, 
               'UND': 2, 'WIS': 3, 'VIT': 3, 'SEX': 2, 'DIV': 2, 'EGO': 3},
    'Rooster': {'MNF': 2, 'SPL': 2, 'BEU': 2, 'STR': 2, 'FND': 2, 'KNO': 2, 
                'UND': 2, 'WIS': 2, 'VIT': 3, 'SEX': 2, 'DIV': 3, 'EGO': 3},
    'Dog': {'MNF': 2, 'SPL': 2, 'BEU': 3, 'STR': 2, 'FND': 3, 'KNO': 2, 
            'UND': 2, 'WIS': 2, 'VIT': 2, 'SEX': 2, 'DIV': 2, 'EGO': 2},
    'Pig': {'MNF': 2, 'SPL': 2, 'BEU': 3, 'STR': 2, 'FND': 3, 'KNO': 2, 
            'UND': 2, 'WIS': 2, 'VIT': 2, 'SEX': 3, 'DIV': 2, 'EGO': 2}
}

# Star Signs with biorhythm bonuses
STAR_SIGNS = {
    'Aries': {'MNF': 3, 'SPL': 1, 'BEU': 2, 'STR': 3, 'FND': 1, 'KNO': 1, 
              'UND': 1, 'WIS': 1, 'VIT': 3, 'SEX': 3, 'DIV': 2, 'EGO': 3},
    'Taurus': {'MNF': 2, 'SPL': 2, 'BEU': 2, 'STR': 3, 'FND': 3, 'KNO': 2, 
               'UND': 2, 'WIS': 2, 'VIT': 2, 'SEX': 2, 'DIV': 2, 'EGO': 2},
    'Gemini': {'MNF': 3, 'SPL': 3, 'BEU': 2, 'STR': 1, 'FND': 2, 'KNO': 3, 
               'UND': 2, 'WIS': 3, 'VIT': 3, 'SEX': 2, 'DIV': 2, 'EGO': 2},
    'Cancer': {'MNF': 2, 'SPL': 3, 'BEU': 3, 'STR': 1, 'FND': 3, 'KNO': 2, 
               'UND': 3, 'WIS': 2, 'VIT': 2, 'SEX': 2, 'DIV': 2, 'EGO': 1},
    'Leo': {'MNF': 3, 'SPL': 2, 'BEU': 2, 'STR': 3, 'FND': 2, 'KNO': 2, 
            'UND': 2, 'WIS': 2, 'VIT': 3, 'SEX': 3, 'DIV': 3, 'EGO': 3},
    'Virgo': {'MNF': 2, 'SPL': 2, 'BEU': 2, 'STR': 2, 'FND': 3, 'KNO': 3, 
              'UND': 2, 'WIS': 3, 'VIT': 2, 'SEX': 1, 'DIV': 2, 'EGO': 2},
    'Libra': {'MNF': 2, 'SPL': 2, 'BEU': 2, 'STR': 2, 'FND': 2, 'KNO': 2, 
              'UND': 2, 'WIS': 3, 'VIT': 2, 'SEX': 2, 'DIV': 3, 'EGO': 2},
    'Scorpio': {'MNF': 3, 'SPL': 2, 'BEU': 2, 'STR': 3, 'FND': 2, 'KNO': 2, 
                'UND': 3, 'WIS': 2, 'VIT': 2, 'SEX': 3, 'DIV': 2, 'EGO': 3},
    'Sagittarius': {'MNF': 3, 'SPL': 2, 'BEU': 3, 'STR': 2, 'FND': 2, 'KNO': 2, 
                    'UND': 2, 'WIS': 3, 'VIT': 3, 'SEX': 2, 'DIV': 3, 'EGO': 2},
    'Capricorn': {'MNF': 2, 'SPL': 1, 'BEU': 2, 'STR': 3, 'FND': 3, 'KNO': 2, 
                  'UND': 2, 'WIS': 3, 'VIT': 1, 'SEX': 1, 'DIV': 2, 'EGO': 3},
    'Aquarius': {'MNF': 3, 'SPL': 3, 'BEU': 2, 'STR': 2, 'FND': 2, 'KNO': 3, 
                 'UND': 2, 'WIS': 3, 'VIT': 3, 'SEX': 2, 'DIV': 3, 'EGO': 2},
    'Pisces': {'MNF': 2, 'SPL': 3, 'BEU': 3, 'STR': 1, 'FND': 2, 'KNO': 2, 
               'UND': 3, 'WIS': 2, 'VIT': 2, 'SEX': 2, 'DIV': 3, 'EGO': 1}
}

# Species base combat stats
SPECIES_BASE = {
    'Human': {'HP': 100, 'ATK': 10, 'DEF': 10, 'SPD': 10, 'MP': 50},
    'Elf': {'HP': 80, 'ATK': 12, 'DEF': 8, 'SPD': 14, 'MP': 80},
    'Dwarf': {'HP': 120, 'ATK': 12, 'DEF': 14, 'SPD': 6, 'MP': 40},
    'Orc': {'HP': 110, 'ATK': 14, 'DEF': 10, 'SPD': 8, 'MP': 30},
    'Imp': {'HP': 60, 'ATK': 14, 'DEF': 6, 'SPD': 16, 'MP': 70},
    'Merr': {'HP': 70, 'ATK': 11, 'DEF': 9, 'SPD': 13, 'MP': 90},
    'Pixie': {'HP': 50, 'ATK': 10, 'DEF': 7, 'SPD': 18, 'MP': 100},
    'Drakian': {'HP': 130, 'ATK': 15, 'DEF': 12, 'SPD': 7, 'MP': 60},
    'Vampyre': {'HP': 90, 'ATK': 13, 'DEF': 9, 'SPD': 12, 'MP': 70},
    'Spirit': {'HP': 75, 'ATK': 11, 'DEF': 8, 'SPD': 11, 'MP': 95}
}

# Type modifiers
TYPE_MODIFIERS = {
    'Warrior': {'HP': 20, 'ATK': 5, 'DEF': 5, 'SPD': -2, 'MP': -10},
    'Beast': {'HP': 15, 'ATK': 5, 'DEF': 2, 'SPD': 3, 'MP': -15},
    'Psychic': {'HP': -10, 'ATK': 2, 'DEF': -2, 'SPD': 2, 'MP': 30},
    'Spellcaster': {'HP': -15, 'ATK': -2, 'DEF': -3, 'SPD': 0, 'MP': 40},
    'Rogue': {'HP': 5, 'ATK': 3, 'DEF': -2, 'SPD': 5, 'MP': 10},
    'Guardian': {'HP': 25, 'ATK': 0, 'DEF': 8, 'SPD': -3, 'MP': 5},
    'Healer': {'HP': 0, 'ATK': -3, 'DEF': 2, 'SPD': 0, 'MP': 35},
    'Monk': {'HP': 10, 'ATK': 4, 'DEF': 3, 'SPD': 4, 'MP': 15}
}

# Tier multipliers
TIER_MULTIPLIERS = {
    'Novice': 1.0,
    'Beginner': 1.2,
    'Mediate': 1.5,
    'Advanced': 2.0,
    'Master': 3.0,
    'Deity': 5.0,
    'Universe': 10.0
}


# ────────────────────────────────────────────────
# Backward Compatibility Aliases
# ────────────────────────────────────────────────
# Note: All functions now delegate to the canonical implementation
# in rememberence_core.logic.biorhythm_calculator for consistency.

# Legacy thought formula (AIR-AI uses different names than canonical)
def generate_thoughts_legacy(biorhythms: Dict[str, int]) -> Dict[str, int]:
    """
    Legacy thought generation (AIR-AI formula - different from canonical).
    Canonical uses: Env, Act, Soc, Mag, Spi, Men
    This uses: Environment, Emotion, Subconscious, Conscious, Abstraction, Perception
    """
    thoughts = {
        'Environment': biorhythms.get('FND', 0) - biorhythms.get('EGO', 0),
        'Emotion': biorhythms.get('BEU', 0) - biorhythms.get('DIV', 0),
        'Subconscious': biorhythms.get('SPL', 0) - biorhythms.get('UND', 0),
        'Conscious': biorhythms.get('MNF', 0) - biorhythms.get('SEX', 0),
        'Abstraction': biorhythms.get('KNO', 0) - biorhythms.get('WIS', 0),
        'Perception': biorhythms.get('VIT', 0) - biorhythms.get('STR', 0)
    }
    thoughts['State'] = sum(thoughts.values())
    return thoughts


# Legacy stats calculation with biorhythm bonuses
def calculate_stats(biorhythms: Dict[str, int], species: str, 
                    char_type: str, level: int = 1, tier: str = 'Novice') -> Dict[str, int]:
    """
    Legacy stat calculation with biorhythm bonuses.
    This adds biorhythm-derived bonuses on top of canonical base stats.
    """
    # Get canonical base
    base = calculate_combat_stats(species, char_type, tier, level)
    
    # Add biorhythm bonuses (AIR-AI specific)
    base['HP'] += biorhythms.get('VIT', 0) * 2
    base['ATK'] += biorhythms.get('STR', 0)
    base['DEF'] += biorhythms.get('FND', 0)
    base['SPD'] += biorhythms.get('SPL', 0)
    base['MP'] += biorhythms.get('MNF', 0) * 2
    
    base['Level'] = level
    base['Tier'] = tier
    return base


def roll_d20(modifier: int = 0) -> Tuple[int, int, bool, bool]:
    """
    Roll d20 with modifier.
    Returns: (raw_roll, total, is_critical, is_failure)
    """
    raw = random.randint(1, 20)
    total = raw + modifier
    is_crit = (raw == 20)
    is_fail = (raw == 1)
    return (raw, total, is_crit, is_fail)


def roll_dice(dice_notation: str) -> int:
    """
    Roll dice using standard notation (e.g., '3d6+2', '1d20', '2d10-1')
    Returns total roll result
    """
    import re
    
    match = re.match(r'(\d+)d(\d+)([+-]\d+)?', dice_notation)
    if not match:
        return 0
    
    num_dice = int(match.group(1))
    die_size = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0
    
    total = sum(random.randint(1, die_size) for _ in range(num_dice)) + modifier
    return total


# ────────────────────────────────────────────────
# Oracle Debt Tracking
# ────────────────────────────────────────────────

class OracleDebtTracker:
    """Track oracle debt per seeker per topic"""
    
    def __init__(self):
        self.debt = {}  # {seeker_id: {topic: count}}
        self.session_count = 0
    
    def get_debt(self, seeker_id: str, topic: str) -> int:
        """Get current debt level for seeker/topic"""
        if seeker_id not in self.debt:
            return 0
        return self.debt[seeker_id].get(topic, 0)
    
    def add_debt(self, seeker_id: str, topic: str, amount: int = 1) -> int:
        """Add debt and return new total"""
        if seeker_id not in self.debt:
            self.debt[seeker_id] = {}
        
        current = self.debt[seeker_id].get(topic, 0)
        self.debt[seeker_id][topic] = current + amount
        return self.debt[seeker_id][topic]
    
    def get_status(self, seeker_id: str) -> Dict[str, Any]:
        """Get debt status for seeker"""
        if seeker_id not in self.debt:
            return {
                'seeker_id': seeker_id,
                'topic_debts': {},
                'total_debt': 0,
                'status': 'clear'
            }
        
        topic_debts = self.debt[seeker_id]
        total_debt = sum(topic_debts.values())
        
        if total_debt < 3:
            status = 'clear'
        elif total_debt < 7:
            status = 'clouded'
        else:
            status = 'dangerous'
        
        return {
            'seeker_id': seeker_id,
            'topic_debts': topic_debts,
            'total_debt': total_debt,
            'status': status
        }
    
    def decay_debt(self, seeker_id: str, topic: str = None) -> None:
        """Reduce debt by 1 (called after 3 sessions without consulting same topic)"""
        if seeker_id not in self.debt:
            return
        
        if topic:
            if topic in self.debt[seeker_id]:
                self.debt[seeker_id][topic] = max(0, self.debt[seeker_id][topic] - 1)
        else:
            # Decay all topics
            for t in list(self.debt[seeker_id].keys()):
                self.debt[seeker_id][t] = max(0, self.debt[seeker_id][t] - 1)
    
    def clear_debt(self, seeker_id: str, topic: str = None) -> None:
        """Clear debt for seeker (optionally specific topic)"""
        if seeker_id not in self.debt:
            return
        
        if topic:
            if topic in self.debt[seeker_id]:
                del self.debt[seeker_id][topic]
        else:
            del self.debt[seeker_id]
    
    def to_dict(self) -> Dict:
        """Export debt tracker state"""
        return self.debt
    
    def from_dict(self, data: Dict) -> None:
        """Import debt tracker state"""
        self.debt = data


# ────────────────────────────────────────────────
# Character Creation Helper
# ────────────────────────────────────────────────

def create_character(animal: str, star: str, species: str, 
                     char_type: str, level: int = 1, tier: str = 'Novice') -> Dict[str, Any]:
    """
    Create a complete character with all calculated stats.
    """
    biorhythms = calculate_biorhythms(animal, star)
    thoughts = generate_thoughts(biorhythms)
    stats = calculate_stats(biorhythms, species, char_type, level, tier)
    
    return {
        'animal_sign': animal,
        'star_sign': star,
        'species': species,
        'type': char_type,
        'level': level,
        'tier': tier,
        'biorhythms': biorhythms,
        'thoughts': thoughts,
        'stats': stats,
        'created': datetime.now().isoformat()
    }


# ────────────────────────────────────────────────
# Test/Demo Functions
# ────────────────────────────────────────────────

if __name__ == '__main__':
    print("=== AIR-AI Oracle Calculations Test ===\n")
    
    # Test character creation
    print("--- Character Creation ---")
    char = create_character('Dragon', 'Scorpio', 'Human', 'Warrior', level=1, tier='Novice')
    print(f"Animal: {char['animal_sign']}, Star: {char['star_sign']}")
    print(f"Species: {char['species']}, Type: {char['type']}")
    print(f"\nBiorhythms: {char['biorhythms']}")
    print(f"\nThoughts: {char['thoughts']}")
    print(f"\nCombat Stats: {char['stats']}")
    
    # Test dice rolling
    print("\n--- Dice Rolling ---")
    for _ in range(5):
        raw, total, crit, fail = roll_d20(2)
        crit_fail = "CRIT!" if crit else "FAIL!" if fail else ""
        print(f"  d20+2: {raw} + 2 = {total} {crit_fail}")
    
    print(f"\n  3d6+1: {roll_dice('3d6+1')}")
    print(f"  2d10: {roll_dice('2d10')}")
    
    # Test oracle debt
    print("\n--- Oracle Debt Tracking ---")
    tracker = OracleDebtTracker()
    tracker.add_debt('player1', 'quest', 1)
    tracker.add_debt('player1', 'quest', 1)
    tracker.add_debt('player1', 'future', 3)
    print(f"  Player1 status: {tracker.get_status('player1')}")
    
    tracker.add_debt('player1', 'quest', 1)
    tracker.add_debt('player1', 'quest', 1)
    tracker.add_debt('player1', 'quest', 1)
    print(f"  After more queries: {tracker.get_status('player1')}")
