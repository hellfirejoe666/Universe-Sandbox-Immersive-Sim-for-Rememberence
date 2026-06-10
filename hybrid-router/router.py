#!/usr/bin/env python3
"""
Hybrid Router - Local AI Optimization Layer

Routes requests through three paths:
- FAST: AIML pattern matching (instant, zero tokens)
- SMART: Local LLM qwen2.5:7b (reasoning, code, creative)
- CLOUD: Cloud LLM qwen3.5:cloud (escape hatch)

Learns new patterns on the fly for gradual improvement.
"""

import subprocess
import json
import re
import os
import hashlib
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────

ROUTER_MODEL = "hybrid-router"
FAST_MODEL = "phi3:mini"
SMART_MODEL = "phi3:mini"  # Fast, lightweight local model
CLOUD_MODEL = "qwen3.5:cloud"  # Escape hatch only

# Paths
WORKSPACE = Path("D:/Ollama/OpenClaw/workspace")
ROUTER_DIR = WORKSPACE / "hybrid-router"
AIML_DIR = Path("D:/GPT4All/AIPlus/alice/DATA")
PATTERNS_FILE = ROUTER_DIR / "learned_patterns.json"
CACHE_FILE = ROUTER_DIR / "response_cache.json"

# Confidence thresholds
FAST_THRESHOLD = 0.75
CLOUD_THRESHOLD = 0.90

# ────────────────────────────────────────────────
# Pattern Matching Engine (FAST Path)
# ────────────────────────────────────────────────

class PatternMatcher:
    """AIML-style pattern matching with wildcard support."""
    
    def __init__(self):
        self.patterns: List[Tuple[re.Pattern, str]] = []
        self.learned_patterns: Dict[str, str] = {}
        self.load_alice_patterns()
        self.load_learned_patterns()
    
    def load_alice_patterns(self):
        """Load patterns from Alice AIML files."""
        aiml_file = AIML_DIR / "newaiml.aiml"
        if not aiml_file.exists():
            print(f"[WARN] AIML file not found: {aiml_file}")
            return
        
        try:
            content = aiml_file.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"[WARN] Could not read AIML: {e}")
            return
        
        # Parse AIML <category> blocks
        pattern_template = re.compile(
            r'<category>\s*<pattern>(.*?)</pattern>\s*<template>(.*?)</template>\s*</category>',
            re.DOTALL | re.IGNORECASE
        )
        
        for match in pattern_template.finditer(content):
            pattern = match.group(1).strip()
            template = match.group(2).strip()
            self.add_pattern(pattern, template, learned=False)
    
    def load_learned_patterns(self):
        """Load previously learned patterns."""
        if PATTERNS_FILE.exists():
            try:
                self.learned_patterns = json.loads(PATTERNS_FILE.read_text())
            except:
                self.learned_patterns = {}
    
    def save_learned_patterns(self):
        """Persist learned patterns."""
        PATTERNS_FILE.write_text(json.dumps(self.learned_patterns, indent=2))
    
    def add_pattern(self, pattern: str, response: str, learned: bool = True):
        """Add a pattern. Convert AIML wildcards to regex."""
        # Convert AIML wildcards: * → .+, # → \d+
        regex_pattern = pattern.upper()
        regex_pattern = regex_pattern.replace('#', r'(\d+)')
        regex_pattern = regex_pattern.replace('*', r'(.+?)')
        regex_pattern = f'^{regex_pattern}$'
        
        try:
            compiled = re.compile(regex_pattern, re.IGNORECASE)
            self.patterns.append((compiled, response))
            
            if learned:
                self.learned_patterns[pattern] = response
                self.save_learned_patterns()
        except re.error as e:
            print(f"[WARN] Invalid pattern '{pattern}': {e}")
    
    def match(self, text: str) -> Optional[str]:
        """Try to match input against patterns. Returns response or None."""
        text_upper = text.upper().strip()
        
        # Check learned patterns first (more recent, more relevant)
        for pattern_str, response in self.learned_patterns.items():
            regex_pattern = pattern_str.upper()
            regex_pattern = regex_pattern.replace('#', r'(\d+)')
            regex_pattern = regex_pattern.replace('*', r'(.+?)')
            regex_pattern = f'^{regex_pattern}$'
            
            try:
                if re.match(regex_pattern, text_upper, re.IGNORECASE):
                    return response
            except:
                pass
        
        # Check compiled patterns
        for compiled, response in self.patterns:
            match = compiled.match(text_upper)
            if match:
                # Substitute wildcards into response
                result = response
                for i, group in enumerate(match.groups(), 1):
                    result = result.replace(f'<star{i}/>', group)
                return result
        
        return None


