# Phase 1 Audit - Rememberence Data Integration

**Date:** 2026-05-31  
**Status:** ✅ Data Complete | 🔧 Bridge Integration Needed

---

## 📦 Available Data Files

| File | Size | Status | Contents |
|------|------|--------|----------|
| `animal_signs.json` | 14 KB | ✅ Complete | 12 Zodiac Animals with biorhythms, species affinities, elements |
| `star_signs.json` | 13 KB | ✅ Complete | 12 Star Signs with biorhythms, type affinities, colors |
| `species.json` | 113 KB | ✅ Complete | 36 Species with full stats, traits (active/passive), lore |
| `types.json` | 69 KB | ✅ Complete | 24 Types with stat modifiers, traits, materia |
| `classes.json` | 18 KB | ✅ Complete | 6 Classes × 6 skills each (36 total) with bonuses/patterns |
| `runes.json` | 11 KB | ✅ Complete | 77 Runes with effects, VoKai cypher |
| `narrative_verses.json` | 9 KB | ✅ Complete | Narrative Matrix verse mappings |

**Total:** 248 KB of structured game data — **ready for integration**

---

## ✅ What's Already Built

### Data Layer (100% Complete)
- All core entities in JSON format
- Consistent structure across files
- Biorhythm values for all signs
- Trait systems (active/passive) for species and types
- Class skill trees with combat patterns
- Rune effect definitions

### Documentation
- `Rememberence (2.0 Full).txt` — Complete rules (341 KB)
- `Rememberence (Story).txt` — Story chronicles (436 KB)

---

## 🔧 What Needs Integration

### 1. Bridge Module Updates (`rememberence_bridge.py`)

| Function | Status | Action Needed |
|----------|--------|---------------|
| `calculate_biorhythms(animal, star)` | ✅ Exists | Update to load from JSON files |
| `calculate_stats(biorhythms, species, type)` | ✅ Exists | Add type stat_modifiers from JSON |
| `generate_thoughts(biorhythms)` | ✅ Exists | Verify against narrative_verses.json |
| `BattleBoard` class | ✅ Exists | Test with full entity data |
| `apply_loyalty_rank()` / `decay_loyalty()` | ✅ Exists | No changes needed |
| `generate_spirit_comment()` | ✅ Exists | Enhance with species/type lore |

### 2. Missing Bridge Functions

| Function | Purpose | Priority |
|----------|---------|----------|
| `load_all_data()` | Load all JSON files into unified data dict | 🔴 High |
| `get_species_traits(species_key)` | Return active/passive traits | 🔴 High |
| `get_type_modifiers(type_key)` | Return stat_modifiers from types.json | 🔴 High |
| `get_class_skill(class, skill_num)` | Return skill bonuses/pattern | 🔴 High |
| `get_rune_effect(rune_key)` | Return rune effect description | 🟠 Medium |
| `calculate_combat_stats(entity)` | Full stat calc with all modifiers | 🔴 High |
| `validate_character_build(choices)` | Verify species/type/class compatibility | 🟠 Medium |

### 3. Data Validation Needed

| Check | Method |
|-------|--------|
| All 36 species have valid stats (HP/ATK/DEF/SPD/MP) | Schema validation |
| All 24 types have stat_modifiers for all 5 combat stats | Schema validation |
| All 36 class skills have valid patterns | Schema validation |
| Biorhythm sums are consistent across signs | Mathematical check |
| Species affinities match actual species keys | Cross-reference |
| Type affinities match actual type keys | Cross-reference |

---

## 🎯 Phase 1 Deliverables

### 1. Unified Data Loader
```python
class RememberenceData:
    def __init__(self, data_dir):
        self.animal_signs = load_json('animal_signs.json')
        self.star_signs = load_json('star_signs.json')
        self.species = load_json('species.json')
        self.types = load_json('types.json')
        self.classes = load_json('classes.json')
        self.runes = load_json('runes.json')
        self.narrative_verses = load_json('narrative_verses.json')
    
    def get_animal(self, key): return self.animal_signs['animalSigns'][key]
    def get_star(self, key): return self.star_signs['starSigns'][key]
    def get_species(self, key): return self.species['species'][key]
    def get_type(self, key): return self.types['types'][key]
    def get_class(self, key): return self.classes['classes'][key]
    def get_rune(self, key): return self.runes['runes'][key]
```

### 2. Enhanced Entity Class
```python
class Entity:
    def __init__(self, name, animal, star, species, type_, classes, tier='NoviceI'):
        self.name = name
        self.animal = data.get_animal(animal)
        self.star = data.get_star(star)
        self.species = data.get_species(species)
        self.type = data.get_type(type_)
        self.classes = {cat: data.get_class(cat)['skills'][num-1] 
                       for cat, num in classes.items()}
        
        # Calculate from data
        self.biorhythms = calculate_biorhythms(self.animal, self.star)
        self.combat = calculate_combat_stats(self.biorhythms, self.species, self.type, self.classes)
        self.thoughts = generate_thoughts(self.biorhythms)
        self.traits = {
            'species_active': self.species['traits']['active'],
            'species_passive': self.species['traits']['passive'],
            'type_active': self.type['traits']['active'],
            'type_passive': self.type['traits']['passive']
        }
```

### 3. Character Creation API
```python
def create_character(choices):
    # Validate choices
    errors = validate_character_build(choices)
    if errors: return {'error': errors}
    
    # Build entity
    entity = Entity(
        name=choices['name'],
        animal=choices['animal'],
        star=choices['star'],
        species=choices['species'],
        type_=choices['type'],
        classes=choices['classes']
    )
    
    return {
        'character_sheet': entity.to_sheet(),
        'biorhythms': entity.biorhythms,
        'combat_stats': entity.combat,
        'thoughts': entity.thoughts,
        'traits': entity.traits
    }
```

### 4. Test Suite
- [ ] Test all 144 zodiac combinations (12×12)
- [ ] Test all 864 species/type combinations (36×24)
- [ ] Test all 216 class builds (6^3 for Melee/Ranged/Magic minimum)
- [ ] Verify stat calculations match expected ranges
- [ ] Test thought generation edge cases

---

## 📋 Next Steps

1. **Create `data_loader.py`** — Unified JSON loader with validation
2. **Update `rememberence_bridge.py`** — Integrate data_loader, add missing functions
3. **Build `character_creator.py`** — Step-by-step creation with validation
4. **Write tests** — Verify all combinations produce valid entities
5. **Document API** — Create spec for webapp module integration

---

## 🚀 Ready for Phase 2 (Webapp Modules)

Once Phase 1 is complete, each webapp module can call:

```javascript
// Character Creation Webapp
POST /api/character/create
{
  "animal": "Dragon",
  "star": "Leo", 
  "species": "Drakian",
  "type": "Pyro",
  "classes": {"Melee": 1, "Ranged": 2, "Magic": 3, "Step": 4, "Special": 5, "Trance": 6}
}

// Response
{
  "biorhythms": {...},
  "combat_stats": {...},
  "thoughts": {...},
  "traits": {...},
  "character_sheet": "formatted text"
}
```
