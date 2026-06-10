#!/usr/bin/env python3
"""
Token Optimizer for Hybrid Router

Strategies to minimize token usage:
1. Semantic caching (fuzzy match similar queries)
2. Query compression (strip noise, normalize)
3. Auto-pattern learning (extract from successful responses)
4. Response condensation (cache summarized versions)
5. Token accounting (track savings)
"""

import hashlib
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from difflib import SequenceMatcher
import subprocess

WORKSPACE = Path("D:/Ollama/OpenClaw/workspace")
ROUTER_DIR = WORKSPACE / "hybrid-router"
TOKEN_STATS_FILE = ROUTER_DIR / "token_stats.json"
SEMANTIC_CACHE_FILE = ROUTER_DIR / "semantic_cache.json"
COMPRESSED_CACHE_FILE = ROUTER_DIR / "compressed_cache.json"


# ────────────────────────────────────────────────
# Query Compression
# ────────────────────────────────────────────────

class QueryCompressor:
    """Compress queries by removing noise while preserving meaning."""
    
    # Words/phrases that add little semantic value (applied in order)
    FILLER_PHRASES = [
        r"\b(can you|could you|please|pretty please|i need|i want|i'd like)\b",
        r"\b(help me|tell me|show me|explain|what is|what's|who is|who's|when is|when's|where is|where's|how is|how's|why is|why's)\b",
        r"\b(let me know|I was wondering|do you know|I'm trying to|I want to|I need to)\b",
        r"\b(if you can|if you could|if possible|when you have time|when you get a chance)\b",
        r"\b(the|a|an|some|any|this|that|these|those|it|its)\b",
        r"\b(actually|basically|literally|just|really|very|quite|pretty|so|too)\b",
        r"\b(understand|know|see|learn|find out|figure out|wondering)\b",
    ]
    
    # Polite prefixes/suffixes
    POLITE_PREFIXES = ["please", "pls", "thx", "thanks", "thank you"]
    POLITE_SUFFIXES = ["please", "pls", "thx", "thanks", "thank you", "if you can", "when you have time"]
    
    def compress(self, query: str) -> str:
        """Compress a query by removing filler words and normalizing."""
        original = query.strip()
        compressed = original
        
        # Remove polite prefixes/suffixes first
        words = compressed.split()
        if words and words[0].lower() in self.POLITE_PREFIXES:
            words = words[1:]
        if words and words[-1].lower() in self.POLITE_SUFFIXES:
            words = words[:-1]
        compressed = " ".join(words)
        
        # Apply filler phrase removal (multiple passes for nested patterns)
        for _ in range(2):  # Two passes to catch nested patterns
            for pattern in self.FILLER_PHRASES:
                compressed = re.sub(pattern, "", compressed, flags=re.IGNORECASE)
        
        # Normalize whitespace
        compressed = re.sub(r"\s+", " ", compressed).strip()
        
        # Remove trailing punctuation (except ?!)
        compressed = compressed.rstrip(".,;:")
        
        # Remove leading/trailing question words that became isolated
        compressed = re.sub(r"^\s*(what|how|when|where|why|who)\s+", "", compressed, flags=re.IGNORECASE)
        
        return compressed if compressed else original
    
    def estimate_savings(self, original: str, compressed: str) -> int:
        """Estimate token savings from compression."""
        # Rough estimate: 1 token ≈ 4 characters (English)
        original_tokens = len(original) / 4
        compressed_tokens = len(compressed) / 4
        return max(0, int(original_tokens - compressed_tokens))


# ────────────────────────────────────────────────
# Semantic Caching (Fuzzy Matching)
# ────────────────────────────────────────────────

class SemanticCache:
    """Cache with semantic similarity matching, not just exact hashes."""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.cache: List[Dict[str, Any]] = []
        self.threshold = similarity_threshold
        self.load_cache()
    
    def load_cache(self):
        if SEMANTIC_CACHE_FILE.exists():
            try:
                self.cache = json.loads(SEMANTIC_CACHE_FILE.read_text(encoding='utf-8'))
            except:
                self.cache = []
    
    def save_cache(self):
        # Keep cache size manageable
        if len(self.cache) > 1000:
            self.cache = self.cache[-500:]  # Keep recent 500
        SEMANTIC_CACHE_FILE.write_text(json.dumps(self.cache, indent=2), encoding='utf-8')
    
    def _similarity(self, a: str, b: str) -> float:
        """Compute string similarity (0-1)."""
        # Normalize for comparison
        a_norm = a.lower().strip()
        b_norm = b.lower().strip()
        return SequenceMatcher(None, a_norm, b_norm).ratio()
    
    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """Find cached response with semantic matching."""
        query_lower = query.lower()
        
        for entry in self.cache:
            # Check exact hash first (fast path)
            if entry.get("hash") == self._hash(query):
                entry["hits"] = entry.get("hits", 0) + 1
                entry["last_used"] = datetime.now().isoformat()
                self.save_cache()
                return entry
            
            # Semantic similarity check
            similarity = self._similarity(query, entry["query"])
            if similarity >= self.threshold:
                entry["hits"] = entry.get("hits", 0) + 1
                entry["last_used"] = datetime.now().isoformat()
                entry["similarity_match"] = similarity
                self.save_cache()
                return entry
        
        return None
    
    def set(self, query: str, response: str, path: str = "smart", tokens_used: int = 0):
        """Cache a response."""
        entry = {
            "hash": self._hash(query),
            "query": query,
            "response": response,
            "path": path,
            "tokens_used": tokens_used,
            "timestamp": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat(),
            "hits": 1,
            "similarity_match": None
        }
        
        # Check if we already have this exact query
        for i, existing in enumerate(self.cache):
            if existing["hash"] == entry["hash"]:
                self.cache[i] = entry
                self.save_cache()
                return
        
        # Add new entry
        self.cache.append(entry)
        self.save_cache()
    
    def get_stats(self) -> Dict[str, Any]:
        total_hits = sum(e.get("hits", 1) for e in self.cache)
        unique_queries = len(self.cache)
        return {
            "entries": unique_queries,
            "total_hits": total_hits,
            "avg_hits_per_entry": round(total_hits / unique_queries, 2) if unique_queries > 0 else 0
        }


