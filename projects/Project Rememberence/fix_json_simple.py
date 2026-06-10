# fix_json_simple.py
# Fix unescaped quotes in JSON string values

import re
from pathlib import Path

def fix_file(filepath):
    """Fix unescaped quotes inside JSON string values."""
    print(f"Fixing {filepath.name}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match string values that have unescaped quotes
    # Look for: "key": "value with "inner quotes" more value"
    # We need to escape the inner quotes
    
    fixed = content
    
    # Find all lines with colons and quotes
    lines = fixed.split('\n')
    new_lines = []
    
    for line in lines:
        # Only process lines that look like string values
        if '": "' in line or '":"' in line:
            # Find the value part after the colon
            if '": "' in line:
                idx = line.find('": "') + 4
            else:
                idx = line.find('":"') + 3
            
            # Get everything before the value start
            prefix = line[:idx-1]
            value_and_suffix = line[idx-1:]
            
            # Find where the value ends (comma or end of object)
            # Look for the last quote that's followed by comma or closing brace
            end_match = re.search(r'"[\s]*[,}]', value_and_suffix[::-1])
            
            if end_match:
                # Extract just the value string
                value_end = len(value_and_suffix) - end_match.start() - 1
                value = value_and_suffix[:value_end]
                suffix = value_and_suffix[value_end:]
                
                # Escape quotes inside the value (but not the boundary quotes)
                inner_value = value[1:-1]  # Remove boundary quotes
                inner_value = inner_value.replace('"', '\\"')
                value = '"' + inner_value + '"'
                
                line = prefix + value + suffix
        
        new_lines.append(line)
    
    fixed = '\n'.join(new_lines)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(fixed)
    
    print(f"  Fixed {filepath.name}")


if __name__ == '__main__':
    data_dir = Path(__file__).parent / 'data'
    
    files = [
        'species.json',
        'types.json', 
        'classes.json',
        'runes.json'
    ]
    
    for filename in files:
        filepath = data_dir / filename
        if filepath.exists():
            fix_file(filepath)
        else:
            print(f"Not found: {filepath}")
    
    print("\nDone! Try running data_loader.py again.")
