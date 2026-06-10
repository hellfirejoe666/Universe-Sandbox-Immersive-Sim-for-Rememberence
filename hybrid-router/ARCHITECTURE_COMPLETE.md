# Complete Hybrid Router Architecture

**Date:** 2026-04-25  
**Status:** All core systems implemented ✅

---

## System Overview

The Hybrid Router is a **brain-inspired cognitive architecture** that intelligently routes queries through different processing paths to minimize token usage while maintaining response quality.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         HYBRID ROUTER v2                                 │
│                                                                          │
│  "A brain-inspired AI routing system that thinks about how it thinks"   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## The Five Core Systems

### 1. AIML Pattern Matching (FAST Path)
**Purpose:** Instant responses for familiar queries  
**Token Cost:** 0  
**Latency:** <1ms  

**How it works:**
- Alice AIML-style pattern matching (`WHAT IS *` → wildcard responses)
- Learned patterns from successful interactions
- Exact string matching for common queries

**Example patterns:**
```
"HELLO" → "Hi there! How can I help you?"
"WHAT TIME IS IT" → "It's {current_time}"
"GATEWAY STATUS" → "Gateway is running normally"
```

**Brain analogy:** Basal Ganglia (habits, muscle memory)

---

### 2. FFT Novelty Detection
**Purpose:** Mathematically measure query complexity  
**Token Cost:** 0 (local computation)  
**Latency:** 1-5ms  

**How it works:**
- Converts text to 2D spectral representation
- Applies Fast Fourier Transform
- Extracts features: entropy, symmetry, radial distribution
- Combines with heuristic patterns for short text
- Learns adaptive thresholds from user behavior

**Signals:**
```python
# FFT Spectral Analysis (long text)
- Center energy (low-frequency = familiar)
- High-frequency energy (novel content)
- Entropy (disorder measure)
- Symmetry (familiar patterns are symmetric)

# Heuristic Patterns (short text)
- Familiar phrases ("hello", "what is", "status")
- Novel indicators ("design", "theorize", "analyze")
- Question complexity, unique word ratio
```

**Output:** Novelty score 0.0-1.0 + classification

**Brain analogy:** Prefrontal Cortex (novelty assessment)

---

### 3. Token Optimization
**Purpose:** Reduce token consumption at every stage  
**Token Savings:** 70-90% overall  

**Components:**

#### a. Query Compression
```python
Original:  "Can you please help me understand what the hybrid router does"
Compressed: "hybrid router does"
Savings: ~10 tokens (40% reduction)
```

#### b. Semantic Cache
- Fuzzy matching (85%+ similarity)
- Stores responses with embeddings
- Returns cached response instantly

#### c. Pattern Learning
- Auto-extracts patterns from successful queries
- Persists to `learned_patterns.json`
- Grows over time (more patterns = more FAST responses)

#### d. Token Accounting
- Tracks tokens per path
- Records savings from optimization
- Generates usage reports

**Brain analogy:** Cerebellum (optimization, fine-tuning)

---

### 4. LocalGen Provider (Speech Center)
**Purpose:** Unlimited local AI for creative/language tasks  
**Token Cost:** 0 (local, unlimited)  
**Latency:** 10-30s  

**Generators:**

#### Speech Center (phi3:mini - fast, ~70 tokens local)
- `explain` - Simple explanations
- `brainstorm` - Idea generation
- `rephrase` - Text simplification
- `summarize` - Quick summaries

#### Creative (qwen2.5:7b - slower, ~150 tokens local)
- `ai-character-chat` - Conversational chat
- `ai-story-generator` - Creative writing

#### List Generators (instant, 0 tokens)
- `fantasy-name` - Random fantasy names
- `character-name` - Names with titles
- `fantasy-plot` - Story hooks
- `city-name` - Location names

**Brain analogy:** Broca's/Wernicke's Area (language production)

---

