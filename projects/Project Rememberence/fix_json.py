# fix_json.py
# Fix JSON syntax errors in Rememberence data files
# Handles unescaped quotes in string values

import json
import re
from pathlib import Path

def fix_json_file(filepath):
    """Attempt to fix common JSON syntax errors in a file."""
    print(f"Processing {filepath.name}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix unescaped quotes inside string values
    # Pattern: Find quotes that are inside strings (not key delimiters)
    # This is a simplified fix - looks for quotes after colons that aren't escaped
    
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Skip lines that are just structural
        stripped = line.strip()
        if stripped in ['{', '}', '[', ']', ''] or stripped.endswith(': {') or stripped.endswith(': ['):
            fixed_lines.append(line)
            continue
        
        # Check if this is a value line (has colon and quotes)
        if ':' in line and '"' in line:
            # Find the value part (after the colon)
            colon_idx = line.find(':')
            value_part = line[colon_idx+1:].strip()
            
            # If value starts with quote, it's a string value
            if value_part.startswith('"'):
                # Check for unescaped quotes in the middle
                # Pattern: "text "word" more text"
                # We need to escape inner quotes
                
                # Simple approach: find the key and escape quotes in value
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0]
                    value = parts[1]
                    
                    # Count quotes - should be even for valid JSON
                    quote_count = value.count('"')
                    
                    # If odd number of quotes and not ending with ", fix it
                    if quote_count > 1:
                        # Check if it's a multiline string issue
                        # For now, escape quotes that aren't at start/end
                        if not value.strip().endswith(','):
                            # This might be a multiline string - skip for now
                            fixed_lines.append(line)
                            continue
                        
                        # Escape inner quotes
                        value_chars = list(value)
                        first_quote = value.find('"')
                        last_quote = value.rfind('"')
                        
                        if first_quote >= 0 and last_quote > first_quote:
                            for j in range(first_quote + 1, last_quote):
                                if value_chars[j] == '"' and (j == 0 or value_chars[j-1] != '\\'):
                                    value_chars[j] = '\\"'
                            
                            line = key + ':' + ''.join(value_chars)
        
        fixed_lines.append(line)
    
    fixed_content = '\n'.join(fixed_lines)
    
    # Try to parse - if still fails, use a more aggressive approach
    try:
        json.loads(fixed_content)
        print(f"  ✓ Fixed with simple approach")
    except json.JSONDecodeError as e:
        print(f"  ⚠ Simple fix failed: {e}")
        # Try alternative: use regex to escape quotes in descriptions
        fixed_content = fix_descriptions_aggressive(original)
        try:
            json.loads(fixed_content)
            print(f"  ✓ Fixed with aggressive approach")
        except json.JSONDecodeError as e2:
            print(f"  ✗ Aggressive fix also failed: {e2}")
            return False
    
    # Write fixed file
    if fixed_content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"  → File updated")
    
    return True


def fix_descriptions_aggressive(content):
    """More aggressive fix for description fields with quotes."""
    # Find all description fields and escape quotes within them
    pattern = r'("description":\s*")([^"]*(?:"[^",\]]+[^"]*)*)(?<!\\)"'
    
    def escape_inner_quotes(match):
        prefix = match.group(1)
        text = match.group(2)
        # Escape any unescaped quotes in the text
        text = re.sub(r'(?<!\\)"', r'\\"', text)
        return f'{prefix}{text}"'
    
    fixed = re.sub(pattern, escape_inner_quotes, content, flags=re.DOTALL)
    return fixed


if __name__ == '__main__':
    data_dir = Path(__file__).parent / 'data'
    
    files_to_fix = [
        data_dir / 'species.json',
        data_dir / 'types.json',
        data_dir / 'classes.json',
        data_dir / 'runes.json'
    ]
    
    print("=== JSON Fixer for Rememberence Data ===\n")
    
    for filepath in files_to_fix:
        if filepath.exists():
            fix_json_file(filepath)
        else:
            print(f"⚠ Not found: {filepath}")
    
    print("\n=== Validation ===")
    # Validate all files
    for filepath in data_dir.glob('*.json'):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                json.load(f)
            print(f"✓ {filepath.name} - Valid JSON")
        except json.JSONDecodeError as e:
            print(f"✗ {filepath.name} - INVALID: {e}")
