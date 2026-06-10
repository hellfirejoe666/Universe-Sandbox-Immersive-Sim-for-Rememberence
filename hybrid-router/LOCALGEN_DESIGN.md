# LocalGen - Self-Hosted Perchance Alternative

**Goal:** Build a local unlimited AI generation service to replace Perchance

**Why:** 
- Perchance blocked by Cloudflare
- Burning through cloud token limits (3/5 accounts used)
- Need unlimited creative/conversational generation
- Local hardware = no rate limits

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LocalGen Service                          │
│                  (Flask/FastAPI Server)                      │
│                                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  List Generator │  │  AI Generator   │  │  Templates   │ │
│  │  (Perchance-    │  │  (Local LLM     │  │  (Story,     │ │
│  │   style random  │  │   via Ollama)   │  │   Character, │ │
│  │   text gen)     │  │                 │  │   Names,etc) │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│                                                               │
│  Endpoints:                                                   │
│  - /api/generate?generator={name}&input={text}               │
│  - /api/list?name={listname}                                  │
│  - /api/chat?generator={name}&message={text}                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │    Hybrid Router Integration   │
              │    (perchance_provider.py)     │
              │    → http://localhost:5000     │
              └───────────────────────────────┘
```

## Components

### 1. List Generator (Perchance-Style)

Pure Python random text generation from lists:

```python
# generators/lists.py
import random

FANTASY_NAMES = [
    "Shadowmere", "Dragonspire", "Winterhold", "Ravenwood",
    "Stormwind", "Ironforge", "Silvermoon", "Thunder Bluff",
]

def generate_name():
    return random.choice(FANTASY_NAMES)

def generate_plot():
    setup = random.choice([
        "A young {hero} discovers {magic}",
        "The kingdom of {kingdom} faces {threat}",
        "An ancient {artifact} is found in {location}",
    ])
    # Fill in blanks from other lists
    return setup.format(
        hero=random.choice(["wizard", "knight", "thief", "princess"]),
        magic=random.choice(["a powerful artifact", "forbidden magic", "their destiny"]),
        kingdom=random.choice(FANTASY_NAMES),
        threat=random.choice(["invasion", "curse", "betrayal"]),
        artifact=random.choice(["sword", "amulet", "tome", "crown"]),
        location=random.choice(["ruins", "cave", "tower", "forest"]),
    )
```

### 2. AI Generator (Local LLM)

Use Ollama for creative/conversational tasks:

```python
# generators/ai_chat.py
import subprocess
import json

def chat_with_character(message, character="default"):
    """AI character chat using local LLM."""
    
    # Load character definition
    characters = {
        "default": "You are a helpful fantasy storyteller.",
        "wizard": "You are a wise old wizard who speaks in riddles.",
        "warrior": "You are a brave warrior who values honor above all.",
    }
    
    system_prompt = characters.get(character, characters["default"])
    
    # Call Ollama
    prompt = f"{system_prompt}\n\nUser: {message}\nAssistant:"
    
    result = subprocess.run(
        ["ollama", "run", "qwen2.5:7b", prompt],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    return result.stdout.strip()
```

### 3. Template Generator

Pre-built templates for common creative tasks:

```python
# generators/templates.py
import random

STORY_TEMPLATES = [
    {
        "name": "Hero's Journey",
        "structure": [
            "Ordinary World",
            "Call to Adventure", 
            "Meeting the Mentor",
            "Crossing the Threshold",
            "Tests and Allies",
            "The Ordeal",
            "The Reward",
            "The Return",
        ]
    },
]

def generate_story(template="Hero's Journey"):
    t = next((x for x in STORY_TEMPLATES if x["name"] == template), STORY_TEMPLATES[0])
    
    story = []
    for beat in t["structure"]:
        # Use AI to generate content for each beat
        content = generate_beat(beat)
        story.append(f"**{beat}**: {content}")
    
    return "\n\n".join(story)
```

## API Endpoints

```python
# server.py
from flask import Flask, request, jsonify
from generators import lists, ai_chat, templates

app = Flask(__name__)

@app.route('/api/generate', methods=['GET'])
def generate():
    generator = request.args.get('generator', 'default')
    input_text = request.args.get('input', '')
    
    if generator == 'fantasy-name':
        return jsonify({"output": lists.generate_name()})
    
    elif generator == 'fantasy-plot':
        return jsonify({"output": lists.generate_plot()})
    
    elif generator == 'ai-character-chat':
        response = ai_chat.chat_with_character(input_text)
        return jsonify({"output": response})
    
    elif generator == 'ai-story-generator':
        story = templates.generate_story()
        return jsonify({"output": story})
    
    else:
        return jsonify({"error": "Unknown generator"}), 404

@app.route('/api/list', methods=['GET'])
def get_list():
    name = request.args.get('name')
    # Return available list items
    return jsonify({"items": lists.get_list(name)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

## Integration with Hybrid Router

Update `perchance_provider.py` to use local service:

```python
LOCALGEN_URL = "http://localhost:5000/api"

def _try_localgen(self, prompt: str, generator: str, start: float):
    """Generate using local LocalGen service."""
    try:
        url = f"{LOCALGEN_URL}/generate?generator={generator}"
        if prompt:
            url += f"&input={requests.utils.quote(prompt[:500])}"
        
        response = self.session.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            result_text = data.get("output", "")
            
            if result_text:
                return {
                    "response": result_text,
                    "provider": "localgen",
                    "generator": generator,
                    "latency_ms": (time.time() - start) * 1000,
                    "tokens_used": 0,  # Local!
                    "error": None,
                }
        
        return self._error_result(f"LocalGen error: {response.status_code}", start)
    
    except Exception as e:
        return self._error_result(f"LocalGen failed: {str(e)}", start)
```

## Deployment

### Option 1: Run as Background Service

```powershell
# Start LocalGen server
python localgen\server.py
```

### Option 2: Integrate with OpenClaw Gateway

Add as a plugin/extension to OpenClaw itself.

### Option 3: Run on Demand

Start server when needed, stop when done.

## Benefits

✅ **Unlimited generation** - Local hardware, no rate limits  
✅ **No Cloudflare** - We control the service  
✅ **Fast** - No network latency (localhost)  
✅ **Customizable** - Add any generators we want  
✅ **Private** - All data stays local  
✅ **Free** - No API costs  

## Tradeoffs

⚠️ **Uses local LLM** - Still consumes tokens (but local, no limits)  
⚠️ **Need to maintain** - We're responsible for updates  
⚠️ **Single-user** - Only serves our machine (by design)  

## Next Steps

1. Create `localgen/` directory structure
2. Implement list generators (names, plots, etc.)
3. Implement AI chat generator (Ollama integration)
4. Create Flask server with API endpoints
5. Update `perchance_provider.py` to use LocalGen
6. Test with hybrid router
7. Add to OpenClaw startup (auto-start with Gateway)

---

**This gives us unlimited creative generation without external dependencies!**
