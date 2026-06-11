# LocalGen - Self-Hosted Unlimited AI Generation

**Status:** ✅ WORKING - Unlimited creative generation, no cloud limits!

## What It Is

LocalGen is a **self-hosted Perchance alternative** that runs on your machine:

- ✅ **Unlimited generation** - No rate limits, no token counts
- ✅ **No external APIs** - Everything runs locally
- ✅ **No Cloudflare blocks** - We control the service
- ✅ **Fast** - Localhost latency (~10-30s for AI, instant for lists)
- ✅ **Customizable** - Add any generators you want

## Architecture

```
User Query → Hybrid Router → LocalGen (localhost:5000) → Response
                                    │
                                    ├─ List Generators (instant, 0 tokens)
                                    │   ├─ fantasy-name
                                    │   ├─ character-name
                                    │   ├─ fantasy-plot
                                    │   └─ city-name
                                    │
                                    └─ AI Generators (local LLM, unlimited)
                                        ├─ ai-character-chat
                                        └─ ai-story-generator
```

## Quick Start

### Start LocalGen Server

```powershell
# Option 1: Use startup script
.\localgen\start-localgen.ps1

# Option 2: Run directly
python localgen\server.py
```

Server runs on: `http://localhost:5000`

### Test It

```powershell
# Test all generators
python hybrid-router\localgen_provider.py --test

# Test single generator
python hybrid-router\localgen_provider.py "Write a story about a wizard"
```

### Use with Hybrid Router

LocalGen is **automatically integrated** into the hybrid router:

```python
python hybrid-router\router_v2.py route "Write a fantasy story"
# Result: path="localgen", tokens_used=0 (local = free!)
```

## API Endpoints

### Health Check
```
GET http://localhost:5000/api/health
```

### Generate Text
```
GET http://localhost:5000/api/generate?generator={name}&input={text}

Examples:
  /api/generate?generator=fantasy-name
  /api/generate?generator=fantasy-plot
  /api/generate?generator=ai-character-chat&input=Tell me a riddle
  /api/generate?generator=ai-story-generator&input=Write about a dragon
```

### Get List Items
```
GET http://localhost:5000/api/list?name={listname}

Examples:
  /api/list?name=fantasy_names
  /api/list?name=character_classes
```

## Available Generators

### List Generators (Instant, 0 tokens)

| Generator | Description | Example Output |
|-----------|-------------|----------------|
| `fantasy-name` | Random fantasy name | "Shadowmere" |
| `character-name` | Character name + title | "Dragonspire the Bold" |
| `fantasy-plot` | Random plot hook | "A young wizard discovers..." |
| `city-name` | Fantasy city name | "Stormhold" |

### AI Generators (Local LLM, Unlimited)

| Generator | Description | Tokens |
|-----------|-------------|--------|
| `ai-character-chat` | Conversational AI with personas | Local (unlimited) |
| `ai-story-generator` | Story/creative writing | Local (unlimited) |

### Adding Custom Generators

Edit `localgen\server.py`:

```python
# Add new list
MY_NAMES = ["Alice", "Bob", "Charlie"]

def generate_my_name() -> str:
    return random.choice(MY_NAMES)

# Add to API route
elif generator == 'my-name':
    return jsonify({"output": generate_my_name()})
```

## Integration with Hybrid Router

### Routing Decision

Creative queries (0.5 < novelty < 0.85) → **LOCALGEN** path:

```python
# In router_v2.py
if is_creative and 0.5 < novelty < 0.85 and localgen.available:
    path = "localgen"  # ← Free, unlimited, localhost!
```

### Token Impact

**Before LocalGen:**
- Creative queries → SMART (qwen2.5:7b, ~150 tokens) or CLOUD (~500 tokens)
- Cloud limits hit frequently

**After LocalGen:**
- Creative queries → LOCALGEN (local LLM, **0 counted tokens**)
- Cloud limits rarely hit
- **Unlimited creative generation**

## Performance

| Generator Type | Latency | Token Cost |
|----------------|---------|------------|
| List (names, plots) | <100ms | 0 |
| AI Chat | 10-30s | Local (unlimited) |
| AI Story | 15-45s | Local (unlimited) |

## Configuration

### Change LLM Model

Edit `localgen\server.py`:

```python
# Change from qwen2.5:7b to another model
result = subprocess.run(
    ["ollama", "run", "phi3:mini", prompt],  # ← Change model here
    ...
)
```

### Change Port

Edit `localgen\server.py`:

```python
app.run(host='0.0.0.0', port=8080, debug=False)  # ← Change port
```

Update `localgen_provider.py`:

```python
LOCALGEN_URL = "http://localhost:8080/api"  # ← Match port
```

## Troubleshooting

### Server Won't Start

```powershell
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill existing process if needed
taskkill /F /PID <pid>

# Try starting again
python localgen\server.py
```

### AI Generators Timeout

- Local LLM may be slow on first run (model loading)
- Increase timeout in `server.py`:
  ```python
  timeout=60  # Increase from 30
  ```

### List Generators Work, AI Doesn't

- Check Ollama is running: `ollama list`
- Test Ollama directly: `ollama run qwen2.5:7b "Hello"`

## Files

```
localgen/
├── server.py                 # Flask server with generators
├── start-localgen.ps1        # PowerShell startup script
└── README.md                 # This file

hybrid-router/
├── localgen_provider.py      # Router integration
├── router_v2.py              # Updated with LocalGen path
└── LOCALGEN_DESIGN.md        # Design document
```

## Why This Works Better Than Perchance

| Feature | Perchance | LocalGen |
|---------|-----------|----------|
| Rate Limits | None (but blocked by Cloudflare) | None (local) |
| Token Limits | None | None (local LLM) |
| Cloud Access | ❌ Blocked | ✅ Always available |
| Speed | 5-15s (network) | <100ms-30s (localhost) |
| Customization | Limited | Full control |
| Privacy | External service | 100% local |

## Next Steps

1. ✅ **Basic server working** - List + AI generators
2. ⏳ **Add more generators** - Dialogues, descriptions, quests
3. ⏳ **Response caching** - Cache common AI responses
4. ⏳ **Persona system** - More character options
5. ⏳ **Auto-start with OpenClaw** - Run as background service

---

**Bottom line:** LocalGen gives us unlimited creative generation without burning cloud token limits. Perfect for roleplay, storytelling, and conversational queries!
