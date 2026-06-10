#!/usr/bin/env python3
"""
Layer 6 Viewer - Stellaris Scale
=================================
Watch procedural cosmic generation.
Star systems, worlds, galaxies, and jump routes.
"""

import sys
import time
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from layers.layer6_stellaris import (
    CosmicManager, GalaxyGenerator, StarSystem,
    StarType, SystemType, GalaxyRegion
)


def view_layer6(systems=5, delay=0.7):
    """
    Watch Layer 6: Stellaris Scale in action.
    
    Shows:
    - Galaxy generation
    - Star systems with multiple worlds
    - World types and properties
    - Jump routes between systems
    - Cosmic phenomena
    """
    
    print("\n" + "=" * 70)
    print("  LAYER 6 VIEWER - Stellaris Scale")
    print("  Watching procedural cosmic generation")
    print("=" * 70)
    print(f"\nGenerating {systems} star systems... (delay: {delay}s)\n")
    
    time.sleep(1)
    
    # Initialize cosmic manager
    cosmic_mgr = CosmicManager(
        galaxy_count=1,
        systems_per_galaxy=systems
    )
    
    galaxies = cosmic_mgr.get_all_galaxies()
    
    # Track stats
    systems_generated = []
    worlds_generated = []
    star_type_counts = {s.value: 0 for s in StarType}
    system_type_counts = {s.value: 0 for s in SystemType}
    world_type_counts = {}
    
    # Show galaxy overview
    print("-" * 70)
    print("  GALAXY OVERVIEW")
    print("-" * 70)
    
    for galaxy in galaxies:
        print(f"\n  GALAXY: {galaxy.name}")
        print(f"    Region: {galaxy.region_type.value}")
        print(f"    Systems: {len(galaxy.systems)}")
        print(f"    Size: {galaxy.diameter} light-years")
        print(f"    Age: {galaxy.age:,} million years")
        
        # Show systems
        print(f"\n    Star Systems:")
        for sys_id, system in list(galaxy.systems.items())[:systems]:
            systems_generated.append(system)
            star_type_counts[system.star_type.value] += 1
            system_type_counts[system.system_type.value] += 1
            
            print(f"\n      {system.name}")
            print(f"        Type: {system.system_type.value}")
            print(f"        Star: {system.star_type.value}")
            print(f"        Age: {system.age:,} MY")
            
            # Show worlds
            if system.worlds:
                print(f"        Worlds: {len(system.worlds)}")
                for world_id, world in list(system.worlds.items())[:3]:
                    worlds_generated.append(world)
                    wtype = world.get('type', 'Unknown')
                    world_type_counts[wtype] = world_type_counts.get(wtype, 0) + 1
                    print(f"          - {world.get('name', 'Unknown')} ({wtype})")
            
            # Show jump routes
            if system.jump_routes:
                print(f"        Jump Routes: {len(system.jump_routes)}")
    
    print("\n" + "=" * 70)
    print("  GENERATION COMPLETE")
    print("=" * 70)
    
    # Summary stats
    print(f"\n  Generated:")
    print(f"    Galaxies:  {len(galaxies)}")
    print(f"    Systems:   {len(systems_generated)}")
    print(f"    Worlds:    {len(worlds_generated)}")
    
    print(f"\n  Star Type Distribution:")
    for star_type, count in sorted(star_type_counts.items()):
        if count > 0:
            pct = (count / len(systems_generated)) * 100 if systems_generated else 0
            print(f"    {star_type:20s}: {count:2d} ({pct:.0f}%)")
    
    print(f"\n  System Type Distribution:")
    for sys_type, count in sorted(system_type_counts.items()):
        if count > 0:
            pct = (count / len(systems_generated)) * 100 if systems_generated else 0
            print(f"    {sys_type:20s}: {count:2d} ({pct:.0f}%)")
    
    if world_type_counts:
        print(f"\n  World Type Distribution:")
        for wtype, count in sorted(world_type_counts.items()):
            pct = (count / len(worlds_generated)) * 100 if worlds_generated else 0
            print(f"    {wtype:20s}: {count:2d} ({pct:.0f}%)")
    
    # Show cosmic phenomena
    print(f"\n  Cosmic Features:")
    regions = {}
    for galaxy in galaxies:
        region = galaxy.region_type.value
        regions[region] = regions.get(region, 0) + 1
    
    for region, count in regions.items():
        print(f"    {region:20s}: {count} galaxy(ies)")
    
    print()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Layer 6: Stellaris Scale Viewer')
    parser.add_argument('--systems', type=int, default=4, help='Number of star systems')
    parser.add_argument('--delay', type=float, default=0.8, help='Delay between sections')
    parser.add_argument('--fast', action='store_true', help='Fast mode (0.3s delay)')
    
    args = parser.parse_args()
    
    if args.fast:
        args.delay = 0.3
    
    view_layer6(systems=args.systems, delay=args.delay)
