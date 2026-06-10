# Neural Router - Brain-Inspired Architecture

**A cognitive architecture for intelligent request routing**

---

## 🧠 Overview

This is not just a router — it's a **simulated brain** for AI request processing. Each subsystem mirrors a brain structure with specialized functions.

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXECUTIVE (Prefrontal Cortex)                │
│  • Strategic planning                                           │
│  • Metacognition ("how am I doing?")                            │
│  • Resource allocation                                          │
│  • Session type inference                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AROUSAL (Reticular System)                   │
│  • System load monitoring                                       │
│  • Adaptive resource allocation                                 │
│  • Alert level adjustment                                       │
│  • Sleep/wake cycles                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ATTENTION (Thalamus)                         │
│  • Context filtering                                            │
│  • Signal amplification                                         │
│  • Relevance gating                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   MEMORY        │  │   LANGUAGE      │  │   REASONING     │
│   (Hippocampus) │  │   (llama3.2)    │  │   (Cloud)       │
│                 │  │                 │  │                 │
│   + HABITS      │  │   + Donjon      │  │   (Novel/       │
│   (Basal Gang.) │  │   + Procedural  │  │    Complex)     │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SALIENCE (Amygdala)                          │
│  • Priority override                                            │
│  • Urgency detection                                            │
│  • Safety checks                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QUALITY (Cerebellum)                         │
│  • Output prediction                                            │
│  • Error correction                                             │
│  • Coherence checking                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DEFAULT MODE (Idle Learning)                 │
│  • Memory consolidation                                         │
│  • Performance reflection                                       │
│  • Self-improvement generation                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Subsystem Files

| File | Brain Region | Function |
|------|--------------|----------|
| `executive.py` | Prefrontal Cortex | Strategy, planning, metacognition |
| `arousal.py` | Reticular System | Load monitoring, resource allocation |
| `attention.py` | Thalamus | Context filtering, relevance gating |
| `memory.py` | Hippocampus | Episodic memory, contextual retrieval |
| `habits.py` | Basal Ganglia | Habit learning, reward-based routing |
| `language.py` | Language Centers | llama3.2 + Donjon procedural generation |
| `reasoning.py` | Prefrontal/Cloud | Complex reasoning, novel queries |
| `salience.py` | Amygdala | Urgency detection, priority override |
| `quality.py` | Cerebellum | Output prediction, error correction |
| `default_mode.py` | Default Mode Network | Idle learning, consolidation |

---

## 🔄 Request Flow

1. **Executive** receives request, sets strategic context
2. **Arousal** checks system load, adjusts resource budget
3. **Attention** filters context, amplifies relevant signals
4. **Memory/Habits** check if this is familiar (FAST path)
5. **Language** handles semi-familiar (SMART path)
6. **Reasoning** handles novel/complex (CLOUD path)
7. **Salience** can override routing for urgent/priority items
8. **Quality** validates output before sending
9. **Response** delivered to user
10. **Default Mode** processes during idle time

---

## 📊 State Files

| File | Purpose |
|------|---------|
| `state/executive_state.json` | Strategic context, session type |
| `state/arousal_state.json` | Load levels, resource quotas |
| `state/memory_index.json` | Episodic memory index |
| `state/habit_weights.json` | Learned routing preferences |
| `state/quality_metrics.json` | Output quality history |

---

## 🚀 Quick Start

```python
from brain.neural_router import NeuralRouter

router = NeuralRouter()

# Route a request
response = router.route(
    query="Write a function to sort a list",
    context={"user_state": "coding", "session_type": "development"}
)

print(response)
```

---

## 🎯 Design Principles

1. **Parallel Processing** - Multiple subsystems work simultaneously
2. **Graceful Degradation** - If one subsystem fails, others compensate
3. **Continuous Learning** - Gets smarter with every interaction
4. **Quality Gates** - Bad outputs caught before user sees them
5. **Idle Improvement** - Learns during downtime, not just during queries

---

*The brain is the ultimate routing system. Let's build one.*
