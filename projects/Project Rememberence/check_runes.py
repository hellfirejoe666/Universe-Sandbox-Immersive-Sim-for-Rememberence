import re
from pathlib import Path

js_path = Path(r'D:\cards\AI Prompts\Oracle Project\Project Files\constants.js')
content = js_path.read_text(encoding='utf-8')

m = re.search(r'const runesData = \{([\s\S]*?)\n\};', content)
if m:
    runes = re.findall(r"'(\w+)': \{", m.group(1))
    print(f'Runes in JS: {len(runes)}')
    print(runes)