# ────────────────────────────────────────────────
# Response Cache (Avoid Repeated LLM Calls)
# ────────────────────────────────────────────────

class ResponseCache:
    """Cache LLM responses by content hash."""
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.load_cache()
    
    def load_cache(self):
        if CACHE_FILE.exists():
            try:
                self.cache = json.loads(CACHE_FILE.read_text())
            except:
                self.cache = {}
    
    def save_cache(self):
        CACHE_FILE.write_text(json.dumps(self.cache, indent=2))
    
    def _hash(self, text: str, context: str = "") -> str:
        key = f"{text}|||{context}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def get(self, text: str, context: str = "") -> Optional[Any]:
        key = self._hash(text, context)
        return self.cache.get(key)
    
    def set(self, text: str, response: Any, context: str = ""):
        key = self._hash(text, context)
        self.cache[key] = {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "uses": 0
        }
        self.save_cache()
    
    def increment_use(self, text: str, context: str = ""):
        key = self._hash(text, context)
        if key in self.cache:
            self.cache[key]["uses"] = self.cache[key].get("uses", 0) + 1
            self.save_cache()


# ────────────────────────────────────────────────
# LLM Router (Classification + Execution)
# ────────────────────────────────────────────────

class HybridRouter:
    """Main router that classifies and routes requests."""
    
    def __init__(self):
        self.matcher = PatternMatcher()
        self.cache = ResponseCache()
        self.stats = {
            "fast": 0,
            "smart": 0,
            "cloud": 0,
            "total": 0
        }
    
    def classify(self, text: str) -> Dict[str, Any]:
        """Use hybrid-router model to classify request."""
        prompt = f"""Analyze this request and route it:

Request: "{text}"

Respond with ONLY JSON:
{{"path": "fast|smart|cloud", "confidence": 0.0-1.0, "reason": "brief explanation"}}"""
        
        try:
            result = subprocess.run(
                ["ollama", "run", ROUTER_MODEL, prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse JSON from output
            output = result.stdout.strip()
            # Extract JSON block
            json_match = re.search(r'\{[^}]+\}', output, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return {"path": "smart", "confidence": 0.5, "reason": "Parse failed, defaulting to smart"}
        
        except subprocess.TimeoutExpired:
            return {"path": "smart", "confidence": 0.5, "reason": "Router timeout, defaulting to smart"}
        except Exception as e:
            return {"path": "smart", "confidence": 0.5, "reason": f"Router error: {e}"}
    
    def run_fast(self, text: str) -> Dict[str, Any]:
        """FAST path: pattern matching."""
        response = self.matcher.match(text)
        
        if response:
            return {
                "path": "fast",
                "response": response,
                "latency_ms": 0,
                "cached": False
            }
        
        # No pattern match - fall through to smart
        return self.run_smart(text, fallback=True)
    
    def run_smart(self, text: str, fallback: bool = False) -> Dict[str, Any]:
        """SMART path: local LLM (phi3:mini)."""
        # Check cache first
        cached = self.cache.get(text)
        if cached:
            self.cache.increment_use(text)
            return {
                "path": "smart",
                "response": cached["response"],
                "latency_ms": 0,
                "cached": True
            }
        
        start = datetime.now()
        
        try:
            result = subprocess.run(
                ["ollama", "run", SMART_MODEL, text],
                capture_output=True,
                text=True,
                timeout=45,  # Increased timeout for phi3:mini
                encoding='utf-8',
                errors='replace'  # Replace undecodable chars
            )
            
            latency = (datetime.now() - start).total_seconds() * 1000
            response = result.stdout.strip()
            
            # Cache the response
            self.cache.set(text, response)
            
            return {
                "path": "smart",
                "response": response,
                "latency_ms": latency,
                "cached": False
            }
        
        except subprocess.TimeoutExpired:
            return {
                "path": "smart",
                "response": "[TIMEOUT] Local model took too long.",
                "latency_ms": 45000,
                "cached": False
            }
        except Exception as e:
            return {
                "path": "smart",
                "response": f"[ERROR] {e}",
                "latency_ms": 0,
                "cached": False
            }
    
    def run_cloud(self, text: str) -> Dict[str, Any]:
        """CLOUD path: cloud LLM (rate-limited, use sparingly)."""
        start = datetime.now()
        
        try:
            result = subprocess.run(
                ["ollama", "run", CLOUD_MODEL, text],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            latency = (datetime.now() - start).total_seconds() * 1000
            
            return {
                "path": "cloud",
                "response": result.stdout.strip(),
                "latency_ms": latency,
                "cached": False
            }
        
        except subprocess.TimeoutExpired:
            return {
                "path": "cloud",
                "response": "[TIMEOUT] Cloud model unavailable. Try again later.",
                "latency_ms": 60000,
                "cached": False
            }
    
    def route(self, text: str, force_path: str = None) -> Dict[str, Any]:
        """Route a request through the appropriate path."""
        self.stats["total"] += 1
        
        # Force a specific path (for testing/override)
        if force_path:
            if force_path == "fast":
                result = self.run_fast(text)
                self.stats["fast"] += 1
                return result
            elif force_path == "smart":
                result = self.run_smart(text)
                self.stats["smart"] += 1
                return result
            elif force_path == "cloud":
                result = self.run_cloud(text)
                self.stats["cloud"] += 1
                return result
        
        # Check pattern matching first (instant, no tokens)
        pattern_response = self.matcher.match(text)
        if pattern_response:
            self.stats["fast"] += 1
            return {
                "path": "fast",
                "response": pattern_response,
                "latency_ms": 0,
                "cached": False
            }
        
        # Classify with router model
        classification = self.classify(text)
        path = classification.get("path", "smart")
        confidence = classification.get("confidence", 0.5)
        
        # Route based on classification
        if path == "fast" or confidence < FAST_THRESHOLD:
            # Low confidence or fast classification → try patterns, fall through
            result = self.run_fast(text)
            self.stats[result["path"]] += 1
            return result
        
        elif path == "cloud" and confidence >= CLOUD_THRESHOLD:
            # High confidence cloud → use cloud
            result = self.run_cloud(text)
            self.stats["cloud"] += 1
            return result
        
        else:
            # Default to smart path
            result = self.run_smart(text)
            self.stats["smart"] += 1
            return result
    
    def learn(self, pattern: str, response: str):
        """Learn a new pattern from interaction."""
        self.matcher.add_pattern(pattern, response, learned=True)
        print(f"[LEARNED] Pattern: '{pattern}' → '{response[:50]}...'")
    
    def get_stats(self) -> Dict[str, Any]:
        """Return routing statistics."""
        total = self.stats["total"] or 1
        return {
            **self.stats,
            "fast_pct": round(self.stats["fast"] / total * 100, 1),
            "smart_pct": round(self.stats["smart"] / total * 100, 1),
            "cloud_pct": round(self.stats["cloud"] / total * 100, 1),
            "cache_size": len(self.cache.cache),
            "learned_patterns": len(self.matcher.learned_patterns)
        }


# ────────────────────────────────────────────────
# CLI Interface
# ────────────────────────────────────────────────

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Hybrid Router - Local AI Optimization")
    parser.add_argument("text", nargs="?", help="Text to route")
    parser.add_argument("--force", choices=["fast", "smart", "cloud"], help="Force routing path")
    parser.add_argument("--learn", nargs=2, metavar=("PATTERN", "RESPONSE"), help="Learn a new pattern")
    parser.add_argument("--stats", action="store_true", help="Show routing statistics")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    router = HybridRouter()
    
    if args.stats:
        stats = router.get_stats()
        print("\n=== Hybrid Router Statistics ===")
        print(f"Total requests: {stats['total']}")
        print(f"FAST path: {stats['fast']} ({stats['fast_pct']}%)")
        print(f"SMART path: {stats['smart']} ({stats['smart_pct']}%)")
        print(f"CLOUD path: {stats['cloud']} ({stats['cloud_pct']}%)")
        print(f"Cache entries: {stats['cache_size']}")
        print(f"Learned patterns: {stats['learned_patterns']}")
        return
    
    if args.learn:
        router.learn(args.learn[0], args.learn[1])
        return
    
    if args.interactive:
        print("=== Hybrid Router Interactive Mode ===")
        print("Commands: /stats, /learn <pattern> <response>, /quit")
        print()
        
        while True:
            try:
                text = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            
            if not text:
                continue
            
            if text.startswith("/"):
                parts = text[1:].split(maxsplit=2)
                cmd = parts[0].lower()
                
                if cmd == "quit" or cmd == "exit":
                    break
                elif cmd == "stats":
                    stats = router.get_stats()
                    print(f"FAST: {stats['fast']}, SMART: {stats['smart']}, CLOUD: {stats['cloud']}")
                elif cmd == "learn" and len(parts) >= 3:
                    router.learn(parts[1], parts[2])
                else:
                    print(f"Unknown command: {text}")
                continue
            
            result = router.route(text, force_path=args.force)
            print(f"[{result['path'].upper()}] ({result['latency_ms']:.0f}ms, cached={result['cached']})")
            print(f"AI: {result['response']}")
            print()
        return
    
    if args.text:
        result = router.route(args.text, force_path=args.force)
        print(f"[{result['path'].upper()}] ({result['latency_ms']:.0f}ms, cached={result['cached']})")
        print(result['response'])
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
