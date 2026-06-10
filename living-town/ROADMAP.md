# Living Town Integration Roadmap

**Foundation:** `workspace/living-town/` (7 layers complete, all tested)  
**Goal:** Aggregate existing workspace components incrementally  
**Philosophy:** One phase at a time, test after each step

---

## Current Status (2026-06-09 17:45)

### ✅ What We Have Working

| Component | Location | Status | Notes |
|-----------|----------|--------|-------|
| **Data Loader** | `living-town/data_loader.py` | ✅ Complete | Loads all JSON data files |
| **Layer 1** | `living-town/layers/layer1_core_rules.py` | ✅ Updated | Uses canonical JSON data |
| **Layer 2** | `living-town/layers/layer2_items.py` | ✅ Complete | Items, weapons, armor |
| **Layer 3** | `living-town/layers/layer3_entities.py` | ✅ Complete | NPCs |
| **Layer 4** | `living-town/layers/layer4_structures.py` | ✅ Complete | Towns, buildings |
| **Layer 5** | `living-town/layers/layer5_factions.py` | ✅ Complete | Factions + decisions |
| **Layer 6** | `living-town/layers/layer6_stellaris.py` | ✅ Complete | Systems, galaxies |
| **Interactive UI** | `living-town/interactive_simulation.py` | ✅ Complete | 6 layer viewers integrated |
| **Save System** | `living-town/save_system.py` | ✅ Complete | Narrative persistence |
| **Hybrid Router** | `hybrid-router/` | ✅ Complete | FFT, caching, routing |

### ✅ Phase 1 Progress

| Task | Status | Notes |
|------|--------|-------|
| **1.1** Interactive viewer | ✅ Done | All 6 layers integrated |
| **1.2** Data consolidation | ✅ Done | JSON files copied, data_loader.py created |
| **1.3** Layer 1 updated | ✅ Done | Uses canonical biorhythm data |
| **1.4** Config file | ⏳ Pending | Next step |
| **1.5** Layers 2-6 data integration | ⏳ Pending | After config |

### 📦 What Exists in Workspace (Needs Integration)

| Component | Location | Purpose | Priority |
|-----------|----------|---------|----------|
| **Game Data (JSON)** | `projects/Project Rememberence/data/` | 12 animals, 12 stars, 36 species, 24 types, 6 classes, 77 runes | 🔴 High |
| **Character Creator** | `projects/Project Rememberence/app/` | Flask API, character generation | 🔴 High |
| **Generators** | `projects/Project Rememberence/generators/` | Donjon, Perchance integration | 🟠 Medium |
| **AIR-AI Oracle** | `projects/AIR-AI/` | LLM bridge, lore bible | 🟠 Medium |
| **Rememberence Bridge** | `projects/Project Rememberence/app/rememberence_bridge.py` | Battle system, loyalty, entity calc | 🟠 Medium |
| **Odysseus IPC** | `odysseus/ipc/` | Message queue system | 🟡 Low |
| **TTS/STT** | `odysseus/services/` | Voice I/O | 🟡 Low |

---

## Phase 1: Stabilize Living Town Foundation

**Duration:** 1-2 days  
**Risk:** Low (no external dependencies)

### Tasks

- [ ] **1.1** Fix `watch_simulation.py` viewer (currently runs, needs polish)
- [ ] **1.2** Add config file for simulation settings (NPC count, speed, etc.)
- [ ] **1.3** Create simple web UI (Flask static pages, no framework)
- [ ] **1.4** Add event variety (more faction action types, NPC interactions)

### Deliverable
Working DF-style viewer you can run and watch for hours.

---

## Phase 2: Integrate Hybrid Router

**Duration:** 1 day  
**Risk:** Low (router is standalone, well-tested)

### What We're Adding
- FFT novelty detection for events
- Semantic caching for narratives
- Token-optimized AI calls

### Tasks

- [ ] **2.1** Import router into `layer0_airai.py`
- [ ] **2.2** Replace simple narrative generation with router calls
- [ ] **2.3** Add caching layer (first examination = generate, subsequent = retrieve)
- [ ] **2.4** Test cost savings (should be 70-85% reduction)

