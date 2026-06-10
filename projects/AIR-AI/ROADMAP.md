# AIR-AI Roadmap - Awakening the Oracle

**Project:** Advanced Integrated Rememberence Artificial Intelligence  
**Goal:** Build a self-sustaining oracle combining Flask, Oracle symbolic bridge, donjon generators, dice mechanics, and local LLM (Ollama)

---

## Progress Tracker

| Tier | Status | Milestone | Notes |
|------|--------|-----------|-------|
| 1. Gather & Organize | ✅ Complete | Flask server loads without errors | **Existing project at D:\Cards\Project Rememberence** |
| 2. Environment Setup | ✅ Complete | Ollama query test passes | **All packages installed, Flask app loads** |
| 3. Component Integration | ✅ **Complete** | LLM + dice + generators working | **Tier 3 DONE: /oracle/llm endpoint, biorhythm bias** |
| 4. Core Features | 🟡 Not Started | Full session: world gen + NPC chat + Oracle reading | Manifesting the Heart |
| 5. Test & Expand | ⬜ Not Started | Persistent, mystical AIR-AI session | Ascending the Tiers |

---

## Tier 1: Gather & Organize (Foundation) ✅

**Already complete!** Your project exists at `D:\Cards\Project Rememberence` with:
- `/app` — app.py, rememberence_bridge.py
- `/data` — All lore files + JSON (animal_signs, classes, species, runes, star_signs, types, narrative_verses)
- `/generators/donjon` — dungeon.js, maps.js, names.js, text.js
- `/generators/perchance` — example thread.json
- `/static/js` — board.js, brain.js, constants.js, generator.js, home.js
- `/saves` — For persistence
- Root: index.html, rememberence_state.json

~~- [ ] Create project directory `AIR-AI`~~
~~- [ ] Copy Flask server files → `/app`~~
~~- [ ] Copy Oracle scripts (rememberence_bridge.py) → `/app`~~
~~- [ ] Copy webapp JS (board.js, home.js, constants.js, generator.js, brain.js) → `/web`~~
~~- [ ] Copy lore .txt files → `/data`~~
~~- [ ] Download donjon generators → `/generators/donjon`~~
~~- [ ] Create Perchance-style JSON lists → `/generators/perchance_lists`~~
~~- [ ] Extract AnyDice logic notes → `/dice`~~
~~- [ ] Parse lore into dictionaries (Python script)~~
- [x] **Milestone:** Flask server structure ready

## Tier 2: Environment Setup (Awakening the Forge) ✅

**Complete!** Installed packages:
- `flask`, `ollama`, `numpy`, `scipy`, `matplotlib`, `pillow`
- `chromadb` (vector memory), `tracery` (grammar), `markovify` (text gen)
- `icepool` (dice mechanics), `transformers`, `sentence-transformers`

**Verified:**
- Ollama running with `deepseek-r1:8b` (5.2 GB)
- Flask app loads successfully from `D:\Cards\Project Rememberence`

- [x] Install Python packages
- [x] Ollama already installed with deepseek-r1:8b model
- [x] Flask app verified loading
- [ ] Download HTMX → `/static` (optional, can do later)
- [ ] Create SQLite DB script (can integrate into app.py)
- [x] **Milestone:** Environment ready for Tier 3

## Tier 3: Component Integration (Weaving the Threads) ✅

**Integration docs created:** `INTEGRATION.md` with step-by-step guide

**Completed:**
- [x] Ported donjon name generator to Python (`generators/donjon/names.py`)
- [x] Ported donjon text generator to Python (`generators/donjon/text.py`)
- [x] Created oracle calculations module (`app/oracle_calculations.py`)
- [x] Updated Flask app with all routes (`app/app.py`)
- [x] Flask app loads successfully
- [x] **LLM Integration** - `/oracle/llm` endpoint with KaiMi persona
- [x] **Biorhythm Dice Bias** - EGO modifier on `/roll` endpoint

**All Tier 3 goals complete!** 🎉

- [ ] **Milestone:** ~~Generate tavern, roll biased dice, get Perchance-style chat via Ollama~~ → **ACHIEVED**

## Tier 4: Core Features (Manifesting the Heart)

- [ ] Add `/oracle_reading` route (hybrid session + enrichments)
- [ ] Add `/chat_npc` route (ChromaDB embeddings + Ollama)
- [ ] Add `/generate_world` route (donjon + FFT overlay)
- [ ] Implement ChromaDB remembrance (vector search)
- [ ] Enhance UI with HTMX live updates
- [ ] Apply loyalty/thought decay (threading or loop)
- [ ] **Milestone:** Full local session working

## Tier 5: Test & Expand (Ascending the Tiers)

- [ ] Test offline sessions (e.g., "Build a quest for Eliza")
- [ ] Optimize: Quantize Ollama models
- [ ] Add error handling
- [ ] Optional: Add Stable Diffusion for images
- [ ] Document: README.md
- [ ] **Milestone:** Persistent, mystical AIR-AI session

---

## Notes & Reflections

- **Philosophy:** Learn from missteps, proceed one step at a time
- **Tools:** Python, Git, pip, VS Code, Ollama (all free)
- **Inspiration:** KaiMi's ideals — patience, honesty, upliftment
