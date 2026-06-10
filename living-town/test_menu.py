"""
Quick Menu Test - Verify menu tree structure
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from menu_system import main_menu

if __name__ == '__main__':
    print("Testing Menu Tree...")
    print("Navigate the menu, then choose 'Exit' or press Ctrl+C")
    print("=" * 60)
    
    try:
        main_menu()
    except (KeyboardInterrupt, EOFError) as e:
        print(f"\n[Exit: {type(e).__name__}]")
    
    print("\nMenu test complete.")
    sys.exit(0)
