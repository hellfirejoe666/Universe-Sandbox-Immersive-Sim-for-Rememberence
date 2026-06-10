# AIR-AI Project - Rememberence Oracle System

**Advanced Integrated Rememberence Artificial Intelligence**

This project bridges the existing Rememberence codebase with a mystical oracle layer powered by local LLM (Ollama).

## Project Structure

```
AIR-AI/
├── README.md                 # This file
├── ROADMAP.md                # Development milestones (5 Tiers)
├── test_ollama.py            # Ollama connection test
├── test_flask_routes.py      # Flask generator route tests
└── [future]
    ├── app/                  # Flask application (from Project Rememberence)
    ├── data/                 # Lore JSON files (from Project Rememberence)
    ├── generators/           # Donjon + Perchance generators
    ├── oracle/               # AIR-AI oracle layer (from air-ai/)
    └── saves/                # Session persistence
```

## Integration Plan

The AIR-AI layer (`workspace/air-ai/`) provides the **oracle personality and lore**, while this project (`projects/AIR-AI/`) provides the **technical implementation**.

### From `workspace/air-ai/` (Oracle Layer)
- `lore-bible.md` → Canonical Rememberence setting lore
- `oracle-system-prompt-v2.md` → AIR-AI Oracle personality
- `oracle-tables.md` → d20/d100 oracle tables
- `oracle_calculations.py` → Biorhythm + combat stat calculations

### From `D:\Cards\Project Rememberence` (Codebase)
- `app.py` → Flask server
- `rememberence_bridge.py` → Oracle symbolic bridge
- `data/*.json` → Animal signs, star signs, species, types, classes
- `generators/donjon/*` → Dungeon, tavern, name generators
- `static/js/*` → Frontend logic

## Current Status (Tier 2 Complete ✅)

**Tier 1: Gather & Organize** ✅
- Project structure ready
- Flask server files identified
- Lore files located

**Tier 2: Environment Setup** ✅
- Packages installed: `flask`, `ollama`, `numpy`, `scipy`, `chromadb`, `tracery`, `markovify`, `icepool`
- Ollama running with `deepseek-r1:8b`
- Flask app loads successfully

**Tier 3: Component Integration** ⬜ Next
- Port donjon generators to Python
- Implement dice rolling with Icepool
- Add biorhythm bias to rolls
- Emulate Perchance chats with Tracery + Ollama

**Tier 4: Core Features** ⬜
- `/oracle_reading` route
- `/chat_npc` route (ChromaDB + Ollama)
- `/generate_world` route
- ChromaDB remembrance (vector search)

**Tier 5: Test & Expand** ⬜
- Offline session testing
- Model quantization
- Documentation

## Quick Start

### Test Ollama Connection
```bash
cd D:\Ollama\OpenClaw\workspace\projects\AIR-AI
python test_ollama.py
```

### Test Flask Routes
```bash
cd D:\Ollama\OpenClaw\workspace\projects\AIR-AI
python test_flask_routes.py
```

### Start Flask Server
```bash
cd D:\Cards\Project Rememberence
python app/app.py
```

## Oracle Integration Example

```python
from oracle_calculations import calculate_biorhythms, generate_thoughts
import ollama

# Load AIR-AI system prompt
with open('D:/Ollama/OpenClaw/workspace/air-ai/oracle-system-prompt-v2.md') as f:
    system_prompt = f.read()

# Calculate seeker's biorhythms
biorhythms = calculate_biorhythms('Dragon', 'Scorpio')
thoughts = generate_thoughts(biorhythms)

# Consult the Oracle
response = ollama.chat(model='deepseek-r1:8b', messages=[
    {'role': 'system', 'content': system_prompt},
    {'role': 'user', 'content': 'The threads tremble. What do you seek, traveler?'}
])

print(response['message']['content'])
```

## Next Steps

1. **Port donjon generators** to Python (or call via subprocess)
2. **Create `/oracle_reading` endpoint** in Flask
3. **Integrate ChromaDB** for memory persistence
4. **Build UI** with HTMX for live oracle consultations
5. **Test full session flow**: World gen → NPC chat → Oracle reading

---

*The Archive awaits. The threads are ready to be woven.*
