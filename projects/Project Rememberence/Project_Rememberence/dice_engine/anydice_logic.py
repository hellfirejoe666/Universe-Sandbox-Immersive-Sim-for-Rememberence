import random
import math

class AnyDiceEngine:
    """
    Implementation of AnyDice-style notation for Rememberence.
    Supports: 
    - '3d6' (Sum of 3 six-sided dice)
    - '1d20+5' (1 twenty-sided die plus 5)
    - '2d10-2' (2 ten-sided dice minus 2)
    - 'd12' (Shorthand for 1d12)
    """
    def roll(self, formula: str) -> int:
        formula = formula.replace(" ", "").lower()
        
        # Handle simple d12/d20 cases
        if formula.startswith('d') and len(formula) > 1 and formula[1:].isdigit():
            return random.randint(1, int(formula[1:]))

        # Parse standard notation: [count]d[sides][op][mod]
        pattern = r'^(\d*)d(\d+)([+-]\d+)?$'
        import re
        match = re.match(pattern, formula)
        if not match:
            return 0 # Or throw error
        
        count = int(match.group(1)) if match.group(1) else 1
        sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        total = sum(random.randint(1, sides) for _ in range(count))
        return total + modifier

    def simulate_distribution(self, formula: str, trials: int = 1000):
        """Simulates a roll to provide the Oracle with probability distributions."""
        results = [self.roll(formula) for _ in range(trials)]
        return {
            "min": min(results),
            "max": max(results),
            "avg": sum(results) / trials,
            "median": sorted(results)[trials // 2]
        }

oracle_dice = AnyDiceEngine()