# ────────────────────────────────────────────────
# Auto-Pattern Learning
# ────────────────────────────────────────────────

class PatternLearner:
    """Automatically extract patterns from successful LLM responses."""
    
    def __init__(self):
        self.patterns_file = ROUTER_DIR / "learned_patterns.json"
        self.patterns: Dict[str, str] = {}
        self.load_patterns()
    
    def load_patterns(self):
        if self.patterns_file.exists():
            try:
                self.patterns = json.loads(self.patterns_file.read_text(encoding='utf-8'))
            except:
                self.patterns = {}
    
    def save_patterns(self):
        self.patterns_file.write_text(json.dumps(self.patterns, indent=2), encoding='utf-8')
    
    def extract_pattern(self, query: str, response: str) -> Optional[str]:
        """
        Extract a generalizable pattern from a query-response pair.
        
        Strategies:
        - Replace specific numbers with #
        - Replace specific names/entities with *
        - Keep structural words intact
        """
        # Replace numbers with wildcard
        pattern = re.sub(r'\b\d+\b', '#', query)
        
        # Replace common entity types with wildcards
        # Names (capitalized words after certain triggers)
        pattern = re.sub(r'\b([A-Z][a-z]+)\b', '*', pattern)
        
        # Replace quoted strings with wildcard
        pattern = re.sub(r'"[^"]+"', '*', pattern)
        pattern = re.sub(r"'[^']+'", '*', pattern)
        
        # Clean up multiple wildcards
        pattern = re.sub(r'\*+', '*', pattern)
        pattern = re.sub(r'#+', '#', pattern)
        
        # Only learn if pattern is meaningfully different from query
        if pattern != query and len(pattern) > 3:
            return pattern
        
        return None
    
    def learn(self, query: str, response: str) -> Optional[str]:
        """Learn a pattern from a query-response pair."""
        pattern = self.extract_pattern(query, response)
        
        if pattern and pattern not in self.patterns:
            # Store condensed response if long
            condensed = response[:200] + "..." if len(response) > 200 else response
            self.patterns[pattern] = condensed
            self.save_patterns()
            return pattern
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "patterns_learned": len(self.patterns),
            "file": str(self.patterns_file)
        }


# ────────────────────────────────────────────────
# Token Accounting
# ────────────────────────────────────────────────

