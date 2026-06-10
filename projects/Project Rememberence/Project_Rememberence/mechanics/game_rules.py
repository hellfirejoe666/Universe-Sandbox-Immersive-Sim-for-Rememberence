import random
from typing import Dict, List, Any

class CharacterGenerator:
    """
    Implements the structured 'Getting Started' flow from Project Instructions 5.0.
    Guide users through: Zodiac -> Star Sign -> Species -> Type -> Classes.
    """
    def __init__(self, lore_path=r'D:\Ollama\OpenClaw\workspace\Rememberence'):
        self.lore_path = lore_path
        self.step = 0
        self.current_character = {}
        self.steps = [
            ("Zodiac Animal", "zodiac"),
            ("Star Sign", "star_sign"),
            ("Species", "species"),
            ("Type", "type"),
            ("Classes", "classes")
        ]

    def get_current_step(self):
        if self.step < len(self.steps):
            return self.steps[self.step]
        return None

    def process_choice(self, choice: Any):
        step_name, key = self.steps[self.step]
        self.current_character[key] = choice
        self.step += 1
        return f"The weave accepts your {step_name}. The path narrows."

    def reset(self):
        self.step = 0
        self.current_character = {}

class CombatMechanics:
    """
    Detailed combat implementation based on TTRPG rules.
    Includes Turn Phases: Upkeep -> Main 1 -> Combat -> Main 2 -> End.
    """
    def __init__(self, board_instance):
        self.board = board_instance
        self.current_phase = "Upkeep"
        self.turn_count = 1

    def advance_phase(self):
        phases = ["Upkeep", "Main Phase 1", "Combat Phase", "Main Phase 2", "End Phase"]
        curr_idx = phases.index(self.current_phase)
        if curr_idx < len(phases) - 1:
            self.current_phase = phases[curr_idx + 1]
        else:
            self.current_phase = "Upkeep"
            self.turn_count += 1
        return self.current_phase

    def resolve_attack(self, attacker_name, target_name, pattern="Omni"):
        """
        Uses the Biorhythm-as-ATK and Loyalty-as-HP logic.
        """
        # Integration with BattleBoard from oracle_engine
        res = self.board.attack_pawn(attacker_name, target_name)
        # Add logic for pattern (Lateral, Diagonal, Omni)
        if pattern != "Omni":
            res += f" [Pattern: {pattern} modified accuracy]"
        return res

class ProgressionSystem:
    """
    Tiers: NoviceI (1-10) -> ... -> Omniversal (100b+)
    Scaling: Lvl x 100 x Lvl x factor.
    """
    TIERS = ["NoviceI", "NoviceII", "Adept", "Master", "Transcendent", "Omniversal"]

    @staticmethod
    def get_tier(level):
        # Simple mapping for implementation
        if level < 10: return "NoviceI"
        if level < 20: return "NoviceII"
        if level < 50: return "Adept"
        if level < 100: return "Master"
        if level < 1000: return "Transcendent"
        return "Omniversal"

    @staticmethod
    def calculate_exp(level):
        return level * 100 * level * 0.5 # Simplified factor
