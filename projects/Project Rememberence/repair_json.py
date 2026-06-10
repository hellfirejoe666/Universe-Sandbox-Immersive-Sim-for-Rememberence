# repair_json.py - Repair corrupted JSON files from fix attempts
import re
from pathlib import Path

def repair_file(filepath):
    """Repair a JSON file that was corrupted by over-escaping."""
    print(f"Repairing {filepath.name}...")
    
    content = filepath.read_text(encoding='utf-8')
    
    lines = content.split('\n')
    repaired = []
    
    for line in lines:
        # Fix double-escaped quotes: ""word"" -> "word"
        # Pattern: "" followed by word followed by ""
        line = re.sub(r'""([^"]+)""', r'"\1"', line)
        
        # Fix over-escaped quotes in values: \"word\" -> "word" (when it's the whole value)
        # But keep escaped quotes that are inside strings
        match = re.match(r'^(\s*"[^"]+"\s*:\s*)"(.*)"(,?\s*)$', line)
        if match:
            prefix = match.group(1)
            value = match.group(2)
            suffix = match.group(3)
            
            # If value is just escaped quotes around a simple string, unescape
            if value.startswith('\\"') and value.endswith('\\"') and '\\"' not in value[2:-2]:
                value = value[2:-2]  # Remove the outer escaped quotes
                line = prefix + '"' + value + '"' + suffix
        
        repaired.append(line)
    
    fixed = '\n'.join(repaired)
    filepath.write_text(fixed, encoding='utf-8')
    print(f"  Repaired {filepath.name}")

if __name__ == '__main__':
    data_dir = Path(__file__).parent / 'data'
    
    files = ['species.json', 'types.json', 'classes.json', 'runes.json']
    
    for filename in files:
        filepath = data_dir / filename
        if filepath.exists():
            repair_file(filepath)
    
    print("\nDone! Files repaired. Now run fix_multiline.py")