class TokenAccountant:
    """Track token usage and savings."""
    
    # Estimated tokens per model (input + output averages)
    MODEL_TOKEN_COSTS = {
        "phi3:mini": 50,      # Small, fast
        "qwen2.5:7b": 150,    # Medium
        "qwen3.5:cloud": 500, # Large, expensive
        "hybrid-router": 30,  # Classifier (small)
    }
    
    def __init__(self):
        self.stats = {
            "tokens_used": 0,
            "tokens_saved": 0,
            "requests_total": 0,
            "requests_fast": 0,
            "requests_smart": 0,
            "requests_cloud": 0,
            "requests_cached": 0,
            "requests_compressed": 0,
        }
        self.load_stats()
    
    def load_stats(self):
        if TOKEN_STATS_FILE.exists():
            try:
                self.stats = json.loads(TOKEN_STATS_FILE.read_text(encoding='utf-8'))
            except:
                pass
    
    def save_stats(self):
        TOKEN_STATS_FILE.write_text(json.dumps(self.stats, indent=2), encoding='utf-8')
    
    def record_request(self, path: str, tokens: int = 0, cached: bool = False, compressed: bool = False):
        """Record a routing decision and token usage."""
        self.stats["requests_total"] += 1
        self.stats[f"requests_{path}"] = self.stats.get(f"requests_{path}", 0) + 1
        
        if cached:
            self.stats["requests_cached"] += 1
            self.stats["tokens_saved"] += tokens
        else:
            self.stats["tokens_used"] += tokens
        
        if compressed:
            self.stats["requests_compressed"] += 1
        
        self.save_stats()
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimate (4 chars ≈ 1 token for English)."""
        return len(text) // 4 + 1
    
    def get_savings_report(self) -> Dict[str, Any]:
        total_tokens = self.stats["tokens_used"] + self.stats["tokens_saved"]
        savings_pct = (self.stats["tokens_saved"] / total_tokens * 100) if total_tokens > 0 else 0
        
        return {
            **self.stats,
            "total_tokens_processed": total_tokens,
            "savings_percentage": round(savings_pct, 2),
            "efficiency_ratio": round(self.stats["tokens_saved"] / max(1, self.stats["tokens_used"]), 3)
        }


# ────────────────────────────────────────────────
# Unified Token Optimizer
# ────────────────────────────────────────────────

class TokenOptimizer:
    """Main interface for all token optimization strategies."""
    
    def __init__(self):
        self.compressor = QueryCompressor()
        self.semantic_cache = SemanticCache()
        self.pattern_learner = PatternLearner()
        self.accountant = TokenAccountant()
    
    def optimize_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Apply all optimization strategies to a query.
        
        Returns: (optimized_query, metadata)
        """
        metadata = {
            "original_length": len(query),
            "compressed": False,
            "cache_hit": False,
            "compression_savings": 0,
        }
        
        # Step 1: Try semantic cache first (before compression)
        cached = self.semantic_cache.get(query)
        if cached:
            metadata["cache_hit"] = True
            metadata["cached_response"] = cached["response"]
            metadata["cached_path"] = cached["path"]
            metadata["tokens_saved"] = cached.get("tokens_used", 100)
            return query, metadata
        
        # Step 2: Compress query
        compressed = self.compressor.compress(query)
        if compressed != query:
            metadata["compressed"] = True
            metadata["compressed_query"] = compressed
            metadata["compression_savings"] = self.compressor.estimate_savings(query, compressed)
            
            # Try cache with compressed version
            cached_compressed = self.semantic_cache.get(compressed)
            if cached_compressed:
                metadata["cache_hit"] = True
                metadata["cached_response"] = cached_compressed["response"]
                metadata["cached_path"] = cached_compressed["path"]
                metadata["tokens_saved"] = cached_compressed.get("tokens_used", 100)
                return compressed, metadata
        
        return compressed if metadata["compressed"] else query, metadata
    
    def record_response(self, query: str, response: str, path: str, tokens_used: int = 0):
        """Record a response for caching and learning."""
        # Cache it
        self.semantic_cache.set(query, response, path, tokens_used)
        
        # Try to learn a pattern
        learned_pattern = self.pattern_learner.learn(query, response)
        
        # Record token usage
        self.accountant.record_request(path, tokens_used, cached=False)
        
        return {
            "cached": True,
            "pattern_learned": learned_pattern
        }
    
    def record_cache_hit(self, tokens_saved: int):
        """Record a cache hit."""
        self.accountant.record_request("cached", tokens_saved, cached=True)
    
    def get_full_stats(self) -> Dict[str, Any]:
        return {
            "token_accounting": self.accountant.get_savings_report(),
            "semantic_cache": self.semantic_cache.get_stats(),
            "pattern_learning": self.pattern_learner.get_stats(),
        }


# ────────────────────────────────────────────────
# CLI Interface
# ────────────────────────────────────────────────

def main():
    import sys
    
    optimizer = TokenOptimizer()
    
    if len(sys.argv) < 2:
        print("Usage: python token_optimizer.py <command> [args]")
        print("Commands:")
        print("  test <query>     - Test query optimization")
        print("  stats            - Show token savings statistics")
        print("  patterns         - Show learned patterns")
        print("  cache            - Show semantic cache stats")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "test":
        query = " ".join(sys.argv[2:])
        optimized, meta = optimizer.optimize_query(query)
        print(f"Original:   {query}")
        print(f"Optimized:  {optimized}")
        print(f"Compressed: {meta.get('compressed', False)}")
        print(f"Cache hit:  {meta.get('cache_hit', False)}")
        if meta.get('compression_savings', 0) > 0:
            print(f"Saved:      ~{meta['compression_savings']} tokens from compression")
        if meta.get('tokens_saved', 0) > 0:
            print(f"Saved:      ~{meta['tokens_saved']} tokens from cache")
    
    elif cmd == "stats":
        stats = optimizer.get_full_stats()
        print(json.dumps(stats, indent=2))
    
    elif cmd == "patterns":
        stats = optimizer.pattern_learner.get_stats()
        print(json.dumps(stats, indent=2))
        print("\nLearned patterns:")
        for pattern, response in list(optimizer.pattern_learner.patterns.items())[:10]:
            print(f"  {pattern} → {response[:50]}...")
    
    elif cmd == "cache":
        stats = optimizer.semantic_cache.get_stats()
        print(json.dumps(stats, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
