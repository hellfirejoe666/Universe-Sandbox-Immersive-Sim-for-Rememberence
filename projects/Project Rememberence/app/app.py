from flask import Flask, send_from_directory, request, jsonify
import json
import os
import time
import threading
import webbrowser
from pathlib import Path
import sys
import random
from datetime import datetime

# Add generators and core directories to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'generators'))
sys.path.insert(0, str(PROJECT_ROOT / 'core'))

# Import queue manager
from queue_manager import get_queue_manager, start_background_processor

# Import character creator
try:
    from character_creator import create_character, get_all_options, get_class_skills
    print("Character creator loaded")
except ImportError as e:
    print(f"Warning: Character creator not available: {e}")
    create_character = None
    get_all_options = None
    get_class_skills = None

# Load donjon generator
try:
    from donjon_generator import DonjonTextGenerator
    donjon_gen = DonjonTextGenerator(str(PROJECT_ROOT / 'generators'))
    print("Donjon generator loaded")
except ImportError as e:
    print(f"Warning: Donjon generator not available: {e}")
    donjon_gen = None

app = Flask(__name__, static_folder='../static', static_url_path='/static')

# State file in root (same level as index.html)
STATE_FILE = PROJECT_ROOT / "rememberence_state.json"
SAVES_DIR = PROJECT_ROOT / 'saves'
SAVES_DIR.mkdir(exist_ok=True)

@app.route('/load-spirit')
def load_spirit():
    path = request.args.get('path')
    if not path or '..' in path:
        return jsonify({"error": "Invalid path"}), 400
    full_path = SAVES_DIR / path
    if not full_path.exists():
        return jsonify({"error": "Spirit not found"}), 404
    with open(full_path, 'r') as f:
        return jsonify(json.load(f))

@app.route('/save-spirit', methods=['POST'])
def save_spirit():
    data = request.json
    path = data.get('path')
    spirit = data.get('spirit')
    if not path or not spirit or '..' in path:
        return jsonify({"error": "Invalid path or data"}), 400
    full_path = SAVES_DIR / path
    full_path.parent.mkdir(exist_ok=True)
    with open(full_path, 'w') as f:
        json.dump(spirit, f, indent=2)
    return jsonify({"status": "saved"})

@app.route('/list-spirits')
def list_spirits():
    names = [f.stem for f in SAVES_DIR.glob('*.json') if f.is_file()]
    return jsonify(names)

DEFAULT_STATE = {
    "spirits": [],
    "posts": [],
    "postCounters": {"lastId": 0},
    "lastSaved": 0
}

def load_state_file():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                data = json.load(f)
            for key in DEFAULT_STATE:
                if key not in data:
                    data[key] = DEFAULT_STATE[key]
            print(f"Loaded state from {STATE_FILE} — {len(data.get('spirits', []))} spirits")
            return data
        except json.JSONDecodeError as e:
            print(f"Corrupted state file: {e} — resetting to default")
    else:
        print(f"State file not found at {STATE_FILE} — creating default")
    return DEFAULT_STATE.copy()

def save_state_file(data):
    data["lastSaved"] = int(time.time())
    STATE_FILE.parent.mkdir(exist_ok=True)  # Ensure parent dir exists
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved state to {STATE_FILE} — {len(data.get('spirits', []))} spirits")

@app.route('/')
def index():
    return send_from_directory(PROJECT_ROOT, 'index.html')

