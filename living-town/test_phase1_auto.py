"""
Phase 1 Auto Test - No user input required
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from world_state import WorldManager
from character_sheet import CharacterSheetGenerator
from layers.layer2_items import ItemGenerator, ItemType

print("=" * 60)
print("PHASE 1 AUTO TEST")
print("=" * 60)

# Setup
manager = WorldManager()
saves = Path(__file__).parent / "saves"
saves.mkdir(parents=True, exist_ok=True)

# Test 1: Create world
print("\n[1] Create World")
world = manager.create_world("Test_Phase1")
print(f"  OK: {world.name}")

# Test 2: Create character
print("\n[2] Create Character")
gen = CharacterSheetGenerator()
char = gen.generate_character(level=10)
char['name'] = "AutoTest Hero"
char_id = world.add_character(char)
world.set_active_character(char_id)
print(f"  OK: {char['name']} (Lvl {char['level']})")

# Test 3: Generate items
print("\n[3] Generate Items")
igen = ItemGenerator()
items = []
for i in range(3):
    item = igen.generate_item(level=(i+1)*5)
    iid = world.add_item(item.to_dict())
    world.give_item_to_character(char_id, iid)
    items.append((iid, item))
    print(f"  OK: {item.name} (Lvl {item.level})")

# Test 4: Equipment
print("\n[4] Equipment Test")
ok = world.equip_item(char_id, items[0][0], 'Weapon')
print(f"  {'OK' if ok else 'FAIL'}: Equip Lvl 5 item")

ok = world.equip_item(char_id, items[2][0], 'Weapon')  # Lvl 15
print(f"  {'OK' if ok else 'FAIL'}: Equip Lvl 15 item (should fail, char is Lvl 10)")

# Test 5: Save
print("\n[5] Save World")
path = saves / "world_phase1_auto.json"
ok = manager.save_world(str(path))
print(f"  {'OK' if ok else 'FAIL'}: Saved")

# Test 6: Load
print("\n[6] Load World")
manager.clear_world()
ok = manager.load_world(str(path))
print(f"  {'OK' if ok else 'FAIL'}: Loaded")

if ok:
    w = manager.world
    print(f"  Characters: {len(w.characters)}")
    print(f"  Items: {len(w.items)}")
    
    # Verify equipment persisted
    equip = w.get_character_equipment(char_id)
    equipped = sum(1 for i in equip.values() if i)
    print(f"  Equipment slots: {equipped}")

print("\n" + "=" * 60)
print("PHASE 1 AUTO TEST COMPLETE")
print("=" * 60)