### Integration Point
```python
# living-town/layer0_airai.py
from hybrid-router.router_v2 import HybridRouter

router = HybridRouter()
narrative = router.route(prompt)  # Instead of direct LLM call
```

### Deliverable
Narrative generation uses Hybrid Router (cheaper, faster, smarter).

---

## Phase 3: Integrate AIR-AI Oracle Lore System

**Duration:** 1-2 days  
**Risk:** Low (read-only integration)

### What We're Adding
- Lore bible for consistent world-building
- Oracle consultation for major events
- Session memory for continuity

### Tasks

- [ ] **3.1** Read `projects/AIR-AI/app/lore-bible.md`
- [ ] **3.2** Load lore into living-town context
- [ ] **3.3** Add oracle consultation for faction decisions (weekly)
- [ ] **3.4** Save oracle responses to witnessed events

### Integration Point
```python
# living-town/layers/layer5_factions.py
from projects.AIR-AI.app.oracle_calculations import consult_oracle

oracle_advice = consult_oracle("What should this faction do?")
```

### Deliverable
Factions make lore-consistent decisions, oracle provides narrative guidance.

---

## Phase 4: Connect to Odysseus IPC

**Duration:** 2-3 days  
**Risk:** Medium (IPC system, requires Odysseus running)

### What We're Adding
- OpenClaw ↔ Living Town communication
- External API endpoints
- Multi-session support

### Tasks

- [ ] **4.1** Study `odysseus/ipc/ipc.py` message queue system
- [ ] **4.2** Create living-town IPC handler
- [ ] **4.3** Add endpoints: `/town/status`, `/npc/list`, `/faction/turn`
- [ ] **4.4** Test OpenClaw → Living Town commands

### Integration Point
```python
# living-town/ipc_handler.py
from odysseus.ipc.ipc import send_message, poll_queue

def handle_task(task):
    if task['type'] == 'run_faction_turn':
        return run_turn(task['faction_id'])
```

### Deliverable
Living Town can be controlled from OpenClaw/chat interfaces.

---

## Phase 5: Add Rememberence Core Mechanics

**Duration:** 2-3 days  
**Risk:** Medium (game logic integration)

### What We're Adding
- Character creation (12 animals × 12 stars × 36 species × 24 types)
- Combat simulation (from rememberence_bridge.py)
- Skill progression (6 classes × 6 skills each)
- Equipment system (from layer2_items.py + data files)

### Existing Components to Integrate

| File | Location | Status | Action |
|------|----------|--------|--------|
| `animal_signs.json` | `projects/.../data/` | ✅ Complete | Load for biorhythm calc |
| `star_signs.json` | `projects/.../data/` | ✅ Complete | Load for biorhythm calc |
| `species.json` | `projects/.../data/` | ✅ Complete | Add traits, lore |
| `types.json` | `projects/.../data/` | ✅ Complete | Add stat modifiers |
| `classes.json` | `projects/.../data/` | ✅ Complete | Replace layer1 classes |
| `runes.json` | `projects/.../data/` | ✅ Complete | Add enchantment system |
| `rememberence_bridge.py` | `projects/.../app/` | ✅ Complete | Use BattleBoard class |

### Tasks

- [ ] **5.1** Load JSON data files into living-town data layer
- [ ] **5.2** Merge Layer 1 biorhythms with animal/star JSON data
- [ ] **5.3** Integrate BattleBoard from rememberence_bridge.py
- [ ] **5.4** Add species/type traits to Layer 2 entities
- [ ] **5.5** Test all 144 zodiac combinations (12×12)

### Integration Point
```python
# living-town/layers/layer1_core_rules.py
import json

# Load canonical data
with open('projects/Project Rememberence/data/animal_signs.json') as f:
    ANIMAL_DATA = json.load(f)['animalSigns']

# Use data instead of hardcoded values
def calculate_biorhythms(animal, star):
    animal_bio = ANIMAL_DATA[animal]['biorhythms']
    # ... rest of calculation
```

### Deliverable
Full Rememberence character system with canonical data files.

---

## Phase 6: Web UI + Player Controls

