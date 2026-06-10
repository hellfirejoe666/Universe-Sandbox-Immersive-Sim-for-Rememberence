# fix_double_quotes.py - Fix double-quoted strings
import re
from pathlib import Path

def fix(filepath):
    content = filepath.read_text(encoding='utf-8')
    
    # Replace ""word"" with "word"
    content = re.sub(r'""([^"]+)""', r'"\1"', content)
    
    # Replace "" with " (standalone)
    content = content.replace('""', '"')
    
    filepath.write_text(content, encoding='utf-8')
    print(f"Fixed {filepath.name}")

if __name__ == '__main__':
    data_dir = Path(__file__).parent / 'data'
    
    for filename in ['species.json', 'types.json', 'classes.json', 'runes.json']:
        filepath = data_dir / filename
        if filepath.exists():
            fix(filepath)
    
    print("Done!")
