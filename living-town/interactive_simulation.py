"""
Interactive Simulation - Main Entry Point

Menu-driven interface for all 6 layers of Rememberence.
Currently implementing Phase 1: Character + Items

Follows Material/Materia ontology (narrative only).
Level gating prevents using items above character level.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from world_state import WorldManager
from character_sheet import CharacterSheetGenerator
from layers.layer2_items import ItemGenerator, ItemType, Rarity


# ────────────────────────────────────────────────
# Global State
# ────────────────────────────────────────────────

world_manager = WorldManager()
current_world = None


# ────────────────────────────────────────────────
# Helper Functions
# ────────────────────────────────────────────────

def clear_screen():
    """Clear terminal screen."""
    print("\n" * 2)

def print_header(title: str):
    """Print section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def print_subheader(title: str):
    """Print subsection header."""
    print("\n" + "-" * 40)
    print(title)
    print("-" * 40)

def get_menu_choice(prompt: str, options: list) -> str:
    """Get validated menu choice."""
    while True:
        print(f"\n{prompt}")
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")
        print(f"  0. Back")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '0':
            return '0'
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a number.")

def confirm(prompt: str) -> bool:
    """Get yes/no confirmation."""
    while True:
        response = input(f"\n{prompt} (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please enter 'y' or 'n'.")


# ────────────────────────────────────────────────
# World Management Menu
# ────────────────────────────────────────────────

def world_management_menu():
    """World save/load/delete management."""
    global current_world
    
    while True:
        clear_screen()
        print_header("WORLD MANAGEMENT")
        
        if current_world:
            print(f"\nCurrent World: {current_world.name}")
            print(f"Characters: {len(current_world.characters)}")
            print(f"Items: {len(current_world.items)}")
            print(f"Last Played: {current_world.last_played[:16]}")
        
        saves_dir = Path(__file__).parent / "saves"
        worlds = world_manager.list_worlds(str(saves_dir))
        
        if worlds:
            print_subheader("Saved Worlds")
            for i, w in enumerate(worlds, 1):
                print(f"  {i}. {w['name']} ({w['characters']} chars)")
                print(f"     Last played: {w['last_played'][:10]}")
        
        choice = get_menu_choice(
            "What would you like to do?",
            [
                "New World",
                "Load World",
                "Save World",
                "Delete World",
            ] + (["Clear Current World"] if current_world else [])
        )
        
        if choice == "New World":
            name = input("\nEnter world name: ").strip()
            if name:
                current_world = world_manager.create_world(name)
                print(f"✓ Created world: {current_world.name}")
                input("\nPress Enter to continue...")
        
        elif choice == "Load World":
            if not worlds:
                print("\nNo saved worlds found.")
                input("\nPress Enter to continue...")
                continue
            
            # Select world
            try:
                idx = int(input("Enter world number: ")) - 1
                if 0 <= idx < len(worlds):
                    success = world_manager.load_world(worlds[idx]['path'])
                    if success:
                        current_world = world_manager.world
                        print(f"✓ Loaded world: {current_world.name}")
                    else:
                        print("✗ Failed to load world")
                    input("\nPress Enter to continue...")
            except ValueError:
                pass
        
        elif choice == "Save World":
            if not current_world:
                print("\nNo active world to save.")
                input("\nPress Enter to continue...")
                continue
            
            saves_dir = Path(__file__).parent / "saves"
            saves_dir.mkdir(parents=True, exist_ok=True)
            save_path = saves_dir / f"world_{current_world.name.replace(' ', '_').lower()}.json"
            
            if world_manager.save_world(str(save_path)):
                print(f"✓ World saved to: {save_path}")
            else:
                print("✗ Failed to save world")
            input("\nPress Enter to continue...")
        
        elif choice == "Delete World":
            if not worlds:
                print("\nNo saved worlds to delete.")
                input("\nPress Enter to continue...")
                continue
            
            try:
                idx = int(input("Enter world number to delete: ")) - 1
                if 0 <= idx < len(worlds):
                    if confirm(f"Delete '{worlds[idx]['name']}'?"):
                        world_manager.delete_world(worlds[idx]['path'])
                        print(f"✓ Deleted world: {worlds[idx]['name']}")
                    input("\nPress Enter to continue...")
            except ValueError:
                pass
        
        elif choice == "Clear Current World" and current_world:
            world_manager.clear_world()
            current_world = None
            print("\n✓ Cleared current world from memory")
            input("\nPress Enter to continue...")


