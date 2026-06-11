"""
LocalGen - Self-Hosted Unlimited AI Generation Service
"Speech Center" of the Hybrid Router brain

Handles: Simple explanations, brainstorming, conversation, creative text
Model: phi3:mini for fast simple tasks, qwen2.5:7b for complex creative

Usage:
    python localgen\server.py
    
API Endpoints:
    GET /api/generate?generator={name}&input={text}
    GET /api/list?name={listname}
    GET /api/health
"""

import sys
import random
import subprocess
import json
from pathlib import Path
from flask import Flask, request, jsonify
from typing import Dict, Any, List

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)

# ============================================================================
# LIST GENERATORS (Perchance-style random text generation)
# ============================================================================

FANTASY_NAMES = [
    "Shadowmere", "Dragonspire", "Winterhold", "Ravenwood", "Stormwind",
    "Ironforge", "Silvermoon", "Thunder Bluff", "Orgrimmar", "Stormrage",
    "Whisperwind", "Brightbane", "Doomhammer", "Frostwhisper", "Starweaver",
    "Moonfire", "Sunstrider", "Nightbringer", "Dawnblade", "Shadow Walker",
]

FANTASY_TITLES = [
    "the Bold", "the Wise", "the Terrible", "the Just", "the Mad",
    "Dragonlord", "Stormcaller", "Shadowbane", "Lightbringer", "the Undying",
]

PLOT_HOOKS = [
    "A young {hero} discovers {magic} in the ruins of {location}.",
    "The kingdom of {kingdom} faces invasion from {threat}.",
    "An ancient {artifact} awakens, calling to those who dare seek it.",
    "A {profession} uncovers a conspiracy that threatens {target}.",
    "The {event} marks the beginning of a new age for {race}.",
    "When {person} vanishes, {hero} must journey to {location} to find them.",
    "A prophecy foretells that {hero} will {action} before {deadline}.",
]

CHARACTER_CLASSES = [
    "wizard", "warrior", "rogue", "paladin", "ranger",
    "necromancer", "druid", "bard", "monk", "sorcerer",
]

LOCATIONS = [
    "the Crystal Caverns", "the Shadow Forest", "Dragon's Peak",
    "the Sunken City", "the Frozen Wastes", "the Burning Desert",
    "the Whispering Ruins", "the Celestial Observatory",
]


def generate_fantasy_name() -> str:
    """Generate a random fantasy name."""
    return random.choice(FANTASY_NAMES)


def generate_character_name() -> str:
    """Generate a character name with optional title."""
    name = random.choice(FANTASY_NAMES)
    if random.random() > 0.7:  # 30% chance of title
        name += f" {random.choice(FANTASY_TITLES)}"
    return name


def generate_plot() -> str:
    """Generate a random plot hook."""
    plot = random.choice(PLOT_HOOKS)
    
    return plot.format(
        hero=random.choice(["young wizard", "brave knight", "cunning thief", "exiled prince", "mysterious stranger"]),
        magic=random.choice(["a powerful artifact", "forbidden magic", "their true destiny", "an ancient power"]),
        location=random.choice(LOCATIONS),
        kingdom=random.choice(FANTASY_NAMES),
        threat=random.choice(["dragon horde", "dark army", "eldritch horror", "plague of undeath"]),
        artifact=random.choice(["sword", "amulet", "tome", "crown", "orb"]),
        profession=random.choice(CHARACTER_CLASSES),
        target=random.choice(["the realm", "the church", "the guild", "their family"]),
        event=random.choice(["eclipse", "comet's passage", "solstice", "great tournament"]),
        race=random.choice(["elves", "dwarves", "humans", "dragonborn"]),
        person=random.choice(["the king", "their mentor", "a mysterious patron", "their sibling"]),
        action=random.choice(["defeat the dark lord", "find the lost relic", "unite the kingdoms"]),
        deadline=random.choice(["the blood moon", "winter's end", "the final battle"]),
    )


