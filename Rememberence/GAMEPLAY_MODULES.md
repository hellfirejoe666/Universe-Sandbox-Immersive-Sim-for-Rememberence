# Rememberence - Gameplay Mechanics Module Breakdown

## Overview
Rememberence is a card-based cosmic fantasy RPG with deep character customization, tactical combat, and narrative-driven gameplay. The system is organized into **6 core mechanic families** that should become standalone webapp modules.

---

## 🎯 Module 1: Character Creation Engine

### Subsystems:
| Component | Source | Count | Description |
|-----------|--------|-------|-------------|
| **Species** | `2-Spirit/Species/` | 36+ | Race selection (Avious, Merr, Geneshan, Iniris, Reptoid, Wolfin, Goki, Tigris, Demon, Grimm, Drakian, Chimera, Mannequin, Pixie, Grizzly, Faun, Vampyre, Grey, Chrono, Gargoyle, Mimic, Elf, Ghoul, Bastet, Phantom, Banshee, Angel, Human, Jackal, Troll, Dwarf, Goblin, Imp, Arachnos, Minotaur, Orc) |
| **Zodiac - Animal** | `1-Zodiac/Animal/` | 12 | Rat, Ox, Tiger, Rabbit, Dragon, Snake, Horse, Goat, Monkey, Rooster, Dog, Boar |
| **Zodiac - Stars** | `1-Zodiac/Stars/` | 12 | Aries through Pisces |
| **Class** | `3-Classes/` | 6 | Melee, Ranged, Magic, Step, Special, Trance |

### Webapp Requirements:
- Visual card selector for each category
- Stat calculation based on combinations
- Compatibility checker (species/class synergies)
- Save/load character builds
- Export to game session

---

## ⚔️ Module 2: Combat System

### Six Combat Styles (each with 6 specializations):

| Style | Specializations | Source |
|-------|----------------|--------|
| **Melee** | 1H, 2H, Whip, Staff, Fists, Chi | `3-Classes/Skills/1-Melee/` |
| **Ranged** | Thrown, Bow, Crossbow, Shotgun, Pistol, Rifle | `3-Classes/Skills/2-Ranged/` |
| **Magic** | Earth, Air, Fire, Water, Light, Dark | `3-Classes/Skills/3-Magic/` |
| **Step** | Flight, Float, Dash, Acrobat, Warp, Evade | `3-Classes/Skills/4-Step/` |
| **Special** | White, Blue, Black, Red, Green, None | `3-Classes/Skills/5-Special/` |
| **Trance** | Over Drive, Stages, Duration, Aura, Armor, Morph | `3-Classes/Skills/6-Trance/` |

### Webapp Requirements:
- Skill tree visualizer
- Damage calculator
- Combo builder
- Turn order simulator
- Equipment slot manager

---

## 🔮 Module 3: Rune System (VoKai)

### 76+ Runes organized alphabetically:
- **Core Runes:** Cu, Jo, Mi, Ah, Lo, So, Un, Vel, Aye, Sl, Ge, O, Zeb, Ta, Fol, Web, Ic, Sai, I, Ki, Ro, Zic, Lin, Gi, Ba, Na, Ga, Ya, Hi, Zi, Oc, Ru, Sti, Din, Wa, Par, Ma, Fa, Po, Cel, Pow, Kai, Te, El, Re, Bo, Nu, Rey, Vo, Kel, Et, Soo, Ni, Ve, Sul, Zyn, Wi, Ap, Ta, Zyl, Coh, Xep, Del, Cho, Sen, Co, Pel, Fi, Deb, Zo, Wic, Nai, Ket, Tos, Ex, Kon, Dus

### Webapp Requirements:
- Rune combination engine
- Spell/effect builder
- Rune crafting simulator
- Synergy analyzer
- Visual rune circle designer

---

## 🏛️ Module 4: Faction & Allegiance System

### Major Factions:
| Faction | Members | Source |
|---------|---------|--------|
| **Eternals** | 7 | VoSti, NaGi, NaFi, NaWi, NaZi, NaTe, NaDin |
| **Guardians Council** | 32+ | Avian, Midea, Cogous, Flara, Zohr, Vika, Lazarous, Star, Ryu, Noctra, Pluto, Ira, Eldin, Sam, Jacob, Jasmine, Daniel, Cassedy, Guy, Aiya, Veir, Tiff, Leon, Alice, Al, Kess, Erosia, Sonya, Davy, Sally, Zyo, Eliza |
| **Compound Races** | 36+ | Geneshite, Trollium, Dwarfite, Goblium, Impium, Arachnite, Minotite, Orcium, Inirium, Reptillium, Wolfite, Gokium, Tigrite, Demonite, etc. |