@app.route('/create-spirit')
def create_spirit():
    """Character creation wizard"""
    return send_from_directory(PROJECT_ROOT, 'create-spirit.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(PROJECT_ROOT / 'static', filename)

@app.route('/load-state', methods=['GET'])
def load_state():
    return jsonify(load_state_file())

@app.route('/save-state', methods=['POST'])
def save_state():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400
    save_state_file(data)
    return jsonify({"status": "saved", "message": "The echoes are preserved."})

@app.route('/generate-spirit', methods=['POST'])
def generate_spirit():
    data = request.json or {}
    spirit = {"name": "Test Spirit", "description": "Generated for test."}
    updated = load_state_file()
    updated["spirits"].append(spirit)
    save_state_file(updated)
    return jsonify(spirit)

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

@app.route('/ask-oracle', methods=['POST'])
def ask_oracle():
    query = request.form.get('query', '')
    response = "The Oracle whispers: " + query.upper() + " — echoes of truth from the weave."
    return f"<div class='message oracle'>{response}</div>"

@app.route('/chat-stream')
def chat_stream():
    def stream():
        yield 'data: The Oracle is awakening...\n\n'
    return app.response_class(stream(), mimetype='text/event-stream')

@app.route('/generate/tavern')
def generate_tavern():
    """Generate a random tavern name using donjon-style generator"""
    if not donjon_gen:
        return jsonify({"error": "Generator not available"}), 503
    
    # Simple tavern name templates
    templates = [
        "The {adjective} {noun}",
        "The {adjective} {animal}",
        "{noun}'s Rest",
        "The {color} {object}",
        "The {animal} and {noun}"
    ]
    
    # Inline data for demo (can load from JSON files later)
    donjon_gen.gen_data = {
        "adjective": ["Broken", "Golden", "Silent", "Mystic", "Ancient", "Crimson", "Wandering", "Forgotten"],
        "noun": ["Knight", "Dragon", "Crown", "Phoenix", "Chalice", "Griffin", "Sword"],
        "animal": ["Badger", "Raven", "Wolf", "Owl", "Serpent", "Hawk", "Fox"],
        "color": ["Red", "Blue", "Green", "Silver", "Black", "Golden", "Pale"],
        "object": ["Lantern", "Shield", "Rose", "Star", "Moon", "Well", "Gate"]
    }
    
    template = request.args.get('template', random.choice(templates))
    name = donjon_gen.expand_tokens(template)
    
    return jsonify({
        "name": name,
        "template": template,
        "type": "tavern"
    })

@app.route('/generate/name')
def generate_name():
    """Generate a random character/place name"""
    if not donjon_gen:
        return jsonify({"error": "Generator not available"}), 503
    
    name_type = request.args.get('type', 'fantasy')
    name = donjon_gen.generate_name(name_type)
    
    return jsonify({
        "name": name,
        "type": name_type
    })


# ────────────────────────────────────────────────
# Character Creation Endpoints
# ────────────────────────────────────────────────

@app.route('/character/options')
def get_character_options():
    """Get all available options for character creation"""
    if not get_all_options:
        return jsonify({"error": "Character creator not available"}), 503
    
    return jsonify(get_all_options())

@app.route('/character/class-skills')
def get_skills_for_class():
    """Get available skills for a specific class"""
    if not get_class_skills:
        return jsonify({"error": "Character creator not available"}), 503
    
    char_class = request.args.get('class', '')
    if not char_class:
        return jsonify({"error": "Class parameter required"}), 400
    
    skills = get_class_skills(char_class)
    return jsonify({"class": char_class, "skills": skills})

@app.route('/character/create', methods=['POST'])
def create_new_character():
    """
    Create a new character with calculated stats.
    
    JSON body:
    {
        "name": "Spirit Name",
        "animal": "Dragon",
        "star": "Aries",
        "species": "Drakian",
        "type": "Warrior",
        "class": "Melee",
        "skills": ["One Handed", "Dragon Breath"]
    }
    """
    if not create_character:
        return jsonify({"error": "Character creator not available"}), 503
    
    data = request.json or {}
    
    required = ['name', 'animal', 'star', 'species', 'type', 'class']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400
    
    try:
        character = create_character(
            name=data['name'],
            animal=data['animal'],
            star=data['star'],
            species=data['species'],
            char_type=data['type'],
            char_class=data['class'],
            skills=data.get('skills', [])
        )
        return jsonify(character)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Character creation failed: {str(e)}"}), 500


# ────────────────────────────────────────────────
# Queue Management Endpoints
# ────────────────────────────────────────────────

@app.route('/queue/status')
def queue_status():
    """Get current queue status"""
    queue = get_queue_manager()
    return jsonify(queue.get_queue_status())

@app.route('/queue/add', methods=['POST'])
def queue_add():
    """
    Add a job to the queue.
    
    JSON body:
    {
        "type": "llm_generate" | "oracle_enrich" | ...,  # Job type
        "service": "ollama" | "openai" | ...,            # API service
        "params": {...},                                  # Job parameters
        "priority": "high" | "normal" | "low",           # Default: "normal"
        "fallback_local": true | false,                   # Default: true
        "callback_url": "..."                             # Optional
    }
    """
    data = request.json or {}
    
    job_type = data.get('type')
    service = data.get('service', 'default')
    params = data.get('params', {})
    priority = data.get('priority', 'normal')
    fallback_local = data.get('fallback_local', True)
    callback_url = data.get('callback_url')
    
    if not job_type:
        return jsonify({"error": "Job type required"}), 400
    
    queue = get_queue_manager()
    job_id = queue.add_job(
        job_type=job_type,
        service=service,
        params=params,
        priority=priority,
        fallback_local=fallback_local,
        callback_url=callback_url
    )
    
    return jsonify({
        "job_id": job_id,
        "status": "queued",
        "priority": priority,
        "fallback_enabled": fallback_local
    })

@app.route('/queue/job/<job_id>')
def get_job(job_id):
    """Get status of a specific job"""
    queue = get_queue_manager()
    job = queue.get_job_status(job_id)
    
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify(job)

@app.route('/queue/process', methods=['POST'])
def process_queue():
    """
    Manually trigger queue processing.
    
    JSON body (optional):
    {
        "executor": "mock"  # For testing, use mock executor
    }
    """
    data = request.json or {}
    
    queue = get_queue_manager()
    
    # Use mock executor for testing
    if data.get('executor') == 'mock':
        def mock_executor(job_type, params):
            time.sleep(0.1)  # Simulate work
            return True, {"mock_result": True, "type": job_type}
        results = queue.process_queue(mock_executor)
    else:
        results = queue.process_queue()
    
    return jsonify({
        "processed": len(results),
        "results": results
    })

@app.route('/queue/clear', methods=['POST'])
def clear_queue():
    """Clear completed/failed jobs from queue"""
    data = request.json or {}
    status_filter = data.get('status')  # Optional: clear only specific status
    
    queue = get_queue_manager()
    queue.clear_queue(status_filter)
    
    return jsonify({"status": "cleared", "filter": status_filter})

@app.route('/queue/retry', methods=['POST'])
def retry_failed():
    """Retry all failed jobs"""
    queue = get_queue_manager()
    count = queue.retry_failed()
    
    return jsonify({"retried": count})

def open_browser():
    time.sleep(1.5)
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    print("Biblio Remembrancia server awakening...")
    
    # Start background queue processor
    start_background_processor(interval=10)
    print("Queue manager initialized")
    
    threading.Timer(1.5, open_browser).start()
    app.run(debug=True, port=5000, use_reloader=True)