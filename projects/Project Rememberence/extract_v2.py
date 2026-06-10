# extract_v2.py - Robust JS to JSON extraction
import re
import json
from pathlib import Path

def extract_biorhythms(block):
    """Extract biorhythm key-value pairs from JS block."""
    result = {}
    for bio in ['MNF', 'SPL', 'BEU', 'STR', 'FND', 'KNO', 'UND', 'WIS', 'VIT', 'SEX', 'DIV', 'EGO']:
        m = re.search(rf"{bio}: (\d+)", block)
        if m:
            result[bio] = int(m.group(1))
    return result

def extract_stats(block):
    """Extract combat stats from JS block."""
    result = {}
    for stat in ['HP', 'ATK', 'DEF', 'SPD', 'MP']:
        m = re.search(rf"{stat}: (\d+)", block)
        if m:
            result[stat] = int(m.group(1))
    m = re.search(r"Move: '([^']+)'", block)
    if m:
        result['Move'] = m.group(1)
    return result

def extract_traits(block):
    """Extract traits arrays from JS block."""
    traits = {'active': [], 'passive': []}
    
    # Find active traits array
    active_match = re.search(r"active:\s*\[([\s\S]*?)\]", block)
    if active_match:
        for m in re.finditer(r"'([^']+)'", active_match.group(1)):
            traits['active'].append(m.group(1).replace("\\'", "'"))
    
    # Find passive traits array  
    passive_match = re.search(r"passive:\s*\[([\s\S]*?)\]", block)
    if passive_match:
        for m in re.finditer(r"'([^']+)'", passive_match.group(1)):
            traits['passive'].append(m.group(1).replace("\\'", "'"))
    
    return traits

