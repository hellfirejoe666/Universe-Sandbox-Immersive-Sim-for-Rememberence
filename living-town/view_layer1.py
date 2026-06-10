#!/usr/bin/env python3
"""
Layer 1 Viewer - Core Rules
===========================
Watch biorhythm calculations, dice rolls, and thought generation.
Pure ASCII, simple console output.
"""

import sys
import time
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from layers.layer1_core_rules import calculate_biorhythms, generate_thoughts, roll_dice


def view_layer1(iterations=10, delay=0.5):
    """
    Watch Layer 1: Core Rules in action.
    
    Shows:
    - Biorhythm calculations (12 traits)
    - Thought generation (6 parameters)
    - Dice rolls with modifiers
    """
    
    print("\n" + "=" * 70)
    print("  LAYER 1 VIEWER - Core Rules")
    print("  Watching biorhythms, thoughts, and dice rolls")
    print("=" * 70)
    print(f"\nRunning {iterations} iterations... (delay: {delay}s)\n")
    
    time.sleep(1)
    
    # Animal and star sign samples
    animals = ["Dragon", "Tiger", "Rat", "Ox", "Snake", "Horse"]
    stars = ["Scorpio", "Aries", "Leo", "Taurus", "Gemini", "Virgo"]
    
    for i in range(iterations):
        print("-" * 70)
        print(f"Iteration {i+1:2d}")
        print("-" * 70)
        
        # Pick random signs
        animal = random.choice(animals)
        star = random.choice(stars)
        
        print(f"\n  Sign Combination: {animal} + {star}")
        
        # Calculate biorhythms
        bio = calculate_biorhythms(animal, star)
        
        print(f"\n  Biorhythms (12 traits):")
        print(f"    MNF={bio.MNF:2d}  SPL={bio.SPL:2d}  BEU={bio.BEU:2d}")
        print(f"    STR={bio.STR:2d}  FND={bio.FND:2d}  KNO={bio.KNO:2d}")
        print(f"    UND={bio.UND:2d}  WIS={bio.WIS:2d}  VIT={bio.VIT:2d}")
        print(f"    SEX={bio.SEX:2d}  DIV={bio.DIV:2d}  EGO={bio.EGO:2d}")
        print(f"    Sum: {bio.sum()}")
        
        # Generate thoughts
        thoughts = generate_thoughts(bio)
        
        print(f"\n  Thoughts (6 parameters):")
        print(f"    Environment:   {thoughts.Environment:3d}  (Chaos <-> Order)")
        print(f"    Emotion:       {thoughts.Emotion:3d}  (Fear <-> Love)")
        print(f"    Subconscious:  {thoughts.Subconscious:3d}  (Reject <-> Embrace)")
        print(f"    Conscious:     {thoughts.Conscious:3d}  (Passive <-> Active)")
        print(f"    Abstraction:   {thoughts.Abstraction:3d}  (Lived <-> Learned)")
        print(f"    Perception:    {thoughts.Perception:3d}  (Negative <-> Positive)")
        print(f"    State:         {thoughts.State:.1f}")
        
        # Dice rolls
        print(f"\n  Dice Rolls:")
        for mod in [0, 2, 5]:
            result = roll_dice(sides=20, modifier=mod)
            total, rolls, is_crit, is_fail = result
            mod_str = f"+{mod}" if mod > 0 else ""
            crit_str = " [CRIT!]" if is_crit else (" [FAIL]" if is_fail else "")
            print(f"    d20{mod_str}: {rolls[0]:2d} {mod_str:>3} = {total:2d}{crit_str}")
        
        # Compatibility test
        if i < iterations - 1:
            animal2 = random.choice(animals)
            star2 = random.choice(stars)
            bio2 = calculate_biorhythms(animal2, star2)
            
            # Simple compatibility (sum of matching traits)
            compat = sum([
                abs(bio.MNF - bio2.MNF),
                abs(bio.SPL - bio2.SPL),
                abs(bio.EGO - bio2.EGO),
            ]) / 3
            compat_pct = 100 - min(100, compat * 5)
            
            print(f"\n  Compatibility ({animal}/{star} vs {animal2}/{star2}):")
            print(f"    Score: {compat_pct:.0f}%")
        
        print()
        time.sleep(delay)
    
    print("=" * 70)
    print("  Layer 1 Viewer Complete")
    print("=" * 70)
    print(f"\n  Total iterations: {iterations}")
    print(f"  Unique combinations: {len(animals)} x {len(stars)} = {len(animals) * len(stars)} possible")
    print()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Layer 1: Core Rules Viewer')
    parser.add_argument('--iterations', type=int, default=5, help='Number of iterations')
    parser.add_argument('--delay', type=float, default=0.8, help='Delay between iterations')
    parser.add_argument('--fast', action='store_true', help='Fast mode (0.3s delay)')
    
    args = parser.parse_args()
    
    if args.fast:
        args.delay = 0.3
    
    view_layer1(iterations=args.iterations, delay=args.delay)