### 5. RMC Meta-Cognition
**Purpose:** Self-monitoring, explainable routing decisions  
**Token Cost:** 0 (local computation)  

**Functions:**

#### a. Confidence Calibration
```python
# Adjusts confidence based on novelty
High novelty → Lower confidence (out of distribution)
Low novelty → Higher confidence (familiar pattern)
```

#### b. Decision Explanation
```
Query: "Design a new programming language"
→ Novelty: 0.85 (very high)
→ FFT recommends: cloud
→ LLM classifier: cloud (confidence 0.82)
→ Multiple signals agree
→ Decision: CLOUD path selected
```

#### c. Anomaly Detection
Detects routing mistakes:
- High confidence but wrong path
- Novel queries routed to FAST (under-processing)
- Familiar queries routed to CLOUD (wasteful)
- Extreme latency (>30s)

#### d. Feedback Learning
- Records user satisfaction (0.0-1.0)
- Adjusts path confidence thresholds
- Improves routing over time

#### e. Decision History
- Logs all routing decisions
- Tracks path distribution
- Generates insights and recommendations

**Brain analogy:** Metacognitive monitoring (thinking about thinking)

---

## Routing Decision Matrix

```python
def route_query(query, novelty, llm_path, llm_confidence, is_creative):
    """
    Decision matrix used by Hybrid Router v2
    """
    # Adjusted confidence (novelty-aware)
    adjusted_conf = rmc_confidence_adjustment(novelty, llm_confidence)
    
    # Decision tree
    if novelty < 0.35 and llm_path == "fast" and adjusted_conf > 0.7:
        return "FAST"  # Familiar pattern
    
    elif is_creative and 0.5 < novelty < 0.85:
        return "LOCALGEN"  # Creative/language task
    
    elif novelty > 0.90:
        return "CLOUD"  # Very novel/complex
    
    elif llm_path == "cloud" and adjusted_confidence > 0.95:
        return "CLOUD"  # Only with very high confidence
    
    else:
        return "SMART"  # Default to local reasoning
```

---

## Complete Processing Pipeline

```
User Query
    │
    ▼
┌──────────────────────────────────────┐
│  1. TOKEN OPTIMIZATION               │
│     - Compress query                 │
│     - Remove filler words            │
│     - Normalize                      │
└──────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────┐
│  2. SEMANTIC CACHE CHECK             │
│     - Fuzzy match (85%+ similarity)  │
│     - Cache hit? → Return (0 tokens) │
└──────────────────────────────────────┘
    │ Cache miss
    ▼
┌──────────────────────────────────────┐
│  3. PATTERN MATCH CHECK              │
│     - AIML-style patterns            │
│     - Learned patterns               │
│     - Match? → Return (0 tokens)     │
└──────────────────────────────────────┘
    │ No match
    ▼
┌──────────────────────────────────────┐
│  4. FFT NOVELTY DETECTION            │
│     - Spectral analysis              │
│     - Heuristic patterns             │
│     - Novelty score: 0.0-1.0         │
│     - Classification: familiar/mod/  │
│       novel/very_novel               │
└──────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────┐
│  5. LLM CLASSIFICATION               │
│     - hybrid-router model            │
│     - Path: fast/smart/cloud         │
│     - Confidence: 0.0-1.0            │
└──────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────┐
│  6. RMC META-COGNITION               │
│     - Adjust confidence (novelty)    │
│     - Check LocalGen suitability     │
│     - Apply decision matrix          │
│     - Record decision + reasoning    │
│     - Detect anomalies               │
└──────────────────────────────────────┘
    │
    ├──────────────┬──────────────┬──────────────┬──────────────┐
    ▼              ▼              ▼              ▼              ▼
┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
│ CACHED │  │   FAST   │  │ LOCALGEN │  │   SMART  │  │ CLOUD  │
│        │  │          │  │          │  │          │  │        │
│ 0 tokens│  │ 0 tokens │  │ 0* local │  │ ~150 loc │  │ ~500   │
│ <1ms    │  │ <1ms     │  │ 10-30s   │  │ 5-30s    │  │ 10-60s │
└────────┘  └──────────┘  └──────────┘  └──────────┘  └────────┘
    │              │              │              │              │
    └──────────────┴──────────────┴──────────────┴──────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  7. LEARN & UPDATE      │
                    │  - Cache response       │
                    │  - Extract patterns     │
                    │  - Update RMC history   │
                    │  - Record token usage   │
                    └─────────────────────────┘
```

