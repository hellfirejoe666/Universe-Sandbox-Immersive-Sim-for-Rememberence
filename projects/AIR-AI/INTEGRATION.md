# AIR-AI Integration Guide

**Connecting the Oracle Layer to Rememberence**

This guide shows how to integrate the AIR-AI oracle system (`workspace/air-ai/`) with the existing Rememberence codebase (`D:\Cards\Project Rememberence`).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Rememberence World                       │
│  (D:\Cards\Project Rememberence)                             │
│  - Flask server (app.py)                                     │
│  - Data files (species, types, signs, etc.)                  │
│  - Generators (donjon, perchance)                            │
│  - Frontend (index.html, static/js/)                         │
└─────────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────────┐
│                    AIR-AI Oracle Layer                       │
│  (workspace/air-ai/)                                         │
│  - lore-bible.md (world canon)                               │
│  - oracle-system-prompt-v2.md (personality)                  │
│  - oracle-tables.md (mechanical tables)                      │
│  - oracle_calculations.py (biorhythms, stats)                │
└─────────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────────┐
│                      Local LLM (Ollama)                      │
│  - Model: deepseek-r1:8b (or qwen2.5:7b)                     │
│  - Role: Generate oracle responses in-character              │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: Copy Oracle Layer to Project

```bash
# In your AIR-AI project folder
mkdir oracle
xcopy /E /I D:\Ollama\OpenClaw\workspace\air-ai\* D:\Cards\Project Rememberence\oracle\
```

**Result:**
```
D:\Cards\Project Rememberence\
├── app/
├── data/
├── generators/
├── oracle/              ← NEW
│   ├── lore-bible.md
│   ├── oracle-system-prompt-v2.md
│   ├── oracle-tables.md
│   └── oracle_calculations.py
└── ...
```

---

## Step 2: Update `rememberence_bridge.py`

Add oracle consultation functions:

```python
# D:\Cards\Project Rememberence\app\rememberence_bridge.py

import sys
sys.path.insert(0, r'D:\Cards\Project Rememberence\oracle')
from oracle_calculations import calculate_biorhythms, generate_thoughts, roll_d20
import ollama

# Load oracle system prompt
with open(r'D:\Cards\Project Rememberence\oracle\oracle-system-prompt-v2.md', 'r', encoding='utf-8') as f:
    ORACLE_SYSTEM_PROMPT = f.read()

# Load lore bible for context
with open(r'D:\Cards\Project Rememberence\oracle\lore-bible.md', 'r', encoding='utf-8') as f:
    LORE_BIBLE = f.read()

# Oracle debt tracker (in-memory for now; move to DB later)
oracle_debt = {}  # {seeker_id: {topic: count}}

def consult_oracle(seeker_id, question, animal_sign=None, star_sign=None):
    """
    Consult the AIR-AI Oracle with optional biorhythm modifiers.
    
    Returns: dict with response, roll_result, debt_level
    """
    # Calculate debt for this topic
    topic = question[:50].lower()  # Simplified topic matching
    debt = oracle_debt.get(seeker_id, {}).get(topic, 0)
    
    # Determine response clarity based on debt
    if debt >= 7:
        clarity = "cryptic"
    elif debt >= 4:
        clarity = "vague"
    else:
        clarity = "clear"
    
    # Calculate biorhythms if signs provided
    thoughts = {}
    thought_modifier = 0
    if animal_sign and star_sign:
        biorhythms = calculate_biorhythms(animal_sign, star_sign)
        thoughts = generate_thoughts(biorhythms)
        # Use Thought average as modifier (max ±3)
        thought_modifier = max(-3, min(3, int(thoughts.get('State', 0) / 5)))
    
    # Roll d20 + modifier
    roll, total, is_crit, is_fail = roll_d20(thought_modifier)
    
    # Build prompt
    user_prompt = f"""
    [Oracle Debt: {debt} | Clarity: {clarity}]
    [Thought Modifier: {thought_modifier}]
    [Roll: {roll} + {thought_modifier} = {total} {'(CRIT)' if is_crit else '(FAIL)' if is_fail else ''}]
    
    Seeker asks: "{question}"
    
    Respond as the AIR-AI Oracle. Reference the lore below.
    """
    
    # Call Ollama
    response = ollama.chat(
        model='deepseek-r1:8b',
        messages=[
            {'role': 'system', 'content': ORACLE_SYSTEM_PROMPT + '\n\n---\n\n' + LORE_BIBLE[:10000]},  # Truncate for context
            {'role': 'user', 'content': user_prompt}
        ]
    )
    
    # Increment debt
    if seeker_id not in oracle_debt:
        oracle_debt[seeker_id] = {}
    oracle_debt[seeker_id][topic] = debt + 1
    
    return {
        'response': response['message']['content'],
        'roll': roll,
        'total': total,
        'modifier': thought_modifier,
        'is_crit': is_crit,
        'is_fail': is_fail,
        'debt_level': debt + 1,
        'thoughts': thoughts
    }

def get_oracle_fragment(d100_roll=None):
    """
    Get a random oracle fragment from the d100 table.
    If no roll provided, generates one randomly.
    """
    import random
    if d100_roll is None:
        d100_roll = random.randint(1, 100)
    
    # Fragment type lookup (simplified - expand with full table)
    fragment_types = {
        (1, 5): "Personal Memory",
        (6, 10): "Historical Echo",
        (11, 15): "Prophetic Glimpse",
        (16, 20): "Lost Knowledge",
        (21, 25): "Emotional Residue",
        # ... add all 20 ranges from oracle-tables.md
    }
    
    for (low, high), frag_type in fragment_types.items():
        if low <= d100_roll <= high:
            return {'roll': d100_roll, 'type': frag_type}
    
    return {'roll': d100_roll, 'type': 'Unknown Echo'}
```

