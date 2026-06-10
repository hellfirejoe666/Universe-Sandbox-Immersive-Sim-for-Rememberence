# AIR-AI Perchance Integration Guide

## Overview

This integration adds **Perchance.org** AI generators to the Rememberence AIR-AI Oracle system, creating a hybrid routing system that intelligently distributes AI requests between:

1. **Perchance.org** - Cloud-based random generators for names, characters, quests
2. **Local GPT4All models** - Private, offline LLM inference
3. **Ollama** - Alternative local model server
4. **Fallback templates** - Simple template-based generation when services are unavailable

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AIR-AI Oracle Interface                   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Hybrid Router                             │
│  - Request classification                                   │
│  - Provider selection                                       │
│  - Caching layer                                            │
│  - Failover handling                                        │
└───────┬──────────────────┬──────────────────┬──────────────┘
        │                  │                  │
┌───────▼───────┐  ┌──────▼───────┐  ┌───────▼───────┐
│   Perchance   │  │  GPT4All     │  │   Fallback    │
│    Router     │  │   Local      │  │   Templates   │
│               │  │              │  │               │
│ - API calls   │  │ - Inference  │  │ - Simple      │
│ - Caching     │  │ - Prompts    │  │   generation  │
│ - Rate limits │  │ - Models     │  │               │
└───────────────┘  └──────────────┘  └───────────────┘
```

## Components

### 1. `perchance_router.py`

Handles all Perchance.org API interactions.

**Features:**
- Rate limiting (10 requests/minute default)
- Response caching with TTL
- Generator type mapping
- Automatic fallback generation

**Usage:**
```python
from perchance_router import get_perchance_router

router = get_perchance_router()

# Generate a character name
result = router.generate("character_name")
print(result["result"])  # "Shadowweaver"

# Generate species-specific trait
result = router.generate("species_trait", context={"species": "Avious"})
print(result["result"])  # "Wings of wisdom carry ancient prophecies"

# Batch generation
results = router.generate_batch(["character_name", "quest_idea", "place_name"])
```

**Supported Element Types:**
- `character_name` - Fantasy character names
- `character_description` - Character descriptions
- `npc_dialogue` - NPC conversation lines
- `quest_idea` - Quest/story prompts
- `species_trait` - Rememberence species-specific traits
- `place_name` - Location names
- `item_name` - Magic item names
- `realm_description` - World/region descriptions

### 2. `hybrid_router.py`

Intelligent request routing between AI providers.

**Features:**
- Request type classification
- Provider health monitoring
- Automatic failover
- Performance metrics
- Unified caching

**Routing Rules:**

| Request Type | Preferred Provider | Fallback 1 | Fallback 2 |
|--------------|-------------------|------------|------------|
| Character Name | Perchance | GPT4All | Templates |
| Quest Generation | Perchance | GPT4All | Templates |
| Species Trait | Perchance | GPT4All | Templates |
| NPC Dialogue | Perchance | Ollama | GPT4All |
| Combat Description | GPT4All | Ollama | Templates |
| Story Iteration | GPT4All | Ollama | Templates |
| Game Master Advice | GPT4All | Ollama | Templates |

**Usage:**
```python
from hybrid_router import get_hybrid_router, RequestType

router = get_hybrid_router()

# Route a request
result = router.route_request(
    RequestType.CHARACTER_NAME,
    {"context": {"species": "Geneshan", "tone": "peaceful"}}
)

print(f"Provider: {result['provider']}")  # "perchance"
print(f"Result: {result['result']}")
print(f"Response time: {result['metadata']['response_time']}s")

# Get metrics
metrics = router.get_metrics()
print(f"Cache hits: {metrics['cache_hits']}")
print(f"Avg response time: {metrics['avg_response_time']:.3f}s")
```

### 3. `queue_manager.py` (Updated)

Enhanced to support Perchance jobs.

**Features:**
- Priority-based job processing
- Rate limit tracking per service
- Persistent queue (survives restarts)
- Automatic retry with backoff

**Usage:**
```python
from queue_manager import get_queue_manager

queue = get_queue_manager()

# Add Perchance generation job
job_id = queue.add_job(
    job_type="perchance_generate",
    service="perchance",
    params={
        "element_type": "species_trait",
        "context": {"species": "Demon"}
    },
    priority="normal",
    fallback_local=True
)

# Process queue
results = queue.process_queue()
```

## Integration with Rememberence

### Species Trait Generation

The system includes mappings for all 36 Rememberence species:

```python
from perchance_router import get_perchance_router

router = get_perchance_router()

# Generate traits for different species
species_list = ["Avious", "Merr", "Geneshan", "Demon", "Angel"]

for species in species_list:
    result = router.generate("species_trait", context={"species": species})
    print(f"{species}: {result['result']}")
```

**Example Output:**
```
Avious: Wings bearing ancient wisdom scan the horizon for omens
Merr: Siren song echoes from the abyssal depths, luring seekers to hidden truths
Geneshan: Life force pulses through ancient roots, healing all who approach
Demon: Shadow tendrils writhe with chaotic power, corrupting order itself
Angel: Divine radiance banishes darkness, guiding lost souls to redemption
```

### Game Master Mode

Use the hybrid router for dynamic GM assistance:

```python
from hybrid_router import get_hybrid_router, RequestType

