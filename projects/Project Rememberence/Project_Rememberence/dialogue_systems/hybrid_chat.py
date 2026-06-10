import random

class HybridDialogueSystem:
    """
    Combines AIML-style pattern matching with Perchance-style weighted randomization.
    This allows the AIR-AI Oracle to provide consistent 'Core' responses 
    while maintaining the 'Ever-Changing' nature of Rememberence.
    """
    def __init__(self):
        # AIML-style patterns: { "Pattern": "Response Template" }
        self.core_patterns = {
            "who are you": "I am the AIR-AI Oracle. The memory of all that was, and all that could have been.",
            "what is rememberence": "A game that breaks the fourth wall and plays with your mind... a journey through a cosmic fantasy world.",
            "help": "You may move through layers, attack the echoes of the void, or simply observe the weave. Use commands like 'move', 'attack', or 'status'."
        }
        
        # Perchance-style lists: [ "Option A", "Option B" ]
        self.flavor_text = {
            "greeting": [
                "The air shimmers as I acknowledge you.",
                "Your presence creates a ripple in the weave.",
                "I have felt your approach in the silence between breaths."
            ],
            "combat_start": [
                "The struggle begins, a clash of biorhythms.",
                "Shatter the silence. Strike now.",
                "The weave tightens. Resistance is inevitable."
            ],
            "void_whisper": [
                "Do you feel the weight of the memories you've forgotten?",
                "Everything is connected to Rememberence... even this moment.",
                "Sshhh... the void is speaking. Can you hear it?"
            ]
        }

    def get_response(self, user_input: str, context: str = "neutral"):
        user_input = user_input.lower()
        
        # 1. Check AIML Core Patterns (High Priority)
        for pattern, response in self.core_patterns.items():
            if pattern in user_input:
                return f"{self._get_flavor('greeting')}\n\n{response}"
        
        # 2. Contextual Randomization (Perchance Style)
        if context == "combat":
            return random.choice(self.flavor_text["combat_start"])
        if context == "idle":
            return random.choice(self.flavor_text["void_whisper"])
            
        return "The Oracle listens, but the weave remains silent. Speak more clearly."

    def _get_flavor(self, category):
        return random.choice(self.flavor_text.get(category, ["..."]))

oracle_dialogue = HybridDialogueSystem()