# ────────────────────────────────────────────────
# Character Menu
# ────────────────────────────────────────────────

def character_menu():
    """Character creation and management."""
    global current_world
    
    if not current_world:
        print("\n✗ No active world. Create or load a world first.")
        input("\nPress Enter to continue...")
        return
    
    while True:
        clear_screen()
        print_header("CHARACTER MANAGEMENT")
        
        # Show active character
        active_char = current_world.get_active_character()
        if active_char:
            print(f"\nActive Character: {active_char.get('name', 'Unknown')}")
            print(f"Level: {active_char.get('level', 1)}")
            print(f"Material: {active_char.get('material', 'Unknown')}")
            print(f"Materia: {active_char.get('materia', 'Unknown')}")
        
        # List all characters
        if current_world.characters:
            print_subheader("Characters")
            for char_id, char in current_world.characters.items():
                active_marker = " (ACTIVE)" if char_id == current_world.active_character_id else ""
                print(f"  • {char.get('name', 'Unknown')} (Lvl {char.get('level', 1)}){active_marker}")
        
        choice = get_menu_choice(
            "What would you like to do?",
            [
                "Create Character",
                "View Character Sheet",
                "Switch Character",
            ]
        )
        
        if choice == "Create Character":
            create_character()
        
        elif choice == "View Character Sheet":
            if active_char:
                view_character_sheet(current_world.active_character_id)
            else:
                print("\n✗ No active character. Switch or create one.")
                input("\nPress Enter to continue...")
        
        elif choice == "Switch Character":
            if len(current_world.characters) <= 1:
                print("\nOnly one character. Create more to switch.")
                input("\nPress Enter to continue...")
                continue
            
            print_subheader("Select Character")
            char_list = list(current_world.characters.items())
            for i, (char_id, char) in enumerate(char_list, 1):
                active_marker = " (CURRENT)" if char_id == current_world.active_character_id else ""
                print(f"  {i}. {char.get('name', 'Unknown')}{active_marker}")
            
            try:
                idx = int(input("Choose character: ")) - 1
                if 0 <= idx < len(char_list):
                    new_id = char_list[idx][0]
                    current_world.set_active_character(new_id)
                    print(f"✓ Switched to: {char_list[idx][1].get('name')}")
                input("\nPress Enter to continue...")
            except ValueError:
                pass


def create_character():
    """Generate new character using character_sheet.py."""
    global current_world
    
    print_header("CREATE CHARACTER")
    
    # Get character name
    name = input("\nEnter character name: ").strip()
    if not name:
        name = f"Hero_{len(current_world.characters) + 1}"
    
    # Get level
    try:
        level = int(input("Enter level (1-100000): ") or "1")
        level = max(1, min(100000, level))
    except ValueError:
        level = 1
    
    # Generate character
    print("\nGenerating character...")
    gen = CharacterSheetGenerator()
    char_data = gen.generate_character(level=level)
    char_data['name'] = name
    
    # Add to world
    char_id = current_world.add_character(char_data)
    
    print(f"\n✓ Created: {name} (Level {level})")
    print(f"  Material: {char_data['material']}")
    print(f"  Materia: {char_data['materia']}")
    print(f"  Species: {char_data['species']}")
    print(f"  Type: {char_data['type']}")
    
    # Set as active
    current_world.set_active_character(char_id)
    
    input("\nPress Enter to continue...")


