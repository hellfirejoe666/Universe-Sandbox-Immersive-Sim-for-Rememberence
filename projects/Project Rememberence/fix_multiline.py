# fix_multiline.py - Fix multi-line strings and escape quotes in JSON
import re
import json
from pathlib import Path

def fix_json_file(filepath):
    """Fix a JSON file with multi-line strings and unescaped quotes."""
    print(f"Fixing {filepath.name}...")
    
    content = filepath.read_text(encoding='utf-8')
    
    # Step 1: Join multi-line strings
    # Pattern: A line ending with "text (no closing quote) followed by continuation
    lines = content.split('\n')
    joined_lines = []
    buffer = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if buffer is not None:
            # We're continuing a multi-line string
            stripped = line.strip()
            
            # Check if this line ends the string (has closing quote followed by comma/brace)
            if stripped.endswith('",') or stripped.endswith('"}'):
                # Remove the closing quote from this line and add to buffer
                if stripped.endswith('",'):
                    buffer += ' ' + stripped[:-2]
                    joined_lines.append(buffer + '",')
                elif stripped.endswith('"}'):
                    buffer += ' ' + stripped[:-2]
                    joined_lines.append(buffer + '"}')
                buffer = None
            else:
                # Continue accumulating
                buffer += ' ' + stripped
            i += 1
            continue
        
        # Check if this line starts a string that doesn't end
        match = re.match(r'^(\s*"[^"]+"\s*:\s*")(.+?)"?([,\s]*?)$', line)
        if match:
            prefix = match.group(1)
            value = match.group(2)
            suffix = match.group(3)
            
            # If value ends with quote, it's complete
            if value.endswith('"') or suffix.strip().startswith(','):
                joined_lines.append(line)
            else:
                # Multi-line string starts
                buffer = prefix + value
                i += 1
                continue
        else:
            joined_lines.append(line)
        
        i += 1
    
    content = '\n'.join(joined_lines)
    
    # Step 2: Escape quotes inside string values
    final_lines = []
    for line in content.split('\n'):
        # Match: "key": "value"
        match = re.match(r'^(\s*"[^"]+"\s*:\s*")(.*)(",?\s*)$', line)
        if match:
            prefix = match.group(1)
            value = match.group(2)
            suffix = match.group(3)
            
            # Remove surrounding quotes from value
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            
            # Escape backslashes first, then quotes
            value = value.replace('\\', '\\\\').replace('"', '\\"')
            
            line = prefix + '"' + value + '"' + suffix
        
        final_lines.append(line)
    
    fixed = '\n'.join(final_lines)
    
    # Write and validate
    filepath.write_text(fixed, encoding='utf-8')
    
    try:
        json.loads(fixed)
        print(f"  SUCCESS - {filepath.name}")
        return True
    except json.JSONDecodeError as e:
        print(f"  FAILED - {filepath.name}: line {e.lineno}, col {e.colno}")
        # Show context
        ctx_lines = fixed.split('\n')
        if e.lineno <= len(ctx_lines):
            print(f"    Context: {repr(ctx_lines[e.lineno-1][:80])}")
        return False

if __name__ == '__main__':
    data_dir = Path(__file__).parent / 'data'
    
    files = ['species.json', 'types.json', 'classes.json', 'runes.json']
    
    results = {}
    for filename in files:
        filepath = data_dir / filename
        if filepath.exists():
            results[filename] = fix_json_file(filepath)
        else:
            print(f"Not found: {filepath}")
    
    print("\n" + "="*50)
    for name, ok in results.items():
        status = "OK" if ok else "FAILED"
        print(f"{name}: {status}")
