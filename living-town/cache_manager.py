"""
Cache Manager with Aggressive Caching for Older Machines

Implements LRU caching for narratives, simulation results, and AI calls.
Optimized for low memory usage.
"""

from typing import Dict, List, Optional, Any
from collections import OrderedDict
from datetime import datetime, timedelta
import json


class LRUCache:
    """Simple LRU cache with size limit."""
    
    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        if key in self.cache:
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def put(self, key: str, value: Any):
        """Put item in cache."""
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        
        # Evict oldest if over limit
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)
    
    def has(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self.cache
    
    def clear(self):
        """Clear cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%"
        }


class CacheManager:
    """
    Manages multiple caches for different purposes.
    
    Optimized for older machines:
    - Aggressive caching (high hit rates)
    - Small memory footprint
    - Time-based expiration for stale data
    """
    
    def __init__(self, profile: str = "conservative"):
        # Cache sizes based on profile
        sizes = {
            "minimal": 500,
            "conservative": 1000,
            "standard": 2000
        }
        
        max_size = sizes.get(profile, 1000)
        
        # Initialize caches
        self.narrative_cache = LRUCache(max_size=max_size)
        self.simulation_cache = LRUCache(max_size=max_size // 2)
        self.ai_cache = LRUCache(max_size=max_size // 4)  # Smaller, AI calls expensive
        
        # Time-based expiration
        self.expiration_times = {}
        self.default_ttl = timedelta(hours=1)  # 1 hour default
        
        # Statistics
        self.total_requests = 0
        self.cache_hits = 0
    
    def get_narrative(self, entity_id: str) -> Optional[str]:
        """Get cached narrative."""
        self.total_requests += 1
        narrative = self.narrative_cache.get(entity_id)
        
        if narrative:
            # Check expiration
            if self._is_expired(entity_id):
                self.narrative_cache.cache.pop(entity_id, None)
                return None
            
            self.cache_hits += 1
            return narrative
        
        return None
    
    def save_narrative(self, entity_id: str, narrative: str, ttl: timedelta = None):
        """Save narrative to cache."""
        self.narrative_cache.put(entity_id, narrative)
        
        if ttl:
            self.expiration_times[entity_id] = datetime.now() + ttl
        else:
            self.expiration_times[entity_id] = datetime.now() + self.default_ttl
    
    def get_simulation_result(self, key: str) -> Optional[Any]:
        """Get cached simulation result."""
        self.total_requests += 1
        result = self.simulation_cache.get(key)
        
        if result:
            if self._is_expired(key):
                self.simulation_cache.cache.pop(key, None)
                return None
            
            self.cache_hits += 1
            return result
        
        return None
    
    def save_simulation_result(self, key: str, result: Any, ttl: timedelta = None):
        """Save simulation result to cache."""
        self.simulation_cache.put(key, result)
        
        if ttl:
            self.expiration_times[key] = datetime.now() + ttl
        else:
            self.expiration_times[key] = datetime.now() + self.default_ttl
    
    def get_ai_result(self, prompt_hash: str) -> Optional[str]:
        """Get cached AI result (for identical prompts)."""
        self.total_requests += 1
        result = self.ai_cache.get(prompt_hash)
        
        if result:
            self.cache_hits += 1
            return result
        
        return None
    
    def save_ai_result(self, prompt_hash: str, result: str):
        """Save AI result to cache (long TTL, AI calls expensive)."""
        self.ai_cache.put(prompt_hash, result)
        # AI results never expire (same prompt = same answer)
        self.expiration_times[prompt_hash] = datetime.now() + timedelta(days=365)
    
    def _is_expired(self, key: str) -> bool:
        """Check if cached item is expired."""
        if key not in self.expiration_times:
            return False
        
        return datetime.now() > self.expiration_times[key]
    
    def cleanup_expired(self):
        """Remove expired items from all caches."""
        expired_keys = [
            key for key, expiry in self.expiration_times.items()
            if datetime.now() > expiry
        ]
        
        for key in expired_keys:
            self.narrative_cache.cache.pop(key, None)
            self.simulation_cache.cache.pop(key, None)
            self.ai_cache.cache.pop(key, None)
            self.expiration_times.pop(key, None)
        
        return len(expired_keys)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        hit_rate = (self.cache_hits / self.total_requests * 100) if self.total_requests > 0 else 0
        
        return {
            'total_requests': self.total_requests,
            'cache_hits': self.cache_hits,
            'hit_rate': f"{hit_rate:.1f}%",
            'narrative_cache': self.narrative_cache.stats(),
            'simulation_cache': self.simulation_cache.stats(),
            'ai_cache': self.ai_cache.stats(),
            'expired_items': len([k for k, v in self.expiration_times.items() if datetime.now() > v])
        }
    
    def clear_all(self):
        """Clear all caches."""
        self.narrative_cache.clear()
        self.simulation_cache.clear()
        self.ai_cache.clear()
        self.expiration_times.clear()
        self.total_requests = 0
        self.cache_hits = 0


# ────────────────────────────────────────────────
# Test
# ────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 60)
    print("CACHE MANAGER TEST (Conservative Profile)")
    print("=" * 60)
    
    cache_mgr = CacheManager(profile="conservative")
    
    # Test narrative caching
    print("\n[1/3] Testing Narrative Caching...")
    
    # First access (miss)
    narrative = cache_mgr.get_narrative('npc_001')
    print(f"  First access: {narrative} (expected: None)")
    
    # Save narrative
    cache_mgr.save_narrative('npc_001', 'Featherwing is a Dragon/Scorpio...')
    print(f"  Saved narrative for npc_001")
    
    # Second access (hit)
    narrative = cache_mgr.get_narrative('npc_001')
    print(f"  Second access: {narrative[:30]}... (expected: cached)")
    
    # Test AI caching
    print("\n[2/3] Testing AI Caching...")
    
    prompt_hash = 'hash_abc123'
    ai_result = cache_mgr.get_ai_result(prompt_hash)
    print(f"  First AI call: {ai_result} (expected: None)")
    
    cache_mgr.save_ai_result(prompt_hash, 'AI-generated narrative text...')
    print(f"  Saved AI result")
    
    ai_result = cache_mgr.get_ai_result(prompt_hash)
    print(f"  Second AI call: {ai_result[:30]}... (expected: cached)")
    
    # Test statistics
    print("\n[3/3] Cache Statistics...")
    stats = cache_mgr.stats()
    
    print(f"  Total Requests: {stats['total_requests']}")
    print(f"  Cache Hits: {stats['cache_hits']}")
    print(f"  Hit Rate: {stats['hit_rate']}")
    print(f"  Narrative Cache: {stats['narrative_cache']['size']}/{stats['narrative_cache']['max_size']}")
    print(f"  AI Cache: {stats['ai_cache']['size']}/{stats['ai_cache']['max_size']}")
    
    print("\n" + "=" * 60)
    print("CACHE MANAGER TEST COMPLETE")
    print("=" * 60)