router = get_hybrid_router()

# Generate quest for player session
quest = router.route_request(
    RequestType.QUEST_GENERATION,
    {"context": {"tone": "mysterious", "location": "ancient ruins"}}
)

# Generate NPC dialogue
dialogue = router.route_request(
    RequestType.NPC_DIALOGUE,
    {"context": {"character": "mysterious stranger", "mood": "urgent"}}
)

# Generate combat description
combat = router.route_request(
    RequestType.COMBAT_DESCRIPTION,
    {"context": {"attacker": "Demon", "defender": "Angel", "environment": "cathedral"}}
)
```

## Configuration

### Rate Limits

Edit `perchance_router.py` to adjust rate limits:

```python
router = PerchanceRouter(
    rate_limit_per_minute=10  # Adjust as needed
)
```

### Cache TTL

Configure cache time-to-live per element type in `GENERATOR_MAP`:

```python
"character_name": {
    "generator": "fantasy-name",
    "params": {"count": 1},
    "cache_ttl": 3600,  # 1 hour
    "category": "character"
}
```

### Provider Priority

Modify routing rules in `hybrid_router.py`:

```python
ROUTING_RULES = {
    RequestType.CHARACTER_NAME: [
        AIProvider.PERCHANCE,      # First choice
        AIProvider.GPT4ALL_LOCAL,  # Second choice
        AIProvider.FALLBACK        # Last resort
    ],
}
```

## Testing

Run the test suite:

```bash
cd "D:\cards\Project Rememberence\app"
python test_perchance_integration.py
```

**Test Coverage:**
- ✅ Perchance router direct API calls
- ✅ Hybrid router provider selection
- ✅ Queue manager integration
- ✅ Rememberence species data integration
- ✅ Caching and rate limiting
- ✅ Fallback mechanisms

## Performance

### Benchmarks (Typical)

| Operation | Perchance | GPT4All Local | Fallback |
|-----------|-----------|---------------|----------|
| Response Time | 0.5-2s | 1-5s | <0.1s |
| Cache Hit | <0.01s | <0.01s | <0.01s |
| Quality | High | Variable | Basic |

### Optimization Tips

1. **Enable caching** - Most repeated requests hit cache
2. **Batch requests** - Generate multiple elements together
3. **Use appropriate TTL** - Balance freshness vs. cache hits
4. **Monitor rate limits** - Adjust based on usage patterns

## API Reference

### PerchanceRouter

```python
class PerchanceRouter:
    def generate(element_type: str, context: Dict = None, 
                 use_cache: bool = True, fallback_local: bool = True) -> Dict
    def generate_batch(element_types: List[str], context: Dict = None) -> Dict
    def get_cache_stats() -> Dict
    def clear_cache(element_type: str = None)
```

### HybridRouter

```python
class HybridRouter:
    def route_request(request_type: RequestType, params: Dict,
                     use_cache: bool = True, timeout: float = 30.0) -> Dict
    def get_metrics() -> Dict
    def get_stats() -> Dict
    def clear_cache(request_type: RequestType = None)
```

### QueueManager

```python
class QueueManager:
    def add_job(job_type: str, service: str, params: Dict,
                priority: str = "normal", fallback_local: bool = True) -> str
    def get_job_status(job_id: str) -> Dict
    def process_queue(executor: Callable = None) -> List[Dict]
    def get_queue_status() -> Dict
```

## Troubleshooting

### Common Issues

**1. Rate Limit Errors**
```
Perchance rate limited, wait 45s
```
**Solution:** Wait for rate limit reset or enable fallback with `fallback_local=True`

**2. Cache Corruption**
```
Perchance cache corrupted, starting fresh
```
**Solution:** Delete `cache/perchance/perchance_cache.json` and restart

**3. Provider Unavailable**
```
Provider status: available=False
```
**Solution:** Check internet connection for Perchance, verify local models for GPT4All

**4. No Results Returned**
```
Perchance returned empty or invalid response
```
**Solution:** Verify generator name exists on Perchance.org

## Future Enhancements

- [ ] Custom Perchance generator creation for Rememberence-specific content
- [ ] WebSocket support for real-time generation streaming
- [ ] Advanced prompt engineering for local models
- [ ] Multi-provider parallel generation with voting
- [ ] Persistent session context for iterative storytelling
- [ ] Integration with Rememberence save/load system
- [ ] Voice synthesis integration for NPC dialogue

## Resources

- [Perchance API Tutorial](https://perchance.org/api-tutorial)
- [Perchance Generator Hub](https://perchance.org/generators)
- [Rememberence Documentation](../data/Rememberence%20(2.0%20Full).txt)
- [GPT4All Documentation](https://gpt4all.io/index.html)

---

**Status:** ✅ Integration Complete  
**Version:** 1.0  
**Last Updated:** 2026-04-24
