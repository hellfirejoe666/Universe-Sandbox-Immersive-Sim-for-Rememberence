"""
Perchance AI Router for AIR-AI Oracle
Integrates Perchance.org generators into the Rememberence hybrid router system

Features:
- Routes requests between Perchance generators and local GPT4All models
- Caches Perchance outputs for common game elements
- Supports character names, quest generation, item creation, narrative elements
- Rate-limited API access with fallback to local generation
- Seamless integration with existing queue_manager.py
"""

import requests
import json
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import random


class PerchanceRouter:
    """
    Router for Perchance AI generators integrated with Rememberence.
    
    Perchance API: https://perchance.org/api/generateList.php?generator=NAME&count=N
    
    Generators for Rememberence:
    - fantasy-character: Character names and descriptions
    - fantasy-plot: Quest/story ideas
    - fantasy-name: Place/item names
    - ai-character-chat: Interactive NPC dialogue
    """
    
    # Perchance API endpoint
    API_BASE = "https://perchance.org/api/generateList.php"
    
    # Generator mappings for Rememberence game elements
    GENERATOR_MAP = {
        # Character generation
        "character_name": {
            "generator": "fantasy-name",
            "params": {"count": 1},
            "cache_ttl": 3600,  # 1 hour
            "category": "character"
        },
        "character_description": {
            "generator": "fantasy-character",
            "params": {"count": 1},
            "cache_ttl": 1800,  # 30 min
            "category": "character"
        },
        "npc_dialogue": {
            "generator": "ai-character-chat",
            "params": {"count": 1},
            "cache_ttl": 300,  # 5 min (dynamic content)
            "category": "dialogue"
        },
        
        # Quest/Narrative generation
        "quest_idea": {
            "generator": "fantasy-plot",
            "params": {"count": 1},
            "cache_ttl": 7200,  # 2 hours
            "category": "narrative"
        },
        "plot_twist": {
            "generator": "plot-twist",
            "params": {"count": 1},
            "cache_ttl": 3600,
            "category": "narrative"
        },
        "story_prompt": {
            "generator": "writing-prompt",
            "params": {"count": 1},
            "cache_ttl": 1800,
            "category": "narrative"
        },
        
        # World building
        "place_name": {
            "generator": "fantasy-name",
            "params": {"count": 1, "type": "place"},
            "cache_ttl": 7200,
            "category": "world"
        },
        "item_name": {
            "generator": "fantasy-name",
            "params": {"count": 1, "type": "item"},
            "cache_ttl": 3600,
            "category": "world"
        },
        "realm_description": {
            "generator": "fantasy-world",
            "params": {"count": 1},
            "cache_ttl": 7200,
            "category": "world"
        },
        
        # Species-specific (Rememberence integration)
        "species_trait": {
            "generator": "fantasy-race",
            "params": {"count": 1},
            "cache_ttl": 3600,
            "category": "species",
            "species_map": {
                "Avious": "bird-like wise messenger",
                "Merr": "water spirit siren",
                "Geneshan": "peaceful life guardian",
                "Iniris": "lucky trickster wanderer",
                "Reptoid": "cunning manipulator",
                "Wolfin": "loyal pack protector",
                "Goki": "proud warrior",
                "Tigris": "majestic spiritual guide",
                "Demon": "chaotic shadow being",
                "Grimm": "death guide psychopomp",
                "Drakian": "ancient dragon sage",
                "Chimera": "chaotic amalgamation",
                "Mannequin": "faceless void puppet",
                "Pixie": "mischievous illusion weaver",
                "Grizzly": "fierce protective teacher",
                "Faun": "truth-seeking mystic",
                "Vampyre": "blood-craving predator",
                "Grey": "primordial ancestor",
                "Chrono": "timeless keeper",
                "Gargoyle": "cursed stone guardian",
                "Mimic": "deceptive shapeshifter",
                "Elf": "magical word architect",
                "Ghoul": "vengeful madness",
                "Bastet": "cat spirit underworld guide",
                "Phantom": "forgotten lost soul",
                "Banshee": "sorrowful wailing omen",
                "Angel": "divine light shepherd",
                "Human": "adaptable innovator",
                "Jackal": "death servant",
                "Troll": "savage rampager",
                "Dwarf": "ancient craftsman philosopher",
                "Goblin": "fearful stealthy outcast",
                "Imp": "loyal cunning advisor",
                "Arachnos": "patient silent predator",
                "Minotaur": "savage warrior",
                "Orc": "greedy strategic thief"
            }
        }
    }
    
    def __init__(self, cache_dir: str = None, rate_limit_per_minute: int = 10):
        """
        Initialize Perchance router.
        
        Args:
            cache_dir: Directory for caching Perchance results
            rate_limit_per_minute: Max API calls per minute
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path(__file__).parent.parent / "cache" / "perchance"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_file = self.cache_dir / "perchance_cache.json"
        self.rate_limit = rate_limit_per_minute
        self.rate_state = {
            "count": 0,
            "reset_time": time.time() + 60
        }
        
        # Load cache
        self.cache: Dict[str, Any] = {}
        self._load_cache()
    
    def _load_cache(self):
        """Load cache from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                # Clean expired entries
                self._clean_cache()
                print(f"Loaded Perchance cache with {len(self.cache)} entries")
            except json.JSONDecodeError:
                print("Perchance cache corrupted, starting fresh")
                self.cache = {}
    
    def _save_cache(self):
        """Save cache to disk"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def _clean_cache(self):
        """Remove expired cache entries"""
        now = time.time()
        expired = [k for k, v in self.cache.items() if v.get('expires', 0) < now]
        for k in expired:
            del self.cache[k]
        if expired:
            self._save_cache()
    
    def _get_cache_key(self, generator: str, params: Dict) -> str:
        """Generate cache key from generator and params"""
        key_str = f"{generator}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _check_rate_limit(self) -> Tuple[bool, float]:
        """
        Check if we can make an API call.
        Returns (allowed, wait_seconds)
        """
        now = time.time()
        
        if now >= self.rate_state["reset_time"]:
            self.rate_state["count"] = 0
            self.rate_state["reset_time"] = now + 60
        
        if self.rate_state["count"] >= self.rate_limit:
            wait = self.rate_state["reset_time"] - now
            return False, max(0, wait)
        
        self.rate_state["count"] += 1
        return True, 0
    
    def _fetch_from_perchance(self, generator: str, params: Dict) -> Optional[List[str]]:
        """
        Fetch results from Perchance API.
        
        Args:
            generator: Perchance generator name
            params: API parameters (count, etc.)
        
        Returns:
            List of generated results or None on error
        """
        # Check rate limit
        allowed, wait = self._check_rate_limit()
        if not allowed:
            print(f"Perchance rate limited, wait {wait:.0f}s")
            return None
        
        try:
            url = f"{self.API_BASE}?generator={generator}&count={params.get('count', 1)}"
            
            # Add additional params
            for key, value in params.items():
                if key != 'count':
                    url += f"&{key}={value}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    return data
                else:
                    print(f"Perchance returned empty or invalid response: {data}")
                    return None
            else:
                print(f"Perchance API error: {response.status_code}")
                return None
        
        except requests.RequestException as e:
            print(f"Perchance request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Perchance response parsing failed: {e}")
            return None
    
    def generate(self, element_type: str, context: Dict = None, 
                 use_cache: bool = True, fallback_local: bool = True) -> Dict[str, Any]:
        """
        Generate a game element using Perchance or fallback.
        
        Args:
            element_type: Type of element (character_name, quest_idea, etc.)
            context: Additional context (species, tone, etc.)
            use_cache: Whether to use cached results
            fallback_local: Whether to fallback to local generation if rate-limited
        
        Returns:
            Dict with 'success', 'result', 'source' (perchance/cache/fallback), 'metadata'
        """
        if element_type not in self.GENERATOR_MAP:
            return {
                "success": False,
                "error": f"Unknown element type: {element_type}",
                "source": "error"
            }
        
        config = self.GENERATOR_MAP[element_type]
        generator = config["generator"]
        params = config["params"].copy()
        
        # Add context-specific params
        if context:
            if "species" in context and "species_map" in config:
                species = context["species"]
                if species in config["species_map"]:
                    params["prompt"] = config["species_map"][species]
            params.update(context)
        
        # Check cache
        cache_key = self._get_cache_key(generator, params)
        now = time.time()
        
        if use_cache and cache_key in self.cache:
            cached = self.cache[cache_key]
            if cached.get('expires', 0) > now:
                print(f"Perchance cache HIT for {element_type}")
                return {
                    "success": True,
                    "result": cached['result'],
                    "source": "cache",
                    "metadata": {
                        "cached_at": cached.get('created'),
                        "element_type": element_type,
                        "generator": generator
                    }
                }
        
        # Fetch from Perchance
        print(f"Perchance fetching {element_type} from {generator}...")
        results = self._fetch_from_perchance(generator, params)
        
        if results:
            # Cache the result
            self.cache[cache_key] = {
                'result': results[0] if len(results) == 1 else results,
                'created': datetime.now().isoformat(),
                'expires': now + config["cache_ttl"]
            }
            self._save_cache()
            
            return {
                "success": True,
                "result": results[0] if len(results) == 1 else results,
                "source": "perchance",
                "metadata": {
                    "generator": generator,
                    "params": params,
                    "element_type": element_type
                }
            }
        
        # Fallback
        if fallback_local:
            print(f"Perchance fallback to local generation for {element_type}")
            return self._fallback_generate(element_type, context)
        else:
            return {
                "success": False,
                "error": "Perchance unavailable and fallback disabled",
                "source": "error"
            }
    
    def _fallback_generate(self, element_type: str, context: Dict = None) -> Dict[str, Any]:
        """
        Fallback local generation when Perchance is unavailable.
        Uses simple templates and random selection from Rememberence data.
        """
        result = None
        
        if element_type == "character_name":
            prefixes = ["Shadow", "Storm", "Moon", "Star", "Fire", "Ice", "Thunder", "Mystic", "Ancient", "Eternal"]
            suffixes = ["walker", "born", "weaver", "heart", "blade", "song", "wind", "flame", "spirit", "guard"]
            result = f"{random.choice(prefixes)}{random.choice(suffixes)}"
        
        elif element_type == "species_trait":
            species = context.get("species", "Human") if context else "Human"
            traits = [
                f"Enhanced {species} instinct manifests in combat",
                f"Ancient {species} wisdom guides decision-making",
                f"{species} heritage provides unique perspective",
                f"Natural {species} abilities emerge under pressure"
            ]
            result = random.choice(traits)
        
        elif element_type == "quest_idea":
            quests = [
                "Retrieve an ancient artifact from a forgotten temple",
                "Protect a village from mysterious shadow creatures",
                "Uncover the truth behind a series of disappearances",
                "Negotiate peace between warring factions",
                "Break an ancient curse that plagues the land"
            ]
            result = random.choice(quests)
        
        elif element_type == "place_name":
            types = ["Keep", "Vale", "Wood", "Stone", "Haven", "Reach", "Spire", "Deep", "Crest", "Moor"]
            prefixes = ["Iron", "Raven", "Silver", "Dragon", "Frost", "Ember", "Wind", "Star", "Night", "Bright"]
            result = f"{random.choice(prefixes)}{random.choice(types)}"
        
        else:
            result = f"Generated {element_type} (fallback)"
        
        return {
            "success": True,
            "result": result,
            "source": "fallback",
            "metadata": {
                "element_type": element_type,
                "context": context,
                "fallback_reason": "perchance_unavailable"
            }
        }
    
    def generate_batch(self, element_types: List[str], context: Dict = None) -> Dict[str, Dict]:
        """
        Generate multiple elements in a batch.
        
        Args:
            element_types: List of element types to generate
            context: Shared context for all generations
        
        Returns:
            Dict mapping element_type to generation result
        """
        results = {}
        
        for element_type in element_types:
            results[element_type] = self.generate(element_type, context)
        
        return results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = time.time()
        valid_entries = len([v for v in self.cache.values() if v.get('expires', 0) > now])
        
        return {
            "total_entries": len(self.cache),
            "valid_entries": valid_entries,
            "expired_entries": len(self.cache) - valid_entries,
            "rate_limit_remaining": max(0, self.rate_limit - self.rate_state["count"]),
            "rate_reset_in": max(0, self.rate_state["reset_time"] - now)
        }
    
    def clear_cache(self, element_type: str = None):
        """
        Clear cache entries.
        
        Args:
            element_type: If provided, only clear entries for this type
        """
        if element_type:
            # Clear specific type
            config = self.GENERATOR_MAP.get(element_type)
            if config:
                cache_key = self._get_cache_key(config["generator"], config["params"])
                if cache_key in self.cache:
                    del self.cache[cache_key]
                    self._save_cache()
                    print(f"Cleared cache for {element_type}")
        else:
            # Clear all
            self.cache = {}
            self._save_cache()
            print("Cleared all Perchance cache")


# Integration with existing queue_manager
def create_perchance_job(queue_manager, element_type: str, context: Dict = None, 
                         priority: str = "normal") -> str:
    """
    Create a Perchance generation job in the queue.
    
    Args:
        queue_manager: QueueManager instance
        element_type: Type of element to generate
        context: Generation context
        priority: Job priority
    
    Returns:
        job_id
    """
    return queue_manager.add_job(
        job_type="perchance_generate",
        service="perchance",
        params={
            "element_type": element_type,
            "context": context
        },
        priority=priority,
        fallback_local=True
    )


# Global instance
_perchance_router: Optional[PerchanceRouter] = None


def get_perchance_router() -> PerchanceRouter:
    """Get or create global Perchance router instance"""
    global _perchance_router
    if _perchance_router is None:
        _perchance_router = PerchanceRouter()
    return _perchance_router
