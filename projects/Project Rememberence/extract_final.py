# extract_final.py - Complete extraction from constants.js
import re
import json
from pathlib import Path

def extract_all():
    js_path = Path(r'D:\cards\AI Prompts\Oracle Project\Project Files\constants.js')
    output_dir = Path(__file__).parent / 'data'
    
    content = js_path.read_text(encoding='utf-8')
    
    # ===== ANIMAL SIGNS =====
    print("Extracting animalSigns...")
    animals = {}
    for match in re.finditer(r"'(\w+)': \{([^}]+)\}", re.search(r"const animalSigns = \{([\s\S]*?)\};", content).group(1)):
        name, bio_str = match.groups()
        animals[name] = {'biorhythms': {k: int(v) for k, v in re.findall(r'(\w+): (\d+)', bio_str)}}
    
    with open(output_dir / 'animal_signs.json', 'w', encoding='utf-8') as f:
        json.dump({'animalSigns': animals}, f, indent=2)
    print(f"  OK: {len(animals)} animal signs")
    
    # ===== STAR SIGNS =====
    print("Extracting starSigns...")
    stars = {}
    for match in re.finditer(r"'(\w+)': \{([^}]+)\}", re.search(r"const starSigns = \{([\s\S]*?)\};", content).group(1)):
        name, bio_str = match.groups()
        stars[name] = {'biorhythms': {k: int(v) for k, v in re.findall(r'(\w+): (\d+)', bio_str)}}
    
    with open(output_dir / 'star_signs.json', 'w', encoding='utf-8') as f:
        json.dump({'starSigns': stars}, f, indent=2)
    print(f"  OK: {len(stars)} star signs")
    
    # ===== SPECIES =====
    print("Extracting speciesData...")
    species = {}
    section = re.search(r"const speciesData = \{([\s\S]*?)\n\};", content)
    current, data, depth = None, {}, 0
    in_active, in_passive = False, False
    
    for line in section.group(1).split('\n'):
        s = line.strip()
        m = re.match(r"'(\w+)': \{", s)
        if m and depth == 0:
            if current: species[current] = data
            current, data, depth = m.group(1), {'traits': {'active': [], 'passive': []}}, 1
            continue
        if current:
            depth += s.count('{') - s.count('}')
            for stat in ['HP', 'ATK', 'DEF', 'SPD', 'MP']:
                m = re.match(rf"{stat}: (\d+),?", s)
                if m:
                    data.setdefault('stats', {})[stat] = int(m.group(1))
            m = re.match(r"Move: '([^']+)',?", s)
            if m: data.setdefault('stats', {})['Move'] = m.group(1)
            if "active: [" in s: in_active, in_passive = True, False
            elif "passive: [" in s: in_active, in_passive = False, True
            elif s.startswith(']'): in_active = in_passive = False
            elif s.startswith("'") and (in_active or in_passive):
                m = re.match(r"'([^']+)',?", s)
                if m: data['traits']['active' if in_active else 'passive'].append(m.group(1).replace("\\'", "'"))
            if depth == 0: species[current] = data; current = None
    
    with open(output_dir / 'species.json', 'w', encoding='utf-8') as f:
        json.dump({'species': species}, f, indent=2, ensure_ascii=False)
    print(f"  OK: {len(species)} species")
    
    # ===== TYPES =====
    print("Extracting typeData...")
    types = {}
    section = re.search(r"const typeData = \{([\s\S]*?)\n\};", content)
    current, data, depth = None, {}, 0
    in_active, in_passive = False, False
    
    for line in section.group(1).split('\n'):
        s = line.strip()
        m = re.match(r"'(\w+)': \{", s)
        if m and depth == 0:
            if current: types[current] = data
            current, data, depth = m.group(1), {'traits': {'active': [], 'passive': []}}, 1
            continue
        if current:
            depth += s.count('{') - s.count('}')
            m = re.match(r"color: '([^']+)',?", s)
            if m: data['color'] = m.group(1)
            for pat in ['move', 'attack']:
                m = re.match(rf"{pat}: '([^']+)',?", s)
                if m: data[f'{pat}_pattern'] = m.group(1)
            for stat in ['HP', 'ATK', 'DEF', 'SPD', 'MP']:
                m = re.match(rf"{stat}: '(\w+)',?", s)
                if m: data.setdefault('stat_modifiers', {})[stat] = m.group(1)
            if "active: [" in s: in_active, in_passive = True, False
            elif "passive: [" in s: in_active, in_passive = False, True
            elif s.startswith(']'): in_active = in_passive = False
            elif s.startswith("'") and (in_active or in_passive):
                m = re.match(r"'([^']+)',?", s)
                if m: data['traits']['active' if in_active else 'passive'].append(m.group(1).replace("\\'", "'"))
            if depth == 0: types[current] = data; current = None
    
    with open(output_dir / 'types.json', 'w', encoding='utf-8') as f:
        json.dump({'types': types}, f, indent=2, ensure_ascii=False)
    print(f"  OK: {len(types)} types")
    
    # ===== CLASSES =====
    print("Extracting classData...")
    classes = {}
    section = re.search(r"const classData = \{([\s\S]*?)\n\};", content)
    current, data, depth = None, {}, 0
    in_skills, current_skill, skill_depth = False, None, 0
    
    for line in section.group(1).split('\n'):
        s = line.strip()
        m = re.match(r"'(\w+)': \{", s)
        if m and depth == 0:
            if current: classes[current] = data
            current, data, depth = m.group(1), {'skills': []}, 1
            continue
        if current:
            depth += s.count('{') - s.count('}')
            m = re.match(r"description: '([^']+)',?", s)
            if m: data['description'] = m.group(1).replace("\\'", "'")
            m = re.match(r"biorhythm_controllers: \[([^\]]+)\]", s)
            if m: data['biorhythm_controllers'] = [x.strip().strip("'") for x in m.group(1).split(',')]
            if "skills: [" in s: in_skills = True; continue
            if in_skills:
                if s.startswith('{'): current_skill, skill_depth = {}, 1
                elif current_skill:
                    skill_depth += s.count('{') - s.count('}')
                    for field in ['name', 'style', 'description', 'pattern']:
                        m = re.match(rf"{field}: '([^']+)',?", s)
                        if m: current_skill[field] = m.group(1).replace("\\'", "'")
                    for stat in ['ATK', 'DEF', 'SPD']:
                        m = re.match(rf"{stat}: (\d+),?", s)
                        if m: current_skill.setdefault('bonuses', {})[stat] = int(m.group(1))
                    if "traits: [" in s: current_skill['traits'] = []
                    elif 'traits' in current_skill and s.startswith("'"):
                        m = re.match(r"'([^']+)',?", s)
                        if m: current_skill['traits'].append(m.group(1).replace("\\'", "'"))
                    if skill_depth == 0 and s.startswith('}'): data['skills'].append(current_skill); current_skill = None
            if depth == 0: classes[current] = data; current = None
    
    with open(output_dir / 'classes.json', 'w', encoding='utf-8') as f:
        json.dump({'classes': classes}, f, indent=2, ensure_ascii=False)
    print(f"  OK: {len(classes)} classes")
    
    # ===== RUNES =====
    print("Extracting runesData...")
    runes = {}
    section = re.search(r"const runesData = \{([\s\S]*?)\n\};", content)
    if section:
        for match in re.finditer(r"'(\w+)': \{ effect: '([^']+)', cost: (\d+), desc: '([^']+)' \}", section.group(1)):
            key, effect, cost, desc = match.groups()
            runes[key] = {'effect': effect, 'cost': int(cost), 'description': desc.replace("\\'", "'")}
    
    with open(output_dir / 'runes.json', 'w', encoding='utf-8') as f:
        json.dump({'runes': runes}, f, indent=2, ensure_ascii=False)
    print(f"  OK: {len(runes)} runes")
    
    # ===== NARRATIVE VERSES =====
    print("Extracting bioToVerse...")
    verses = {}
    section = re.search(r"const bioToVerse = \{([\s\S]*?)\};", content)
    if section:
        for match in re.finditer(r"'(\w+)': \{ dominant: '([^']+)', recessive: '([^']+)' \}", section.group(1)):
            bio, dom, rec = match.groups()
            verses[bio] = {'dominant': dom, 'recessive': rec}
    
    with open(output_dir / 'narrative_verses.json', 'w', encoding='utf-8') as f:
        json.dump({'verses': verses}, f, indent=2, ensure_ascii=False)
    print(f"  OK: {len(verses)} biorhythm verses")
    
    print("\nAll extraction complete!")

if __name__ == '__main__':
    extract_all()
