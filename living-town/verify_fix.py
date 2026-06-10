"""Verify character sheet displays correctly"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from world_state import WorldManager
from character_sheet import CharacterSheetGenerator
from calc_utils import calculate_biorhythms, calculate_thoughts, calculate_stats

# Setup
manager = WorldManager()
world = manager.create_world("VerifyTest")

# Create character matching user's test
gen = CharacterSheetGenerator()
char = gen.generate_character(level=10)
char['name'] = "Chad"
char['animal'] = "Ox"
char['star'] = "Gemini"
char['species'] = "Chimera"
char['species2'] = "Merr"
char['type'] = "Holy"
char['description'] = "Offspring of Ox and Gemini, born in the cosmic weave."

# Recalculate with correct animal/star
animal_data = gen.loader.get_animal_sign('Ox')
star_data = gen.loader.get_star_sign('Gemini')
char['biorhythms'] = calculate_biorhythms(animal_data, star_data)
char['thoughts'] = calculate_thoughts(char['biorhythms'])
char['stats'] = calculate_stats(
    char['biorhythms'],
    gen.loader.get_species('Chimera'),
    gen.loader.get_type('Holy'),
    None, None, 10
)

char_id = world.add_character(char)

# Display like the menu does
print("=" * 60)
print(f" {char['name']}")
print("=" * 60)

print(f"\nLevel: {char['level']} [{char['tier']}I]")
print(f"Animal: {char['animal']} / Star: {char['star']}")
print(f"Species: {char['species']}{('-' + char['species2']) if char['species2'] else ''}")
print(f"Type: {char['type']}")
print(f"\n{char['description']}")

print("\n" + "-" * 40)
print("Combat Stats")
print("-" * 40)
for stat, val in char['stats'].items():
    print(f" {stat}: {val}")

print("\n" + "-" * 40)
print("Biorhythms")
print("-" * 40)
for key in ['MNF', 'SPL', 'BEU', 'STR', 'FND', 'KNO', 'UND', 'WIS', 'VIT', 'SEX', 'DIV', 'EGO']:
    print(f" {key}: {char['biorhythms'].get(key, 0)}")

print("\n" + "-" * 40)
print("Thoughts")
print("-" * 40)
for thought, val in char['thoughts'].items():
    print(f" {thought}: {val}")

print("\n" + "=" * 60)
print("DATA COMPLETE")
print("=" * 60)
