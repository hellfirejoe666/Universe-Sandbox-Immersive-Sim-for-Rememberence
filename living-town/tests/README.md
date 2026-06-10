# Living Town Tests

## Test Suite

| File | Purpose | Speed | Layers Tested |
|------|---------|-------|---------------|
| `test_full_stack.py` | All 6 layers connected | ~3s | 1-6 |
| `test_integration.py` | NPCs ↔ Factions | ~1s | 3, 5 |
| `odysseus_integration.py` | Neural Router + NPCs | ~2s | 3, 5, Router |

## Run All Tests

```bash
cd D:\Ollama\OpenClaw\workspace\living-town
python tests\test_full_stack.py
python tests\test_integration.py
python tests\odysseus_integration.py
```

## Run Individual Layer Tests

```bash
python layers\layer1_core_rules.py
python layers\layer2_items.py
python layers\layer3_entities.py
python layers\layer4_structures.py
python layers\layer5_factions.py
python layers\layer6_worlds.py
```

## Test Principles

1. **Fast** - All tests complete in <5 seconds
2. **Minimal** - Small test data (3-5 NPCs, 2-3 factions)
3. **Isolated** - Each test can run independently
4. **Reproducible** - Same output every run (seeded random)

## DEV_MODE

For fastest iteration, ensure `simulation.py` has:
```python
DEV_MODE = True
DEV_NPC_COUNT = 5
DEV_BUILDING_COUNT = 3
```

This skips state persistence and uses minimal data.
