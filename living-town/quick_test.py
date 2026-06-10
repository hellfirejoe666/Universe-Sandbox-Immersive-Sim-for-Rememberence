"""Quick test - create character and show full sheet"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from world_state import WorldManager
from character_sheet import CharacterSheetGenerator
from layers.layer2_items import ItemGenerator

# Setup
manager = WorldManager()
world = manager.create_world("QuickTest")

# Create character
gen = CharacterSheetGenerator()
char = gen.generate_character(level=10)
char['name'] = "Test Hero"
char_id = world.add_character(char)

# Show full sheet
print("=" * 60)
print(f"CHARACTER: {char['name']}")
print("=" * 60)

print(f"\nLevel: {char['level']} [{char['tier']}I]")
print(f"Animal: {char['animal']} / Star: {char['star']}")
print(f"Species: {char['species']}{('-' + char['species2']) if char['species2'] else ''}")
print(f"Type: {char['type']}{('-' + char['type2']) if char['type2'] else ''}")
print(f"\n{char['description']}")

print("\n" + "-" * 40)
print("COMBAT STATS")
print("-" * 40)
for stat, val in char['stats'].items():
    print(f"  {stat}: {val}")

print("\n" + "-" * 40)
print("BIORHYTHMS")
print("-" * 40)
for key in ['MNF', 'SPL', 'BEU', 'STR', 'FND', 'KNO', 'UND', 'WIS', 'VIT', 'SEX', 'DIV', 'EGO']:
    print(f"  {key}: {char['bios'].get(key, 0)}")

print("\n" + "-" * 40)
print("THOUGHTS")
print("-" * 40)
for thought, val in char['thoughts'].items():
    print(f"  {thought}: {val}")

print("\n" + "-" * 40)
print("CLASS SKILLS")
print("-" * 40)
for cat, skill in char['skills'].items():
    print(f"  {cat.capitalize()}: {skill}")

print("\n" + "-" * 40)
print("TRAITS")
print("-" * 40)
print(f"  Species Active: {char['species_traits'][0] if char['species_traits'] else 'None'}")
print(f"  Type Active: {char['type_traits'][0] if char['type_traits'] else 'None'}")

print("\n" + "=" * 60)
print("ALL DATA PRESENT ✓")
print("=" * 60)
