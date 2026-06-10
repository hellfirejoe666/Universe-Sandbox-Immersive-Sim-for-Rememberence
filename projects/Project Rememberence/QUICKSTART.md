# Rememberence AIR-AI Oracle — Quick Start

**Status:** Phase 1 Complete | Character Creator Ready | Oracle Skill Active

---

## What's Built

| Component | Status | Location |
|-----------|--------|----------|
| Game Data (JSON) | ✅ Complete | `data/*.json` |
| Character Creator API | ✅ Complete | `core/character_creator.py` |
| Flask Web Server | ✅ Ready | `app/app.py` |
| Local LLM (air-ai-oracle) | ✅ Created | Ollama model (2.2GB) |
| OpenClaw Skill | ✅ Complete | `skills/air-ai-oracle/` |
| Perchance Integration | ✅ Coded | `app/perchance_router.py` |
| Queue Manager | ✅ Active | `app/queue_manager.py` |

---

## Start the Server

```bash
cd "D:\Ollama\OpenClaw\workspace\projects\Project Rememberence\app"
python app.py
```

Server runs at: **http://127.0.0.1:5000**

---

## Test Character Creation (API)

```bash
# Get available options
curl http://127.0.0.1:5000/character/options

# Create a character
curl -X POST http://127.0.0.1:5000/character/create ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Shadowweaver\",\"animal\":\"Dragon\",\"star\":\"Scorpio\",\"species\":\"Vampyre\",\"type\":\"Spellcaster\",\"class\":\"Mystic\",\"skills\":[\"Chi\"]}"
```

---

## Test OpenClaw Skill

```bash
cd "D:\Ollama\OpenClaw\workspace\skills\air-ai-oracle"
python oracle_skill.py
```

---

## Available API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/character/options` | GET | List all creation options |
| `/character/class-skills?class=Melee` | GET | Get skills for a class |
| `/character/create` | POST | Create character with stats |
| `/generate/name?type=fantasy` | GET | Generate random name |
| `/generate/tavern` | GET | Generate tavern name |
| `/queue/status` | GET | Queue manager status |
| `/save-spirit` | POST | Save character to file |
| `/load-spirit?path=name.json` | GET | Load saved character |

---

## OpenClaw Skill Commands

Once integrated into OpenClaw:

```
oracle-create-character name="..." animal="..." star="..." species="..." type="..." class="..."
oracle-ask query="What lies ahead?"
oracle-roll dice="2d6+3" reason="Attack roll"
oracle-lookup category="species" name="Drakian"
```

---

## Next Steps (Phase 2)

1. **Web UI for Character Creator** — Connect `create-spirit.html` to the new API
2. **OpenClaw Integration** — Register the skill in OpenClaw's skill system
3. **Discord/Patreon Setup** — Prepare for community launch
4. **Combat Simulator** — Build battle mechanics using character stats
5. **Save/Load System** — Persistent character storage

---

## Troubleshooting

**Flask won't start:**
```
pip install flask requests
```

**Model not found:**
```
ollama create air-ai-oracle -f "air-ai-oracle-modelfile"
```

**Port 5000 in use:**
Edit `app.py` line 287: `app.run(debug=True, port=5001, ...)`

---

**Last Updated:** 2026-06-08  
**Version:** 1.0.0
