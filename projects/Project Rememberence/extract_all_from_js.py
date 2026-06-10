# extract_all_from_js.py - Extract ALL data from constants.js
import re
import json
from pathlib import Path

def extract_data():
    js_path = Path(r'D:\cards\AI Prompts\Oracle Project\Project Files\constants.js')
    output_dir = Path(__file__).parent / 'data'
    
    content = js_path.read_text(encoding='utf-8')
    
    # ===== ANIMAL SIGNS =====
    print("Extracting animalSigns...")
    animal_match = re.search(r"const animalSigns = \{([\s\S]*?)\};", content)
    if animal_match:
        animals = {}
        for match in re.finditer(r"'(\w+)': \{([^}]+)\}", animal_match.group(1)):
            name = match.group(1)
            bio_str = match.group(2)
            biorhythms = {}
            for bio_match in re.finditer(r'(\w+): (\d+)', bio_str):
                biorhythms[bio_match.group(1)] = int(bio_match.group(2))
            animals[name] = {'biorhythms': biorhythms}
        
        with open(output_dir / 'animal_signs.json', 'w', encoding='utf-8') as f:
            json.dump({'animalSigns': animals}, f, indent=2)
        print(f"  OK: {len(animals)} animal signs")
    
    # ===== STAR SIGNS =====
    print("Extracting starSigns...")
    star_match = re.search(r"const starSigns = \{([\s\S]*?)\};", content)
    if star_match:
        stars = {}
        for match in re.finditer(r"'(\w+)': \{([^}]+)\}", star_match.group(1)):
            name = match.group(1)
            bio_str = match.group(2)
            biorhythms = {}
            for bio_match in re.finditer(r'(\w+): (\d+)', bio_str):
                biorhythms[bio_match.group(1)] = int(bio_match.group(2))
            stars[name] = {'biorhythms': biorhythms}
        
        with open(output_dir / 'star_signs.json', 'w', encoding='utf-8') as f:
            json.dump({'starSigns': stars}, f, indent=2)
        print(f"  OK: {len(stars)} star signs")
    
    # ===== SPECIES DATA =====
    print("Extracting speciesData...")
    species_section = re.search(r"const speciesData = \{([\s\S]*?)\n\};", content)
    if species_section:
        species = {}
        current = None
        data = {}
        brace_depth = 0
        in_active = False
        in_passive = False
        
        for line in species_section.group(1).split('\n'):
            stripped = line.strip()
            
            # New species
            m = re.match(r"'(\w+)': \{", stripped)
            if m and brace_depth == 0:
                if current:
                    species[current] = data
                current = m.group(1)
                data = {'traits': {'active': [], 'passive': []}}
                brace_depth = 1
                continue
            
            if current:
                brace_depth += stripped.count('{') - stripped.count('}')
                
                # Stats
                for stat in ['HP', 'ATK', 'DEF', 'SPD', 'MP']:
                    m = re.match(rf"{stat}: (\d+),?", stripped)
                    if m:
                        if 'stats' not in data:
                            data['stats'] = {}
                        data['stats'][stat] = int(m.group(1))
                
                # Move
                m = re.match(r"Move: '([^']+)',?", stripped)
                if m:
                    if 'stats' not in data:
                        data['stats'] = {}
                    data['stats']['Move'] = m.group(1)
                
                # Trait arrays
                if "active: [" in stripped:
                    in_active = True
                    in_passive = False
                elif "passive: [" in stripped:
                    in_active = False
                    in_passive = True
                elif stripped.startswith(']'):
                    in_active = False
                    in_passive = False
                elif stripped.startswith("'") and (in_active or in_passive):
                    m = re.match(r"'([^']+)',?", stripped)
                    if m:
                        trait = m.group(1).replace("\\'", "'")
                        if in_active:
                            data['traits']['active'].append(trait)
                        elif in_passive:
                            data['traits']['passive'].append(trait)
                
                if brace_depth == 0:
                    species[current] = data
                    current = None
        
        with open(output_dir / 'species.json', 'w', encoding='utf-8') as f:
            json.dump({'species': species}, f, indent=2, ensure_ascii=False)
        print(f"  OK: {len(species)} species")
    
    # ===== TYPES DATA =====
    print("Extracting typeData...")
    types_section = re.search(r"const typeData = \{([\s\S]*?)\n\};", content)
    if types_section:
        types = {}
        current = None
        data = {}
        brace_depth = 0
        in_active = False
        in_passive = False
        
        for line in types_section.group(1).split('\n'):
            stripped = line.strip()
            
            m = re.match(r"'(\w+)': \{", stripped)
            if m and brace_depth == 0:
                if current:
                    types[current] = data
                current = m.group(1)
                data = {'traits': {'active': [], 'passive': []}}
                brace_depth = 1
                continue
            
            if current:
                brace_depth += stripped.count('{') - stripped.count('}')
                
                # Color
                m = re.match(r"color: '([^']+)',?", stripped)
                if m:
                    data['color'] = m.group(1)
                
                # Move/Attack patterns
                m = re.match(r"move: '([^']+)',?", stripped)
                if m:
                    data['move_pattern'] = m.group(1)
                m = re.match(r"attack: '([^']+)',?", stripped)
                if m:
                    data['attack_pattern'] = m.group(1)
                
                # Stat modifiers
                for stat in ['HP', 'ATK', 'DEF', 'SPD', 'MP']:
                    m = re.match(rf"{stat}: '(\w+)',?", stripped)
                    if m:
                        if 'stat_modifiers' not in data:
                            data['stat_modifiers'] = {}
                        data['stat_modifiers'][stat] = m.group(1)
                
                # Traits
                if "active: [" in stripped:
                    in_active = True
                    in_passive = False
                elif "passive: [" in stripped:
                    in_active = False
                    in_passive = True
                elif stripped.startswith(']'):
                    in_active = False
                    in_passive = False
                elif stripped.startswith("'") and (in_active or in_passive):
                    m = re.match(r"'([^']+)',?", stripped)
                    if m:
                        trait = m.group(1).replace("\\'", "'")
                        if in_active:
                            data['traits']['active'].append(trait)
                        elif in_passive:
                            data['traits']['passive'].append(trait)
                
                if brace_depth == 0:
                    types[current] = data
                    current = None
        
        with open(output_dir / 'types.json', 'w', encoding='utf-8') as f:
            json.dump({'types': types}, f, indent=2, ensure_ascii=False)
        print(f"  OK: {len(types)} types")
    
    # ===== CLASSES DATA =====
    print("Extracting classData...")
    classes_section = re.search(r"const classData = \{([\s\S]*?)\n\};", content)
    if classes_section:
        classes = {}
        current = None
        data = {}
        brace_depth = 0
        in_skills = False
        current_skill = None
        skill_brace_depth = 0
        
        for line in classes_section.group(1).split('\n'):
            stripped = line.strip()
            
            # New class
            m = re.match(r"'(\w+)': \{", stripped)
            if m and brace_depth == 0:
                if current:
                    classes[current] = data
                current = m.group(1)
                data = {'skills': []}
                brace_depth = 1
                continue
            
            if current:
                brace_depth += stripped.count('{') - stripped.count('}')
                
                # Description
                m = re.match(r"description: '([^']+)',?", stripped)
                if m:
                    data['description'] = m.group(1).replace("\\'", "'")
                
                # Biorhythm controllers
                m = re.match(r"biorhythm_controllers: \[([^\]]+)\]", stripped)
                if m:
                    data['biorhythm_controllers'] = [x.strip().strip("'") for x in m.group(1).split(',')]
                
                # Skills array start
                if "skills: [" in stripped:
                    in_skills = True
                    continue
                
                if in_skills:
                    # New skill object
                    if stripped.startswith('{'):
                        current_skill = {}
                        skill_brace_depth = 1
                    elif current_skill:
                        skill_brace_depth += stripped.count('{') - stripped.count('}')
                        
                        # Skill properties
                        m = re.match(r"name: '([^']+)',?", stripped)
                        if m:
                            current_skill['name'] = m.group(1)
                        m = re.match(r"style: '([^']+)',?", stripped)
                        if m:
                            current_skill['style'] = m.group(1)
                        m = re.match(r"description: '([^']+)',?", stripped)
                        if m:
                            current_skill['description'] = m.group(1).replace("\\'", "'")
                        m = re.match(r"pattern: '([^']+)',?", stripped)
                        if m:
                            current_skill['pattern'] = m.group(1)
                        
                        # Bonuses
                        for stat in ['ATK', 'DEF', 'SPD']:
                            m = re.match(rf"{stat}: (\d+),?", stripped)
                            if m:
                                if 'bonuses' not in current_skill:
                                    current_skill['bonuses'] = {}
                                current_skill['bonuses'][stat] = int(m.group(1))
                        
                        # Traits array
                        if "traits: [" in stripped:
                            current_skill['traits'] = []
                        elif 'traits' in current_skill and stripped.startswith("'"):
                            m = re.match(r"'([^']+)',?", stripped)
                            if m:
                                current_skill['traits'].append(m.group(1).replace("\\'", "'"))
                        
                        # End of skill
                        if skill_brace_depth == 0 and stripped.startswith('}'):
                            data['skills'].append(current_skill)
                            current_skill = None
        
        with open(output_dir / 'classes.json', 'w', encoding='utf-8') as f:
            json.dump({'classes': classes}, f, indent=2, ensure_ascii=False)
        print(f"  OK: {len(classes)} classes")
    
    # ===== RUNES DATA =====
    print("Extracting runesData...")
    runes_section = re.search(r"const runesData = \{([\s\S]*?)\n\};", content)
    if runes_section:
        runes = {}
        current = None
        data = {}
        brace_depth = 0
        
        for line in runes_section.group(1).split('\n'):
            stripped = line.strip()
            
            # New rune entry
            m = re.match(r"'(\d+-\w+)': \{", stripped)
            if m and brace_depth == 0:
                if current:
                    runes[current] = data
                current = m.group(1)
                data = {}
                brace_depth = 1
                continue
            
            if current:
                brace_depth += stripped.count('{') - stripped.count('}')
                
                # Name
                m = re.match(r"name: '([^']+)',?", stripped)
                if m:
                    data['name'] = m.group(1)
                
                # Description
                m = re.match(r"description: '([^']+)',?", stripped)
                if m:
                    data['description'] = m.group(1).replace("\\'", "'")
                
                # Effect
                m = re.match(r"effect: '([^']+)',?", stripped)
                if m:
                    data['effect'] = m.group(1)
                
                if brace_depth == 0:
                    runes[current] = data
                    current = None
        
        # Add intro/cypher
        intro_match = re.search(r"intro: \{([\s\S]*?)\},", runes_section.group(1))
        if intro_match:
            intro = {}
            for m in re.finditer(r"(\w+): '([^']+)'", intro_match.group(1)):
                intro[m.group(1)] = m.group(2).replace("\\'", "'")
            runes['intro'] = intro
        
        cypher_match = re.search(r"cypher: \{([\s\S]*?)\n    \},", runes_section.group(1))
        if cypher_match:
            cypher = {'vowel_map': {}, 'consonant_map': {}}
            for m in re.finditer(r"(\w): '([A-Z])'", cypher_match.group(1)):
                if m.group(1) in 'AEIOUY':
                    cypher['vowel_map'][m.group(1)] = m.group(2)
                else:
                    cypher['consonant_map'][m.group(1)] = m.group(2)
            runes['cypher'] = cypher
        
        with open(output_dir / 'runes.json', 'w', encoding='utf-8') as f:
            json.dump({'runes': runes}, f, indent=2, ensure_ascii=False)
        print(f"  OK: {len([k for k in runes if k not in ['intro','cypher']])} runes")
    
    print("\nExtraction complete!")

if __name__ == '__main__':
    extract_data()
