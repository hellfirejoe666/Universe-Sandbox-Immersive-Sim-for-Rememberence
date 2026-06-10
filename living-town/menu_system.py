"""
Menu System - Complete Menu Tree for Rememberence

This is the UI skeleton. Backend systems will be plugged in as we progress through phases.
"""

import sys
from pathlib import Path


# ────────────────────────────────────────────────
# Menu Helper Functions
# ────────────────────────────────────────────────

def clear_screen():
    print("\n" * 2)

def print_header(title: str):
    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60)

def print_subheader(title: str):
    print("\n" + "-" * 40)
    print(title)
    print("-" * 40)

def get_choice(prompt: str, options: list, allow_back=True) -> str:
    """Get menu choice from user."""
    while True:
        print(f"\n{prompt}")
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")
        if allow_back:
            print(f"  0. Back")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '0' and allow_back:
            return 'BACK'
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            print("Invalid choice.")
        except ValueError:
            print("Enter a number.")

def confirm(prompt: str) -> bool:
    """Yes/no confirmation."""
    resp = input(f"\n{prompt} (y/n): ").strip().lower()
    return resp in ['y', 'yes']


# ────────────────────────────────────────────────
# Menu Handlers (Placeholder - to be implemented)
# ────────────────────────────────────────────────

# Phase 1: Character + Items
def world_management_menu():
    print_subheader("WORLD MANAGEMENT")
    print("  [ ] New World")
    print("  [ ] Load World")
    print("  [ ] Save World")
    print("  [ ] Delete World")
    input("\n[Phase 1 - Not yet implemented] Press Enter...")

def character_management_menu():
    print_subheader("CHARACTER MANAGEMENT")
    print("  [ ] Create Character")
    print("  [ ] View Character Sheet")
    print("  [ ] Switch Character")
    input("\n[Phase 1 - Not yet implemented] Press Enter...")

def items_equipment_menu():
    print_subheader("ITEMS & EQUIPMENT")
    print("  [ ] Generate Random Item")
    print("  [ ] Equip Item")
    print("  [ ] Unequip Item")
    print("  [ ] Drop Item")
    input("\n[Phase 1 - Not yet implemented] Press Enter...")

# Phase 2: NPCs
def npc_management_menu():
    print_subheader("NPC MANAGEMENT")
    print("  [ ] Generate NPC")
    print("  [ ] View NPC Details")
    print("  [ ] Recruit to Party")
    print("  [ ] NPC Interactions")
    input("\n[Phase 2 - Not yet implemented] Press Enter...")

# Phase 3: Structures
def structure_management_menu():
    print_subheader("STRUCTURE MANAGEMENT")
    print("  [ ] Build Structure")
    print("  [ ] View Structures")
    print("  [ ] Structure Upgrades")
    print("  [ ] Structure Network")
    input("\n[Phase 3 - Not yet implemented] Press Enter...")

# Phase 4: Factions
def faction_management_menu():
    print_subheader("FACTION MANAGEMENT")
    print("  [ ] Create Faction")
    print("  [ ] View Faction (6-tier constructs)")
    print("  [ ] Faction Actions")
    print("  [ ] Diplomacy")
    input("\n[Phase 4 - Not yet implemented] Press Enter...")

# Phase 5: Cosmic
def cosmic_exploration_menu():
    print_subheader("COSMIC EXPLORATION")
    print("  [ ] Generate Galaxy")
    print("  [ ] Explore Systems")
    print("  [ ] Colonize Worlds")
    print("  [ ] Cosmic Events")
    input("\n[Phase 5 - Not yet implemented] Press Enter...")

# Phase 6: Simulation
def simulation_controls_menu():
    print_subheader("SIMULATION CONTROLS")
    print("  [ ] Run Turn (all layers)")
    print("  [ ] View Status Report")
    print("  [ ] Save/Load World")
    input("\n[Phase 6 - Not yet implemented] Press Enter...")


# ────────────────────────────────────────────────
# Main Menu Tree
# ────────────────────────────────────────────────

def main_menu():
    """
    Complete menu tree for Rememberence.
    
    Phases:
    - Phase 1: Character + Items (CURRENT)
    - Phase 2: NPCs
    - Phase 3: Structures
    - Phase 4: Factions
    - Phase 5: Cosmic
    - Phase 6: Turn Processor
    """
    
    running = True
    
    while running:
        clear_screen()
        print_header("REMEMBERENCE SIMULATION")
        print("\nA text-based cosmic fantasy RPG")
        print("\nMaterial/Materia Ontology")
        
        # Show current phase
        print("\n[Phase 1: Character + Items]")
        print("Progress: Menu Tree Built, Backend Pending")
        
        print("\n" + "=" * 60)
        print("MAIN MENU")
        print("=" * 60)
        
        choice = get_choice(
            "Select an option:",
            [
                "World Management",      # Phase 1
                "Character Management",  # Phase 1
                "Items & Equipment",     # Phase 1
                "NPC Management",        # Phase 2
                "Structure Management",  # Phase 3
                "Faction Management",    # Phase 4
                "Cosmic Exploration",    # Phase 5
                "Simulation Controls",   # Phase 6
                "Exit",
            ],
            allow_back=False
        )
        
        # Route to sub-menus
        if choice == "World Management":
            world_management_menu()
        
        elif choice == "Character Management":
            character_management_menu()
        
        elif choice == "Items & Equipment":
            items_equipment_menu()
        
        elif choice == "NPC Management":
            npc_management_menu()
        
        elif choice == "Structure Management":
            structure_management_menu()
        
        elif choice == "Faction Management":
            faction_management_menu()
        
        elif choice == "Cosmic Exploration":
            cosmic_exploration_menu()
        
        elif choice == "Simulation Controls":
            simulation_controls_menu()
        
        elif choice == "Exit":
            if confirm("Exit simulation?"):
                print("\nGoodbye!")
                running = False


# ────────────────────────────────────────────────
# Entry Point
# ────────────────────────────────────────────────

if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n[Interrupted] Goodbye!")
        sys.exit(0)
    except EOFError:
        print("\n\n[EOF] Goodbye!")
        sys.exit(0)