def view_character_sheet(char_id: str):
    """View full character sheet."""
    global current_world
    
    char = current_world.characters.get(char_id)
    if not char:
        return
    
    print_header(f"CHARACTER SHEET: {char.get('name', 'Unknown')}")
    
    # Basic info
    print(f"\nLevel: {char.get('level', 1)} [{char.get('tier', 'Novice')}I]")
    print(f"Material (Species): {char.get('material', 'Unknown')}")
    print(f"Materia (Type): {char.get('materia', 'Unknown')}")
    print(f"Animal: {char.get('animal', 'Unknown')}")
    print(f"Star: {char.get('star', 'Unknown')}")
    print(f"\n{char.get('description', '')}")
    
    # Stats
    print_subheader("Combat Stats")
    stats = char.get('stats', {})
    for stat, val in stats.items():
        print(f"  {stat}: {val}")
    
    # Biorhythms
    print_subheader("Biorhythms")
    bios = char.get('biorhythms', {})
    for key in ['MNF', 'SPL', 'BEU', 'STR', 'FND', 'KNO', 'UND', 'WIS', 'VIT', 'SEX', 'DIV', 'EGO']:
        print(f"  {key}: {bios.get(key, 0)}")
    
    # Equipment
    print_subheader("Equipment")
    equipment = current_world.get_character_equipment(char_id)
    for slot, item in equipment.items():
        if item:
            print(f"  {slot}: {item['name']} (Lvl {item['level']})")
            print(f"    Material: {item.get('material', 'Unknown')} / Materia: {item.get('materia', 'Unknown')}")
        else:
            print(f"  {slot}: (empty)")
    
    # Inventory
    print_subheader("Inventory")
    inventory = current_world.get_character_inventory(char_id)
    if inventory:
        for item in inventory:
            print(f"  • {item['name']} (Lvl {item['level']}, {item.get('type', 'Unknown')})")
    else:
        print("  (empty)")
    
    input("\nPress Enter to continue...")


# ────────────────────────────────────────────────
# Items Menu
# ────────────────────────────────────────────────

def items_menu():
    """Item management and equipment."""
    global current_world
    
    if not current_world:
        print("\n✗ No active world.")
        input("\nPress Enter to continue...")
        return
    
    active_char = current_world.get_active_character()
    if not active_char:
        print("\n✗ No active character.")
        input("\nPress Enter to continue...")
        return
    
    while True:
        clear_screen()
        print_header("ITEMS & EQUIPMENT")
        print(f"\nCharacter: {active_char.get('name')} (Level {active_char.get('level', 1)})")
        
        # Show current equipment
        equipment = current_world.get_character_equipment(current_world.active_character_id)
        print_subheader("Current Equipment")
        for slot, item in equipment.items():
            if item:
                print(f"  {slot}: {item['name']} (Lvl {item['level']})")
            else:
                print(f"  {slot}: (empty)")
        
        # Show inventory
        inventory = current_world.get_character_inventory(current_world.active_character_id)
        print_subheader(f"Inventory ({len(inventory)} items)")
        if inventory:
            for i, item in enumerate(inventory, 1):
                level_ok = "✓" if item['level'] <= active_char.get('level', 1) else "✗ (too high level)"
                print(f"  {i}. {item['name']} - {item.get('type', 'Unknown')} (Lvl {item['level']}) {level_ok}")
        else:
            print("  (empty)")
        
        choice = get_menu_choice(
            "What would you like to do?",
            [
                "Generate Random Item",
                "Equip Item",
                "Unequip Item",
                "Drop Item",
            ]
        )
        
        if choice == "Generate Random Item":
            generate_item()
        
        elif choice == "Equip Item":
            if not inventory:
                print("\n✗ No items in inventory.")
                input("\nPress Enter to continue...")
                continue
            
            # Select item
            try:
                idx = int(input("Enter item number: ")) - 1
                if 0 <= idx < len(inventory):
                    item = inventory[idx]
                    item_id = item['id']
                    
                    # Select slot
                    print("\nEquipment slots:")
                    slots = ['Head', 'Body', 'Hands', 'Legs', 'Feet', 'Other', 'Weapon']
                    for i, slot in enumerate(slots, 1):
                        print(f"  {i}. {slot}")
                    
                    slot_idx = int(input("Choose slot: ")) - 1
                    if 0 <= slot_idx < len(slots):
                        slot = slots[slot_idx]
                        success = current_world.equip_item(current_world.active_character_id, item_id, slot)
                        
                        if success:
                            print(f"✓ Equipped {item['name']} to {slot}")
                        else:
                            print(f"✗ Can't equip (level too high or invalid)")
                input("\nPress Enter to continue...")
            except ValueError:
                pass
        
        elif choice == "Unequip Item":
            print("\nUnequip from which slot?")
            slots = ['Head', 'Body', 'Hands', 'Legs', 'Feet', 'Other', 'Weapon']
            for i, slot in enumerate(slots, 1):
                current = equipment.get(slot)
                if current:
                    print(f"  {i}. {slot}: {current['name']}")
                else:
                    print(f"  {i}. {slot}: (empty)")
            
            try:
                idx = int(input("Choose slot: ")) - 1
                if 0 <= idx < len(slots):
                    slot = slots[idx]
                    success = current_world.unequip_item(current_world.active_character_id, slot)
                    if success:
                        print(f"✓ Unequipped from {slot}")
                    else:
                        print(f"✗ Nothing equipped in {slot}")
                input("\nPress Enter to continue...")
            except ValueError:
                pass
        
        elif choice == "Drop Item":
            if not inventory:
                print("\n✗ No items to drop.")
                input("\nPress Enter to continue...")
                continue
            
            try:
                idx = int(input("Enter item number to drop: ")) - 1
                if 0 <= idx < len(inventory):
                    item = inventory[idx]
                    if confirm(f"Drop '{item['name']}'?"):
                        char = current_world.characters[current_world.active_character_id]
                        char['inventory'].remove(item['id'])
                        print(f"✓ Dropped {item['name']}")
                input("\nPress Enter to continue...")
            except ValueError:
                pass


