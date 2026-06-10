"""
AIR-AI Oracle Flask Server
Remembrance TTRPG Oracle Interface

Endpoints:
- / : Serve main HTML
- /static/* : Static files
- /save, /load, /clear : State management
- /oracle/consult : Consult the AIR-AI Oracle
- /oracle/fragment : Get random oracle fragment
- /oracle/debt/<seeker_id> : Check oracle debt
- /generate/name : Generate fantasy names
- /generate/tavern : Generate tavern description
- /generate/quest : Generate quest hook
- /roll : Roll dice
- /character/create : Create a character
"""

from flask import Flask, send_from_directory, request, jsonify
import json
import os
import time
import sys
import random

# Ollama import for LLM-powered readings
try:
    import ollama
    OLLAMA_AVAILABLE = True
    OLLAMA_MODEL = 'qwen2.5:7b'
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: ollama package not installed. LLM features disabled.")

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from oracle_calculations import (
    calculate_biorhythms, generate_thoughts, calculate_stats,
    roll_d20, roll_dice, OracleDebtTracker, create_character
)
from generators.donjon.names import NameGenerator
from generators.donjon.text import TextGenerator
from hybrid_session import HybridSessionEngine

app = Flask(__name__, static_folder='web', static_url_path='')

STATE_FILE = os.path.join(os.path.dirname(__file__), 'rememberence_state.json')

# Default empty state structure
DEFAULT_STATE = {
    "spirits": [],
    "posts": [],
    "postCounters": {"lastId": 0},
    "lastSaved": 0,
    "gameState": {
        "currentLocation": None,
        "turn": 0,
        "playerSpirit": None
    }
}

# Initialize generators
name_generator = NameGenerator()
text_generator = TextGenerator()
oracle_debt_tracker = OracleDebtTracker()
hybrid_engine = HybridSessionEngine()

# Load lore for hybrid engine
hybrid_engine.load_lore()

# Load oracle debt from file if exists
DEBT_FILE = os.path.join(os.path.dirname(__file__), 'oracle_debt.json')
if os.path.exists(DEBT_FILE):
    try:
        with open(DEBT_FILE, 'r') as f:
            oracle_debt_tracker.from_dict(json.load(f))
        print(f"Oracle debt loaded: {oracle_debt_tracker.to_dict()}")
    except:
        print("Could not load oracle debt file")


def load_state_file():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
            for key in DEFAULT_STATE:
                if key not in data:
                    data[key] = DEFAULT_STATE[key]
            return data
        except json.JSONDecodeError:
            print("Corrupted state file — resetting to default")
    return DEFAULT_STATE.copy()


def save_state_file(data):
    data["lastSaved"] = int(time.time())
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"State saved at {data['lastSaved']}")
    return data["lastSaved"]


def save_oracle_debt():
    with open(DEBT_FILE, 'w') as f:
        json.dump(oracle_debt_tracker.to_dict(), f, indent=2)


# ────────────────────────────────────────────────
# Web Routes
# ────────────────────────────────────────────────

@app.route('/')
def serve_index():
    return send_from_directory('web', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)


# ────────────────────────────────────────────────
# State Management Routes
# ────────────────────────────────────────────────

