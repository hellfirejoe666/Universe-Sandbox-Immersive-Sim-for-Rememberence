# Living Town Simulation

**A 6-layer procedural simulation for Rememberence**

Autonomous NPCs living in procedurally generated towns, worlds, and faction systems. Each layer is modular, fast, and designed for emergent complexity.

---

## 🏗️ Architecture

```
Layer 6: Worlds        ──→ Multiple towns, trade routes, star maps
Layer 5: Factions      ──→ Procedural collectives with ideology
Layer 4: Structures    ──→ Towns, buildings, rooms
Layer 3: Entities      ──→ NPCs with biorhythms, schedules
Layer 2: Items         ──→ Weapons, armor, materials, materia
Layer 1: Core Rules    ──→ Biorhythms, thoughts, dice rolls
```

**Design Principles:**
- **Modular:** Each layer works independently
- **Procedural:** Donjon-style generation at every layer
- **Fast:** DEV_MODE for <5s test runs
- **Emergent:** Complexity from layer interactions

---

## 🚀 Quick Start

### Run Full Stack Test

```bash
cd D:\Ollama\OpenClaw\workspace\living-town
python test_full_stack.py
```

**Expected output:** All 6 layers connected in <5 seconds

### Run Individual Layer Tests

```bash
# Layer 1: Core Rules
python layers\layer1_core_rules.py

# Layer 2: Items
python layers\layer2_items.py

# Layer 3: Entities
python layers\layer3_entities.py

# Layer 4: Structures
python layers\layer4_structures.py

# Layer 5: Factions
python layers\layer5_factions.py

# Layer 6: Worlds
python layers\layer6_worlds.py
```

---

## 📚 Layer Documentation

### Layer 1: Core Rules

**File:** `layers/layer1_core_rules.py`

**What it does:**
- Calculates 12 biorhythms from Animal + Star signs
- Derives 6 thought parameters from biorhythm pairs
- Provides dice roll mechanics

**Usage:**
```python
from layers.layer1_core_rules import calculate_biorhythms, generate_thoughts

# Calculate biorhythms for a sign combination
bio = calculate_biorhythms("Tiger", "Aries")
print(f"MNF: {bio.MNF}, SPL: {bio.SPL}, BEU: {bio.BEU}")

# Generate thoughts from biorhythms
thoughts = generate_thoughts(bio)
print(f"Environment: {thoughts.Environment}")
print(f"State: {thoughts.State}")
```

**Key Functions:**
- `calculate_biorhythms(animal_sign, star_sign)` → Biorhythms object
- `generate_thoughts(biorhythms)` → Thoughts object
- `roll_dice(sides=20)` → int (1-20)

---

### Layer 2: Items

**File:** `layers/layer2_items.py`

**What it does:**
- Procedural weapon/armor generation
- 36 materials, 24 materia types
- 5 rarity tiers (Common → Transcendent)

**Usage:**
```python
from layers.layer2_items import ItemGenerator

gen = ItemGenerator()

# Generate weapons
weapon = gen.generate_weapon()
print(f"{weapon.name} - {weapon.rarity.value}")

# Generate armor
armor = gen.generate_armor()
print(f"{armor.name} - {armor.item_type.value}")

# Generate with specific rarity
from layers.layer2_items import ItemRarity
rare_weapon = gen.generate_weapon(rarity=ItemRarity.RARE)
```

**Key Classes:**
- `ItemGenerator` - Main generator
- `Item` - Item dataclass (name, stats, rarity, type)
- `ItemRarity` - Enum (Common, Uncommon, Rare, Exotic, Transcendent)
- `ItemType` - Enum (Weapon, Armor)

---

### Layer 3: Entities

**File:** `layers/layer3_entities.py`

**What it does:**
- NPC generation with 12 animal signs + 12 star signs
- Biorhythm-based personalities
- Daily schedules, relationships, thoughts

