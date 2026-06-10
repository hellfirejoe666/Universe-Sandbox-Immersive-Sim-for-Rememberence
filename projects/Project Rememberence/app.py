from flask import Flask, request, jsonify, send_from_directory
import os
import json
from rememberence_core.logic.oracle_engine import oracle
from rememberence_core.logic.atmosphere_engine import oracle_audio
from rememberence_core.dialogue_systems.hybrid_chat import oracle_dialogue
from rememberence_core.dice_engine.anydice_logic import oracle_dice
from rememberence_core.generators.donjon_hybrid import oracle_gen

app = Flask(__name__, static_folder='D:/Ollama/OpenClaw/workspace/rememberence_core/web')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/oracle/chat', methods=['POST'])
def chat():
    data = request.json
    user_msg = data.get("message", "")
    context = data.get("context", "neutral")
    
    # 1. Use the Hybrid Dialogue System for flavor/core
    response = oracle_dialogue.get_response(user_msg, context)
    
    # 2. If it's a command, route it to the Engine
    if any(cmd in user_msg.lower() for cmd in ["move", "attack", "status", "inventory"]):
        # Simple extraction for demo; real implementation uses RMC
        cmd = user_msg.lower().split()[0]
        args = user_msg.lower().split()[1:]
        engine_res = oracle.process_command(cmd, args)
        response = f"{response}\n\n[Oracle Logic]: {engine_res}"

    return jsonify({"response": response, "mood": oracle_audio.current_mood})

@app.route('/api/oracle/generate', methods=['POST'])
def generate():
    # Use Donjon Hybrid Generator
    npc = oracle_gen.generate_npc()
    return jsonify(npc)

@app.route('/api/oracle/roll', methods=['POST'])
def roll():
    data = request.json
    formula = data.get("formula", "1d20")
    result = oracle_dice.roll(formula)
    return jsonify({"result": result})

@app.route('/api/oracle/state', methods=['GET', 'POST'])
def handle_state():
    if request.method == 'GET':
        return jsonify(oracle.state)
    
    new_state = request.json
    oracle.state = new_state
    oracle.save_state()
    return jsonify({"status": "State synchronized with the Weave."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