def generate_item():
    """Generate random item and add to world."""
    global current_world
    
    print_header("GENERATE ITEM")
    
    # Get item type
    print("\nItem type:")
    types = ['Weapon', 'Armor', 'Accessory']
    for i, t in enumerate(types, 1):
        print(f"  {i}. {t}")
    
    try:
        type_idx = int(input("Choose type: ")) - 1
        if 0 <= type_idx < len(types):
            item_type = {
                'Weapon': ItemType.WEAPON,
                'Armor': ItemType.ARMOR,
                'Accessory': ItemType.ACCESSORY,
            }[types[type_idx]]
        else:
            item_type = ItemType.WEAPON
    except ValueError:
        item_type = ItemType.WEAPON
    
    # Generate item
    gen = ItemGenerator()
    item = gen.generate_item(
        item_type=item_type,
        level=None,  # Random
        rarity=None  # Random
    )
    
    # Add to world
    item_id = current_world.add_item(item.to_dict())
    
    # Give to active character
    current_world.give_item_to_character(current_world.active_character_id, item_id)
    
    print(f"\n✓ Generated: {item.name}")
    print(f"  Type: {item.item_type.value}")
    print(f"  Material: {item.material}")
    print(f"  Materia: {item.materia}")
    print(f"  Level: {item.level}")
    print(f"  Rarity: {item.rarity.value}")
    
    input("\nPress Enter to continue...")


# ────────────────────────────────────────────────
# Main Menu
# ────────────────────────────────────────────────

def main_menu():
    """Main application menu."""
    global current_world
    
    while True:
        clear_screen()
        print_header("REMEMBERENCE SIMULATION")
        print("\nA text-based cosmic fantasy RPG")
        print("\nMaterial/Materia Ontology - All layers unified")
        
        if current_world:
            print(f"\n[ACTIVE] World: {current_world.name}")
            print(f"   Characters: {len(current_world.characters)}")
            print(f"   Items: {len(current_world.items)}")
            print(f"   Time: Y{current_world.time['year']} M{current_world.time['month']} D{current_world.time['day']} H{current_world.time['hour']}")
        else:
            print("\n[WARNING] No active world")
        
        print("\n" + "=" * 60)
        print("MAIN MENU")
        print("=" * 60)
        
        # Dynamic menu based on world state
        options = [
            "World Management",
            "Character Management",
        ]
        
        if current_world and current_world.get_active_character():
            options.extend([
                "Items & Equipment",
                # Future phases:
                # "NPCs",
                # "Structures",
                # "Factions",
                # "Cosmic Exploration",
                # "Advance Time",
            ])
        
        options.append("Exit")
        
        choice = get_menu_choice("Select an option:", options)
        
        if choice == "World Management":
            world_management_menu()
        
        elif choice == "Character Management":
            character_menu()
        
        elif choice == "Items & Equipment":
            items_menu()
        
        elif choice == "Exit":
            print("\nGoodbye!")
            sys.exit(0)


# ────────────────────────────────────────────────
# Entry Point
# ────────────────────────────────────────────────

if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        sys.exit(0)