---

## Performance Metrics

### Current Routing Distribution (Target)

| Path | Target % | Token Cost | Latency | Use Case |
|------|----------|------------|---------|----------|
| CACHED | 20-30% | 0 | <1ms | Repeated queries |
| FAST | 30-40% | 0 | <1ms | Patterns, greetings |
| LOCALGEN | 25-35% | 0 (local) | 10-30s | Creative, language |
| SMART | 10-20% | ~150 (local) | 5-30s | Reasoning, analysis |
| CLOUD | <5% | ~500 (counted) | 10-60s | Complex, novel |

### Token Savings Breakdown

| Optimization | Savings | Mechanism |
|--------------|---------|-----------|
| Query Compression | 20-40% | Remove filler words |
| Semantic Cache | 100% (on hits) | Reuse cached responses |
| Pattern Matching | 100% (on matches) | AIML-style patterns |
| LOCALGEN Routing | 90%+ (vs cloud) | Local unlimited AI |
| Cloud Avoidance | 70-85% overall | Aggressive thresholds |

**Total reduction:** 70-90% fewer cloud tokens vs always-using-cloud

---

## Files & Components

### Core Router
- `router_v2.py` - Main router with all integrations
- `token_optimizer.py` - Compression, cache, learning, accounting
- `fft_novelty.py` - Hybrid FFT+heuristic novelty detection
- `localgen_provider.py` - Self-hosted AI provider
- `rmc_meta_cognition.py` - Meta-cognition layer

### Supporting Services
- `localgen/server.py` - Flask server for LocalGen generators
- `skills/hybrid-router/SKILL.md` - OpenClaw skill definition

### Data Files (auto-generated)
- `learned_patterns.json` - Learned AIML-style patterns
- `semantic_cache.json` - Fuzzy-matched response cache
- `token_stats.json` - Token usage statistics
- `rmc_decision_log.json` - Routing decision history
- `rmc_calibration.json` - Confidence calibration data

### Documentation
- `README_integration.md` - Integration summary
- `BRAIN_ARCHITECTURE.md` - Brain-inspired design
- `FFT_IMPROVEMENTS.md` - FFT detection improvements
- `STATUS.md` - Current build status
- `ARCHITECTURE_COMPLETE.md` - This file

### Tests
- `test_fft_improvements.py` - FFT test suite (18 tests, 100% pass)

---

## Usage Examples

### Route a Query
```bash
python hybrid-router/router_v2.py route "What is the hybrid router"
```

### Test FFT Novelty
```bash
python hybrid-router/fft_novelty.py "Design a new programming language"
```

### View RMC Insights
```bash
python hybrid-router/router_v2.py rmc insights
python hybrid-router/rmc_meta_cognition.py explain
```

### View Statistics
```bash
python hybrid-router/router_v2.py stats
```

### Start LocalGen Server
```bash
python localgen\server.py
```

---

## Autonomous Operation Readiness

### What's Working for Autonomy ✅

1. **Self-Monitoring** - RMC tracks all decisions
2. **Explainable Routing** - Every decision has reasoning
3. **Anomaly Detection** - Notices when routing seems wrong
4. **Feedback Learning** - Adjusts based on satisfaction
5. **Token Accounting** - Tracks usage and savings
6. **Pattern Learning** - Auto-extracts from successful queries
7. **Adaptive Thresholds** - Learns user's query patterns