**Duration:** 3-5 days  
**Risk:** Low (frontend only, backend stable)

### What We're Adding
- Browser-based interface
- Sims-style NPC selection
- Real-time simulation view
- Player commands

### Tasks

- [ ] **6.1** Create Flask web server (`app.py`)
- [ ] **6.2** Build HTML templates (minimal, no framework)
- [ ] **6.3** Add WebSocket for live updates
- [ ] **6.4** Implement player commands (pause, speed, select NPC)

### Tech Stack
- Flask (already in workspace)
- Vanilla JS (no React/Vue overhead)
- Server-sent events for live updates

### Deliverable
Playable web interface for living town simulation.

---

## Phase 7: TTRPG Integration

**Duration:** 2-3 days  
**Risk:** Low (adds DM tools, doesn't break existing)

### What We're Adding
- AIR-AI as DM assistant
- Session export for tabletop play
- Character sheets for players
- Adventure hooks from simulation

### Tasks

- [ ] **7.1** Export NPC stats as character sheets (PDF/text)
- [ ] **7.2** Generate adventure hooks from faction conflicts
- [ ] **7.3** Add DM view (behind-the-scenes info)
- [ ] **7.4** Session recording/playback

### Deliverable
Living Town can power actual TTRPG sessions.

---

## Future Phases (Post-MVP)

### Phase 8: Multiplayer Persistent Worlds
- Multiple players in same simulation
- Shared faction control
- Persistent world state

### Phase 9: Modding Support
- Custom layers
- User-created factions, items, events
- Workshop integration

### Phase 10: Mobile Port
- Touch-optimized UI
- Push notifications for events
- Offline mode

---

## Dependency Graph

```
Phase 1 (Foundation)
    ↓
Phase 2 (Hybrid Router) ────→ Phase 3 (AIR-AI Lore)
    ↓                               ↓
Phase 4 (Odysseus IPC) ────→ Phase 5 (Rememberence Core)
    ↓                               ↓
Phase 6 (Web UI) ────────────→ Phase 7 (TTRPG)
```

---

## Risk Assessment

| Phase | Risk | Mitigation |
|-------|------|------------|
| 1 | Low | Pure living-town, no external deps |
| 2 | Low | Router is standalone, well-tested |
| 3 | Low | Read-only lore integration |
| 4 | Medium | IPC system, needs Odysseus running |
| 5 | Medium | Game logic merge, test thoroughly |
| 6 | Low | Frontend only, backend stable |
| 7 | Low | Adds tools, doesn't break existing |

---

## Testing Strategy

After **each phase**:
1. Run `test_all_layers.py` (verify foundation intact)
2. Run 10-week simulation (verify stability)
3. Manual playtest (verify UX)

After **Phase 4+**:
4. IPC integration test
5. OpenClaw command test

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Simulation speed | <1s/week | ~0.3s/week ✅ |
| Narrative cost | <$0.01/playthrough | N/A (not integrated) |
| Event variety | 20+ types | ~10 types |
| Player engagement | 1+ hour sessions | N/A (no UI yet) |
| TTRPG readiness | Exportable characters | Partial ✅ |

---

## Next Immediate Actions

1. **Phase 1.1** - Polish `watch_simulation.py` viewer (current focus)
2. **Review data files** - Check `projects/Project Rememberence/data/*.json` for completeness
3. **Test Phase 1** - Run viewer for 10+ weeks, note any issues
4. **Phase 2 prep** - Verify Hybrid Router still works standalone

---

## Data Inventory Summary

**Project Rememberence has complete data files we can use:**
- ✅ 12 Animal signs (biorhythms, species affinities)
- ✅ 12 Star signs (biorhythms, type affinities)
- ✅ 36 Species (full stats, active/passive traits, lore)
- ✅ 24 Types (stat modifiers, traits, materia)
- ✅ 6 Classes × 6 skills each (36 total skills)
- ✅ 77 Runes (effects, VoKai cypher)
- ✅ Battle system (rememberence_bridge.py)

**These replace/augment living-town's procedural generation in Phase 5.**

---

**Last Updated:** 2026-06-09  
**Status:** Ready for Phase 1