def generate_city_name() -> str:
    """Generate a fantasy city name."""
    prefixes = ["Storm", "Iron", "Silver", "Gold", "Shadow", "Light", "Dragon", "Frost"]
    suffixes = ["hold", "gard", "heim", "fort", "haven", "spire", "reach", "watch"]
    return random.choice(prefixes) + random.choice(suffixes)


# ============================================================================
# MODEL SELECTION
# ============================================================================

# Use smaller model for simple tasks (faster, fewer tokens)
SIMPLE_MODEL = "phi3:mini"      # Fast explanations, simple text (~70 tokens)
CREATIVE_MODEL = "qwen2.5:7b"   # Creative writing, complex chat (~150 tokens)


def call_ollama(prompt: str, model: str = SIMPLE_MODEL, timeout: int = 30) -> str:
    """Call Ollama with specified model."""
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='ignore',
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "[Timeout]"
    except Exception as e:
        return f"[Error: {str(e)[:100]}]"


# ============================================================================
# AI GENERATORS (Local LLM)
# ============================================================================

CHARACTER_PERSONAS = {
    "default": "You are a creative fantasy storyteller. Write engaging, imaginative content.",
    "wizard": "You are a wise old wizard who speaks in mystical riddles and ancient wisdom.",
    "warrior": "You are a brave warrior who values honor, courage, and strength above all.",
    "rogue": "You are a cunning thief with a witty, sarcastic sense of humor.",
    "storyteller": "You are a master bard who weaves tales with dramatic flair.",
}


def chat_with_ai(message: str, persona: str = "default") -> str:
    """Chat with local LLM using specified persona."""
    system_prompt = CHARACTER_PERSONAS.get(persona, CHARACTER_PERSONAS["default"])
    prompt = f"{system_prompt}\n\nUser: {message[:500]}\n\nAssistant:"
    response = call_ollama(prompt, CREATIVE_MODEL, 30)
    return response.split("Assistant:")[-1].strip() if "Assistant:" in response else response


def explain_simple(concept: str) -> str:
    """Explain a concept in 2-3 simple sentences (phi3:mini, fast)."""
    prompt = f"Explain '{concept}' in 2-3 simple sentences. Be clear and concise."
    return call_ollama(prompt, SIMPLE_MODEL, 20)


def brainstorm_ideas(topic: str, count: int = 5) -> str:
    """Brainstorm N ideas about a topic (phi3:mini, fast)."""
    prompt = f"Give me {count} creative ideas about '{topic}'. List them as bullet points."
    return call_ollama(prompt, SIMPLE_MODEL, 25)


def rephrase_simple(text: str) -> str:
    """Rephrase text more simply (phi3:mini, fast)."""
    prompt = f"Say this more simply and clearly:\n\n{text[:500]}"
    return call_ollama(prompt, SIMPLE_MODEL, 20)


def summarize_text(text: str) -> str:
    """Summarize text in 1-2 sentences (phi3:mini, fast)."""
    prompt = f"Summarize this in 1-2 sentences:\n\n{text[:500]}"
    return call_ollama(prompt, SIMPLE_MODEL, 20)


def generate_story_segment(prompt_text: str) -> str:
    """Generate a story segment (qwen2.5:7b, creative)."""
    system = "You are a fantasy author. Write vivid, engaging narrative prose in 2-4 paragraphs."
    full_prompt = f"{system}\n\nWrite a story segment: {prompt_text[:500]}"
    return call_ollama(full_prompt, CREATIVE_MODEL, 45)


# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "LocalGen",
        "generators": [
            "fantasy-name", "character-name", "fantasy-plot", "city-name",
            "explain", "brainstorm", "rephrase", "summarize",
            "ai-character-chat", "ai-story-generator"
        ]
    })


