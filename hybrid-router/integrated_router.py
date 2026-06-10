#!/usr/bin/env python3
"""
Integrated Hybrid Router with FFT Novelty Detection

Combines:
1. Pattern matching (FAST path)
2. FFT novelty detection (spectral analysis)
3. LLM classification (phi3:mini router)
4. Response caching

Makes routing decisions using all signals together.
"""

import sys
import json
import subprocess
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Import FFT detector
sys.path.insert(0, str(Path(__file__).parent))
from fft_novelty import FFTNoveltyDetector, rmc_confidence_adjustment

ROUTER_MODEL = "hybrid-router"
SMART_MODEL = "qwen2.5:7b"
CLOUD_MODEL = "qwen3.5:cloud"

WORKSPACE = Path("D:/Ollama/OpenClaw/workspace")
ROUTER_DIR = WORKSPACE / "hybrid-router"
PATTERNS_FILE = ROUTER_DIR / "learned_patterns.json"
CACHE_FILE = ROUTER_DIR / "response_cache.json"


class IntegratedRouter:
    """Router combining pattern matching, FFT novelty, and LLM classification."""
    
    def __init__(self):
        self.fft_detector = FFTNoveltyDetector(image_size=(64, 64))  # Smaller for speed
        self.patterns = self._load_patterns()
        self.cache = self._load_cache()
        self.stats = {"fast": 0, "smart": 0, "cloud": 0, "total": 0}
    
    def _load_patterns(self) -> Dict[str, str]:
        if PATTERNS_FILE.exists():
            try:
                return json.loads(PATTERNS_FILE.read_text(encoding='utf-8'))
            except:
                pass
        return {}
    
    def _load_cache(self) -> Dict[str, Any]:
        if CACHE_FILE.exists():
            try:
                return json.loads(CACHE_FILE.read_text(encoding='utf-8'))
            except:
                pass
        return {}
    
    def _save_patterns(self):
        PATTERNS_FILE.write_text(json.dumps(self.patterns, indent=2), encoding='utf-8')
    
    def _save_cache(self):
        CACHE_FILE.write_text(json.dumps(self.cache, indent=2), encoding='utf-8')
    
    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    def check_pattern(self, text: str) -> Optional[str]:
        """Check for pattern match."""
        text_upper = text.upper().strip()
        
        for pattern, response in self.patterns.items():
            regex = pattern.upper().replace('#', r'(\d+)').replace('*', r'(.+?)')
            try:
                if re.match(f'^{regex}$', text_upper):
                    return response
            except:
                pass
        return None
    
    def check_cache(self, text: str) -> Optional[str]:
        """Check response cache."""
        key = self._hash(text)
        if key in self.cache:
            return self.cache[key]["response"]
        return None
    
    def get_fft_novelty(self, text: str) -> Dict[str, Any]:
        """Get FFT novelty analysis."""
        return self.fft_detector.analyze(text)
    
    def get_llm_classification(self, text: str) -> Dict[str, Any]:
        """Get LLM-based classification with timeout protection."""
        prompt = f"Route: {text[:100]}"
        
        try:
            result = subprocess.run(
                ["ollama", "run", ROUTER_MODEL, prompt],
                capture_output=True,
                text=True,
                timeout=15,  # Reduced timeout
                encoding='utf-8',
                errors='ignore'
            )
            
            json_match = re.search(r'\{[^}]+\}', result.stdout, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass
        
        return {"path": "smart", "confidence": 0.5, "reason": "default"}
    
    def route(self, text: str, use_fft: bool = True) -> Dict[str, Any]:
        """
        Route a request using all available signals.
        
        Decision tree:
        1. Pattern match? → FAST (0ms)
        2. Cached? → Return cached (0ms)
        3. FFT novelty low + LLM says fast? → FAST
        4. FFT novelty high? → SMART or CLOUD
        5. Default → SMART
        """
        self.stats["total"] += 1
        start = datetime.now()
        
        # Step 1: Pattern match (instant)
        pattern_response = self.check_pattern(text)
        if pattern_response:
            self.stats["fast"] += 1
            return {
                "path": "fast",
                "source": "pattern",
                "response": pattern_response,
                "latency_ms": 0
            }
        
        # Step 2: Cache check (instant)
        cached_response = self.check_cache(text)
        if cached_response:
            self.stats["fast"] += 1
            return {
                "path": "fast",
                "source": "cache",
                "response": cached_response,
                "latency_ms": 0
            }
        
        # Step 3: FFT novelty analysis
        fft_result = None
        if use_fft:
            fft_result = self.get_fft_novelty(text)
        
        # Step 4: LLM classification
        llm_class = self.get_llm_classification(text)
        
        # Step 5: Decision logic
        path = "smart"  # Default
        
        if fft_result and llm_class:
            novelty = fft_result["novelty_score"]
            llm_conf = llm_class.get("confidence", 0.5)
            llm_path = llm_class.get("path", "smart")
            
            # Adjust LLM confidence based on FFT novelty
            adjusted_conf = rmc_confidence_adjustment(fft_result, llm_conf)
            
            # Decision matrix
            if novelty < 0.4 and llm_path == "fast" and adjusted_conf > 0.7:
                path = "fast"
            elif novelty > 0.8:
                path = "cloud"  # Very novel → cloud
            elif llm_path == "cloud" and adjusted_conf > 0.85:
                path = "cloud"
            else:
                path = "smart"
        
        # Step 6: Execute routing
        if path == "fast":
            # No pattern/cache, but classified as fast → learn it
            self.stats["fast"] += 1
            return {
                "path": "fast",
                "source": "classification",
                "response": "[No pattern yet - this would be learned]",
                "latency_ms": (datetime.now() - start).total_seconds() * 1000,
                "fft": fft_result,
                "llm": llm_class
            }
        
        elif path == "smart":
            try:
                result = subprocess.run(
                    ["ollama", "run", SMART_MODEL, text],
                    capture_output=True,
                    text=True,
                    timeout=90,
                    encoding='utf-8',
                    errors='ignore'
                )
                
                response = result.stdout.strip()
                # Cache it
                self.cache[self._hash(text)] = {"response": response, "timestamp": datetime.now().isoformat()}
                self._save_cache()
                
                self.stats["smart"] += 1
                return {
                    "path": "smart",
                    "response": response,
                    "latency_ms": (datetime.now() - start).total_seconds() * 1000,
                    "fft": fft_result,
                    "llm": llm_class
                }
            except subprocess.TimeoutExpired:
                return {
                    "path": "smart",
                    "response": "[TIMEOUT]",
                    "latency_ms": 90000,
                    "error": "Timeout"
                }
        
        else:  # cloud
            try:
                result = subprocess.run(
                    ["ollama", "run", CLOUD_MODEL, text],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    encoding='utf-8',
                    errors='ignore'
                )
                
                self.stats["cloud"] += 1
                return {
                    "path": "cloud",
                    "response": result.stdout.strip(),
                    "latency_ms": (datetime.now() - start).total_seconds() * 1000,
                    "fft": fft_result,
                    "llm": llm_class
                }
            except:
                return {
                    "path": "cloud",
                    "response": "[CLOUD UNAVAILABLE]",
                    "error": "Cloud model unavailable"
                }
    
    def learn(self, pattern: str, response: str):
        """Learn a new pattern."""
        self.patterns[pattern] = response
        self._save_patterns()
        return {"success": True, "pattern": pattern}
    
    def get_stats(self) -> Dict[str, Any]:
        total = self.stats["total"] or 1
        return {
            **self.stats,
            "fast_pct": round(self.stats["fast"] / total * 100, 1),
            "smart_pct": round(self.stats["smart"] / total * 100, 1),
            "cloud_pct": round(self.stats["cloud"] / total * 100, 1),
            "cache_size": len(self.cache),
            "learned_patterns": len(self.patterns)
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python integrated_router.py <command> [args]")
        print("Commands: route, learn, stats, fft")
        sys.exit(1)
    
    router = IntegratedRouter()
    cmd = sys.argv[1].lower()
    
    if cmd == "route":
        text = " ".join(sys.argv[2:])
        result = router.route(text)
        
    elif cmd == "learn":
        if len(sys.argv) < 4:
            print("Usage: learn <pattern> <response>")
            sys.exit(1)
        result = router.learn(sys.argv[2], sys.argv[3])
        
    elif cmd == "stats":
        result = router.get_stats()
        
    elif cmd == "fft":
        text = " ".join(sys.argv[2:])
        result = router.get_fft_novelty(text)
        
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
