# Rememberence - AIR-AI Oracle Module Roadmap

**Created:** 2026-05-25  
**Status:** Active Development  
**Model:** Cloud (qwen3.5:cloud) for development phase

---

## 📦 Existing Modules (Working)

| Module | Status | Location | Notes |
|--------|--------|----------|-------|
| **State Management** | ✅ Working | `rememberence_bridge.py` | Save/load JSON, spirits array, posts timeline |
| **Entity Class** | ✅ Working | `rememberence_bridge.py` | Biorhythms, thoughts, loyalty, combat stats, memory_log |
| **BattleBoard** | ✅ Working | `rememberence_bridge.py` | 4-layer grid (A/B/C/D), pawn placement, movement, attacks |
| **Loyalty System** | ✅ Working | `rememberence_bridge.py` | Loyalty maps, ranks, decay, activity_heat |
| **SpiritTimeline** | ✅ Working | `rememberence_bridge.py` | Post-based narrative feed |
| **RMC (Recursive Meta-Cognition)** | ✅ Working | `rememberence_bridge.py` | Self-verification, confidence scoring, ethical filters |
| **Flask API Server** | ✅ Working | `app.py` | `/save`, `/load`, `/clear`, `/simulate` endpoints |
| **Dice Tables** | ✅ Documented | `0-Core/6-Dice Table.txt` | All roll tables for Species, Types, Skills, Signs |

---

## 🎯 Core Mechanics Reference

### Character Creation (6 Gates)
1. **Animal Sign** (D12) → Rat, Ox, Tiger, Rabbit, Dragon, Snake, Horse, Goat, Monkey, Rooster, Dog, Boar
2. **Star Sign** (D12) → Aries through Pisces
3. **Species** (D36) → Avious, Merr, Human, Elf, Drakian, Vampyre, etc.
4. **Type** (D24) → Thunder, Warrior, Spell, Pyro, Psychic, Holy, etc.
5. **Class** (6) → Melee, Ranged, Magic, Step, Special, Trance
6. **Skill/Style** (D6 per class) → e.g., Melee: 1H, 2H, Whip, Staff, Fists, Chi

### Biorhythms (12 Stats)
MNF, SPL, BEU, STR, FND, KNO, UND, WIS, VIT, SEX, DIV, EGO
- Generated from Animal + Star sign combinations
- Drive all interactions (ATK vs DEF model)
- Feed into 6 Thought Parameters: Environment, Emotion, Subconscious, Conscious, Abstraction, Perception

### Tier Progression
Novice (1-10) → Beginner (10-100) → Mediate (100-1k) → Advanced (1k-10k) → Master (10k-100k) → Deity (100k-1m)

---

## 🔨 Modules To Build (Prioritized)

### 🔴 P1 - Foundation

| Priority | Module | Status | Description | Dependencies |
|----------|--------|--------|-------------|--------------|
| **P1** | **Dice Roller API** | 🟡 In Progress | `roll(dice)` → `3d6+2`, supports all tables | None |
| **P1** | **Biorhythm Calculator** | ⬜ Not Started | Animal + Star → 12 stats + 6 thoughts | Dice roller, lookup tables |
| **P1** | **Character Creation Wizard** | ⬜ Not Started | 6-gate flow with dice rolls, validates combinations | Dice roller, Species/Types data |

### 🟡 P2 - Core Gameplay

| Priority | Module | Status | Description | Dependencies |
|----------|--------|--------|-------------|--------------|
| **P2** | **Interaction Engine** | ⬜ Not Started | Biorhythm ATK vs DEF, loyalty changes, thought shifts | Biorhythm calc, Entity class |
| **P2** | **Oracle LLM Endpoint** | ⬜ Not Started | `/oracle/llm` → mechanical rolls + narrative prose | Cloud model, prompt templates |
| **P2** | **Inventory System** | ⬜ Not Started | Gear slots (Head/Body/Hands/Legs/Feet/Other), weapons, potions | Treasure tables, Material/Materia |
| **P2** | **Combat System** | ⬜ Not Started | Turn-based, BattleBoard integration, skill styles | BattleBoard, Entity combat stats |

### 🟢 P3 - Advanced Features

| Priority | Module | Status | Description | Dependencies |
|----------|--------|--------|-------------|--------------|
| **P3** | **Crafting System** | ⬜ Not Started | Material (Species) + Materia (Type) → weapons/gear/spells | Species/Types data, recipes |
| **P3** | **Dreamscape Tutorial** | ⬜ Not Started | Guided dreams per tier, skill training | State tracking, tutorial scripts |
| **P3** | **Social/Faction System** | ⬜ Not Started | Loyalty maps, faction standings, diplomacy | Interaction engine, timeline |
| **P3** | **Exploration Engine** | ⬜ Not Started | Search rolls, dungeon generation, treasure drops | Dice tables, text generation |

---

## 📁 Reference Files

### Primary Sources
- `D:\Ollama\OpenClaw\workspace\Rememberence\0-Core\4-Guide.txt` - Core mechanics reference
- `D:\Ollama\OpenClaw\workspace\Rememberence\0-Core\6-Dice Table.txt` - All dice tables
- `D:\Ollama\OpenClaw\workspace\Rememberence\0-Core\5-Biorhythms.txt` - Biorhythm interaction framework
- `D:\Ollama\OpenClaw\workspace\Rememberence\2-Spirit\Species\` - Updated Species definitions
- `D:\Ollama\OpenClaw\workspace\Rememberence\2-Spirit\Types\` - Updated Type definitions

### Legacy Sources (for comparison)
- `D:\cards\Rememberence\` - Original game files
- `D:\GPT4All\AIPlus\Rememberence\` - GPT4All mirrors
- `D:\cards\Rememberence-Flask\` - Flask API server

---

## 🧪 Test Commands

```bash
cd D:\Ollama\OpenClaw\workspace\projects\AIR-AI

# Start Flask server
python app/app.py

# Test endpoints
curl "http://localhost:5000/generate/name?type=dwarf&count=3"
curl "http://localhost:5000/roll?dice=3d6+2"
curl "http://localhost:5000/character/create?animal=dragon&star=scorpio"
curl "http://localhost:5000/oracle/fragment?roll=75"
```

---

## 📝 Session Notes

- **2026-05-25:** Switched to cloud model (qwen3.5:cloud) for development speed. Module roadmap created. Character Creation Wizard selected as P1 focus.

---

**Next Session:** Review generator.js, integrate with Flask API, build Character Creation endpoint
