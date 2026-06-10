"""
Data Loader - Canonical Game Data
==================================
Loads JSON data files for Rememberence game data.
Centralized loading with caching.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class DataLoader:
    """
    Loads and caches game data from JSON files.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize data loader.
        
        Args:
            data_dir: Path to data directory (defaults to living-town/data/)
        """
        if data_dir is None:
            data_dir = Path(__file__).parent / 'data'
        
        self.data_dir = Path(data_dir)
        self.cache: Dict[str, Any] = {}
        self._load_all()
    
    def _load_all(self):
        """Pre-load all data files."""
        files = [
            'animal_signs.json',
            'star_signs.json',
            'species.json',
            'types.json',
            'classes.json',
            'runes.json',
            'narrative_verses.json',
        ]
        
        for filename in files:
            filepath = self.data_dir / filename
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        key = filename.replace('.json', '')
                        self.cache[key] = data
                        print(f"[DataLoader] Loaded {filename}")
                except Exception as e:
                    print(f"[DataLoader] Error loading {filename}: {e}")
            else:
                print(f"[DataLoader] Warning: {filename} not found")
    
    def get(self, data_type: str, key: Optional[str] = None) -> Any:
        """
        Get data by type and optional key.
        
        Args:
            data_type: Type of data (animal_signs, star_signs, species, etc.)
            key: Specific key within data type (e.g., 'Dragon', 'Aries')
        
        Returns:
            Data dict or None if not found
        """
        data = self.cache.get(data_type)
        
        if data is None:
            return None
        
        if key is None:
            return data
        
        # Handle nested structures
        if data_type in ['animal_signs', 'star_signs']:
            return data.get(data_type, {}).get(key)
        elif data_type in ['species', 'types', 'classes', 'runes']:
            return data.get(data_type, {}).get(key)
        else:
            return data.get(key)
    
    def get_animal_sign(self, name: str) -> Optional[Dict]:
        """Get animal sign data by name."""
        data = self.cache.get('animal_signs', {})
        return data.get('animalSigns', {}).get(name)
    
    def get_star_sign(self, name: str) -> Optional[Dict]:
        """Get star sign data by name."""
        data = self.cache.get('star_signs', {})
        return data.get('starSigns', {}).get(name)
    
    def get_species(self, name: str) -> Optional[Dict]:
        """Get species data by name."""
        return self.get('species', name)
    
    def get_type(self, name: str) -> Optional[Dict]:
        """Get type data by name."""
        return self.get('types', name)
    
    def get_class(self, name: str) -> Optional[Dict]:
        """Get class data by name."""
        return self.get('classes', name)
    
    def get_rune(self, name: str) -> Optional[Dict]:
        """Get rune data by name."""
        return self.get('runes', name)
    
    def get_all_animal_signs(self) -> Dict:
        """Get all animal signs."""
        data = self.cache.get('animal_signs', {})
        return data.get('animalSigns', {})
    
    def get_all_star_signs(self) -> Dict:
        """Get all star signs."""
        data = self.cache.get('star_signs', {})
        return data.get('starSigns', {})
    
    def get_all_species(self) -> Dict:
        """Get all species."""
        data = self.cache.get('species', {})
        return data.get('species', {})
    
    def get_all_types(self) -> Dict:
        """Get all types."""
        data = self.cache.get('types', {})
        return data.get('types', {})
    
    def get_all_classes(self) -> Dict:
        """Get all classes."""
        data = self.cache.get('classes', {})
        return data.get('classes', {})
    
    def get_all_runes(self) -> Dict:
        """Get all runes."""
        data = self.cache.get('runes', {})
        return data.get('runes', {})
    
    def get_narrative_verses(self) -> Dict:
        """Get narrative verses."""
        return self.cache.get('narrative_verses', {})


# Global instance (lazy loaded)
_loader: Optional[DataLoader] = None


def get_loader() -> DataLoader:
    """Get or create global data loader instance."""
    global _loader
    if _loader is None:
        _loader = DataLoader()
    return _loader


def load_data(data_type: str, key: Optional[str] = None) -> Any:
    """Convenience function to load data."""
    return get_loader().get(data_type, key)


# ────────────────────────────────────────────────
# Test
# ────────────────────────────────────────────────

if __name__ == '__main__':
    print("Testing DataLoader...")
    
    loader = DataLoader()
    
    print("\nAnimal Signs:")
    for name in ['Dragon', 'Tiger', 'Rat']:
        data = loader.get_animal_sign(name)
        if data:
            bio = data.get('biorhythms', {})
            print(f"  {name}: MNF={bio.get('MNF', '?')}, EGO={bio.get('EGO', '?')}")
    
    print("\nStar Signs:")
    for name in ['Aries', 'Leo', 'Scorpio']:
        data = loader.get_star_sign(name)
        if data:
            bio = data.get('biorhythms', {})
            print(f"  {name}: STR={bio.get('STR', '?')}, VIT={bio.get('VIT', '?')}")
    
    print("\nSpecies count:", len(loader.get_all_species()))
    print("Types count:", len(loader.get_all_types()))
    print("Classes count:", len(loader.get_all_classes()))
    print("Runes count:", len(loader.get_all_runes()))
