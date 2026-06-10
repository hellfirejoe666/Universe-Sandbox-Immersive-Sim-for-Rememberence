#!/usr/bin/env python3
"""
Layer 2 Viewer - Items
======================
Watch procedural item generation.
Weapons, armor, materials, materia, and rarity.
"""

import sys
import time
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from layers.layer2_items import ItemGenerator, ItemRarity, ItemType


def view_layer2(iterations=10, delay=0.5):
    """
    Watch Layer 2: Items in action.
    
    Shows:
    - Weapon generation
    - Armor generation
    - Material variations
    - Materia attachments
    - Rarity tiers
    """
    
    print("\n" + "=" * 70)
    print("  LAYER 2 VIEWER - Items")
    print("  Watching procedural item generation")
    print("=" * 70)
    print(f"\nRunning {iterations} iterations... (delay: {delay}s)\n")
    
    time.sleep(1)
    
    gen = ItemGenerator()
    
    # Track stats
    weapons_generated = 0
    armor_generated = 0
    rarity_counts = {r.value: 0 for r in ItemRarity}
    
    for i in range(iterations):
        print("-" * 70)
        print(f"Iteration {i+1:2d}")
        print("-" * 70)
        
        # Generate a weapon
        weapon = gen.generate_weapon()
        weapons_generated += 1
        rarity_counts[weapon.rarity.value] += 1
        
        print(f"\n  WEAPON:")
        print(f"    Name:   {weapon.name}")
        print(f"    Type:   {weapon.item_type.value}")
        print(f"    Rarity: {weapon.rarity.value}")
        print(f"    Value:  {weapon.value} gold")
        
        if weapon.material:
            print(f"    Material: {weapon.material}")
        if weapon.materia:
            print(f"    Materia: {weapon.materia}")
        
        # Show effects
        if weapon.effects:
            print(f"    Effects:")
            for effect, val in weapon.effects.items():
                print(f"      {effect}: {val}")
        
        # Generate armor
        armor = gen.generate_armor()
        armor_generated += 1
        rarity_counts[armor.rarity.value] += 1
        
        print(f"\n  ARMOR:")
        print(f"    Name:   {armor.name}")
        print(f"    Type:   {armor.item_type.value}")
        print(f"    Rarity: {armor.rarity.value}")
        print(f"    Value:  {armor.value} gold")
        
        if armor.material:
            print(f"    Material: {armor.material}")
        if armor.materia:
            print(f"    Materia: {armor.materia}")
        
        if armor.effects:
            print(f"    Effects:")
            for effect, val in armor.effects.items():
                print(f"      {effect}: {val}")
        
        # Generate with specific rarity (every 3rd iteration)
        if (i + 1) % 3 == 0:
            rarity = random.choice(list(ItemRarity))
            rare_item = gen.generate_weapon(rarity=rarity)
            
            print(f"\n  [RARE GENERATION - {rarity.value}]")
            print(f"    {rare_item.name}")
            print(f"    Value: {rare_item.value}g")
            if rare_item.effects:
                print(f"    Effects: {rare_item.effects}")
        
        print()
        time.sleep(delay)
    
    # Summary
    print("=" * 70)
    print("  Layer 2 Viewer Complete")
    print("=" * 70)
    
    print(f"\n  Items Generated:")
    print(f"    Weapons: {weapons_generated}")
    print(f"    Armor:   {armor_generated}")
    print(f"    Total:   {weapons_generated + armor_generated}")
    
    print(f"\n  Rarity Distribution:")
    for rarity, count in rarity_counts.items():
        if count > 0:
            pct = (count / (weapons_generated + armor_generated)) * 100
            print(f"    {rarity:12s}: {count:2d} ({pct:.0f}%)")
    
    print()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Layer 2: Items Viewer')
    parser.add_argument('--iterations', type=int, default=5, help='Number of iterations')
    parser.add_argument('--delay', type=float, default=0.8, help='Delay between iterations')
    parser.add_argument('--fast', action='store_true', help='Fast mode (0.3s delay)')
    
    args = parser.parse_args()
    
    if args.fast:
        args.delay = 0.3
    
    view_layer2(iterations=args.iterations, delay=args.delay)
