"""Test stat calculations match JS generator"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from character_sheet import CharacterSheetGenerator

gen = CharacterSheetGenerator()

# Test case: Ox + Gemini, Chimera-Merr + Holy, Level 10
print("=" * 60)
print("TEST: Ox + Gemini, Chimera-Merr + Holy, Level 10")
print("=" * 60)

# Get data
animal = gen.loader.get_animal_sign('Ox')
star = gen.loader.get_star_sign('Gemini')
species = gen.loader.get_species('Chimera')
type_data = gen.loader.get_type('Holy')

print(f"\nOx biorhythms: {animal.get('biorhythms', {})}")
print(f"Gemini biorhythms: {star.get('biorhythms', {})}")

# Calculate biorhythms
bios = gen._calc_biorhythms(animal, star)
print(f"\nCombined biorhythms: {bios}")

# Get species stats
print(f"\nChimera species stats: HP={species.get('HP')}, ATK={species.get('ATK')}, DEF={species.get('DEF')}, SPD={species.get('SPD')}, MP={species.get('MP')}")

# Get type biorhythm mappings
print(f"\nHoly type mappings: HP={type_data.get('HP')}, ATK={type_data.get('ATK')}, DEF={type_data.get('DEF')}, SPD={type_data.get('SPD')}, MP={type_data.get('MP')}")

# Calculate stats
stats = gen._calc_stats(bios, species, type_data, None, None, 10)
print(f"\nCalculated stats: {stats}")

# Manual calculation for verification
print("\n" + "-" * 40)
print("Manual calculation:")
print("-" * 40)
scale = 10  # Level 10
for stat, bio_key in [('HP', 'VIT'), ('ATK', 'STR'), ('DEF', 'FND'), ('SPD', 'SEX'), ('MP', 'WIS')]:
    species_val = species.get(stat, 0)
    bio_val = bios.get(bio_key, 0)
    result = (species_val + bio_val) * scale
    print(f"  {stat}: ({species_val} + {bio_val}) * {scale} = {result}")
