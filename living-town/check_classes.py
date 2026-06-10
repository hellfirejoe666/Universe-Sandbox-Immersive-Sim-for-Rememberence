"""Check classes.json structure"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import get_loader

loader = get_loader()

# Get all classes
classes = loader.get_all_classes()
print("Classes structure:")
print(classes)

# Check a few specific ones
print("\n" + "=" * 60)
print("Sample classes:")
for name in ['Warrior', 'Spellcaster', 'Thunder', 'Pyro']:
    c = classes.get(name, {})
    print(f"\n{name}:")
    print(f"  {c}")
