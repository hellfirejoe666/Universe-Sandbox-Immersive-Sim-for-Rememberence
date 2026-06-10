import random
import json

class DonjonGenerator:
    """
    Hybrid generator inspired by Donjon. 
    Produces structured game content (NPCs, Loot, Locations) 
    that the AIR-AI Oracle can then 'weave' into narrative.
    """
    def __init__(self):
        # Templates would typically be loaded from D:\GPT4All\AIPlus\donjon
        self.templates = {
            "npc": {
                "names": ["Kaelen", "Sariel", "Thalric", "Elara", "Maelis"],
                "roles": ["Wandering Scholar", "Shattered Guard", "Void Weaver", "Silent Monk"],
                "traits": ["Obsessive", "Benevolent", "Cynical", "Enigmatic"]
            },
            "location": {
                "adjectives": ["Luminous", "Desolate", "Whispering", "Fractured"],
                "nouns": ["Spires", "Catacombs", "Void-Garden", "Shattered Archive"],
                "atmosphere": ["Cold dread", "Warm nostalgia", "Electric tension"]
            },
            "loot": {
                "rarity": ["Common", "Rare", "Exotic", "Transcendent"],
                "types": ["Rune-Sliver", "Echo-Glass", "Sprit-Binding Thread", "Void-Calyx"]
            }
        }

    def generate_npc(self):
        return {
            "name": random.choice(self.templates["npc"]["names"]),
            "role": random.choice(self.templates["npc"]["roles"]),
            "trait": random.choice(self.templates["npc"]["traits"]),
            "biorhythms": self._generate_biorhythms()
        }

    def generate_location(self):
        return {
            "name": f"{random.choice(self.templates['location']['adjectives'])} {random.choice(self.templates['location']['nouns'])}",
            "atmosphere": random.choice(self.templates['location']['atmosphere'])
        }

    def _generate_biorhythms(self):
        # Generate 12 biorhythms based on Project Rememberence spec
        bios = ['MNF', 'SPL', 'BEU', 'STR', 'FND', 'KNO', 'UND', 'WIS', 'VIT', 'SEX', 'DIV', 'EGO']
        return {b: random.randint(1, 20) for b in bios}

oracle_gen = DonjonGenerator()
