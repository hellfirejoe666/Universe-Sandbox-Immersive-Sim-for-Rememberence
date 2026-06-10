"""Check passive traits structure in species and types"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import get_loader

loader = get_loader()

# Check species passives
print("=" * 60)
print("SPECIES PASSIVE TRAITS")
print("=" * 60)

for name in ['Chimera', 'Human', 'Drakian', 'Orc', 'Elf']:
    species = loader.get_species(name)
    traits = species.get('traits', {})
    passive = traits.get('passive', [])
    print(f"\n{name}:")
    for p in passive:
        print(f"  - {p}")

# Check type passives
print("\n" + "=" * 60)
print("TYPE PASSIVE TRAITS")
print("=" * 60)

for name in ['Holy', 'Warrior', 'Thunder', 'Pyro', 'Aqua']:
    type_data = loader.get_type(name)
    traits = type_data.get('traits', {})
    passive = traits.get('passive', [])
    print(f"\n{name}:")
    for p in passive:
        print(f"  - {p}")
