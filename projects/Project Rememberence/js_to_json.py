# js_to_json.py - Convert constants.js to proper JSON files
import re
import json
from pathlib import Path

def parse_js_value(value_str):
    """Parse a JS value string to Python."""
    value_str = value_str.strip()
    if value_str.startswith("'") and value_str.endswith("'"):
        return value_str[1:-1].replace("\\'", "'")
    if value_str.isdigit():
        return int(value_str)
    return value_str

def extract_nested_object(text, start_pos):
    """Extract a nested JS object starting at start_pos."""
    if text[start_pos] != '{':
        return None, start_pos
    
    depth = 0
    end_pos = start_pos
    
    for i in range(start_pos, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[start_pos:i+1], i+1
    
    return None, start_pos

def parse_js_object(obj_text):
    """Parse a JS object literal to Python dict."""
    result = {}
    
    # Remove outer braces
    obj_text = obj_text.strip()[1:-1].strip()
    
    # Simple pattern for key: value pairs (handles nested objects)
    pos = 0
    while pos < len(obj_text):
        # Skip whitespace and commas
        while pos < len(obj_text) and obj_text[pos] in ' \t\n,':
            pos += 1
        
        if pos >= len(obj_text):
            break
        
        # Find key
        key_match = re.match(r"'([^']+)'", obj_text[pos:])
        if not key_match:
            pos += 1
            continue
        
        key = key_match.group(1)
        pos += key_match.end()
        
        # Skip : and whitespace
        while pos < len(obj_text) and obj_text[pos] in ' \t\n:':
            pos += 1
        
        # Check if value is nested object or array
        if pos < len(obj_text) and obj_text[pos] in '{[':
            value_text, new_pos = extract_nested_object(obj_text, pos)
            if value_text:
                if obj_text[pos] == '{':
                    result[key] = parse_js_object(value_text)
                else:
                    # Array - parse as list
                    result[key] = [parse_js_value(v.strip()) for v in value_text[1:-1].split(',') if v.strip()]
                pos = new_pos
            else:
                pos += 1
        else:
            # Simple value
            value_match = re.match(r"'[^']*'|\d+", obj_text[pos:])
            if value_match:
                result[key] = parse_js_value(value_match.group(0))
                pos += value_match.end()
            else:
                pos += 1
    
    return result

def main():
    js_path = Path(r'D:\cards\AI Prompts\Oracle Project\Project Files\constants.js')
    output_dir = Path(__file__).parent / 'data'
    
    content = js_path.read_text(encoding='utf-8')
    
    # ===== ANIMAL SIGNS =====
    print("Extracting animalSigns...")
    match = re.search(r"const animalSigns = (\{[\s\S]*?\});", content)
    if match:
        animals = parse_js_object(match.group(1))
        with open(output_dir / 'animal_signs.json', 'w', encoding='utf-8') as f:
            json.dump({'animalSigns': animals}, f, indent=2)
        print(f"  OK: {len(animals)} animal signs")
    
    # ===== STAR SIGNS =====
    print("Extracting starSigns...")
    match = re.search(r"const starSigns = (\{[\s\S]*?\});", content)
    if match:
        stars = parse_js_object(match.group(1))
        with open(output_dir / 'star_signs.json', 'w', encoding='utf-8') as f:
            json.dump({'starSigns': stars}, f, indent=2)
        print(f"  OK: {len(stars)} star signs")
    
    # ===== SPECIES DATA =====
    print("Extracting speciesData...")
    match = re.search(r"const speciesData = (\{[\s\S]*?\n\});", content)
    if match:
        species = parse_js_object(match.group(1))
        with open(output_dir / 'species.json', 'w', encoding='utf-8') as f:
            json.dump({'species': species}, f, indent=2, ensure_ascii=False)
        print(f"  OK: {len(species)} species")
    
    # ===== TYPE DATA =====
    print("Extracting typeData...")
    match = re.search(r"const typeData = (\{[\s\S]*?\n\});", content)
    if match:
        types = parse_js_object(match.group(1))
        with open(output_dir / 'types.json', 'w', encoding='utf-8') as f:
            json.dump({'types': types}, f, indent=2, ensure_ascii=False)
        print(f"  OK: {len(types)} types")
    
    # ===== CLASS DATA =====
    print("Extracting classData...")
    match = re.search(r"const classData = (\{[\s\S]*?\n\});", content)
    if match:
        classes = parse_js_object(match.group(1))
        with open(output_dir / 'classes.json', 'w', encoding='utf-8') as f:
            json.dump({'classes': classes}, f, indent=2, ensure_ascii=False)
        print(f"  OK: {len(classes)} classes")
    
    # ===== RUNES DATA =====
    print("Extracting runesData...")
    match = re.search(r"const runesData = (\{[\s\S]*?\n\});", content)
    if match:
        runes = parse_js_object(match.group(1))
        with open(output_dir / 'runes.json', 'w', encoding='utf-8') as f:
            json.dump({'runes': runes}, f, indent=2, ensure_ascii=False)
        print(f"  OK: {len(runes)} runes")
    
    print("\nExtraction complete!")
    print("\nValidating files...")
    
    # Validate all files
    for filename in ['animal_signs.json', 'star_signs.json', 'species.json', 'types.json', 'classes.json', 'runes.json']:
        try:
            data = json.load(open(output_dir / filename))
            key = list(data.keys())[0]
            print(f"  {filename}: {len(data[key])} entries")
        except Exception as e:
            print(f"  {filename}: ERROR - {e}")

if __name__ == '__main__':
    main()
