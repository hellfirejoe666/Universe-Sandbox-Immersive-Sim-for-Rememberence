"""
Phase 1 - World Management Implementation

Test this file first, then integrate into menu_system.py
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from world_state import WorldManager
from character_sheet import CharacterSheetGenerator
from layers.layer2_items import ItemGenerator, ItemType, Rarity

# Global
world_manager = WorldManager()
current_world = None

def clear():
    print("\n" * 2)

def header(title):
    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60)

def subheader(title):
    print("\n" + "-" * 40)
    print(title)
    print("-" * 40)

def get_choice(prompt, options):
    while True:
        print(f"\n{prompt}")
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")
        print("  0. Back")
        
        c = input("\nChoice: ").strip()
        if c == '0':
            return None
        try:
            idx = int(c) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except:
            pass
        print("Invalid.")

def confirm(prompt):
    return input(f"\n{prompt} (y/n): ").strip().lower() in ['y', 'yes']

def world_menu():
    """World management - Phase 1"""
    global current_world
    
    while True:
        clear()
        header("WORLD MANAGEMENT")
        
        if current_world:
            print(f"\nCurrent: {current_world.name}")
            print(f"  Characters: {len(current_world.characters)}")
            print(f"  Items: {len(current_world.items)}")
        
        # List saves
        saves = Path(__file__).parent / "saves"
        worlds = world_manager.list_worlds(str(saves))
        
        if worlds:
            subheader("Saved Worlds")
            for i, w in enumerate(worlds, 1):
                print(f"  {i}. {w['name']} ({w['characters']} chars)")
        
        choice = get_choice(
            "Action?",
            ["New World", "Load World", "Save World", "Delete World"]
            + (["Clear"] if current_world else [])
        )
        
        if not choice:
            return
        
        if choice == "New World":
            name = input("World name: ").strip()
            if name:
                current_world = world_manager.create_world(name)
                print(f"[OK] Created: {name}")
                input("\nEnter...")
        
        elif choice == "Load World":
            if not worlds:
                print("[INFO] No saves.")
                input("\nEnter...")
                continue
            try:
                idx = int(input("Number: ")) - 1
                if 0 <= idx < len(worlds):
                    if world_manager.load_world(worlds[idx]['path']):
                        current_world = world_manager.world
                        print(f"[OK] Loaded: {current_world.name}")
                    input("\nEnter...")
            except:
                pass
        
        elif choice == "Save World":
            if not current_world:
                print("[INFO] No active world.")
                input("\nEnter...")
                continue
            saves.mkdir(parents=True, exist_ok=True)
            path = saves / f"world_{current_world.name.replace(' ', '_').lower()}.json"
            if world_manager.save_world(str(path)):
                print(f"[OK] Saved: {path}")
            input("\nEnter...")
        
        elif choice == "Delete World":
            if not worlds:
                print("[INFO] Nothing to delete.")
                input("\nEnter...")
                continue
            try:
                idx = int(input("Delete number: ")) - 1
                if 0 <= idx < len(worlds):
                    if confirm(f"Delete '{worlds[idx]['name']}'?"):
                        world_manager.delete_world(worlds[idx]['path'])
                        print("[OK] Deleted")
                input("\nEnter...")
            except:
                pass
        
        elif choice == "Clear" and current_world:
            world_manager.clear_world()
            current_world = None
            print("[OK] Cleared")
            input("\nEnter...")

def character_menu():
    """Character management - Phase 1"""
    global current_world
    
    if not current_world:
        print("[INFO] No world. Create one first.")
        input("\nEnter...")
        return
    
    while True:
        clear()
        header("CHARACTER MANAGEMENT")
        
        active = current_world.get_active_character()
        if active:
            print(f"\nActive: {active.get('name')} (Lvl {active.get('level', 1)})")
        
        if current_world.characters:
            subheader("Characters")
            for cid, c in current_world.characters.items():
                mark = " (ACTIVE)" if cid == current_world.active_character_id else ""
                print(f"  - {c.get('name')}{mark}")
        
        choice = get_choice("Action?", ["Create", "View", "Switch"])
        
        if not choice:
            return
        
        if choice == "Create":
            name = input("Name: ").strip() or f"Hero_{len(current_world.characters)+1}"
            try:
                level = int(input("Level: ") or "1")
                level = max(1, min(100000, level))
            except:
                level = 1
            
            gen = CharacterSheetGenerator()
            char = gen.generate_character(level=level)
            char['name'] = name
            char_id = current_world.add_character(char)
            current_world.set_active_character(char_id)
            
            print(f"[OK] Created: {name} (Lvl {level})")
            input("\nEnter...")
        
        elif choice == "View":
            if not active:
                print("[INFO] No active character.")
                input("\nEnter...")
                continue
            
            header(active.get('name', 'Unknown'))
            print(f"Level: {active.get('level')} [{active.get('tier', 'Novice')}I]")
            print(f"Animal: {active.get('animal')} / Star: {active.get('star')}")
            print(f"Species: {active.get('species')}{('-' + active.get('species2', '')) if active.get('species2') else ''}")
            print(f"Type: {active.get('type')}{('-' + active.get('type2', '')) if active.get('type2') else ''}")
            print(f"\n{active.get('description', '')}")
            
            # Stats
            subheader("Combat Stats")
            stats = active.get('stats', {})
            for stat, val in stats.items():
                print(f"  {stat}: {val}")
            
            # Biorhythms
            subheader("Biorhythms")
            bios = active.get('biorhythms', {})
            for key in ['MNF', 'SPL', 'BEU', 'STR', 'FND', 'KNO', 'UND', 'WIS', 'VIT', 'SEX', 'DIV', 'EGO']:
                print(f"  {key}: {bios.get(key, 0)}")
            
            # Thoughts
            subheader("Thoughts")
            thoughts = active.get('thoughts', {})
            for thought, val in thoughts.items():
                print(f"  {thought}: {val}")
            
            # Skills
            subheader("Class Skills")
            skills = active.get('skills', {})
            for cat, skill in skills.items():
                print(f"  {cat.capitalize()}: {skill}")
            
            # Traits
            subheader("Traits")
            print(f"  Species Active: {active.get('species_traits', ['None'])[0] if active.get('species_traits') else 'None'}")
            print(f"  Type Active: {active.get('type_traits', ['None'])[0] if active.get('type_traits') else 'None'}")
            
            # Equipment
            subheader("Equipment")
            equip = current_world.get_character_equipment(current_world.active_character_id)
            for slot, item in equip.items():
                if item:
                    print(f"  {slot}: {item['name']} (Lvl {item['level']})")
                    print(f"    {item.get('material', '?')} + {item.get('materia', '?')}")
                else:
                    print(f"  {slot}: (empty)")
            
            # Inventory
            subheader("Inventory")
            inv = current_world.get_character_inventory(current_world.active_character_id)
            if inv:
                for item in inv:
                    ok = "[OK]" if item['level'] <= active.get('level', 1) else "[!] Too High"
                    print(f"  - {item['name']} (Lvl {item['level']}) {ok}")
            else:
                print("  (empty)")
            
            input("\nEnter...")
        
        elif choice == "Switch":
            chars = list(current_world.characters.items())
            if len(chars) <= 1:
                print("[INFO] Only one character.")
                input("\nEnter...")
                continue
            
            for i, (cid, c) in enumerate(chars, 1):
                mark = " (CURRENT)" if cid == current_world.active_character_id else ""
                print(f"  {i}. {c.get('name')}{mark}")
            
            try:
                idx = int(input("Choose: ")) - 1
                if 0 <= idx < len(chars):
                    current_world.set_active_character(chars[idx][0])
                    print(f"[OK] Switched to: {chars[idx][1].get('name')}")
                input("\nEnter...")
            except:
                pass

def items_menu():
    """Items & Equipment - Phase 1"""
    global current_world
    
    if not current_world:
        print("[INFO] No world.")
        input("\nEnter...")
        return
    
    active = current_world.get_active_character()
    if not active:
        print("[INFO] No character.")
        input("\nEnter...")
        return
    
    while True:
        clear()
        header("ITEMS & EQUIPMENT")
        print(f"\n{active.get('name')} (Lvl {active.get('level', 1)})")
        
        subheader("Equipment")
        equip = current_world.get_character_equipment(current_world.active_character_id)
        for slot, item in equip.items():
            if item:
                print(f"  {slot}: {item['name']} (Lvl {item['level']})")
            else:
                print(f"  {slot}: (empty)")
        
        subheader("Inventory")
        inv = current_world.get_character_inventory(current_world.active_character_id)
        if inv:
            for i, item in enumerate(inv, 1):
                ok = "[OK]" if item['level'] <= active.get('level', 1) else "[!] Too High"
                print(f"  {i}. {item['name']} {ok}")
        else:
            print("  (empty)")
        
        choice = get_choice("Action?", ["Generate", "Equip", "Unequip", "Drop"])
        
        if not choice:
            return
        
        if choice == "Generate":
            gen = ItemGenerator()
            item = gen.generate_item()
            item_id = current_world.add_item(item.to_dict())
            current_world.give_item_to_character(current_world.active_character_id, item_id)
            print(f"[OK] Generated: {item.name}")
            input("\nEnter...")
        
        elif choice == "Equip":
            if not inv:
                print("[INFO] No items.")
                input("\nEnter...")
                continue
            
            try:
                idx = int(input("Item: ")) - 1
                if 0 <= idx < len(inv):
                    item = inv[idx]
                    slots = ['Head', 'Body', 'Hands', 'Legs', 'Feet', 'Other', 'Weapon']
                    print("Slots:")
                    for i, s in enumerate(slots, 1):
                        print(f"  {i}. {s}")
                    sidx = int(input("Slot: ")) - 1
                    if 0 <= sidx < len(slots):
                        if current_world.equip_item(current_world.active_character_id, item['id'], slots[sidx]):
                            print(f"[OK] Equipped to {slots[sidx]}")
                        else:
                            print("[FAIL] Level too high")
                input("\nEnter...")
            except:
                pass
        
        elif choice == "Unequip":
            slots = ['Head', 'Body', 'Hands', 'Legs', 'Feet', 'Other', 'Weapon']
            for i, s in enumerate(slots, 1):
                item = equip.get(s)
                print(f"  {i}. {s}: {item['name'] if item else '(empty)'}")
            
            try:
                idx = int(input("Slot: ")) - 1
                if 0 <= idx < len(slots):
                    if current_world.unequip_item(current_world.active_character_id, slots[idx]):
                        print(f"[OK] Unequipped")
                    else:
                        print("[INFO] Empty slot")
                input("\nEnter...")
            except:
                pass
        
        elif choice == "Drop":
            if not inv:
                print("[INFO] No items.")
                input("\nEnter...")
                continue
            
            try:
                idx = int(input("Drop item: ")) - 1
                if 0 <= idx < len(inv):
                    item = inv[idx]
                    if confirm(f"Drop '{item['name']}'?"):
                        char = current_world.characters[current_world.active_character_id]
                        char['inventory'].remove(item['id'])
                        print(f"[OK] Dropped")
                input("\nEnter...")
            except:
                pass

def main():
    """Main menu - Phase 1"""
    global current_world
    
    while True:
        try:
            clear()
            header("REMEMBERENCE - Phase 1")
            print("\nCharacter + Items")
            
            if current_world:
                print(f"\n[ACTIVE] {current_world.name}")
            else:
                print("\n[NO WORLD]")
            
            print("\n" + "=" * 60)
            choice = get_choice(
                "Menu:",
                ["World Management", "Character Management", "Items & Equipment", "Exit"],
            )
            
            if not choice:
                continue
            
            if choice == "World Management":
                world_menu()
            elif choice == "Character Management":
                character_menu()
            elif choice == "Items & Equipment":
                items_menu()
            elif choice == "Exit":
                if confirm("Exit?"):
                    print("\nGoodbye!")
                    return
        except KeyboardInterrupt:
            print("\n\n[Interrupted]")
            return
        except EOFError:
            print("\n\n[EOF]")
            return

if __name__ == '__main__':
    main()
