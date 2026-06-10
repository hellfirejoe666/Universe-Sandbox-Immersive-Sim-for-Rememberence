#!/usr/bin/env python3
"""
Layer 4 Viewer - Structures (Towns & Buildings)
================================================
Watch procedural town and building generation.
Towns, buildings, rooms, materials, and schedules.
"""

import sys
import time
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from layers.layer4_structures import TownGenerator, BuildingGenerator, Town, Building, BuildingType, BuildingMaterial


def view_layer4(iterations=6, delay=0.6):
    """
    Watch Layer 4: Structures in action.
    
    Shows:
    - Town generation
    - Building generation (houses, shops, taverns, etc.)
    - Room layouts
    - Construction materials
    - Opening/closing schedules
    """
    
    print("\n" + "=" * 70)
    print("  LAYER 4 VIEWER - Structures")
    print("  Watching procedural town and building generation")
    print("=" * 70)
    print(f"\nRunning {iterations} iterations... (delay: {delay}s)\n")
    
    time.sleep(1)
    
    town_gen = TownGenerator()
    building_gen = BuildingGenerator()
    
    # Track stats
    towns_generated = []
    buildings_generated = []
    type_counts = {t.value: 0 for t in BuildingType}
    
    for i in range(iterations):
        print("-" * 70)
        print(f"Iteration {i+1:2d}")
        print("-" * 70)
        
        # Generate a town (every other iteration)
        if i % 2 == 0:
            town = town_gen.generate_town(building_count=random.randint(3, 6))
            towns_generated.append(town)
            
            print(f"\n  TOWN: {town.name}")
            print(f"    Region: {town.region}")
            print(f"    Population: {town.population}")
            print(f"    Buildings: {len(town.buildings)}")
            
            # Show buildings in town
            print(f"\n  Buildings:")
            for b_id, building in list(town.buildings.items())[:4]:
                type_counts[building.building_type.value] += 1
                buildings_generated.append(building)
                
                print(f"    - {building.name}")
                print(f"      Type: {building.building_type.value}")
                print(f"      Material: {building.material.value if isinstance(building.material, BuildingMaterial) else building.material}")
                print(f"      Rooms: {len(building.rooms)}")
                
                # Show rooms
                if building.rooms:
                    room_names = [r.name for r in building.rooms[:3]]
                    print(f"      Room types: {', '.join(room_names)}")
                
                # Show schedule
                if building.schedule:
                    opens = building.schedule.get('opens', 'N/A')
                    closes = building.schedule.get('closes', 'N/A')
                    print(f"      Hours: {opens} - {closes}")
                
                # Show occupants
                if building.occupants:
                    print(f"      Occupants: {len(building.occupants)}")
                
                print()
        
        # Generate individual buildings
        else:
            # Generate different building types
            btype = random.choice(list(BuildingType))
            building = building_gen.generate_building(building_type=btype)
            buildings_generated.append(building)
            type_counts[building.building_type.value] += 1
            
            print(f"\n  BUILDING: {building.name}")
            print(f"    Type: {building.building_type.value}")
            print(f"    Material: {building.material.value if isinstance(building.material, BuildingMaterial) else building.material}")
            print(f"    Size: {building.size}")
            
            # Show rooms
            print(f"\n    Rooms ({len(building.rooms)}):")
            for room in building.rooms[:4]:
                print(f"      - {room.name}")
            
            # Show schedule
            print(f"\n    Schedule:")
            for key, val in building.schedule.items():
                print(f"      {key}: {val}")
            
            print()
        
        time.sleep(delay)
    
    # Summary
    print("=" * 70)
    print("  Layer 4 Viewer Complete")
    print("=" * 70)
    
    print(f"\n  Generated:")
    print(f"    Towns:      {len(towns_generated)}")
    print(f"    Buildings:  {len(buildings_generated)}")
    
    if towns_generated:
        avg_pop = sum(t.population for t in towns_generated) / len(towns_generated)
        avg_buildings = sum(len(t.buildings) for t in towns_generated) / len(towns_generated)
        print(f"\n  Town Stats:")
        print(f"    Avg Population:  {avg_pop:.0f}")
        print(f"    Avg Buildings:   {avg_buildings:.1f}")
    
    print(f"\n  Building Type Distribution:")
    for btype, count in sorted(type_counts.items()):
        if count > 0:
            pct = (count / len(buildings_generated)) * 100 if buildings_generated else 0
            print(f"    {btype:15s}: {count:2d} ({pct:.0f}%)")
    
    print()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Layer 4: Structures Viewer')
    parser.add_argument('--iterations', type=int, default=5, help='Number of iterations')
    parser.add_argument('--delay', type=float, default=0.8, help='Delay between iterations')
    parser.add_argument('--fast', action='store_true', help='Fast mode (0.3s delay)')
    
    args = parser.parse_args()
    
    if args.fast:
        args.delay = 0.3
    
    view_layer4(iterations=args.iterations, delay=args.delay)
