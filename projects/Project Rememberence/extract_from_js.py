# extract_from_js.py - Extract data from constants.js and generate clean JSON
import re
import json
from pathlib import Path

def parse_js_to_json():
    """Parse constants.js and extract data as JSON."""
    
    js_path = Path(r'D:\cards\AI Prompts\Oracle Project\Project Files\constants.js')
    output_dir = Path(__file__).parent / 'data'
    
    content = js_path.read_text(encoding='utf-8')
    
    # Extract animalSigns
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
        print(f"  Saved {len(animals)} animal signs")
    
    # Extract starSigns
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
        print(f"  Saved {len(stars)} star signs")
    
    # Extract speciesData
    print("Extracting speciesData...")
    # This is more complex - need to handle nested structures
    species_match = re.search(r"const speciesData = \{([\s\S]*?)\n\};", content)
    if species_match:
        species_content = species_match.group(1)
        species = {}
        
        # Split by species entries
        current_species = None
        current_data = {}
        brace_count = 0
        in_traits = False
        current_trait_list = None
        current_trait_name = None
        
        lines = species_content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # New species entry
            species_key_match = re.match(r"'(\w+)': \{", line)
            if species_key_match and brace_count == 0:
                if current_species:
                    species[current_species] = current_data
                current_species = species_key_match.group(1)
                current_data = {'traits': {'active': [], 'passive': []}}
                brace_count = 1
                i += 1
                continue
            
            if current_species:
                # Count braces
                brace_count += line.count('{') - line.count('}')
                
                # Parse stats
                stat_match = re.match(r"(HP|ATK|DEF|SPD|MP): (\d+),?", line)
                if stat_match:
                    if 'stats' not in current_data:
                        current_data['stats'] = {}
                    current_data['stats'][stat_match.group(1)] = int(stat_match.group(2))
                
                # Parse Move
                move_match = re.match(r"Move: '([^']+)',?", line)
                if move_match:
                    if 'stats' not in current_data:
                        current_data['stats'] = {}
                    current_data['stats']['Move'] = move_match.group(1)
                
                # Parse traits
                if 'traits:' in line:
                    in_traits = True
                
                if in_traits:
                    # Active traits array
                    if "active: [" in line:
                        current_trait_list = 'active'
                    elif "passive: [" in line:
                        current_trait_list = 'passive'
                    elif line.startswith("]"):
                        current_trait_list = None
                    elif current_trait_list and line.startswith("'"):
                        # Extract trait text
                        trait_match = re.match(r"'([^']+)',?", line)
                        if trait_match:
                            trait_text = trait_match.group(1).replace("\\'", "'")
                            current_data['traits'][current_trait_list].append(trait_text)
                
                if brace_count == 0:
                    species[current_species] = current_data
                    current_species = None
            
            i += 1
        
        with open(output_dir / 'species.json', 'w', encoding='utf-8') as f:
            json.dump({'species': species}, f, indent=2, ensure_ascii=False)
        print(f"  Saved {len(species)} species")
    
    print("\nExtraction complete!")

if __name__ == '__main__':
    parse_js_to_json()