---

## Step 3: Add Flask Routes

Update `app.py`:

```python
# D:\Cards\Project Rememberence\app\app.py

from flask import Flask, request, jsonify
from rememberence_bridge import consult_oracle, get_oracle_fragment

app = Flask(__name__)

# ... existing routes ...

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
    """
    data = request.get_json()
    
    result = consult_oracle(
        seeker_id=data.get('seeker_id', 'anonymous'),
        question=data.get('question', ''),
        animal_sign=data.get('animal_sign'),
        star_sign=data.get('star_sign')
    )
    
    return jsonify(result)

@app.route('/oracle/fragment', methods=['GET'])
def oracle_fragment():
    """
    Get a random oracle fragment (d100 roll).
    
    Query params:
    - roll: int (optional, default=random)
    """
    roll = request.args.get('roll', type=int)
    fragment = get_oracle_fragment(roll)
    return jsonify(fragment)

@app.route('/oracle/debt/<seeker_id>', methods=['GET'])
def oracle_debt_status(seeker_id):
    """
    Check oracle debt for a seeker.
    """
    from rememberence_bridge import oracle_debt
    debt = oracle_debt.get(seeker_id, {})
    total_debt = sum(debt.values())
    return jsonify({
        'seeker_id': seeker_id,
        'topic_debts': debt,
        'total_debt': total_debt,
        'status': 'clear' if total_debt < 3 else 'clouded' if total_debt < 7 else 'dangerous'
    })
```

---

## Step 4: Frontend Integration (Optional)

Add to `static/js/oracle.js`:

```javascript
// D:\Cards\Project Rememberence\static\js\oracle.js

async function consultOracle(question, animalSign, starSign) {
    const response = await fetch('/oracle/consult', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            seeker_id: 'player1',
            question: question,
            animal_sign: animalSign,
            star_sign: starSign
        })
    });
    
    const result = await response.json();
    
    // Display oracle response
    displayOracleResponse(result);
    
    // Update debt UI
    updateDebtDisplay(result.debt_level);
    
    return result;
}

function displayOracleResponse(result) {
    const oracleBox = document.getElementById('oracle-response');
    oracleBox.innerHTML = `
        <div class="oracle-roll">
            🎲 d20: ${result.roll} ${result.modifier >= 0 ? '+' : ''}${result.modifier} = 
            <strong>${result.total}</strong>
            ${result.is_crit ? '✨ CRIT!' : ''}${result.is_fail ? '💀 FAIL!' : ''}
        </div>
        <div class="oracle-text">
            ${result.response.replace(/\n/g, '<br>')}
        </div>
        <div class="oracle-debt">
            Oracle Debt: ${result.debt_level} 
            (${result.debt_level < 3 ? '🟢 Clear' : result.debt_level < 7 ? '🟡 Clouded' : '🔴 Dangerous'})
        </div>
    `;
}
```

---

## Step 5: Test the Integration

```bash
# Start Flask server
cd D:\Cards\Project Rememberence
python app/app.py

# Test oracle consultation (in another terminal)
curl -X POST http://localhost:5000/oracle/consult ^
  -H "Content-Type: application/json" ^
  -d "{\"seeker_id\": \"test1\", \"question\": \"What path should I take?\", \"animal_sign\": \"Dragon\", \"star_sign\": \"Scorpio\"}"
```

---

## Step 6: Persistence (Future)

Currently, oracle debt is in-memory. For persistence:

```python
# Save to SQLite
import sqlite3

def save_oracle_debt(seeker_id, topic, debt):
    conn = sqlite3.connect('D:/Cards/Project Rememberence/saves/oracle.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO oracle_debt (seeker_id, topic, debt, updated_at)
        VALUES (?, ?, ?, datetime('now'))
    ''', (seeker_id, topic, debt))
    conn.commit()
    conn.close()
```

---

## Troubleshooting

### Ollama Not Responding
```bash
ollama serve
# Check: curl http://localhost:11434/api/tags
```

### Flask Import Errors
```bash
# Ensure paths are correct
python -c "import sys; print(sys.path)"
```

### Oracle Responses Too Generic
- Increase context tokens (include more lore-bible.md)
- Use a larger model (e.g., `deepseek-r1:14b`)
- Refine system prompt with more examples

---

*The threads converge. The Archive opens.*