**Usage:**
```python
from layers.layer3_entities import NPCGenerator, TownManager

# Generate NPCs
gen = NPCGenerator()
npc = gen.generate_npc()
print(f"{npc.name} - {npc.animal_sign}/{npc.star_sign}")
print(f"Biorhythms: {npc.biorhythms.to_dict()}")
print(f"Thoughts: {npc.thoughts.to_dict()}")

# Manage multiple NPCs
manager = TownManager()
manager.add_npc(npc)
```

**Key Classes:**
- `NPCGenerator` - NPC generation
- `NPC` - NPC dataclass (biorhythms, thoughts, schedule, relationships)
- `TownManager` - NPC collection management

**12 Animal Signs:** Rat, Ox, Tiger, Rabbit, Dragon, Snake, Horse, Goat, Monkey, Rooster, Dog, Pig

**12 Star Signs:** Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces

---

### Layer 4: Structures

**File:** `layers/layer4_structures.py`

**What it does:**
- Procedural town generation
- Building generation with rooms
- Material-based construction
- Opening/closing schedules

**Usage:**
```python
from layers.layer4_structures import TownGenerator, BuildingGenerator

# Generate a town
town_gen = TownGenerator()
town = town_gen.generate_town(building_count=6)
print(f"{town.name} - Population: {town.population}")
print(f"Buildings: {len(town.buildings)}")

# Generate a building
building_gen = BuildingGenerator()
from layers.layer4_structures import BuildingType
shop = building_gen.generate_building(building_type=BuildingType.SHOP)
print(f"{shop.name} - {shop.building_type.value}")
```

**Key Classes:**
- `TownGenerator` - Town generation
- `BuildingGenerator` - Building generation
- `Town` - Town dataclass (buildings, population, region)
- `Building` - Building dataclass (rooms, material, schedule)
- `BuildingType` - Enum (House, Shop, Tavern, Temple, Barracks, Library, Workshop)

---

### Layer 5: Factions

**File:** `layers/layer5_factions.py`

**What it does:**
- Procedural faction generation as collective groups
- Ideology, purpose, symbols, colors
- Group structure (Hierarchy, Collective, Cell, Guild)
- Shared resources, artifacts, traditions

**Usage:**
```python
from layers.layer5_factions import FactionManager, FactionGenerator

# Generate factions
manager = FactionManager(count=3)
factions = manager.get_all_factions()

for faction in factions:
    print(f"{faction.name} ({faction.structure.value})")
    print(f"  Ideology: {faction.ideology}")
    print(f"  Purpose: {faction.purpose}")
    print(f"  Members: ~{faction.member_count}")
```

**Key Classes:**
- `FactionManager` - Faction management
- `FactionGenerator` - Procedural generation
- `Faction` - Faction dataclass (identity, ideology, resources)
- `FactionType` - Enum (Archive, Forgetting Order, Thread Walkers, etc.)
- `CollectiveStructure` - Enum (Hierarchy, Collective, Cell, Guild)

---

### Layer 6: Worlds

**File:** `layers/layer6_worlds.py`

**What it does:**
- Procedural world generation
- Multiple towns with coordinates
- Trade routes between towns
- Star maps for navigation

**Usage:**
```python
from layers.layer6_worlds import WorldManager, WorldGenerator

# Generate a world
manager = WorldManager(world_count=1, towns_per_world=3)
world = manager.get_all_worlds()[0]

print(f"{world.name} ({world.world_type.value})")
print(f"Towns: {len(world.towns)}")
print(f"Trade Routes: {len(world.trade_routes)}")
print(f"Star Maps: {len(world.star_maps)}")

# List towns
for town in world.towns.values():
    print(f"  {town.name} at ({town.x}, {town.y}) - {town.population} pop")
```

**Key Classes:**
- `WorldManager` - World management
- `WorldGenerator` - Procedural generation
- `World` - World dataclass (towns, routes, star maps)
- `Town` - Town dataclass (coordinates, population, terrain)
- `TradeRoute` - Trade route dataclass (goods, volume, safety)
- `StarMap` - Star map dataclass (constellation, navigation bonus)