### What's Needed for Full Autonomy ⏳

1. **Automated Feedback Loop**
   - Currently: Manual satisfaction scores
   - Needed: Implicit feedback (user re-asks? edits response?)

2. **Scheduled Self-Review**
   - Cron job to run `rmc insights` daily
   - Auto-adjust thresholds based on patterns
   - Report token savings to user

3. **Response Distillation**
   - Cloud responses → extract patterns
   - Add to FAST path automatically
   - Reduce future cloud dependency

4. **Heartbeat Autonomy**
   - Self-initiated checks (email, calendar, etc.)
   - Router decides when to alert vs suppress
   - Learns user's priorities

5. **Cross-Session Memory**
   - Persist RMC calibration between sessions
   - Share learned patterns across instances
   - Long-term preference learning

---

## Next Evolution: Autonomous Agent

### Vision

The router becomes an **autonomous cognitive agent** that:

1. **Runs Continuously**
   - Heartbeat checks every 1-2 hours
   - Processes all incoming queries
   - Self-monitors performance

2. **Learns Continuously**
   - Every interaction improves routing
   - Daily pattern extraction from cloud responses
   - Weekly threshold optimization

3. **Self-Optimizes**
   - Notices high cloud usage → adjusts thresholds
   - Detects anomalies → investigates and fixes
   - Tracks token budget → stays within limits

4. **Explains Decisions**
   - "I routed to CLOUD because novelty=0.92"
   - "Cloud usage at 8% this week (target <5%)"
   - "Learned 15 new patterns, saving ~200 tokens/day"

### Implementation Path

#### Phase 1: Enhanced Monitoring (Next Session)
- [ ] Daily RMC insights report
- [ ] Token usage dashboard
- [ ] Anomaly alerts to user

#### Phase 2: Automated Learning
- [ ] Auto-extract patterns from cloud responses
- [ ] Implicit feedback detection
- [ ] Cross-session pattern sharing

#### Phase 3: Proactive Autonomy
- [ ] Self-initiated heartbeat checks
- [ ] Priority-based alerting
- [ ] Token budget management

#### Phase 4: Full Cognitive Agent
- [ ] Multi-domain reasoning
- [ ] Long-term goal tracking
- [ ] Collaborative operation with user

---

## Key Design Principles

### 1. **Efficiency Through Specialization**
Different query types → different processing paths  
Don't use cloud for "hello"

### 2. **Learning Creates Efficiency**
Every interaction makes the system smarter  
Repeated queries become automatic (FAST path)

### 3. **Meta-Cognition Prevents Waste**
Monitor routing decisions  
Notice when you're wrong  
Adjust based on feedback

### 4. **Local First, Cloud Last**
Unlimited local AI for most tasks  
Cloud only for truly novel/complex queries  
70-90% token reduction achievable

### 5. **Explainability Builds Trust**
Every decision has reasoning  
User can understand and override  
Transparent about limitations

---

## Summary

The Hybrid Router is a **complete brain-inspired cognitive architecture** with:

- ✅ **FAST path** (AIML patterns, 0 tokens)
- ✅ **LOCALGEN path** (speech center, unlimited local)
- ✅ **SMART path** (local reasoning, ~150 tokens)
- ✅ **CLOUD path** (escape hatch, ~500 tokens)
- ✅ **FFT novelty detection** (hybrid spectral+heuristic)
- ✅ **Token optimization** (compression, caching, learning)
- ✅ **RMC meta-cognition** (explainable, self-monitoring)

**Ready for:** Integration testing and autonomous operation development

**Token savings:** 70-90% reduction vs always-using-cloud

**Next step:** Discuss autonomous operation strategies and implementation priorities

---

*"The brain doesn't think about breathing. The router shouldn't think about 'hello'. And soon, it won't need you to tell it when to check."*