def main():
    js_path = Path(r'D:\cards\AI Prompts\Oracle Project\Project Files\constants.js')
    output_dir = Path(__file__).parent / 'data'
    
    content = js_path.read_text(encoding='utf-8')
    
    # ===== ANIMAL SIGNS =====
    print("Extracting animalSigns...")
    animals = {}
    match = re.search(r"const animalSigns = \{([\s\S]*?)\};", content)
    if match:
        for m in re.finditer(r"'(\w+)': \{([^}]+)\}", match.group(1)):
            name, bio_block = m.groups()
            animals[name] = {'biorhythms': extract_biorhythms(bio_block)}
    
    with open(output_dir / 'animal_signs.json', 'w', encoding='utf-8') as f:
        json.dump({'animalSigns': animals}, f, indent=2)
    print(f"  OK: {len(animals)} animals")
    
    # ===== STAR SIGNS =====
    print("Extracting starSigns...")
    stars = {}
    match = re.search(r"const starSigns = \{([\s\S]*?)\};", content)
    if match:
        for m in re.finditer(r"'(\w+)': \{([^}]+)\}", match.group(1)):
            name, bio_block = m.groups()
            stars[name] = {'biorhythms': extract_biorhythms(bio_block)}
    
    with open(output_dir / 'star_signs.json', 'w', encoding='utf-8') as f:
        json.dump({'starSigns': stars}, f, indent=2)
    print(f"  OK: {len(stars)} stars")
    
    # ===== SPECIES =====
    print("Extracting speciesData...")
    species = {}
    match = re.search(r"const speciesData = \{([\s\S]*?)\n\};", content)
    if match:
        # Split by species entries
        entries = re.split(r"\n    '(\w+)': \{", match.group(1))
        for i in range(1, len(entries), 2):
            name = entries[i]
            # Get content until next species or end
            block = entries[i+1] if i+1 < len(entries) else ""
            # Cut at closing brace
            brace_end = block.find("\n    }")
            if brace_end > 0:
                block = block[:brace_end]
            
            data = {
                'stats': extract_stats(block),
                'traits': extract_traits(block)
            }
            species[name] = data
    
    with open(output_dir / 'species.json', 'w', encoding='utf-8') as f:
        json.dump({'species': species}, f, indent=2, ensure_ascii=False)
    print(f"  OK: {len(species)} species")
    
    # ===== TYPES =====
    print("Extracting typeData...")
    types = {}
    match = re.search(r"const typeData = \{([\s\S]*?)\n\};", content)
    if match:
        entries = re.split(r"\n    '(\w+)': \{", match.group(1))
        for i in range(1, len(entries), 2):
            name = entries[i]
            block = entries[i+1] if i+1 < len(entries) else ""
            brace_end = block.find("\n    }")
            if brace_end > 0:
                block = block[:brace_end]
            
            data = {'traits': extract_traits(block)}
            
            # Color
            m = re.search(r"color: '([^']+)'", block)
            if m:
                data['color'] = m.group(1)
            
            # Patterns
            for pat in ['move', 'attack']:
                m = re.search(rf"{pat}: '([^']+)'", block)
                if m:
                    data[f'{pat}_pattern'] = m.group(1)
            
            # Stat modifiers
            mods = {}
            for stat in ['HP', 'ATK', 'DEF', 'SPD', 'MP']:
                m = re.search(rf"{stat}: '(\w+)'", block)
                if m:
                    mods[stat] = m.group(1)
            if mods:
                data['stat_modifiers'] = mods
            
            types[name] = data
    
    with open(output_dir / 'types.json', 'w', encoding='utf-8') as f:
        json.dump({'types': types}, f, indent=2, ensure_ascii=False)
    print(f"  OK: {len(types)} types")
    
    # ===== CLASSES =====
    print("Extracting classData...")
    classes = {}
    match = re.search(r"const classData = \{([\s\S]*?)\n\};", content)
    if match:
        entries = re.split(r"\n    '(\w+)': \{", match.group(1))
        for i in range(1, len(entries), 2):
            name = entries[i]
            block = entries[i+1] if i+1 < len(entries) else ""
            brace_end = block.find("\n    },")
            if brace_end > 0:
                block = block[:brace_end]
            
            data = {'skills': []}
            
            # Description
            m = re.search(r"description: '([^']+)'", block)
            if m:
                data['description'] = m.group(1).replace("\\'", "'")
            
            # Biorhythm controllers
            m = re.search(r"controlled: '([^']+)'", block)
            if m:
                data['controlled'] = m.group(1)
            
            # Skills - find each skill block
            skill_pattern = r"'([^']+)': \{([^}]+)\}"
            for skill_m in re.finditer(skill_pattern, block):
                skill_name = skill_m.group(1)
                skill_block = skill_m.group(2)
                
                skill = {'name': skill_name}
                
                # Bonuses
                for stat in ['atk_bonus', 'def_bonus', 'spd_bonus']:
                    m = re.search(rf"{stat}: (\d+)", skill_block)
                    if m:
                        skill[stat] = int(m.group(1))
                
                # Pattern
                m = re.search(r"pattern: '([^']+)'", skill_block)
                if m:
                    skill['pattern'] = m.group(1)
                
                # Traits
                m = re.search(r"traits: '([^']+)'", skill_block)
                if m:
                    skill['traits'] = [m.group(1).replace("\\'", "'")]
                
                data['skills'].append(skill)
            
            classes[name] = data
    
    with open(output_dir / 'classes.json', 'w', encoding='utf-8') as f:
        json.dump({'classes': classes}, f, indent=2, ensure_ascii=False)
    print(f"  OK: {len(classes)} classes")
    
    # ===== RUNES =====
    print("Extracting runesData...")
    runes = {}
    match = re.search(r"const runesData = \{([\s\S]*?)\n\};", content)
    if match:
        for m in re.finditer(r"'(\w+)': \{ effect: '([^']+)', cost: (\d+), desc: '([^']+)' \}", match.group(1)):
            key, effect, cost, desc = m.groups()
            runes[key] = {
                'effect': effect,
                'cost': int(cost),
                'description': desc.replace("\\'", "'")
            }
    
    with open(output_dir / 'runes.json', 'w', encoding='utf-8') as f:
        json.dump({'runes': runes}, f, indent=2, ensure_ascii=False)
    print(f"  OK: {len(runes)} runes")
    
    print("\nExtraction complete!")
    print("\nValidation:")
    for filename in ['animal_signs.json', 'star_signs.json', 'species.json', 'types.json', 'classes.json', 'runes.json']:
        try:
            d = json.load(open(output_dir / filename))
            key = list(d.keys())[0]
            print(f"  {filename}: {len(d[key])} entries - VALID")
        except Exception as e:
            print(f"  {filename}: ERROR - {e}")

if __name__ == '__main__':
    main()