---

## 🔧 Configuration

### DEV_MODE (Fast Iteration)

Edit `simulation.py`:
```python
class LivingTownSimulation:
    DEV_MODE = True           # Skip state persistence
    DEV_NPC_COUNT = 5         # Minimal NPCs for testing
    DEV_BUILDING_COUNT = 3    # Minimal buildings
```

**Benefits:**
- No state file accumulation
- Faster test runs (<5s)
- Clean slate each run

---

## 🧪 Testing

### Test Files

| File | Purpose | Speed |
|------|---------|-------|
| `test_full_stack.py` | All 6 layers connected | ~3s |
| `test_integration.py` | NPCs ↔ Factions | ~1s |
| `odysseus_integration.py` | Neural Router + NPCs | ~2s |
| `layers/layer*.py` | Individual layer tests | <1s each |

### Run All Tests

```bash
cd D:\Ollama\OpenClaw\workspace\living-town
python test_full_stack.py
python test_integration.py
python odysseus_integration.py
```

---

## 🎯 Integration Points

### NPCs → Factions
```python
# Assign NPC to faction based on personality
for npc in npcs:
    faction = factions[0]  # Your matching logic here
    print(f"{npc.name} joins {faction.name}")
```

### Town → World
```python
# Place town in world
town = town_gen.generate_town()
world.towns[town.id] = town
```

### Items → NPCs
```python
# Equip NPC with item
npc.inventory.append(item_gen.generate_weapon())
```

---

## 📁 Project Structure

```
living-town/
├── layers/
│   ├── layer1_core_rules.py      # Biorhythms, thoughts, dice
│   ├── layer2_items.py           # Weapons, armor, materials
│   ├── layer3_entities.py        # NPCs, schedules, relationships
│   ├── layer4_structures.py      # Towns, buildings
│   ├── layer5_factions.py        # Factions, collectives
│   └── layer6_worlds.py          # Worlds, trade routes, stars
├── simulation.py                  # Main simulation runner
├── test_full_stack.py            # Full integration test
├── test_integration.py           # NPC-Faction test
├── odysseus_integration.py       # Neural Router test
└── README.md                     # This file
```

---

## 🚀 Next Steps

### Current Status
- ✅ All 6 layers complete and tested
- ✅ Full stack integration working
- ✅ Odysseus/Neural Router integration ready
- ✅ DEV_MODE for fast iteration

### Future Enhancements
1. **Player Control** - Sims-style NPC selection/commands
2. **Odysseus Agents** - Each NPC as autonomous AI agent
3. **Emergent Events** - Faction wars, trade disputes, natural disasters
4. **UI/Visual Layer** - Web or desktop interface
5. **Persistence** - Save/load world state (production mode)

---

## 🧠 Neural Router Integration

See `../hybrid-router/README.md` for Neural Router documentation.

**Quick Integration:**
```python
from hybrid_router.brain.neural_router import NeuralRouter

router = NeuralRouter()
decision = router.process("Should I join this faction?", npc_context)
```

---

## 📝 Design Philosophy

**"Make it work, then make it pretty"**

1. **Foundation First** - Simple, modular layers
2. **Procedural Everything** - Donjon-style generation
3. **Fast Iteration** - DEV_MODE, minimal tests
4. **Emergent Complexity** - Layers interact to create depth
5. **Expand Later** - Add complexity without breaking foundation

---

## 🎮 Rememberence Context

This simulation powers the **Living Town** aspect of Rememberence:

- **TTRPG Setting** - Dynamic world for tabletop play
- **Emergent Stories** - NPCs create stories through interactions
- **Procedural Content** - Infinite unique worlds
- **AI Game Master** - Neural Router + Odysseus orchestrate events

See `../rememberence_core/` for core game mechanics.

---

**Last Updated:** 2026-06-08  
**Status:** Foundation Complete, Ready for Enhancement
