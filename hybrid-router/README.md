# Hybrid Router - Local AI Optimization

## What This Is

A routing layer that decides which processing path to use for each request, minimizing token usage and maximizing speed. Learns new patterns on the fly for gradual improvement.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Request                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Pattern Matcher (FAST) - Check learned + AIML patterns  │
│     └─► Match found? Return instantly (0ms, 0 tokens)       │
└─────────────────────────────────────────────────────────────┘
                            │
                    No match ─┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Router Classifier (phi3:mini) - Classify request type   │
│     └─► Returns: {"path": "fast|smart|cloud", "conf": 0.X}  │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    FAST      │  │    SMART     │  │    CLOUD     │
│  (patterns)  │  │ (qwen2.5:7b) │  │(qwen3.5:cloud│
│   0ms, 0tk   │  │  ~4s, local  │  │ rate-limited │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Models

| Model | Size | Purpose | Speed |
|-------|------|---------|-------|
| `hybrid-router` | 2.2GB | Classifies requests | ~2-5s |
| `phi3:mini` | 2.2GB | Fast responses, routing | ~2-5s |
| `qwen2.5:7b` | 4.7GB | Smart path (code, reasoning) | ~4-10s |
| `qwen3.5:cloud` | N/A | Cloud escape hatch | Varies |

## Path Definitions

### FAST Path (0ms, 0 tokens)
- Pattern-matched commands and questions
- Learned responses from previous interactions
- Alice AIML patterns (greetings, FAQs, small talk)
- **Example:** "What is your name?" → Instant response

### SMART Path (~4s, local)
- Code generation/debugging
- Creative writing
- Complex reasoning
- Ambiguous queries
- **Example:** "Write a haiku about computers" → 4.2s

### CLOUD Path (varies, rate-limited)
- Specialized knowledge beyond local models
- Explicitly requested by user
- Extremely complex analysis
- **Example:** "Analyze this 50-page legal document"

## Usage

```bash
# Route a request (auto-decides path)
python router.py "What time is it there"

# Force a specific path
python router.py "Write code for X" --force smart

# Learn a new pattern (persists across sessions)
python router.py --learn "WHAT IS X" "X is..."

# View statistics
python router.py --stats

# Interactive mode
python router.py --interactive
```

### Interactive Mode Commands
- `/stats` - Show routing statistics
- `/learn <pattern> <response>` - Learn a new pattern
- `/quit` - Exit

## Performance (Tested on this hardware)

| Hardware | Value |
|----------|-------|
| RAM | 16GB (8GB free) |
| CPU | Intel (no GPU) |
| Inference | CPU-only |

**Results:**
- FAST path: 0ms (pattern match)
- SMART path: ~4s (qwen2.5:7b, 4.7GB)
- Router overhead: ~2-3s (phi3:mini classification)

**Target distribution:** 80% FAST, 15% SMART, 5% CLOUD

## Files

| File | Purpose |
|------|---------|
| `router.py` | Main router script |
| `Modelfile` | Custom phi3:mini router model |
| `learned_patterns.json` | Persisted learned patterns |
| `response_cache.json` | LLM response cache |
| `README.md` | This file |

## Integration with Rememberence

The router architecture shares DNA with the FFT + RMC pipeline from `rememberence_bridge.py`:

- **FFT** → Decomposes tasks into frequency components (simple vs. complex)
- **RMC** → Recursive confidence scoring for routing decisions
- **State machine** → Pattern matching with wildcard state transitions

Future: Integrate FFT symbolic analysis for novel task classification.

## Next Steps

- [ ] Integrate with OpenClaw tool routing
- [ ] Add FFT-based novelty detection
- [ ] Profile real session patterns (what % is actually FAST?)
- [ ] Build PowerShell wrapper for OpenClaw integration
- [ ] Add response streaming for SMART/CLOUD paths
