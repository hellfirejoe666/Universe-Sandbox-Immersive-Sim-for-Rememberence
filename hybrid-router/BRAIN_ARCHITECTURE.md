# Hybrid Router as a Brain-Inspired Architecture

**Inspired by:** Human cognitive architecture  
**Goal:** Efficient, specialized processing for different query types

---

## The Brain Analogy

```
┌─────────────────────────────────────────────────────────────────┐
│                    HYBRID ROUTER (The Brain)                     │
│                                                                  │
│  ┌─────────────────┐                                            │
│  │  PREFRONTAL     │ ← FFT Novelty Detection                    │
│  │  CORTEX         │   "How novel/complex is this?"             │
│  │  (Decision)     │   Novelty score: 0.0-1.0                   │
│  └────────┬────────┘                                            │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              ANTERIOR CINGULATE CORTEX                   │   │
│  │              (Routing Decision Matrix)                   │   │
│  │                                                          │   │
│  │  if novelty < 0.35 → FAST PATH (habit/pattern)          │   │
│  │  if 0.35-0.85 → LOCALGEN (language/speech)              │   │
│  │  if 0.85-0.90 → SMART (local reasoning)                 │   │
│  │  if > 0.90 → CLOUD (complex abstract reasoning)         │   │
│  └─────────────────────────────────────────────────────────┘   │
│           │                                                      │
│           ├──────────────┬──────────────┬──────────────┐       │
│           ▼              ▼              ▼              ▼       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐ │
│  │ FAST PATH   │ │ LOCALGEN    │ │ SMART PATH  │ │ CLOUD    │ │
│  │ (Basal      │ │ (Speech     │ │ (Local      │ │ (Complex │ │ │
│  │  Ganglia)   │ │  Center)    │ │  Cortex)    │ │  Reason) │ │
│  │             │ │             │ │             │ │          │ │
│  │ • Patterns  │ │ • Language  │ │ • Reasoning │ │ • Abstract│ │
│  │ • Habits    │ │ • Speech    │ │ • Analysis  │ │ • Novel  │ │
│  │ • Cached    │ │ • Simple    │ │ • Problem   │ │ • Complex│ │
│  │             │ │ • Creative  │ │ • Math      │ │ • Deep   │ │
│  │ 0 tokens    │ │ 0* tokens   │ │ ~150 tokens │ │ ~500     │ │
│  │ <1ms        │ │ 10-30s      │ │ 5-30s       │ │ 10-60s   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘ │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              HIPPOCAMPUS (Memory System)                │   │
│  │                                                          │   │
│  │  • Semantic Cache (fuzzy match past responses)          │   │
│  │  • Pattern Learning (AIML-style patterns)               │   │
│  │  • Response Caching (store successful outputs)          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              CEREBELLUM (Optimization)                  │   │
│  │                                                          │   │
│  │  • Token Optimization (compression)                     │   │
│  │  • Confidence Calibration (RMC meta-cognition)          │   │
│  │  • Learning from feedback                               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Specialized Centers

### 1. FAST Path (Basal Ganglia - Habits/Patterns)

**What it handles:**
- Greetings ("Hello", "Good morning")
- Status checks ("Gateway status", "Are you running?")
- Common commands ("Help", "What can you do?")
- Learned patterns (from experience)

**Characteristics:**
- Instant (<1ms)
- 0 tokens
- No thinking required
- Muscle memory / reflex

**Example:**
```
User: "What time is it?"
→ Pattern match: "WHAT TIME IS IT"
→ Response: "IT IS {time}"
→ 0 tokens, 0ms
```

---

### 2. LOCALGEN (Speech/Language Center - Broca's/Wernicke's Area)

**What it handles:**
- Simple explanations
- Brainstorming ideas
- Creative writing
- Conversational chat
- Name/story generation
- Descriptions

**Characteristics:**
- Fast (10-30s)
- 0 counted tokens (local LLM)
- Language production
- "Automatic speech"

**Example:**
```
User: "Explain what a hybrid router is"
→ LocalGen (ai-character-chat)
→ Response: "A hybrid router is like a traffic director..."
→ Local tokens (unlimited), ~15s
```

**Why it's like the speech center:**
- Produces fluent language automatically
- Doesn't require deep reasoning
- Handles most日常 conversation
- Can run continuously without "fatigue" (token limits)

---

### 3. SMART Path (Local Cortex - Reasoning/Analysis)

**What it handles:**
- Math problems
- Code debugging
- Logical analysis
- Multi-step reasoning
- Local problem-solving

**Characteristics:**
- Moderate speed (5-30s)
- ~150 tokens (local, no limits)
- Active reasoning
- Working memory engaged

**Example:**
```
User: "Why is my Python loop not working?"
→ SMART path (qwen2.5:7b)
→ Analyzes code, finds bug, explains fix
→ ~150 local tokens
```

---

### 4. CLOUD Path (Prefrontal Cortex - Complex Abstract Reasoning)

**What it handles:**
- Highly novel queries (>0.90 novelty)
- Complex multi-domain synthesis
- Advanced abstract reasoning
- Edge cases requiring best model

**Characteristics:**
- Slow (10-60s)
- ~500 tokens (counted, rate-limited)
- Deep thinking
- Last resort

**Example:**
```
User: "Design a new programming language that combines 
       functional programming with quantum computing principles"
