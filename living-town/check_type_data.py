"""Check what's in types.json for Holy"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import get_loader

loader = get_loader()

# Get Holy type
holy = loader.get_type('Holy')
print("Holy type data:")
print(holy)

# Get all types to see structure
print("\n" + "=" * 60)
print("Sample types:")
for type_name in ['Holy', 'Warrior', 'Thunder', 'Pyro']:
    t = loader.get_type(type_name)
    print(f"\n{type_name}:")
    print(f"  HP: {t.get('HP')}")
    print(f"  ATK: {t.get('ATK')}")
    print(f"  DEF: {t.get('DEF')}")
    print(f"  SPD: {t.get('SPD')}")
    print(f"  MP: {t.get('MP')}")
