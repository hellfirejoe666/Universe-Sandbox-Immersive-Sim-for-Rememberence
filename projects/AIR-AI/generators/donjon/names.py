"""
name_generator.py
Python port of donjon name generator (public domain by drow)
Markov chain-based fantasy name generation
"""

import random
import json
import os

class NameGenerator:
    def __init__(self):
        self.name_sets = {}
        self.chain_cache = {}
        self._load_name_sets()
    
    def _load_name_sets(self):
        """Load predefined name lists for different cultures/types"""
        # Fantasy name samples for different cultures
        self.name_sets = {
            'human': [
                'Aldric', 'Beron', 'Cedric', 'Darius', 'Edric', 'Falcon', 'Gareth', 'Hadrian',
                'Ivan', 'Jorah', 'Kael', 'Landon', 'Marcus', 'Nolan', 'Oscar', 'Percival',
                'Quinn', 'Roland', 'Stefan', 'Thorin', 'Ulric', 'Victor', 'Walter', 'Xander',
                'Yoric', 'Zane', 'Adela', 'Brynn', 'Cera', 'Daria', 'Elara', 'Fiona', 'Greta',
                'Hanna', 'Isla', 'Jessa', 'Kara', 'Lena', 'Mira', 'Nora', 'Orla', 'Petra',
                'Quinn', 'Rosa', 'Sera', 'Tessa', 'Una', 'Vera', 'Wren', 'Xena', 'Yara', 'Zora'
            ],
            'elf': [
                'Aelindra', 'Caelynn', 'Elandril', 'Faenor', 'Gwyndolyn', 'Ilythira', 'Lirael',
                'Myrddin', 'Nymara', 'Oberon', 'Phaera', 'Quelana', 'Rhiannon', 'Sylvaris',
                'Thalandra', 'Umbriel', 'Vaelindra', 'Whisper', 'Xylia', 'Yandira', 'Zephyra',
                'Aethon', 'Caelum', 'Eamon', 'Fenris', 'Galen', 'Isolde', 'Jareth', 'Kaelen',
                'Lucian', 'Meridian', 'Nerion', 'Orion', 'Peregrin', 'Quillon', 'Rowan', 'Sorian'
            ],
            'dwarf': [
                'Bardin', 'Dwalin', 'Fundin', 'Gloin', 'Harald', 'Ivar', 'Jorund', 'Korgan',
                'Lofar', 'Morgrim', 'Narvi', 'Oin', 'Perrin', 'Quar', 'Ragnar', 'Sten',
                'Thrain', 'Ulfgar', 'Vondal', 'Wulfgar', 'Xoln', 'Yorg', 'Zephyr',
                'Bera', 'Disa', 'Frigga', 'Gerta', 'Helga', 'Ingrid', 'Jora', 'Kari',
                'Lofn', 'Mira', 'Nanna', 'Oda', 'Rinda', 'Sigyn', 'Thora', 'Ulla', 'Vestra', 'Ylva'
            ],
            'orc': [
                'Bagron', 'Drog', 'Gorbag', 'Grish', 'Grom', 'Gruumsh', 'Korgul', 'Lug',
                'Morg', 'Narzug', 'Ogrish', 'Pug', 'Quag', 'Rorg', 'Shagrat', 'Throk',
                'Ugluk', 'Vorg', 'Warg', 'Yazg', 'Zog', 'Ashnak', 'Bonecrusher', 'Dush',
                'Ghazghkull', 'Harg', 'Ishnub', 'Jagh', 'Kazag', 'Lob', 'Muzgash', 'Narzug'
            ],
            'mystic': [
                'Azarel', 'Balthazar', 'Celestine', 'Damaris', 'Ezekiel', 'Gabriel', 'Haniel',
                'Ithuriel', 'Jophiel', 'Kether', 'Lailah', 'Metatron', 'Nuriel', 'Oraphael',
                'Phanuel', 'Quintessence', 'Raziel', 'Sandalphon', 'Tiphareth', 'Uriel',
                'Vretil', 'Witchlight', 'Xaphan', 'Yahriel', 'Zadkiel'
            ],
            'dark': [
                'Malakor', 'Shadowmere', 'Nightshade', 'Voidwalker', 'Darkwhisper', 'Grimoire',
                'Umbrage', 'Nocturne', 'Eclipse', 'Phantom', 'Specter', 'Wraith', 'Bane',
                'Dread', 'Doom', 'Fang', 'Ghoul', 'Hex', 'Jinx', 'Kraven', 'Lich', 'Mortis',
                'Necro', 'Onyx', 'Plague', 'Quell', 'Raven', 'Scourge', 'Torment', 'Vex', 'Wrath'
            ]
        }
    
    def _construct_chain(self, name_list):
        """Build Markov chain from list of names"""
        chain = {}
        
        for name_entry in name_list:
            # Handle multi-part names
            names = name_entry.split()
            chain = self._incr_chain(chain, 'parts', len(names))
            
            for name in names:
                name = name.strip()
                if not name:
                    continue
                    
                chain = self._incr_chain(chain, 'name_len', len(name))
                
                # Track initial letter
                if len(name) > 0:
                    c = name[0]
                    chain = self._incr_chain(chain, 'initial', c)
                
                # Build letter transitions
                last_c = name[0] if len(name) > 0 else ''
                for i in range(1, len(name)):
                    c = name[i]
                    chain = self._incr_chain(chain, last_c, c)
                    last_c = c
        
        return self._scale_chain(chain)
    
    def _incr_chain(self, chain, key, token):
        """Increment count in chain for given key/token"""
        if key not in chain:
            chain[key] = {}
        if token not in chain[key]:
            chain[key][token] = 1
        else:
            chain[key][token] += 1
        return chain
    
    def _scale_chain(self, chain):
        """Scale chain weights for better name generation"""
        table_len = {}
        
        for key in chain:
            table_len[key] = 0
            for token in chain[key]:
                count = chain[key][token]
                weighted = int(count ** 1.3)
                table_len[key] += weighted
        
        # Normalize
        for key in chain:
            for token in list(chain[key].keys()):
                count = chain[key][token]
                chain[key][token] = int(count ** 1.3)
        
        return chain
    
    def _markov_chain(self, name_type):
        """Get or create Markov chain for name type"""
        if name_type in self.chain_cache:
            return self.chain_cache[name_type]
        
        if name_type in self.name_sets and len(self.name_sets[name_type]) > 0:
            chain = self._construct_chain(self.name_sets[name_type])
            self.chain_cache[name_type] = chain
            return chain
        
        return None
    
    def _weighted_choice(self, weights_dict):
        """Select item based on weights"""
        total = sum(weights_dict.values())
        if total == 0:
            return None
        
        r = random.randint(1, total)
        upto = 0
        for item, weight in weights_dict.items():
            upto += weight
            if upto >= r:
                return item
        return None
    
    def _generate_name(self, name_type):
        """Generate a single name using Markov chain"""
        chain = self._markov_chain(name_type)
        if not chain:
            return self._fallback_name(name_type)
        
        # Determine name length
        if 'name_len' in chain and chain['name_len']:
            name_len = self._weighted_choice(chain['name_len'])
        else:
            name_len = random.randint(4, 8)
        
        if name_len is None or name_len < 2:
            name_len = 5
        
        # Start with initial letter
        if 'initial' in chain and chain['initial']:
            current = self._weighted_choice(chain['initial'])
        else:
            current = random.choice('abcdefghijklmnopqrstuvwxyz')
        
        name = current.capitalize()
        
        # Generate remaining letters
        for _ in range(name_len - 1):
            if current in chain and chain[current]:
                next_char = self._weighted_choice(chain[current])
                if next_char:
                    name += next_char
                    current = next_char
                else:
                    break
            else:
                # Fallback to random vowel/consonant
                if current.lower() in 'aeiou':
                    current = random.choice('bcdfghjklmnpqrstvwxyz')
                else:
                    current = random.choice('aeiou')
                name += current
        
        return name
    
    def _fallback_name(self, name_type):
        """Return a simple fallback name if generation fails"""
        if name_type in self.name_sets and self.name_sets[name_type]:
            return random.choice(self.name_sets[name_type])
        return "Traveler"
    
    def generate(self, name_type='human'):
        """Generate a single name"""
        return self._generate_name(name_type.lower())
    
    def generate_list(self, name_type='human', count=5):
        """Generate multiple names"""
        names = []
        for _ in range(count):
            name = self.generate(name_type)
            if name not in names:  # Avoid duplicates
                names.append(name)
        return names
    
    def generate_npc(self):
        """Generate a full NPC with name and basic traits"""
        name_type = random.choice(['human', 'elf', 'dwarf', 'mystic', 'dark'])
        name = self.generate(name_type)
        
        # Basic NPC template
        npc = {
            'name': name,
            'race': name_type,
            'role': random.choice([
                'Merchant', 'Guard', 'Scholar', 'Priest', 'Rogue',
                'Warrior', 'Mage', 'Healer', 'Blacksmith', 'Innkeeper',
                'Hunter', 'Minstrel', 'Alchemist', 'Sage', 'Noble'
            ]),
            'disposition': random.choice([
                'Friendly', 'Cautious', 'Hostile', 'Neutral', 'Curious',
                'Anxious', 'Confident', 'Mysterious', 'Gruff', 'Welcoming'
            ])
        }
        
        return npc


# Convenience functions
def generate_name(name_type='human'):
    """Quick name generation"""
    gen = NameGenerator()
    return gen.generate(name_type)

def generate_names(name_type='human', count=5):
    """Generate multiple names"""
    gen = NameGenerator()
    return gen.generate_list(name_type, count)

def generate_npc():
    """Generate a random NPC"""
    gen = NameGenerator()
    return gen.generate_npc()


if __name__ == '__main__':
    # Test the generator
    gen = NameGenerator()
    
    print("=== Donjon Name Generator (Python) ===\n")
    
    for race in ['human', 'elf', 'dwarf', 'orc', 'mystic', 'dark']:
        names = gen.generate_list(race, 5)
        print(f"{race.capitalize()}: {', '.join(names)}")
    
    print("\n=== Sample NPCs ===")
    for _ in range(3):
        npc = gen.generate_npc()
        print(f"{npc['name']} ({npc['race']} {npc['role']}) - {npc['disposition']}")