@app.route('/api/generate', methods=['GET'])
def generate():
    """
    Main generation endpoint.
    
    Params:
        generator: Name of generator to use
        input: Input text (for AI generators)
        persona: Character persona (for AI chat)
    """
    generator = request.args.get('generator', 'default')
    input_text = request.args.get('input', '')
    persona = request.args.get('persona', 'default')
    
    # List-based generators (instant, 0 tokens)
    if generator == 'fantasy-name':
        return jsonify({
            "output": generate_fantasy_name(),
            "generator": generator,
            "tokens_used": 0,
        })
    
    elif generator == 'character-name':
        return jsonify({
            "output": generate_character_name(),
            "generator": generator,
            "tokens_used": 0,
        })
    
    elif generator == 'fantasy-plot':
        return jsonify({
            "output": generate_plot(),
            "generator": generator,
            "tokens_used": 0,
        })
    
    elif generator == 'city-name':
        return jsonify({
            "output": generate_city_name(),
            "generator": generator,
            "tokens_used": 0,
        })
    
    # Speech/Language center generators (phi3:mini - fast, simple)
    elif generator == 'explain':
        output = explain_simple(input_text)
        return jsonify({
            "output": output,
            "generator": generator,
            "model": SIMPLE_MODEL,
            "tokens_used": "local",
        })
    
    elif generator == 'brainstorm':
        output = brainstorm_ideas(input_text, count=5)
        return jsonify({
            "output": output,
            "generator": generator,
            "model": SIMPLE_MODEL,
            "tokens_used": "local",
        })
    
    elif generator == 'rephrase':
        output = rephrase_simple(input_text)
        return jsonify({
            "output": output,
            "generator": generator,
            "model": SIMPLE_MODEL,
            "tokens_used": "local",
        })
    
    elif generator == 'summarize':
        output = summarize_text(input_text)
        return jsonify({
            "output": output,
            "generator": generator,
            "model": SIMPLE_MODEL,
            "tokens_used": "local",
        })
    
    # Creative generators (qwen2.5:7b - slower, more creative)
    elif generator == 'ai-character-chat':
        response = chat_with_ai(input_text, persona)
        return jsonify({
            "output": response,
            "generator": generator,
            "persona": persona,
            "model": CREATIVE_MODEL,
            "tokens_used": "local",
        })
    
    elif generator == 'ai-story-generator':
        story = generate_story_segment(input_text)
        return jsonify({
            "output": story,
            "generator": generator,
            "model": CREATIVE_MODEL,
            "tokens_used": "local",
        })
    
    else:
        return jsonify({
            "error": f"Unknown generator: {generator}",
            "available": ["fantasy-name", "character-name", "fantasy-plot", "city-name", 
                         "explain", "brainstorm", "rephrase", "summarize",
                         "ai-character-chat", "ai-story-generator"]
        }), 404


@app.route('/api/list', methods=['GET'])
def get_list():
    """Get available items from a named list."""
    list_name = request.args.get('name', '')
    
    lists = {
        "fantasy_names": FANTASY_NAMES,
        "character_classes": CHARACTER_CLASSES,
        "locations": LOCATIONS,
        "titles": FANTASY_TITLES,
    }
    
    if list_name in lists:
        return jsonify({
            "name": list_name,
            "items": lists[list_name],
            "count": len(lists[list_name]),
        })
    else:
        return jsonify({
            "error": f"Unknown list: {list_name}",
            "available": list(lists.keys())
        }), 404


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 60)
    print("LocalGen - Self-Hosted Unlimited AI Generation")
    print("(Speech Center of Hybrid Router)")
    print("=" * 60)
    print()
    print("Starting server on http://localhost:5000")
    print()
    print("Available generators:")
    print("  List Generators (instant, 0 tokens):")
    print("    - fantasy-name, character-name, fantasy-plot, city-name")
    print("  Speech Center (phi3:mini, fast, ~70 tokens):")
    print("    - explain, brainstorm, rephrase, summarize")
    print("  Creative (qwen2.5:7b, slower, ~150 tokens):")
    print("    - ai-character-chat, ai-story-generator")
    print()
    print("API Endpoints:")
    print("  GET /api/generate?generator={name}&input={text}")
    print("  GET /api/list?name={listname}")
    print("  GET /api/health")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    main()
