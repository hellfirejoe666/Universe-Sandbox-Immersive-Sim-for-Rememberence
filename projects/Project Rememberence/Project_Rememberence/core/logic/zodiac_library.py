import re
import json
from typing import Dict, List, Any

class ZodiacBiorhythmLibrary:
    """
    Parsed data and logic for Animal Signs in Rememberence.
    Extracts Biorhythms and Species mappings from the raw TTRPG files.
    """
    def __init__(self):
        # This would ideally be parsed from 0-Animal Signs.txt
        # I am hard-coding the extracted values for stability and speed.
        self.signs = {
            1: {
                "name": "Rat",
                "style": "Clever",
                "bios": {"MNF": 4, "SPL": 3, "BEU": 1, "STR": 0, "FND": 1, "KNO": 2, "UND": 2, "WIS": 5, "VIT": 3, "SEX": 4, "DIV": 5, "EGO": 6},
                "elements": ["Water", "Dark"],
                "species": {"Imp": "ATK + EGO", "Merr": "DEF + EGO", "Pixie": "SPD + EGO"}
            },
            2: {
                "name": "Ox",
                "style": "Resolute",
                "bios": {"MNF": 3, "SPL": 4, "BEU": 0, "STR": 1, "FND": 2, "KNO": 3, "UND": 1, "WIS": 4, "VIT": 2, "SEX": 5, "DIV": 6, "EGO": 5},
                "elements": ["Earth", "Water"],
                "species": {"Geneshan": "ATK + DIV", "Minotaur": "DEF + DIV", "Arachnos": "SPD + DIV"}
            },
            3: {
                "name": "Tiger",
                "style": "Radical",
                "bios": {"MNF": 2, "SPL": 5, "BEU": 1, "STR": 2, "FND": 3, "KNO": 4, "UND": 0, "WIS": 3, "VIT": 1, "SEX": 6, "DIV": 5, "EGO": 4},
                "elements": ["Air", "Fire"],
                "species": {"Tigris": "ATK + SEX", "Bastet": "DEF + SEX", "Chrono": "SPD + SEX"}
            },
            4: {
                "name": "Rabbit",
                "style": "Generous",
                "bios": {"MNF": 1, "SPL": 6, "BEU": 2, "STR": 3, "FND": 4, "KNO": 5, "UND": 1, "WIS": 2, "VIT": 0, "SEX": 5, "DIV": 4, "EGO": 3},
                "elements": ["Light", "Earth"],
                "species": {"Mannequin": "ATK + SPL", "Iniris": "DEF + SPL", "Angel": "SPD + SPL"}
            },
            5: {
                "name": "Dragon",
                "style": "Noble",
                "bios": {"MNF": 0, "SPL": 5, "BEU": 3, "STR": 4, "FND": 5, "KNO": 6, "UND": 2, "WIS": 1, "VIT": 1, "SEX": 4, "DIV": 3, "EGO": 2},
                "elements": ["Fire", "Air"],
                "species": {"Drakian": "ATK + KNO", "Gargoyle": "DEF + KNO", "Demon": "SPD + KNO"}
            },
            6: {
                "name": "Snake",
                "style": "Cunning",
                "bios": {"MNF": 1, "SPL": 4, "BEU": 4, "STR": 5, "FND": 6, "KNO": 5, "UND": 3, "WIS": 0, "VIT": 2, "SEX": 3, "DIV": 2, "EGO": 1},
                "elements": ["Dark", "Water"],
                "species": {"Reptoid": "ATK + FND", "Ghoul": "DEF + FND", "Vampyre": "SPD + FND"}
            },
            7: {
                "name": "Horse",
                "style": "Honest",
                "bios": {"MNF": 2, "SPL": 3, "BEU": 5, "STR": 6, "FND": 5, "KNO": 4, "UND": 4, "WIS": 1, "VIT": 3, "SEX": 2, "DIV": 1, "EGO": 0},
                "elements": ["Light", "Fire"],
                "species": {"Dwarf": "ATK + STR", "Human": "DEF + STR", "Troll": "SPD + STR"}
            },
            8: {
                "name": "Goat",
                "style": "Sturdy",
                "bios": {"MNF": 3, "SPL": 2, "BEU": 6, "STR": 5, "FND": 4, "KNO": 3, "UND": 5, "WIS": 2, "VIT": 4, "SEX": 1, "DIV": 0, "EGO": 1},
                "elements": ["Earth", "Light"],
                "species": {"Faun": "ATK + BEU", "Elf": "DEF + BEU", "Grey": "SPD + BEU"}
            },
            9: {
                "name": "Monkey",
                "style": "Active",
                "bios": {"MNF": 4, "SPL": 1, "BEU": 5, "STR": 4, "FND": 3, "KNO": 2, "UND": 6, "WIS": 3, "VIT": 5, "SEX": 0, "DIV": 1, "EGO": 2},
                "elements": ["Air", "Earth"],
                "species": {"Goki": "ATK + UND", "Goblin": "DEF + UND", "Mimic": "SPD + UND"}
            },
            10: {
                "name": "Rooster",
                "style": "Defiant",
                "bios": {"MNF": 5, "SPL": 0, "BEU": 4, "STR": 3, "FND": 2, "KNO": 1, "UND": 5, "WIS": 4, "VIT": 6, "SEX": 1, "DIV": 2, "EGO": 3},
                "elements": ["Fire", "Air"],
                "species": {"Avious": "ATK + VIT", "Grimm": "DEF + VIT", "Banshee": "SPD + VIT"}
            },
            11: {
                "name": "Dog",
                "style": "Loyal",
                "bios": {"MNF": 6, "SPL": 1, "BEU": 3, "STR": 2, "FND": 1, "KNO": 0, "UND": 4, "WIS": 5, "VIT": 5, "SEX": 2, "DIV": 3, "EGO": 4},
                "elements": ["Dark", "Earth"],
                "species": {"Jackal": "ATK + MNF", "Wolfin": "DEF + MNF", "Phantom": "SPD + MNF"}
            },
            12: {
                "name": "Boar",
                "style": "Mellow",
                "bios": {"MNF": 5, "SPL": 2, "BEU": 2, "STR": 1, "FND": 0, "KNO": 1, "UND": 3, "WIS": 6, "VIT": 4, "SEX": 3, "DIV": 4, "EGO": 5},
                "elements": ["Water", "Dark"],
                "species": {"Grizzly": "ATK + WIS", "Chimera": "DEF + WIS", "Orc": "SPD + WIS"}
            }
        }

    def get_sign_data(self, sign_num: int) -> Dict:
        return self.signs.get(sign_num, {})

    def get_biorhythms_for_sign(self, sign_num: int) -> Dict:
        return self.get_sign_data(sign_num).get("bios", {})

    def get_species_for_sign(self, sign_num: int) -> List[str]:
        species_map = self.get_sign_data(sign_num).get("species", {})
        return list(species_map.keys())