→ CLOUD path (qwen3.5:cloud)
→ Novel, complex, requires best reasoning
→ ~500 tokens (counted)
```

---

## Memory Systems

### Hippocampus (Semantic Cache + Pattern Learning)

**Functions:**
- Stores recent experiences (semantic cache)
- Learns patterns from repetition (AIML-style)
- Consolidates frequent responses into habits

**Process:**
```
1st time: "What is OpenClaw?" → SMART path → ~150 tokens
2nd time: "What is OpenClaw?" → Cache hit → 0 tokens
10th time: "What is OpenClaw?" → Learned pattern → FAST path
```

---

### Cerebellum (Optimization + Meta-Cognition)

**Functions:**
- Compresses queries (removes filler words)
- Monitors confidence (RMC layer)
- Adjusts routing thresholds over time
- Learns from feedback

**Example:**
```
Original: "Can you please help me understand what OpenClaw is?"
Compressed: "What is OpenClaw?"
Savings: ~8 tokens, faster processing
```

---

## Routing Decision Matrix (Anterior Cingulate)

The ACC monitors conflict and makes routing decisions:

```python
def route_query(query, novelty, confidence):
    # Novelty from FFT (spectral analysis)
    # Confidence from LLM classifier + RMC adjustment
    
    if novelty < 0.35 and confidence > 0.7:
        return "FAST"  # Habit/pattern
    
    elif 0.35 <= novelty < 0.85:
        return "LOCALGEN"  # Language/speech (unlimited!)
    
    elif 0.85 <= novelty < 0.90:
        return "SMART"  # Local reasoning
    
    else:  # novelty >= 0.90
        return "CLOUD"  # Complex abstract reasoning