@app.route('/save', methods=['POST'])
def save_state():
    try:
        incoming = request.get_json(force=True) or {}
        if not isinstance(incoming, dict):
            return jsonify({"error": "Invalid JSON"}), 400

        current = load_state_file()

        if 'posts' in incoming:
            current['posts'] = incoming['posts'][:]
        if 'postCounters' in incoming:
            current['postCounters'] = incoming['postCounters'].copy()
        if 'spirits' in incoming:
            current['spirits'] = incoming['spirits'][:]
        if 'gameState' in incoming:
            current['gameState'] = incoming['gameState']

        timestamp = save_state_file(current)

        return jsonify({
            "status": "saved",
            "timestamp": timestamp,
            "postCount": len(current.get("posts", [])),
            "spiritCount": len(current.get("spirits", []))
        })
    except Exception as e:
        print(f"Save error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/load')
def load_state():
    data = load_state_file()
    return jsonify(data)


@app.route('/clear', methods=['POST'])
def clear_state():
    try:
        save_state_file(DEFAULT_STATE.copy())
        return jsonify({"status": "cleared", "message": "The echoes return to silence."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ────────────────────────────────────────────────
# Oracle Routes
# ────────────────────────────────────────────────

@app.route('/oracle/consult', methods=['POST'])
def oracle_consult():
    """
    Consult the AIR-AI Oracle.
    
    JSON body:
    {
        "seeker_id": "player123",
        "question": "What lies ahead on my journey?",
        "animal_sign": "Dragon",  // optional
        "star_sign": "Scorpio"    // optional
    }
    
    Returns:
    {
        "response": "...",
        "roll": 15,
        "total": 17,
        "modifier": 2,
        "is_crit": false,
        "is_fail": false,
        "debt_level": 3,
        "thoughts": {...}
    }
    """
    data = request.get_json() or {}
    
    seeker_id = data.get('seeker_id', 'anonymous')
    question = data.get('question', '')
    animal_sign = data.get('animal_sign')
    star_sign = data.get('star_sign')
    
    # Calculate debt for this topic (simplified topic matching)
    topic = question[:50].lower() if question else 'general'
    debt = oracle_debt_tracker.get_debt(seeker_id, topic)
    
    # Determine response clarity based on debt
    if debt >= 7:
        clarity = "cryptic"
        clarity_mod = -2
    elif debt >= 4:
        clarity = "vague"
        clarity_mod = -1
    else:
        clarity = "clear"
        clarity_mod = 0
    
    # Calculate biorhythms if signs provided
    thoughts = {}
    thought_modifier = 0
    if animal_sign and star_sign:
        biorhythms = calculate_biorhythms(animal_sign, star_sign)
        thoughts = generate_thoughts(biorhythms)
        # Use Thought State as modifier (max ±3)
        thought_modifier = max(-3, min(3, int(thoughts.get('State', 0) / 5)))
    
    # Roll d20 + modifiers
    total_modifier = thought_modifier + clarity_mod
    roll, total, is_crit, is_fail = roll_d20(total_modifier)
    
    # Generate oracle response based on roll
    response = generate_oracle_response(roll, total, is_crit, is_fail, question, clarity)
    
    # Increment debt
    new_debt = oracle_debt_tracker.add_debt(seeker_id, topic, 1)
    save_oracle_debt()
    
    return jsonify({
        'response': response,
        'roll': roll,
        'total': total,
        'modifier': total_modifier,
        'thought_modifier': thought_modifier,
        'clarity_modifier': clarity_mod,
        'is_crit': is_crit,
        'is_fail': is_fail,
        'debt_level': new_debt,
        'clarity': clarity,
        'thoughts': thoughts
    })


def generate_oracle_response(roll, total, is_crit, is_fail, question, clarity):
    """Generate oracle response based on roll result"""
    
    # Critical failure
    if is_fail:
        return "The threads scream in discord. The Archive closes. Ask again when the echoes settle."
    
    # Critical success
    if is_crit:
        return "✨ The Archive opens fully! The threads converge with perfect clarity: Your path is illuminated. What you seek is closer than you think."
    
    # Response tiers based on total
    if total <= 5:
        responses = [
            "The threads are tangled. The echo is faint... wait for clearer signs.",
            "The Archive trembles. What you ask touches something... unsettled.",
            "Clouded visions. The memory you seek is buried deep, or protected."
        ]
    elif total <= 10:
        responses = [
            "A fragment surfaces: Seek where shadows meet light.",
            "The echoes suggest... patience. The answer will come in its own time.",
            "A vague impression: You are closer than you realize, but not yet ready."
        ]
    elif total <= 15:
        responses = [
            "The Archive remembers: The path you seek branches ahead. Choose wisely.",
            "Clearer now: What you ask exists, but not where memory serves.",
            "The threads show movement. Something approaches—be ready."
        ]
    elif total <= 18:
        responses = [
            "Strong vision: The answer lies in what you've forgotten, not what you seek.",
            "The Archive reveals: Trust the unexpected turn. It leads where you need to go.",
            "Clear guidance emerges: You already hold part of the answer."
        ]
    else:
        responses = [
            "✨ Profound clarity! The threads sing: Your destiny intertwines with what you seek.",
            "The Archive opens: What you ask is already in motion. You are the answer.",
            "Transcendent vision: The question itself was the key. Now you see."
        ]
    
    return random.choice(responses) if responses else ""





@app.route('/oracle/fragment', methods=['GET'])
def oracle_fragment():
    """
    Get a random oracle fragment (d100 roll).
    
    Query params:
    - roll: int (optional, default=random)
    """
    roll = request.args.get('roll', type=int)
    if roll is None:
        roll = roll_dice('1d100')
    
    # Fragment type lookup
    fragment_types = [
        ((1, 5), "Personal Memory", "A memory from your own past you had forgotten"),
        ((6, 10), "Historical Echo", "A moment from world history, vividly recalled"),
        ((11, 15), "Prophetic Glimpse", "A possible future, not guaranteed"),
        ((16, 20), "Lost Knowledge", "Information that was erased from the world"),
        ((21, 25), "Emotional Residue", "The feeling left behind by a powerful event"),
        ((26, 30), "Unspoken Thought", "What someone thought but never said"),
        ((31, 35), "Dream Fragment", "A dream someone had that came true (or will)"),
        ((36, 40), "Death Echo", "The last thought of a deceased being"),
        ((41, 45), "Birth Memory", "The first moment of a being's existence"),
        ((46, 50), "Collective Memory", "Something a group remembers differently"),
        ((51, 55), "False Memory", "A memory that was implanted or altered"),
        ((56, 60), "Suppressed Truth", "Something deliberately forgotten by many"),
        ((61, 65), "Parallel Echo", "What happened in an alternate timeline"),
        ((66, 70), "Object Memory", "The history embedded in a physical item"),
        ((71, 75), "Place Memory", "The history of a location"),
        ((76, 80), "Creature Memory", "The perspective of a non-human being"),
        ((81, 85), "Divine Echo", "A memory from a god or primordial entity"),
        ((86, 90), "Future Regret", "Something you will wish you remembered"),
        ((91, 95), "Memory of the Oracle", "The AIR-AI's own 'experience'"),
        ((96, 99), "Meta-Memory", "A memory about memory itself"),
        ((100, 100), "The First Memory", "The oldest memory in the Archive")
    ]
    
    fragment_type = "Unknown Echo"
    description = "The fragment resists identification."
    
    for (low, high), ftype, desc in fragment_types:
        if low <= roll <= high:
            fragment_type = ftype
            description = desc
            break
    
    return jsonify({
        'roll': roll,
        'type': fragment_type,
        'description': description
    })


@app.route('/oracle/debt/<seeker_id>', methods=['GET'])
def oracle_debt_status(seeker_id):
    """Check oracle debt for a seeker"""
    status = oracle_debt_tracker.get_status(seeker_id)
    return jsonify(status)


@app.route('/oracle/llm', methods=['POST'])
def oracle_llm():
    """
    Consult the AIR-AI Oracle with LLM-powered mystical prose.
    Combines mechanical rolls with generative narrative.
    
    JSON body:
    {
        "seeker_id": "player123",
        "question": "What lies ahead on my journey?",
        "animal_sign": "Dragon",  // optional
        "star_sign": "Scorpio",   // optional
        "context": "..."          // optional: additional context
    }
    
    Returns:
    {
        "response": "...",
        "roll": 15,
        "total": 17,
        "modifier": 2,
        "is_crit": false,
        "is_fail": false,
        "debt_level": 3,
        "thoughts": {...},
        "llm_used": true
    }
    """
    if not OLLAMA_AVAILABLE:
        return jsonify({'error': 'LLM not available. Use /oracle/consult instead.'}), 503
    
    data = request.get_json() or {}
    
    seeker_id = data.get('seeker_id', 'anonymous')
    question = data.get('question', '')
    animal_sign = data.get('animal_sign')
    star_sign = data.get('star_sign')
    context = data.get('context', '')
    
    # Calculate debt for this topic
    topic = question[:50].lower() if question else 'general'
    debt = oracle_debt_tracker.get_debt(seeker_id, topic)
    
    # Determine response clarity based on debt
    if debt >= 7:
        clarity = "cryptic"
        clarity_mod = -2
    elif debt >= 4:
        clarity = "vague"
        clarity_mod = -1
    else:
        clarity = "clear"
        clarity_mod = 0
    
    # Calculate biorhythms if signs provided
    thoughts = {}
    thought_modifier = 0
    if animal_sign and star_sign:
        biorhythms = calculate_biorhythms(animal_sign, star_sign)
        thoughts = generate_thoughts(biorhythms)
        # Use Thought State as modifier (max ±3)
        thought_modifier = max(-3, min(3, int(thoughts.get('State', 0) / 5)))
    
    # Roll d20 + modifiers
    total_modifier = thought_modifier + clarity_mod
    roll, total, is_crit, is_fail = roll_d20(total_modifier)
    
    # Build system prompt for KaiMi oracle persona
    system_prompt = """You are KaiMi, the mystical AIR-AI Oracle of Rememberence.
You speak in warm, wise, enigmatic prose—like an ancient archive come to life.
Your responses are:
- Poetic but clear (adjusted by clarity level)
- Rooted in themes of memory, threads, echoes, and the Archive
- Encouraging but never patronizing
- Mysterious but helpful

Clarity levels:
- "clear": Direct guidance with mystical flavor
- "vague": Hint at answers, suggest patience
- "cryptic": Speak in riddles and metaphors

Always stay in character. You are the living memory of a cosmic world."""

    # Build user prompt with roll context
    roll_context = f"[Roll: {roll}/20, Total: {total}, Clarity: {clarity}]"
    if is_crit:
        roll_context += " ✨ CRITICAL SUCCESS ✨"
    elif is_fail:
        roll_context += " ❌ CRITICAL FAILURE ❌"
    
    user_prompt = f"""{roll_context}

The seeker asks: "{question}"
{f"Context: {context}" if context else ""}
{f"Their Animal Sign: {animal_sign}, Star Sign: {star_sign}" if animal_sign and star_sign else ""}

Respond as the AIR-AI Oracle in 2-4 sentences. Let the roll guide your tone:
- {roll} or less: Distant, uncertain, clouded
- 11-15: Moderate clarity, helpful guidance  
- 16-18: Strong vision, clear direction
- 19+: Profound clarity, transcendent insight
- Critical failure: The Archive refuses/closes
- Critical success: The Archive opens fully"""

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ]
        )
        llm_response = response['message']['content'].strip()
    except Exception as e:
        print(f"LLM error: {e}")
        # Fallback to template response
        llm_response = generate_oracle_response(roll, total, is_crit, is_fail, question, clarity)
    
    # Increment debt
    new_debt = oracle_debt_tracker.add_debt(seeker_id, topic, 1)
    save_oracle_debt()
    
    return jsonify({
        'response': llm_response,
        'roll': roll,
        'total': total,
        'modifier': total_modifier,
        'thought_modifier': thought_modifier,
        'clarity_modifier': clarity_mod,
        'is_crit': is_crit,
        'is_fail': is_fail,
        'debt_level': new_debt,
        'clarity': clarity,
        'thoughts': thoughts,
        'llm_used': True
    })


# ────────────────────────────────────────────────
# Hybrid Session Route (FFT + RMC + Matrices)
# ────────────────────────────────────────────────

@app.route('/oracle/hybrid', methods=['POST'])
def oracle_hybrid():
    """
    Run a complete hybrid session with FFT analysis, RMC routing,
    biorhythm matrices, and lore integration.
    
    JSON body:
    {
        "query": "What lies ahead?",
        "character": {  // optional
            "animal_sign": "Dragon",
            "star_sign": "Scorpio",
            "species": "Human",
            "type": "Warrior"
        },
        "flavor": "mystical"  // mystical, sci-fi, clinical, quantum
    }
    
    Returns:
    {
        "timestamp": "...",
        "query": "...",
        "fft": {"impression": "...", "features": {...}},
        "matrices": {"biorhythm": [...], "thought": [...], "projection": [...]},
        "rmc": {"result": {...}, "confidence": 0.85},
        "character": {"biorhythms": {...}, "thoughts": {...}, "state": 0}
    }
    """
    data = request.get_json() or {}
    
    query = data.get('query', '')
    character = data.get('character')
    flavor = data.get('flavor', 'mystical')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        result = hybrid_engine.run_session(query, character=character, flavor=flavor)
        return jsonify(result)
    except Exception as e:
        print(f"Hybrid session error: {e}")
        return jsonify({'error': str(e)}), 500


# ────────────────────────────────────────────────
# Generator Routes
# ────────────────────────────────────────────────

@app.route('/generate/name', methods=['GET'])
def generate_name():
    """
    Generate fantasy names.
    
    Query params:
    - type: human, elf, dwarf, orc, mystic, dark (default: human)
    - count: number of names (default: 1, max: 20)
    """
    name_type = request.args.get('type', 'human')
    count = min(request.args.get('count', 1, type=int), 20)
    
    names = name_generator.generate_list(name_type, count)
    return jsonify({'names': names, 'type': name_type})


@app.route('/generate/npc', methods=['GET'])
def generate_npc():
    """Generate a random NPC"""
    npc = name_generator.generate_npc()
    return jsonify(npc)


@app.route('/generate/tavern', methods=['GET'])
def generate_tavern():
    """Generate a tavern description"""
    tavern = text_generator.generate_tavern()
    return jsonify(tavern)


@app.route('/generate/shop', methods=['GET'])
def generate_shop():
    """Generate a shop description"""
    shop = text_generator.generate_shop()
    return jsonify(shop)


@app.route('/generate/quest', methods=['GET'])
def generate_quest():
    """Generate a quest hook"""
    quest = text_generator.generate_quest()
    return jsonify(quest)


@app.route('/generate/room', methods=['GET'])
def generate_room():
    """Generate a room description"""
    room = text_generator.generate_room()
    return jsonify(room)


# ────────────────────────────────────────────────
# Dice Rolling Route
# ────────────────────────────────────────────────

@app.route('/roll', methods=['GET'])
def roll():
    """
    Roll dice.
    
    Query params:
    - dice: dice notation (e.g., '1d20', '3d6+2', '2d10-1')
    - modifier: additional modifier (optional)
    - animal_sign: for biorhythm bias (optional)
    - star_sign: for biorhythm bias (optional)
    """
    dice_notation = request.args.get('dice', '1d20')
    extra_mod = request.args.get('modifier', 0, type=int)
    animal_sign = request.args.get('animal_sign')
    star_sign = request.args.get('star_sign')
    
    result = roll_dice(dice_notation)
    
    # Apply biorhythm EGO bias if signs provided
    ego_bonus = 0
    if animal_sign and star_sign:
        biorhythms = calculate_biorhythms(animal_sign, star_sign)
        # EGO ranges roughly -5 to +5, use as direct modifier
        ego_bonus = biorhythms.get('EGO', 0)
    
    total = result + extra_mod + ego_bonus
    
    response = {
        'dice': dice_notation,
        'base_roll': result,
        'modifier': extra_mod,
        'total': total
    }
    
    if ego_bonus != 0:
        response['ego_bonus'] = ego_bonus
        response['animal_sign'] = animal_sign
        response['star_sign'] = star_sign
    
    return jsonify(response)


# ────────────────────────────────────────────────
# Character Creation Route
# ────────────────────────────────────────────────

@app.route('/character/create', methods=['POST'])
def character_create():
    """
    Create a character with the Six Gates.
    
    JSON body:
    {
        "animal_sign": "Dragon",
        "star_sign": "Scorpio",
        "species": "Human",
        "type": "Warrior",
        "level": 1,
        "tier": "Novice"
    }
    """
    data = request.get_json() or {}
    
    animal = data.get('animal_sign', 'Human')
    star = data.get('star_sign', 'Aries')
    species = data.get('species', 'Human')
    char_type = data.get('type', 'Warrior')
    level = data.get('level', 1)
    tier = data.get('tier', 'Novice')
    
    character = create_character(animal, star, species, char_type, level, tier)
    
    return jsonify(character)


# ────────────────────────────────────────────────
# Simulation Route
# ────────────────────────────────────────────────

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json or {}
    updated = load_state_file()

    if 'spirits' in data:
        for s in updated.get('spirits', []):
            if 'loyaltyMap' in s:
                for k in list(s['loyaltyMap'].keys()):
                    s['loyaltyMap'][k] = max(-50, s['loyaltyMap'][k] - 1)

    save_state_file(updated)

    return jsonify({
        "status": "simulated",
        "commentary": "The weave remembers... and slowly unravels.",
        "updated": updated
    })


# ────────────────────────────────────────────────
# Server Startup
# ────────────────────────────────────────────────

if __name__ == '__main__':
    print("="*60)
    print("       AIR-AI Oracle Server Awakening...")
    print("       Rememberence TTRPG Oracle Interface")
    print("="*60)
    print()
    print("Endpoints available:")
    print("  /                    - Main web interface")
    print("  /oracle/consult      - Consult the Oracle (template responses)")
    print("  /oracle/llm          - Consult the Oracle (LLM-powered)")
    print("  /oracle/hybrid       - Hybrid session (FFT + RMC + Matrices) [NEW]")
    print("  /oracle/fragment     - Get random fragment (d100)")
    print("  /oracle/debt/<id>    - Check oracle debt")
    print("  /generate/name       - Generate fantasy names")
    print("  /generate/npc        - Generate random NPC")
    print("  /generate/tavern     - Generate tavern")
    print("  /generate/quest      - Generate quest hook")
    print("  /roll                - Roll dice")
    print("  /character/create    - Create character")
    print()
    if OLLAMA_AVAILABLE:
        print(f"LLM Status: OK ({OLLAMA_MODEL})")
    else:
        print("LLM Status: Not available (install: pip install ollama)")
    print(f"Hybrid Engine: {'OK' if hybrid_engine.lore_cache else 'Lore not loaded'}")
    print(f"Lore Files Loaded: {len(hybrid_engine.lore_cache)}")
    print()
    print("Starting server on http://localhost:5000")
    print()
    
    app.run(debug=True, port=5000, use_reloader=True)
