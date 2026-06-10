# extract_final_v2.py - Clean extraction with proper quote handling
import re
import json
from pathlib import Path

def extract_js_string_array(text, array_name):
    """Extract a named string array from JS, handling escaped quotes."""
    # Find the array block
    pattern = rf"{array_name}:\s*\[([\s\S]*?)\]"
    match = re.search(pattern, text)
    if not match:
        return []
    
    array_text = match.group(1)
    results = []
    
    # Find complete quoted strings (handling escaped quotes inside)
    # Pattern: start quote, content (including escaped quotes), end quote not preceded by backslash
    pos = 0
    while pos < len(array_text):
        # Find next unescaped quote
        start = array_text.find("'", pos)
        if start < 0:
            break
        
        # Find end quote (not escaped)
        end = start + 1
        while end < len(array_text):
            if array_text[end] == "'" and array_text[end-1] != '\\':
                break
            end += 1
        
        if end < len(array_text):
            string_val = array_text[start+1:end].replace("\\'", "'")
            results.append(string_val)
            pos = end + 1
        else:
            break
    
    return results

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
            animals[name] = {'biorhythms': {}}
            for bio in ['MNF', 'SPL', 'BEU', 'STR', 'FND', 'KNO', 'UND', 'WIS', 'VIT', 'SEX', 'DIV', 'EGO']:
                bm = re.search(rf"{bio}: (\d+)", bio_block)
                if bm:
                    animals[name]['biorhythms'][bio] = int(bm.group(1))
    
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
            stars[name] = {'biorhythms': {}}
            for bio in ['MNF', 'SPL', 'BEU', 'STR', 'FND', 'KNO', 'UND', 'WIS', 'VIT', 'SEX', 'DIV', 'EGO']:
                bm = re.search(rf"{bio}: (\d+)", bio_block)
                if bm:
                    stars[name]['biorhythms'][bio] = int(bm.group(1))
    
    with open(output_dir / 'star_signs.json', 'w', encoding='utf-8') as f:
        json.dump({'starSigns': stars}, f, indent=2)
    print(f"  OK: {len(stars)} stars")
    
    # ===== SPECIES =====
    print("Extracting speciesData...")
    species = {}
    match = re.search(r"const speciesData = \{([\s\S]*?)\n\};", content)
    if match:
        # Find each species block - improved pattern for last entry
        species_pattern = r"'(\w+)': \{([\s\S]*?)(?=\n    '\w+': \{|\n    \})"
        for m in re.finditer(species_pattern, match.group(1)):
            name = m.group(1)
            block = m.group(2)
            
            # Extract stats
            stats = {}
            for stat in ['HP', 'ATK', 'DEF', 'SPD', 'MP']:
                sm = re.search(rf"{stat}: (\d+)", block)
                if sm:
                    stats[stat] = int(sm.group(1))
            sm = re.search(r"Move: '([^']+)'", block)
            if sm:
                stats['Move'] = sm.group(1)
            
            # Extract traits using the helper
            traits = {
                'active': extract_js_string_array(block, 'active'),
                'passive': extract_js_string_array(block, 'passive')
            }
            
            species[name] = {'stats': stats, 'traits': traits}
    
    with open(output_dir / 'species.json', 'w', encoding='utf-8') as f:
        json.dump({'species': species}, f, indent=2, ensure_ascii=False)
    print(f"  OK: {len(species)} species")
    
    # ===== TYPES =====
    print("Extracting typeData...")
    types = {}
    match = re.search(r"const typeData = \{([\s\S]*?)\n\};", content)
    if match:
        type_pattern = r"'(\w+)': \{([\s\S]*?)(?=\n    '\w+': \{|\n    \})"
        for m in re.finditer(type_pattern, match.group(1)):
            name = m.group(1)
            block = m.group(2)
            
            data = {'traits': {
                'active': extract_js_string_array(block, 'active'),
                'passive': extract_js_string_array(block, 'passive')
            }}
            
            # Color
            cm = re.search(r"color: '([^']+)'", block)
            if cm:
                data['color'] = cm.group(1)
            
            # Patterns
            for pat in ['move', 'attack']:
                pm = re.search(rf"{pat}: '([^']+)'", block)
                if pm:
                    data[f'{pat}_pattern'] = pm.group(1)
            
            # Stat modifiers
            mods = {}
            for stat in ['HP', 'ATK', 'DEF', 'SPD', 'MP']:
                sm = re.search(rf"{stat}: '(\w+)'", block)
                if sm:
                    mods[stat] = sm.group(1)
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
        class_pattern = r"'(\w+)': \{([\s\S]*?)(?=\n    '\w+': \{|\n    \})"
        for m in re.finditer(class_pattern, match.group(1)):
            name = m.group(1)
            block = m.group(2)
            
            data = {'skills': []}
            
            # Description
            dm = re.search(r"description: '([^']+)'", block)
            if dm:
                data['description'] = dm.group(1).replace("\\'", "'")
            
            # Controlled
            cm = re.search(r"controlled: '([^']+)'", block)
            if cm:
                data['controlled'] = cm.group(1)
            
            # Skills - each skill is a named block
            skill_pattern = r"'([^']+)': \{([\s\S]*?)(?=\n            '(?:[^']+)': |\n        \})"
            for sm in re.finditer(skill_pattern, block):
                skill_name = sm.group(1)
                skill_block = sm.group(2)
                
                skill = {'name': skill_name}
                
                # Bonuses
                for stat in ['atk_bonus', 'def_bonus', 'spd_bonus']:
                    bm = re.search(rf"{stat}: (\d+)", skill_block)
                    if bm:
                        skill[stat] = int(bm.group(1))
                
                # Pattern
                pm = re.search(r"pattern: '([^']+)'", skill_block)
                if pm:
                    skill['pattern'] = pm.group(1)
                
                # Traits (single string in this format)
                tm = re.search(r"traits: '([^']+)'", skill_block)
                if tm:
                    skill['traits'] = [tm.group(1).replace("\\'", "'")]
                
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
    
    print("\nAll extraction complete!")

if __name__ == '__main__':
    main()
