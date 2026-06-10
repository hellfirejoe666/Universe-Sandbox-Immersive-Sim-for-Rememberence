"""Debug biorhythm loading"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import get_loader

loader = get_loader()

# Check animal signs
print("=" * 60)
print("ANIMAL SIGNS")
print("=" * 60)

animals = loader.get_all_animal_signs()
print(f"Loaded {len(animals)} animal signs")

# Check Boar specifically
boar = loader.get_animal_sign('Boar')
print(f"\nBoar data: {boar}")

# Check star signs
print("\n" + "=" * 60)
print("STAR SIGNS")
print("=" * 60)

stars = loader.get_all_star_signs()
print(f"Loaded {len(stars)} star signs")

# Check Sagittarius specifically
sag = loader.get_star_sign('Sagittarius')
print(f"\nSagittarius data: {sag}")

# Calculate manually
if boar and sag:
    print("\n" + "=" * 60)
    print("BIORHYTHM CALCULATION")
    print("=" * 60)
    
    boar_bio = boar.get('biorhythms', {})
    sag_bio = sag.get('biorhythms', {})
    
    print(f"Boar biorhythms: {boar_bio}")
    print(f"Sagittarius biorhythms: {sag_bio}")
    
    bios = {}
    for key in ['MNF', 'SPL', 'BEU', 'STR', 'FND', 'KNO', 'UND', 'WIS', 'VIT', 'SEX', 'DIV', 'EGO']:
        bios[key] = boar_bio.get(key, 0) + sag_bio.get(key, 0)
        print(f"  {key}: {boar_bio.get(key, 0)} + {sag_bio.get(key, 0)} = {bios[key]}")
