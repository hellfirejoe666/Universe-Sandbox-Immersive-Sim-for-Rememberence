"""Check species.json structure"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import get_loader

loader = get_loader()

# Check Chimera
chimera = loader.get_species('Chimera')
print("Chimera species data:")
print(chimera)

# Check a few others
print("\n" + "=" * 60)
print("Sample species:")
for name in ['Chimera', 'Human', 'Orc', 'Drakian', 'Elf']:
    s = loader.get_species(name)
    print(f"\n{name}:")
    print(f"  HP: {s.get('HP')}")
    print(f"  ATK: {s.get('ATK')}")
    print(f"  DEF: {s.get('DEF')}")
    print(f"  SPD: {s.get('SPD')}")
    print(f"  MP: {s.get('MP')}")