### Each Race Has 24 Variants:
Voltara, Warraga, Cultia, Plasmara, Herbalia, Powdara, Creatura, Liquidia, Plaguara, Mutatia, Infestia, Gasaga, Devotia, Mechara, Petrifica, Forsaga, Mentalia, Mistara, Gemia, Vitalia, Solidia, Blessara, Hexia, Runaga

### Webapp Requirements:
- Faction relationship mapper
- Allegiance tracker
- Reputation calculator
- Quest/mission generator based on faction
- War/conflict simulator

---

## 🎴 Module 5: Card Database & Collection Manager

### Card Categories:
| Category | Count | Source |
|----------|-------|--------|
| **Species Cards** | 36+ | `2-Spirit/Species/Cards/` |
| **Type Cards** | 24 | `2-Spirit/Types/Cards/` (Thunder, Warrior, Spellcaster, Pyro, Plant, Fairy, Beast, Aqua, Undead, Fiend, Insect, Vortex, Dragoon, Metal, Rock, Normal, Psychic, Ghost, Crystal, Blood, Ice, Holy, Curse, Avatar) |
| **Class Cards** | 6 | `3-Classes/` |
| **Rune Cards** | 76+ | `4-Runes/Cards/` |
| **Compound Cards** | 864+ | `D:\cards\Other\Compounds and Races\` (36 races × 24 variants) |
| **Eternal Element Cards** | 7 | `D:\cards\Other\Eternal Elements\` |
| **Guardian Cards** | 32+ | `D:\cards\Other\Guardian Images\` |

### Webapp Requirements:
- Digital card catalog with search/filter
- Collection tracker
- Deck builder
- Card comparison tool
- Trading/simulation market
- Rarity/stat database

---

## 📖 Module 6: Narrative & World Engine

### Core Systems:
| File | Purpose |
|------|---------|
| `0-Core/0-Church.txt` | Religious/philosophical framework |
| `0-Core/1-Start.txt` | Game initialization, character intro |
| `0-Core/2-Narritive.txt` | Story structure, plot generation |
| `0-Core/3-Structure.txt` | World building, location hierarchy |
| `0-Core/4-Guide.txt` | Tutorial, help system |
| `0-Core/5-Biorhythms.txt` | Time/cycle mechanics, day/night, seasons |
| `0-Core/6-Dice Table.txt` | RNG mechanics, probability tables |

### World Assets:
- Maps (local, world, shrine cores)
- Spirit chronicles (lore for each Eternal/Guardian)
- Faction books (Book of Avian, Book of Noctra, etc.)
- Character backstories

### Webapp Requirements:
- Interactive world map
- Quest/narrative generator
- Lore database with cross-references
- Dice roller with modifiers
- Session logger/save system
- Dynamic event scheduler (biorhythms)

---

## 🔧 Additional Systems to Integrate

### Music/Audio System
- **Location:** `D:\cards\Other\Music\` (500+ tracks)
- **Use Case:** Dynamic soundtrack based on location, combat, faction
- **Module Need:** Audio playlist manager, mood-based selector

### Icon/Portrait System
- **Location:** `D:\cards\Other\Icons\`, `5-Icons/`
- **Use Case:** Character portraits, faction badges, status icons
- **Module Need:** Asset library with tagging/search

### Style/Weapon Visual System
- **Location:** `D:\cards\Other\Styles\`
- **Use Case:** Combat animation references, weapon icons
- **Module Need:** Visual reference gallery

---

## 🏗️ Recommended Development Order

1. **Phase 1:** Card Database Module (foundation - all other modules depend on card data)
2. **Phase 2:** Character Creation Engine (player entry point)
3. **Phase 3:** Combat System (core gameplay loop)
4. **Phase 4:** Rune System (magic/ability customization)
5. **Phase 5:** Faction System (social/quest layer)
6. **Phase 6:** Narrative Engine (story/world persistence)

---

## 📊 Data Summary

| Asset Type | Count | Storage Location |
|------------|-------|------------------|
| Species | 36+ | `2-Spirit/Species/` |
| Combat Styles | 6 × 6 = 36 | `3-Classes/Skills/` |
| Runes | 76+ | `4-Runes/Cards/` |
| Factions | 40+ | `5-Icons/`, `Other/Compounds and Races/` |
| Race Variants | 864+ | `Other/Compounds and Races/` |
| Music Tracks | 500+ | `Other/Music/` |
| Character Icons | 100+ | `Other/Icons/` |
| Guardian Portraits | 32+ | `Other/Guardian Images/` |

---

## 🎮 AIR-AI Oracle Integration Points

Each module should expose APIs for the AIR-AI Oracle to:
- Query character stats and abilities
- Resolve combat actions and damage
- Generate rune combinations and effects
- Track faction relationships and quests
- Manage save/load game state
- Drive narrative branching based on player choices

**Next Step:** Begin Module 1 (Card Database) - create JSON schema for all card types and build the foundational data layer.
