# extract_robust.py - Robust extraction using JS parser approach
import re
import json
from pathlib import Path

def extract_species(content):
    """Extract species data with proper handling of escaped quotes."""
    section = re.search(r"const speciesData = \{([\s\S]*?)\n\};", content)
    if not section:
        return {}
    
    species = {}
    text = section.group(1)
    
    # Find each species block
    pattern = r"'(\w+)': \{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\n    \}"
    
    for match in re.finditer(pattern, text, re.MULTILINE):
        name = match.group(1)
        block = match.group(2)
        
        data = {'traits': {'active': [], 'passive': []}}
        
        # Extract stats
        for stat in ['HP', 'ATK', 'DEF', 'SPD', 'MP']:
            m = re.search(rf"{stat}: (\d+)", block)
            if m:
                data.setdefault('stats', {})[stat] = int(m.group(1))
        
        # Extract Move
        m = re.search(r"Move: '([^']+)'", block)
        if m:
            data.setdefault('stats', {})['Move'] = m.group(1)
        
        # Extract traits - find the arrays
        active_match = re.search(r"active: \[([\s\S]*?)\]", block)
        if active_match:
            for trait_m in re.finditer(r"'([^']+)'", active_match.group(1)):
                data['traits']['active'].append(trait_m.group(1).replace("\\'", "'"))
        
        passive_match = re.search(r"passive: \[([\s\S]*?)\]", block)
        if passive_match:
            for trait_m in re.finditer(r"'([^']+)'", passive_match.group(1)):
                data['traits']['passive'].append(trait_m.group(1).replace("\\'", "'"))
        
        species[name] = data
    
    return species

def extract_types(content):
    """Extract type data."""
    section = re.search(r"const typeData = \{([\s\S]*?)\n\};", content)
    if not section:
        return {}
    
    types = {}
    text = section.group(1)
    
    pattern = r"'(\w+)': \{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\n    \}"
    
    for match in re.finditer(pattern, text, re.MULTILINE):
        name = match.group(1)
        block = match.group(2)
        
        data = {'traits': {'active': [], 'passive': []}}
        
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
        for stat in ['HP', 'ATK', 'DEF', 'SPD', 'MP']:
            m = re.search(rf"{stat}: '(\w+)'", block)
            if m:
                data.setdefault('stat_modifiers', {})[stat] = m.group(1)
        
        # Traits
        active_match = re.search(r"active: \[([\s\S]*?)\]", block)
        if active_match:
            for trait_m in re.finditer(r"'([^']+)'", active_match.group(1)):
                data['traits']['active'].append(trait_m.group(1).replace("\\'", "'"))
        
        passive_match = re.search(r"passive: \[([\s\S]*?)\]", block)
        if passive_match:
            for trait_m in re.finditer(r"'([^']+)'", passive_match.group(1)):
                data['traits']['passive'].append(trait_m.group(1).replace("\\'", "'"))
        
        types[name] = data
    
    return types

def extract_classes(content):
    """Extract class data with skills."""
    section = re.search(r"const classData = \{([\s\S]*?)\n\};", content)
    if not section:
        return {}
    
    classes = {}
    text = section.group(1)
    
    # Find each class block (more complex due to nested skills)
    class_pattern = r"'(\w+)': \{([\s\S]*?)\n    \},"
    
    for match in re.finditer(class_pattern, text):
        name = match.group(1)
        block = match.group(2)
        
        data = {'skills': []}
        
        # Description
        m = re.search(r"description: '([^']+)'", block)
        if m:
            data['description'] = m.group(1).replace("\\'", "'")
        
        # Biorhythm controllers
        m = re.search(r"biorhythm_controllers: \[([^\]]+)\]", block)
        if m:
            data['biorhythm_controllers'] = [x.strip().strip("'") for x in m.group(1).split(',')]
        
        # Skills - find skill objects
        skill_pattern = r"\{ name: '([^']+)', style: '([^']+)', description: '([^']+)', bonuses: \{ ATK: (\d+), DEF: (\d+), SPD: (\d+) \}, pattern: '([^']+)', traits: \[([^\]]*)\] \}"
        
        for skill_m in re.finditer(skill_pattern, block, re.DOTALL):
            skill = {
                'name': skill_m.group(1),
                'style': skill_m.group(2),
                'description': skill_m.group(3).replace("\\'", "'"),
                'bonuses': {
                    'ATK': int(skill_m.group(4)),
                    'DEF': int(skill_m.group(5)),
                    'SPD': int(skill_m.group(6))
                },
                'pattern': skill_m.group(7),
                'traits': [t.strip().strip("'").replace("\\'", "'") for t in skill_m.group(8).split(',') if t.strip()]
            }
            data['skills'].append(skill)
        
        classes[name] = data
    
    return classes

