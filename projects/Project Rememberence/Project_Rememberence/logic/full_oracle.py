from rememberence_core.logic.oracle_engine import oracle
from rememberence_core.logic.atmosphere_engine import oracle_audio
from rememberence_core.dialogue_systems.hybrid_chat import oracle_dialogue
from rememberence_core.dice_engine.anydice_logic import oracle_dice
from rememberence_core.generators.donjon_hybrid import oracle_gen
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from mechanics.game_rules import CharacterGenerator, CombatMechanics, ProgressionSystem

class AIRAIFullOracle:
    def __init__(self):
        self.engine = oracle
        self.audio = oracle_audio
        self.dialogue = oracle_dialogue
        self.dice = oracle_dice
        self.gen = oracle_gen
        self.char_gen = CharacterGenerator()
        self.combat = CombatMechanics(oracle.board)
        self.progression = ProgressionSystem()

    def handle_user_input(self, text):
        # 1. Check for Game Command
        if text.lower().startswith("/"):
            return self.process_command(text[1:])
        
        # 2. Character Generation Flow
        if self.char_gen.get_current_step():
            return self.handle_generation_flow(text)

        # 3. Standard Dialogue
        return self.dialogue.get_response(text)

    def handle_generation_flow(self, text):
        step = self.char_gen.get_current_step()
        if not step: return "The void of creation is empty."
        
        res = self.char_gen.process_choice(text)
        next_step = self.char_gen.get_current_step()
        
        if next_step:
            return f"{res}\n\nNext: {next_step[0]}. What is your choice?"
        else:
            return f"{res}\n\nYour Spirit is formed. Now, give them a name and a description."

    def process_command(self, cmd):
        # Router for /move, /attack, /status, /phase etc.
        parts = cmd.split()
        action = parts[0].lower()
        args = parts[1:]
        
        if action == "move": return self.engine.process_command("move", args)
        if action == "attack": return self.engine.process_command("attack", args)
        if action == "phase": return self.combat.advance_phase()
        if action == "status": return self.engine.process_command("status", args)
        
        return "The Oracle does not comprehend this command."

# Singleton for the session
full_oracle = AIRAIFullOracle()
