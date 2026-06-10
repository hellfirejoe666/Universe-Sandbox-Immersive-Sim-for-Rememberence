"""Trace where biorhythm data is lost"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from world_state import WorldManager
from character_sheet import CharacterSheetGenerator

# Create world
manager = WorldManager()
world = manager.create_world("TraceTest")

# Generate character
gen = CharacterSheetGenerator()
char = gen.generate_character(level=10)
char['name'] = "Trace Test"

print("=" * 60)
print("STEP 1: After generate_character()")
print("=" * 60)
print(f"Biorhythms: {char.get('biorhythms', {})}")
print(f"MNF: {char.get('biorhythms', {}).get('MNF', 'MISSING')}")

# Add to world
char_id = world.add_character(char)

print("\n" + "=" * 60)
print("STEP 2: After add_character()")
print("=" * 60)
stored = world.characters[char_id]
print(f"Biorhythms: {stored.get('biorhythms', {})}")
print(f"MNF: {stored.get('biorhythms', {}).get('MNF', 'MISSING')}")

# Get via method
retrieved = world.get_active_character()

print("\n" + "=" * 60)
print("STEP 3: Via get_active_character()")
print("=" * 60)
print(f"Biorhythms: {retrieved.get('biorhythms', {})}")
print(f"MNF: {retrieved.get('biorhythms', {}).get('MNF', 'MISSING')}")
