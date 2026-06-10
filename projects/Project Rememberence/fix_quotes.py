# fix_quotes.py - Properly escape quotes in JSON string values
import re
from pathlib import Path
import json

def smart_fix(filepath):
    """Fix JSON by properly escaping quotes in string values."""
    print(f"Processing {filepath.name}...")
    
    content = filepath.read_text(encoding='utf-8')
    
    # Strategy: Parse line by line, fix string values
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Match lines like: "key": "value with quotes",
        # or: "key": "value"
        match = re.match(r'^(\s*"[^"]+"\s*:\s*")(.*)("$|",?$)', line)
        if match:
            prefix = match.group(1)  # '      "key": "'
            value = match.group(2)    # The actual value text
            suffix = match.group(3)   # '"' or '",'
            
            # Escape quotes and backslashes in the value
            value = value.replace('\\', '\\\\').replace('"', '\\"')
            
            line = prefix + value + suffix
        
        fixed_lines.append(line)
    
    fixed = '\n'.join(fixed_lines)
    filepath.write_text(fixed, encoding='utf-8')
    
    # Validate
    try:
        json.loads(fixed)
        print(f"  OK - {filepath.name}")
        return True
    except json.JSONDecodeError as e:
        print(f"  FAILED - {filepath.name}: {e}")
        return False

if __name__ == '__main__':
    data_dir = Path(__file__).parent / 'data'
    
    files = ['species.json', 'types.json', 'classes.json', 'runes.json']
    
    all_ok = True
    for filename in files:
        filepath = data_dir / filename
        if filepath.exists():
            if not smart_fix(filepath):
                all_ok = False
        else:
            print(f"Not found: {filepath}")
    
    if all_ok:
        print("\nAll files fixed successfully!")
    else:
        print("\nSome files still have errors.")
