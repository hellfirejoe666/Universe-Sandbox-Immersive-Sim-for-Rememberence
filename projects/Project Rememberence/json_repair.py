# json_repair.py - Robust JSON repair for multiline strings and escape issues
import re
from pathlib import Path

def repair_json_content(content):
    """
    Repair JSON content with:
    1. Multiline strings (join with \n escape)
    2. Unescaped quotes inside strings
    3. Double-quoted strings from previous fix attempts
    """
    lines = content.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Skip empty lines and structural lines
        stripped = line.strip()
        if not stripped or stripped in ['{', '}', '[', ']']:
            result.append(line)
            i += 1
            continue
        
        # Check for key-value pair with string value
        match = re.match(r'^(\s*)("([^"]+)")\s*:\s*(.*)$', line)
        if match:
            indent = match.group(1)
            key_full = match.group(2)  # "key"
            key_name = match.group(3)  # key
            value_part = match.group(4)  # The value
            
            # Check if value starts with quote (string value)
            if value_part.startswith('"'):
                # Find the complete string value (may span multiple lines)
                string_start = i
                string_content = value_part[1:]  # Remove opening quote
                
                # Check if string ends on this line
                if value_part.endswith('",') or value_part.endswith('"}') or value_part.endswith('"'):
                    # Single line string - just need to fix escapes
                    if value_part.endswith('",'):
                        string_content = value_part[1:-2]
                        suffix = '", '
                    elif value_part.endswith('"}'):
                        string_content = value_part[1:-2]
                        suffix = '"}'
                    elif value_part.endswith('"'):
                        string_content = value_part[1:-1]
                        suffix = '"'
                    else:
                        result.append(line)
                        i += 1
                        continue
                    
                    # Fix double quotes from previous repairs
                    string_content = string_content.replace('""', '"')
                    
                    # Escape internal quotes and backslashes properly
                    string_content = string_content.replace('\\', '\\\\').replace('"', '\\"')
                    
                    # Escape control characters
                    string_content = string_content.replace('\t', '\\t').replace('\r', '\\r')
                    
                    result.append(f'{indent}{key_full}: "{string_content}{suffix}')
                    i += 1
                    continue
                else:
                    # Multiline string - collect all lines until closing quote
                    i += 1
                    while i < len(lines):
                        next_line = lines[i].strip()
                        if next_line.endswith('",') or next_line.endswith('"}') or next_line.endswith('"'):
                            # Last line of multiline string
                            if next_line.endswith('",'):
                                string_content += ' ' + next_line[:-2]
                                suffix = '", '
                            elif next_line.endswith('"}'):
                                string_content += ' ' + next_line[:-2]
                                suffix = '"}'
                            else:
                                string_content += ' ' + next_line[:-1]
                                suffix = '"'
                            break
                        else:
                            # Continue line
                            string_content += ' ' + next_line
                            i += 1
                    
                    # Fix and escape
                    string_content = string_content.replace('""', '"')
                    string_content = string_content.replace('\\', '\\\\').replace('"', '\\"')
                    string_content = string_content.replace('\t', '\\t').replace('\r', '\\r')
                    
                    result.append(f'{indent}{key_full}: "{string_content}{suffix}')
                    i += 1
                    continue
        
        result.append(line)
        i += 1
    
    return '\n'.join(result)

def repair_file(filepath):
    """Repair a JSON file."""
    print(f"Repairing {filepath.name}...")
    
    content = filepath.read_text(encoding='utf-8')
    fixed = repair_json_content(content)
    
    filepath.write_text(fixed, encoding='utf-8')
    
    # Validate
    import json
    try:
        json.loads(fixed)
        print(f"  SUCCESS - {filepath.name}")
        return True
    except json.JSONDecodeError as e:
        print(f"  FAILED - {filepath.name}: line {e.lineno}, col {e.colno}")
        print(f"    Error: {e.msg}")
        ctx = fixed.split('\n')
        if e.lineno <= len(ctx):
            print(f"    Line: {repr(ctx[e.lineno-1][:100])}")
        return False

if __name__ == '__main__':
    import json
    from pathlib import Path
    
    data_dir = Path(__file__).parent / 'data'
    
    # First validate the good files
    print("=== Validating existing files ===")
    for filename in ['animal_signs.json', 'star_signs.json']:
        filepath = data_dir / filename
        try:
            json.load(open(filepath, 'r', encoding='utf-8'))
            print(f"  OK - {filename}")
        except Exception as e:
            print(f"  ERROR - {filename}: {e}")
    
    # Then repair the broken ones
    print("\n=== Repairing broken files ===")
    files = ['species.json', 'types.json', 'classes.json', 'runes.json']
    
    for filename in files:
        filepath = data_dir / filename
        if filepath.exists():
            repair_file(filepath)
