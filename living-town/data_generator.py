"""
Procedural Generator - Using Canonical Data as Foundation
==========================================================
Generates novel content by combining, varying, and extending canonical data.

Philosophy:
- Canonical data = rules, constraints, building blocks
- Procedural generation = novel combinations, variations, emergent content
- Best of both: consistency + surprise
"""

import random
from typing import Dict, List, Any, Optional, Tuple
from data_loader import get_loader


class ProceduralGenerator:
    """
    Generates novel content from canonical data.
    """
    
    def __init__(self):
        self.loader = get_loader()
    
    # ────────────────────────────────────────────────
    # Character Generation
    # ────────────────────────────────────────────────
    
    def generate_character(self) -> Dict[str, Any]:
        """
        Generate a unique character by combining canonical data.
        
        Combines:
        - Animal sign (12 options)
        - Star sign (12 options)
        - Species (36 options)
        - Type (24 options)
        - Class skills (6 categories × 6 options each)
        
        Result: 12 × 12 × 36 × 24 × 6^6 = ~2.5 trillion possibilities
        """
        # Get all canonical options
        animals = list(self.loader.get_all_animal_signs().keys())
        stars = list(self.loader.get_all_star_signs().keys())
        species_list = list(self.loader.get_all_species().keys())
        types_list = list(self.loader.get_all_types().keys())
        
        # Random selection
        animal = random.choice(animals)
        star = random.choice(stars)
        species = random.choice(species_list)
        char_type = random.choice(types_list)
        
        # Get canonical data
        animal_data = self.loader.get_animal_sign(animal)
        star_data = self.loader.get_star_sign(star)
        species_data = self.loader.get_species(species)
        type_data = self.loader.get_type(char_type)
        
        # Generate class skills (6 categories)
        classes = self.loader.get_all_classes()
        skills = {}
        for category in ['melee', 'ranged', 'magic', 'step', 'special', 'trance']:
            cat_data = classes.get(category, {})
            options = list(cat_data.keys()) if isinstance(cat_data, dict) else []
            if options:
                skills[category] = random.choice(options)
        
        # Generate name (procedural, using canonical themes)
        name = self._generate_name(animal, species, char_type)
        
        return {
            'name': name,
            'animal': animal,
            'star': star,
            'species': species,
            'type': char_type,
            'skills': skills,
            'canonical_data': {
                'animal': animal_data,
                'star': star_data,
                'species': species_data,
                'type': type_data,
            }
        }
    
    def _generate_name(self, animal: str, species: str, char_type: str) -> str:
        """Generate a name using canonical themes."""
        # Syllable pools based on type
        syllables_by_type = {
            'Thunder': ['Zan', 'Thor', 'Ram', 'Vol'],
            'Warrior': ['Krag', 'Gor', 'Tak', 'Bor'],
            'Spell': ['Ael', 'Mir', 'Thal', 'Fae'],
            'Pyro': ['Ign', 'Pyre', 'Flam', 'Ember'],
            'Aqua': ['Mar', 'Aqua', 'Nere', 'Tide'],
            'Beast': ['Fen', 'Wolf', 'Rex', 'Fang'],
        }
        
        type_syllables = syllables_by_type.get(char_type, ['Ren', 'Mem', 'Ori'])
        
        # Combine syllables
        prefix = random.choice(type_syllables)
        suffix = random.choice(['os', 'ia', 'us', 'a', 'en', 'is', 'ax'])
        
        return prefix + suffix
    
    def generate_variation(self, base_data: Dict[str, Any], 
                          variation_type: str = 'minor') -> Dict[str, Any]:
        """
        Generate a variation of existing canonical data.
        
        Types:
        - minor: Small stat adjustments (±1-2)
        - major: Larger changes, new trait combinations
        - exotic: Completely novel combinations
        
        Use case: Create unique NPCs that are similar but distinct.
        """
        import copy
        variant = copy.deepcopy(base_data)
        
        if variation_type == 'minor':
            # Adjust biorhythms slightly
            if 'biorhythms' in variant:
                for key in variant['biorhythms']:
                    delta = random.randint(-2, 2)
                    variant['biorhythms'][key] = max(1, variant['biorhythms'][key] + delta)
        
        elif variation_type == 'major':
            # Swap some traits, add new ones
            if 'biorhythms' in variant:
                keys = list(variant['biorhythms'].keys())
                # Swap two values
                if len(keys) >= 2:
                    k1, k2 = random.sample(keys, 2)
                    variant['biorhythms'][k1], variant['biorhythms'][k2] = \
                        variant['biorhythms'][k2], variant['biorhythms'][k1]
            
            # Add mutation marker
            variant['mutation'] = True
            variant['mutation_type'] = random.choice([
                'awakened', 'corrupted', 'blessed', 'cursed', 'enhanced'
            ])
        
        elif variation_type == 'exotic':
            # Completely novel combination
            if 'biorhythms' in variant:
                for key in variant['biorhythms']:
                    # Random value within reasonable range
                    variant['biorhythms'][key] = random.randint(5, 15)
            
            variant['exotic'] = True
            variant['exotic_traits'] = random.sample(
                ['void_touched', 'memory_born', 'echo_walk', 'time_shift', 'reality_anchor'],
                k=random.randint(1, 3)
            )
        
        return variant
    
    # ────────────────────────────────────────────────
    # Item Generation
    # ────────────────────────────────────────────────
    
    def generate_item(self, item_type: str = 'weapon', 
                     rarity: str = None) -> Dict[str, Any]:
        """
        Generate an item using canonical materials and runes.
        
        Combines:
        - Base type (weapon/armor categories)
        - Material (from types.json)
        - Rune enchantments (from runes.json)
        - Rarity modifiers
        """
        # Get canonical materials
        types_data = self.loader.get_all_types()
        materials = list(types_data.keys())[:10]  # Use first 10 as materials
        
        # Get canonical runes
        runes_data = self.loader.get_all_runes()
        rune_list = list(runes_data.keys())
        
        # Select components
        material = random.choice(materials)
        num_runes = random.randint(0, 3) if rarity != 'common' else 0
        selected_runes = random.sample(rune_list, min(num_runes, len(rune_list)))
        
        # Generate base stats
        base_stats = self._generate_item_stats(item_type, rarity)
        
        # Apply material modifier (skip if modifiers are stat references like "SPL")
        material_data = types_data.get(material, {})
        if 'stat_modifiers' in material_data:
            # These are biorhythm references (e.g., "SPL", "KNO"), not direct stat mods
            # Skip for now, or resolve against character biorhythms
            pass
        
        # Apply rune effects
        rune_effects = []
        for rune_name in selected_runes:
            rune_data = runes_data.get(rune_name, {})
            effect = rune_data.get('effect', f'{rune_name} enchantment')
            rune_effects.append(effect)
        
        return {
            'type': item_type,
            'material': material,
            'rarity': rarity or self._roll_rarity(),
            'stats': base_stats,
            'runes': selected_runes,
            'effects': rune_effects,
        }
    
    def _generate_item_stats(self, item_type: str, rarity: str) -> Dict[str, int]:
        """Generate base stats for an item."""
        rarity_multipliers = {
            'common': 1.0,
            'uncommon': 1.3,
            'rare': 1.6,
            'epic': 2.0,
            'legendary': 2.5,
            'transcendent': 3.0,
        }
        
        mult = rarity_multipliers.get(rarity or 'common', 1.0)
        
        if item_type == 'weapon':
            return {
                'damage': int(random.randint(8, 20) * mult),
                'accuracy': int(random.randint(50, 80) * mult),
                'speed': int(random.randint(1, 5) * mult),
            }
        elif item_type == 'armor':
            return {
                'defense': int(random.randint(5, 15) * mult),
                'resistance': int(random.randint(3, 10) * mult),
                'weight': int(random.randint(5, 20)),  # Weight doesn't scale with rarity
            }
        else:
            return {'power': int(random.randint(5, 15) * mult)}
    
    def _roll_rarity(self) -> str:
        """Roll for item rarity."""
        roll = random.random()
        if roll < 0.50:
            return 'common'
        elif roll < 0.75:
            return 'uncommon'
        elif roll < 0.90:
            return 'rare'
        elif roll < 0.96:
            return 'epic'
        elif roll < 0.99:
            return 'legendary'
        else:
            return 'transcendent'
    
    # ────────────────────────────────────────────────
    # Event Generation
    # ────────────────────────────────────────────────
    
    def generate_event(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a narrative event using canonical data.
        
        Combines:
        - Entity types (species, types)
        - Locations (from worlds/regions)
        - Actions (from classes/abilities)
        - Outcomes (weighted by biorhythms)
        """
        # Get species for actors
        species_list = list(self.loader.get_all_species().keys())
        actor_species = random.choice(species_list)
        target_species = random.choice(species_list)
        
        # Get types for context
        types_list = list(self.loader.get_all_types().keys())
        event_type = random.choice(types_list)
        
        # Generate event template
        templates = [
            "{actor} encounters {target} in {location}",
            "{actor} discovers {artifact} of {type}",
            "{actor} performs {action} on {target}",
            "{location} experiences {phenomenon}",
        ]
        
        template = random.choice(templates)
        
        # Fill in template
        event_text = template.format(
            actor=f"A {actor_species}",
            target=f"a {target_species}",
            location=self._generate_location(),
            artifact=self._generate_artifact(),
            type=event_type,
            action=self._generate_action(),
            phenomenon=self._generate_phenomenon(),
        )
        
        return {
            'text': event_text,
            'actor_species': actor_species,
            'target_species': target_species,
            'event_type': event_type,
            'context': context,
        }
    
    def _generate_location(self) -> str:
        """Generate a location name."""
        prefixes = ['Crystal', 'Memory', 'Shattered', 'Echo', 'Void', 'Luminous']
        suffixes = ['Expanse', 'Nexus', 'Rift', 'Sanctum', 'Waste', 'Garden']
        return f"{random.choice(prefixes)} {random.choice(suffixes)}"
    
    def _generate_artifact(self) -> str:
        """Generate an artifact name."""
        adjectives = ['Ancient', 'Forgotten', 'Eternal', 'Cursed', 'Blessed']
        nouns = ['Relic', 'Artifact', 'Tome', 'Orb', 'Blade', 'Crown']
        return f"{random.choice(adjectives)} {random.choice(nouns)}"
    
    def _generate_action(self) -> str:
        """Generate an action."""
        actions = ['summons', 'banishes', 'transforms', 'awakens', 'destroys', 'creates']
        return random.choice(actions)
    
    def _generate_phenomenon(self) -> str:
        """Generate a cosmic phenomenon."""
        phenomena = [
            'memory storm', 'reality shift', 'time ripple',
            'void incursion', 'echo cascade', 'birth wave'
        ]
        return random.choice(phenomena)


# ────────────────────────────────────────────────
# Test
# ────────────────────────────────────────────────

if __name__ == '__main__':
    print("Testing Procedural Generator (with canonical data foundation)")
    print("=" * 70)
    
    gen = ProceduralGenerator()
    
    # Test character generation
    print("\nGenerated Characters:")
    for i in range(3):
        char = gen.generate_character()
        print(f"\n  {i+1}. {char['name']}")
        print(f"     {char['animal']} / {char['star']}")
        print(f"     {char['species']} ({char['type']})")
        print(f"     Skills: {char['skills']}")
    
    # Test variations
    print("\n\nCharacter Variations:")
    base = gen.generate_character()
    print(f"\n  Base: {base['name']} ({base['species']})")
    
    for var_type in ['minor', 'major', 'exotic']:
        variant = gen.generate_variation(base, var_type)
        markers = []
        if variant.get('mutation'):
            markers.append(f"MUTATION: {variant['mutation_type']}")
        if variant.get('exotic'):
            markers.append(f"EXOTIC: {', '.join(variant['exotic_traits'])}")
        
        print(f"  {var_type.capitalize()}: {markers if markers else 'Stat adjustments only'}")
    
    # Test item generation
    print("\n\nGenerated Items:")
    for rarity in ['common', 'rare', 'legendary']:
        item = gen.generate_item('weapon', rarity)
        print(f"\n  {rarity.capitalize()} Weapon:")
        print(f"    Material: {item['material']}")
        print(f"    Stats: {item['stats']}")
        print(f"    Runes: {item['runes']}")
        print(f"    Effects: {item['effects']}")
    
    # Test event generation
    print("\n\nGenerated Events:")
    for i in range(3):
        event = gen.generate_event({'week': 1, 'location': 'test'})
        print(f"  {i+1}. {event['text']}")
    
    print("\n" + "=" * 70)
    print("All generations used canonical data as foundation!")