def extract_runes(content):
    """Extract runes data."""
    section = re.search(r"const runesData = \{([\s\S]*?)\n\};", content)
    if not section:
        return {}
    
    runes = {}
    text = section.group(1)
    
    # Pattern: 'Cu': { effect: 'Target Other', cost: 100, desc: 'Togetherness...' }
    pattern = r"'(\w+)': \{ effect: '([^']+)', cost: (\d+), desc: '([^']+)' \}"
    
    for match in re.finditer(pattern, text):
        key, effect, cost, desc = match.groups()
        runes[key] = {
            'effect': effect,
            'cost': int(cost),
            'description': desc.replace("\\'", "'")
        }
    
    return runes

def main():
    js_path = Path(r'D:\cards\AI Prompts\Oracle Project\Project Files\constants.js')
    output_dir = Path(__file__).parent / 'data'
    
    content = js_path.read_text(encoding='utf-8')
    
    print("Extracting animalSigns...")
    animals = {}
    for m in re.finditer(r"'(\w+)': \{([^}]+)\}", re.search(r"const animalSigns = \{([\s\S]*?)\};", content).group(1)):
        name, bio_str = m.groups()
        animals[name] = {'biorhythms': {k: int(v) for k, v in re.findall(r'(\w+): (\d+)', bio_str)}}
    
    with open(output_dir / 'animal_signs.json', 'w', encoding='utf-8') as f:
        json.dump({'animalSigns': animals}, f, indent=2)
    print(f"  OK: {len(animals)} animal signs")
    
    print("Extracting starSigns...")
    stars = {}
    for m in re.finditer(r"'(\w+)': \{([^}]+)\}", re.search(r"const starSigns = \{([\s\S]*?)\};", content).group(1)):
        name, bio_str = m.groups()
        stars[name] = {'biorhythms': {k: int(v) for k, v in re.findall(r'(\w+): (\d+)', bio_str)}}
    
    with open(output_dir / 'star_signs.json', 'w', encoding='utf-8') as f:
        json.dump({'starSigns': stars}, f, indent=2)
    print(f"  OK: {len(stars)} star signs")
    
    print("Extracting speciesData...")
    species = extract_species(content)
    with open(output_dir / 'species.json', 'w', encoding='utf-8') as f:
        json.dump({'species': species}, f, indent=2, ensure_ascii=False)
    print(f"  OK: {len(species)} species")
    
    print("Extracting typeData...")
    types = extract_types(content)
    with open(output_dir / 'types.json', 'w', encoding='utf-8') as f:
        json.dump({'types': types}, f, indent=2, ensure_ascii=False)
    print(f"  OK: {len(types)} types")
    
    print("Extracting classData...")
    classes = extract_classes(content)
    with open(output_dir / 'classes.json', 'w', encoding='utf-8') as f:
        json.dump({'classes': classes}, f, indent=2, ensure_ascii=False)
    print(f"  OK: {len(classes)} classes")
    
    print("Extracting runesData...")
    runes = extract_runes(content)
    with open(output_dir / 'runes.json', 'w', encoding='utf-8') as f:
        json.dump({'runes': runes}, f, indent=2, ensure_ascii=False)
    print(f"  OK: {len(runes)} runes")
    
    print("\nExtraction complete!")

if __name__ == '__main__':
    main()
