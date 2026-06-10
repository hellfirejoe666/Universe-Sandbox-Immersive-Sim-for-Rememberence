"""
text_generator.py
Python port of donjon text generator (public domain by drow)
Template-based text generation with weighted tables
"""

import random
import re

class TextGenerator:
    def __init__(self):
        self.gen_data = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load text generation templates for various purposes"""
        
        # Tavern names
        self.gen_data['tavern_name'] = {
            '1-10': 'The {adjective} {noun}',
            '11-20': 'The {adjective} {animal}',
            '21-30': 'The {noun} and {noun}',
            '31-40': '{proper_name}\'s {noun}',
            '41-50': 'The {color} {animal}',
            '51-60': '{proper_name}\'s {adjective} {noun}',
            '61-70': 'The {adjective} {color} {noun}',
            '71-80': 'The {animal} and {animal}',
            '81-90': 'The {noun} of {proper_name}',
            '91-00': 'The {adjective} {noun} and {animal}'
        }
        
        self.gen_data['adjective'] = [
            'Drunken', 'Weary', 'Merry', 'Broken', 'Silent', 'Golden', 'Silver',
            'Crimson', 'Shadow', 'Gilded', 'Rusty', 'Ancient', 'Forgotten',
            'Cursed', 'Blessed', 'Haunted', 'Enchanted', 'Crystal', 'Iron',
            'Bronze', 'Sapphire', 'Ruby', 'Emerald', 'Diamond', 'Obsidian'
        ]
        
        self.gen_data['noun'] = [
            'Tankard', 'Goblet', 'Chalice', 'Tankard', 'Mug', 'Flagon',
            'Sword', 'Shield', 'Helm', 'Anvil', 'Hammer', 'Forge',
            'Dragon', 'Griffin', 'Phoenix', 'Unicorn', 'Castle', 'Tower',
            'Garden', 'Fountain', 'Well', 'Bridge', 'Gate', 'Door',
            'Lantern', 'Torch', 'Candle', 'Fire', 'Ember', 'Ash'
        ]
        
        self.gen_data['animal'] = [
            'Lion', 'Tiger', 'Bear', 'Wolf', 'Fox', 'Hawk', 'Eagle',
            'Raven', 'Owl', 'Serpent', 'Dragon', 'Wyvern', 'Griffin',
            'Stag', 'Boar', 'Ram', 'Bull', 'Horse', 'Mare', 'Hound'
        ]
        
        self.gen_data['proper_name'] = [
            'Aldric', 'Beron', 'Cedric', 'Darius', 'Edric', 'Falcon',
            'Gareth', 'Hadrian', 'Ivan', 'Jorah', 'Kael', 'Landon',
            'Marcus', 'Nolan', 'Oscar', 'Percival', 'Quinn', 'Roland',
            'Adela', 'Brynn', 'Cera', 'Daria', 'Elara', 'Fiona',
            'Greta', 'Hanna', 'Isla', 'Jessa', 'Kara', 'Lena'
        ]
        
        self.gen_data['color'] = [
            'Red', 'Blue', 'Green', 'Gold', 'Silver', 'Black', 'White',
            'Crimson', 'Azure', 'Emerald', 'Amber', 'Violet', 'Scarlet',
            'Bronze', 'Copper', 'Iron', 'Steel', 'Pearl', 'Onyx'
        ]
        
        # Shop names
        self.gen_data['shop_name'] = {
            '1-15': 'The {adjective} {trade}',
            '16-30': '{proper_name}\'s {trade}',
            '31-45': 'The {noun} of {trade}',
            '46-60': 'The {color} {trade}',
            '61-75': '{proper_name} and {proper_name}\'s {trade}',
            '76-90': 'The {adjective} {noun}',
            '91-00': 'The {trade}\'s {noun}'
        }
        
        self.gen_data['trade'] = [
            'Smith', 'Cobbler', 'Tailor', 'Baker', 'Butcher', 'Candlemaker',
            'Apothecary', 'Alchemist', 'Enchanter', 'Jeweler', 'Armorer',
            'Weaponsmith', 'Leatherworker', 'Cartographer', 'Scribe',
            'Herbalist', 'Gemcutter', 'Glassblower', 'Potter', 'Woodworker'
        ]
        
        # Quest hooks
        self.gen_data['quest_hook'] = {
            '1-10': 'A {npc} needs help with {problem}',
            '11-20': 'Find the {item} hidden in {location}',
            '21-30': 'Defeat the {creature} terrorizing {location}',
            '31-40': 'Deliver {item} to {npc} at {location}',
            '41-50': 'Investigate the mystery at {location}',
            '51-60': 'Protect {npc} from {threat}',
            '61-70': 'Retrieve {item} from {creature}',
            '71-80': 'Solve the riddle of {mystery}',
            '81-90': 'Stop the {threat} before {consequence}',
            '91-00': 'The prophecy speaks of {prophecy}'
        }
        
        self.gen_data['npc'] = [
            'merchant', 'priest', 'scholar', 'noble', 'peasant',
            'soldier', 'wizard', 'thief', 'hunter', 'healer'
        ]
        
        self.gen_data['problem'] = [
            'a missing heirloom', 'cursed lands', 'bandit raids',
            'a family feud', 'stolen documents', 'a broken promise',
            'disappearing livestock', 'strange noises', 'a lost child'
        ]
        
        self.gen_data['item'] = [
            'ancient tome', 'crystal shard', 'golden amulet', 'cursed ring',
            'magic sword', 'sacred relic', 'royal seal', 'dragon egg',
            'phoenix feather', 'unicorn horn', 'shadow essence', 'star metal'
        ]
        
        self.gen_data['location'] = [
            'the old forest', 'the haunted castle', 'the sunken temple',
            'the crystal caves', 'the burning wastes', 'the frozen peaks',
            'the whispering swamp', 'the desert ruins', 'the cloud city',
            'the underground kingdom', 'the island fortress', 'the void between stars'
        ]
        
        self.gen_data['creature'] = [
            'dragon', 'lich', 'demon', 'giant', 'hydra', 'kraken',
            'phoenix', 'griffin', 'manticore', 'chimera', 'gorgon', 'behemoth'
        ]
        
        self.gen_data['threat'] = [
            'plague', 'war', 'famine', 'curse', 'invasion', 'cult',
            'natural disaster', 'magical catastrophe', 'ancient evil awakening'
        ]
        
        self.gen_data['mystery'] = [
            'the vanished kingdom', 'the silent tower', 'the blood moon',
            'the weeping statue', 'the endless storm', 'the floating city',
            'the time loop', 'the shadow plague', 'the dream realm'
        ]
        
        self.gen_data['consequence'] = [
            'the world ends', 'time unravels', 'darkness consumes all',
            'the gods return', 'reality fractures', 'memory is lost forever'
        ]
        
        self.gen_data['prophecy'] = [
            'a hero born of two worlds', 'the return of the lost king',
            'the breaking of the ancient seal', 'the union of fire and ice',
            'the child of prophecy awakens', 'the final battle approaches',
            'the threads of fate converge', 'the oracle speaks truth at last'
        ]
        
        # Room descriptions
        self.gen_data['room_desc'] = {
            '1-20': 'A {size} {condition} chamber with {lighting} and {furnishing}',
            '21-40': '{size} {condition} hall, {lighting}, furnished with {furnishing}',
            '41-60': 'The {condition} {size} room contains {furnishing} under {lighting}',
            '61-80': 'A {size} space, {condition}, lit by {lighting}, holding {furnishing}',
            '81-00': 'This {condition} {size} chamber features {furnishing} and {lighting}'
        }
        
        self.gen_data['size'] = [
            'small', 'cramped', 'modest', 'spacious', 'large', 'vast',
            'enormous', 'tiny', 'expansive', 'cozy', 'grand', 'massive'
        ]
        
        self.gen_data['condition'] = [
            'pristine', 'dusty', 'ancient', 'new', 'crumbling', 'elegant',
            'rustic', 'ornate', 'simple', 'magnificent', 'squalid', 'luxurious',
            'abandoned', 'well-kept', 'mysterious', 'haunted', 'blessed', 'cursed'
        ]
        
        self.gen_data['lighting'] = [
            'flickering torchlight', 'soft candlelight', 'bright sunlight',
            'dim lanterns', 'magical glow', 'shadowy darkness',
            'moonlight streaming through windows', 'warm fireplace light',
            'cold blue radiance', 'shifting colored lights', 'natural daylight'
        ]
        
        self.gen_data['furnishing'] = [
            'a long table and benches', 'scattered chairs', 'a throne',
            'bookshelves lining the walls', 'a large bed', 'chests and crates',
            'tapestries and rugs', 'weapons on display', 'alchemical equipment',
            'a writing desk', 'statues and sculptures', 'nothing but bare stone'
        ]
    
    def _select_from(self, data):
        """Select from array or weighted table"""
        if isinstance(data, list):
            return random.choice(data)
        elif isinstance(data, dict):
            return self._select_from_table(data)
        return ''
    
    def _select_from_table(self, table):
        """Select from weighted d100 table"""
        roll = random.randint(1, 100)
        
        for key, value in table.items():
            range_match = self._parse_range(key)
            if range_match and range_match[0] <= roll <= range_match[1]:
                return value
        
        return ''
    
    def _parse_range(self, key):
        """Parse d100 range key (e.g., '1-10', '91-00')"""
        if key == '00':
            return (100, 100)
        
        match = re.match(r'(\d+)-(\d+)', key)
        if match:
            low = int(match.group(1))
            high = int(match.group(2))
            if high == 0:  # Handle '91-00' as 91-100
                high = 100
            return (low, high)
        
        match = re.match(r'(\d+)-00', key)
        if match:
            return (int(match.group(1)), 100)
        
        try:
            num = int(key)
            return (num, num)
        except:
            return None
    
    def _expand_tokens(self, template):
        """Expand {token} placeholders in template"""
        max_iterations = 10
        iteration = 0
        
        while '{' in template and iteration < max_iterations:
            iteration += 1
            match = re.search(r'\{(\w+)\}', template)
            if not match:
                break
            
            token = match.group(1)
            if token in self.gen_data:
                replacement = self._select_from(self.gen_data[token])
                template = template.replace('{' + token + '}', replacement)
            else:
                # Token not found, remove braces
                template = template.replace('{' + token + '}', token)
        
        return template
    
    def generate(self, template_type):
        """Generate text from template type"""
        if template_type not in self.gen_data:
            return f"[Unknown template: {template_type}]"
        
        template = self._select_from(self.gen_data[template_type])
        return self._expand_tokens(template)
    
    def generate_list(self, template_type, count=5):
        """Generate multiple texts"""
        results = []
        for _ in range(count):
            text = self.generate(template_type)
            results.append(text)
        return results
    
    def generate_tavern(self):
        """Generate a complete tavern description"""
        name = self.generate('tavern_name')
        
        # Tavern qualities
        size = self._select_from(self.gen_data['size'])
        condition = self._select_from(self.gen_data['condition'])
        lighting = self._select_from(self.gen_data['lighting'])
        furnishing = self._select_from(self.gen_data['furnishing'])
        
        # Generate patrons
        patron_count = random.randint(2, 8)
        patrons = []
        for _ in range(patron_count):
            patron_type = self._select_from(self.gen_data['npc'])
            patrons.append(f"a {patron_type}")
        
        patron_desc = ', '.join(patrons[:-1])
        if len(patrons) > 1:
            patron_desc += f' and {patrons[-1]}'
        else:
            patron_desc = patrons[0] if patrons else 'no one'
        
        return {
            'name': name,
            'description': f"A {size} {condition} tavern with {lighting} and {furnishing}. {patron_desc.capitalize()} sit at the tables.",
            'atmosphere': f"{condition} and {size}",
            'patrons': patrons
        }
    
    def generate_shop(self):
        """Generate a complete shop description"""
        name = self.generate('shop_name')
        trade = self._select_from(self.gen_data['trade'])
        
        return {
            'name': name,
            'trade': trade,
            'description': f"{name} - A {trade}'s establishment offering quality goods and services."
        }
    
    def generate_quest(self):
        """Generate a complete quest hook"""
        hook = self.generate('quest_hook')
        
        return {
            'hook': hook,
            'type': 'adventure',
            'difficulty': random.choice(['Easy', 'Moderate', 'Challenging', 'Deadly'])
        }
    
    def generate_room(self):
        """Generate a room description"""
        desc = self.generate('room_desc')
        
        return {
            'description': desc,
            'explored': False,
            'features': []
        }


# Convenience functions
def generate(template_type):
    """Quick text generation"""
    gen = TextGenerator()
    return gen.generate(template_type)

def generate_tavern():
    """Generate a tavern"""
    gen = TextGenerator()
    return gen.generate_tavern()

def generate_shop():
    """Generate a shop"""
    gen = TextGenerator()
    return gen.generate_shop()

def generate_quest():
    """Generate a quest hook"""
    gen = TextGenerator()
    return gen.generate_quest()

def generate_room():
    """Generate a room description"""
    gen = TextGenerator()
    return gen.generate_room()


if __name__ == '__main__':
    # Test the generator
    gen = TextGenerator()
    
    print("=== Donjon Text Generator (Python) ===\n")
    
    print("--- Tavern Names ---")
    for _ in range(5):
        print(f"  {gen.generate('tavern_name')}")
    
    print("\n--- Shop Names ---")
    for _ in range(5):
        print(f"  {gen.generate('shop_name')}")
    
    print("\n--- Quest Hooks ---")
    for _ in range(3):
        quest = gen.generate_quest()
        print(f"  [{quest['difficulty']}] {quest['hook']}")
    
    print("\n--- Room Descriptions ---")
    for _ in range(3):
        room = gen.generate_room()
        print(f"  {room['description']}")
    
    print("\n--- Complete Tavern ---")
    tavern = gen.generate_tavern()
    print(f"  Name: {tavern['name']}")
    print(f"  {tavern['description']}")