```

---

## Token Economics (Energy Metabolism)

Just as the brain allocates glucose efficiently:

| Path | Token Cost | Energy Analogy |
|------|------------|----------------|
| FAST | 0 tokens | ATP from stored creatine (instant) |
| LOCALGEN | 0 counted (local) | Aerobic metabolism (sustainable) |
| SMART | ~150 local | Glycogen stores (plenty available) |
| CLOUD | ~500 counted | Adrenaline spike (expensive, rare) |

**Brain efficiency:** 20W power, handles everything  
**Hybrid router goal:** Minimize "cloud glucose" usage

**Current distribution:**
- FAST: 50-60% (goal: 70-80%)
- LOCALGEN: 20-30% (new! replaces cloud for language)
- SMART: 15-25% (goal: 15-20%)
- CLOUD: <5% (goal: <3%)

---

## RMC Meta-Cognition (Metacognitive Monitoring)

The brain knows when it's uncertain. RMC layer adds:

1. **Confidence Calibration**
   - "I'm 85% confident this is a FAST path query"
   - Adjusts based on past accuracy

2. **Explainable Routing**
   - "Chose LOCALGEN because: creative (0.72 novelty), conversational"
   - Transparent decision-making

3. **Feedback Learning**
   - User satisfied? → Reinforce this path
   - User re-asked? → Adjust thresholds

4. **Cognitive Load Monitoring**
   - Track token usage per path
   - Detect when cloud usage spikes
   - Auto-adjust thresholds to compensate

---

## Why This Analogy Matters

### 1. **Efficiency Through Specialization**

Just as the brain doesn't use prefrontal cortex for breathing:
- Don't use CLOUD for greetings (use FAST)
- Don't use SMART for simple chat (use LOCALGEN)
- Reserve CLOUD for truly novel/complex tasks

### 2. **Unlimited "Speech" via LOCALGEN**

The speech center can run continuously:
- You don't "run out of words" talking
- LocalGen doesn't burn cloud tokens
- Perfect for brainstorming, explanations, chat

### 3. **Learning Creates Efficiency**

Brain: Repeated tasks become habits (basal ganglia)  
Router: Repeated queries become patterns (FAST path)

```
Novel query → CLOUD (thinking hard)
    ↓ (repeated)
Familiar query → SMART (reasoning)
    ↓ (repeated)
Habitual query → FAST (pattern match, automatic)
```

### 4. **Meta-Cognition Prevents Waste**

Brain: "I don't know" saves energy vs. guessing  
Router: Route to CLOUD only when confident it's needed

---

## Implementation Priorities

### ✅ Phase 1: Basic Architecture (DONE)
- FAST path (patterns, cache)
- LOCALGEN (speech center)
- SMART path (local reasoning)
- CLOUD path (escape hatch)
- FFT novelty detection

### ⏳ Phase 2: RMC Meta-Cognition (NEXT)
- Confidence calibration
- Explainable routing
- Decision history
- Feedback learning

### ⏳ Phase 3: Optimization
- Query compression (cerebellum)
- Adaptive thresholds
- Pattern auto-learning
- Token accounting dashboard

---

## LocalGen Optimization for "Speech Center"

To make LocalGen better at simple language tasks:

### Add These Generators:

1. **Simple Explainer**
   ```python
   def explain_concept(concept: str) -> str:
       # Use phi3:mini for fast, simple explanations
       prompt = f"Explain {concept} in 2-3 simple sentences."
   ```

2. **Brainstorming**
   ```python
   def brainstorm(topic: str, count: int = 5) -> List[str]:
       # Generate N ideas quickly
       prompt = f"Give me {count} ideas about {topic}."
   ```

3. **Rephrasing**
   ```python
   def rephrase_simple(text: str) -> str:
       # Make complex text simpler
       prompt = f"Say this more simply: {text}"
   ```

4. **Summarization**
   ```python
   def summarize(text: str) -> str:
       # Quick summary in 1-2 sentences
       prompt = f"Summarize in 2 sentences: {text}"
   ```

### Use Smaller Model for Speed:

```python
# For simple language tasks, use phi3:mini instead of qwen2.5:7b
MODEL = "phi3:mini"  # Faster, fewer tokens, good for simple text
```

---

## Summary

The hybrid router is a **brain-inspired cognitive architecture**:

- **FAST** = Basal ganglia (habits/patterns)
- **LOCALGEN** = Speech center (language production, unlimited)
- **SMART** = Local cortex (reasoning/analysis)
- **CLOUD** = Prefrontal cortex (complex abstract thought)
- **Cache/Learning** = Hippocampus (memory consolidation)
- **Optimization** = Cerebellum (fine-tuning)
- **RMC** = Metacognitive monitoring (knowing what you know)

**Result:** Human-like efficiency with unlimited "speech" via LocalGen, reserving expensive cloud tokens for truly novel/complex reasoning.

---

*"The brain doesn't think about breathing. Neither should the router think about greetings."*
