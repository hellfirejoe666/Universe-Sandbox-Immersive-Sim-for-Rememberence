#!/usr/bin/env python3
"""
Perchance Provider - Free unlimited AI as a router path

Perchance.org offers free, unlimited AI chat without rate limits.
This integrates it as a fourth routing path:

Routing paths now:
1. FAST - Pattern/cache (0 tokens, instant)
2. SMART - Local LLM qwen2.5:7b (~150 tokens, 5-30s)
3. PERCHANCE - Perchance AI (0 cost, unlimited, 5-15s)
4. CLOUD - qwen3.5:cloud (~500 tokens, rate limited)

Perchance is best for:
- Creative/roleplay queries
- Conversational interactions
- Long-form content
- When cloud is rate-limited

STATUS (2026-04-24):
- DIY API is down (HTTP 410 Gone)
- Browser automation BLOCKED BY CLOUDFLARE bot protection
- Provider gracefully falls back to SMART path
"""

import sys
import requests
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path("D:/Ollama/OpenClaw/workspace")
ROUTER_DIR = WORKSPACE / "hybrid-router"

# Community DIY Perchance API (currently DOWN as of 2026-04-24)
DIY_API_BASE = "https://diy-perchance-api.glitch.me/api"
DIY_API_AVAILABLE = False  # Currently down (HTTP 410)

# Browser automation blocked by Cloudflare bot protection (2026-04-24)
BROWSER_AUTOMATION_AVAILABLE = False  # Cloudflare blocks headless browsers

# Alternative: Direct generator download endpoint (for non-AI generators)
DOWNLOAD_API = "https://perchance.org/api/downloadGenerator"

# Public AI generators for different query types
GENERATORS = {
    "creative": "ai-character-chat",      # Creative writing, roleplay
    "story": "ai-story-generator",         # Story generation  
    "character": "fantasy-character",      # Character creation
    "name": "fantasy-name",                # Name generation
    "dialogue": "ai-character-chat",       # Conversational
    "default": "ai-character-chat",        # Fallback
}

# Keywords for routing
CREATIVE_KEYWORDS = [
    "story", "poem", "write", "create", "imagine",
    "roleplay", "character", "fiction", "narrative",
    "describe", "paint a picture", "tell me a tale",
    "adventure", "quest", "fantasy", "magic",
    "dragon", "wizard", "knight", "castle",
]

FACTUAL_KEYWORDS = [
    "calculate", "math", "code", "programming",
    "python", "javascript", "error", "bug",
    "compile", "debug", "syntax", "algorithm",
]


class PerchanceProvider:
    """
    Perchance AI provider.
    
    STATUS: UNAVAILABLE (2026-04-24)
    - DIY API: Down (HTTP 410)
    - Browser automation: Blocked by Cloudflare bot protection
    
    Falls back gracefully - router uses SMART path instead.
    
    Original intent:
    - Completely free, no rate limits
    - Good for creative/conversational tasks
    - No API key required
    
    Why it doesn't work:
    - Perchance uses Cloudflare bot protection
    - Headless browsers get stuck on "Checking your browser" page
    - Would require solving CAPTCHA-like challenges
    - Violates ToS to automate access
    
    Alternative: Focus on local optimization (FAST + SMART paths)
    """
    
    def __init__(self):
        self.available = BROWSER_AUTOMATION_AVAILABLE  # False - Cloudflare
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.stats = {
            "requests": 0,
            "success": 0,
            "failures": 0,
            "avg_latency_ms": 0,
        }
        self.last_failure = "Cloudflare bot protection blocks automated access"
        self.failure_count = 0
    
    def _select_generator(self, prompt: str) -> str:
        """Select the best generator for this prompt."""
        prompt_lower = prompt.lower()
        
        # Check for factual/code queries (not suitable for Perchance)
        for kw in FACTUAL_KEYWORDS:
            if kw in prompt_lower:
                return None  # Not suitable
        
        # Check for creative keywords
        for kw in CREATIVE_KEYWORDS:
            if kw in prompt_lower:
                if kw in ["story", "tale", "adventure", "quest", "write"]:
                    return "ai-story-generator"
                elif kw in ["character", "person", "who", "describe"]:
                    return "ai-character-chat"
                elif kw in ["name", "named"]:
                    return "fantasy-name"
                elif kw in ["poem", "poetry"]:
                    return "ai-story-generator"
        
        return "ai-character-chat"  # Default for conversational
    
    def generate(self, prompt: str, max_tokens: int = 2000, 
                 generator: str = None) -> Dict[str, Any]:
        """
        Generate text from Perchance using browser automation.
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens (used for context)
            generator: Specific generator to use (auto-selected if None)
        
        Returns:
            Dict with response and metadata
        """
        start = time.time()
        
        if generator is None:
            generator = self._select_generator(prompt)
        
        # If generator returned None, this query type isn't suitable
        if generator is None:
            return self._error_result("Query type not suitable for Perchance (factual/code)", start)
        
        try:
            # Try browser automation (Playwright)
            if BROWSER_AUTOMATION_AVAILABLE:
                result = self._try_browser_automation(prompt, generator, start)
                
                if result and not result.get("error"):
                    return result
            
            # Fallback: DIY API (currently down)
            if DIY_API_AVAILABLE:
                result = self._try_diy_api(prompt, generator, start)
                
                if result and not result.get("error"):
                    return result
            
            return self._error_result("All Perchance methods unavailable", start)
        
        except Exception as e:
            return self._error_result(f"Unexpected error: {str(e)}", start)
    
    def _try_browser_automation(self, prompt: str, generator: str, start: float) -> Optional[Dict[str, Any]]:
        """Browser automation blocked by Cloudflare (2026-04-24)."""
        return self._error_result("Cloudflare bot protection blocks automated access (headless browser detected)", start)
    
    def _try_diy_api(self, prompt: str, generator: str, start: float) -> Optional[Dict[str, Any]]:
        """Try to generate using the DIY Perchance API (currently down)."""
        try:
            url = f"{DIY_API_BASE}?generator={generator}&list=output"
            
            if prompt and len(prompt) < 500:
                url += f"&input={requests.utils.quote(prompt[:500])}"
            
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                result_text = response.text.strip()
                
                if result_text and len(result_text) > 10 and not result_text.startswith("<!"):
                    latency_ms = (time.time() - start) * 1000
                    
                    self.stats["requests"] += 1
                    self.stats["success"] += 1
                    self.stats["avg_latency_ms"] = (
                        (self.stats["avg_latency_ms"] * (self.stats["success"] - 1) + latency_ms)
                        / self.stats["success"]
                    )
                    self.failure_count = 0
                    
                    return {
                        "response": result_text,
                        "provider": "perchance",
                        "generator": generator,
                        "latency_ms": latency_ms,
                        "tokens_used": 0,
                        "error": None,
                    }
                else:
                    return self._error_result("Invalid response format from DIY API", start)
            else:
                return self._error_result(f"DIY API HTTP {response.status_code}", start)
        
        except requests.Timeout:
            return self._error_result("DIY API timeout (30s)", start)
        
        except requests.RequestException as e:
            return self._error_result(f"DIY API request failed: {str(e)}", start)
    
    def _error_result(self, error: str, start: float) -> Dict[str, Any]:
        """Create error result dict."""
        latency_ms = (time.time() - start) * 1000
        self.stats["requests"] += 1
        self.stats["failures"] += 1
        self.last_failure = error
        self.failure_count += 1
        
        # Mark unavailable after 3 consecutive failures
        if self.failure_count >= 3:
            self.available = False
        
        return {
            "response": "",
            "provider": "perchance",
            "latency_ms": latency_ms,
            "tokens_used": 0,
            "error": error,
        }
    
    def is_suitable_for(self, query: str, novelty: float) -> bool:
        """
        Determine if Perchance is suitable for this query.
        
        Best for:
        - Creative writing
        - Roleplay
        - Conversational queries
        - Long-form content
        - When cloud is rate-limited
        
        Not ideal for:
        - Code generation
        - Math/factual queries
        - Simple commands
        """
        if not self.available:
            return False
        
        query_lower = query.lower()
        
        # Check if query matches creative patterns
        is_creative = any(kw in query_lower for kw in CREATIVE_KEYWORDS)
        
        # High novelty queries that don't need cloud-level reasoning
        is_novel_but_not_complex = 0.5 < novelty < 0.85
        
        # Factual/math queries → not suitable
        is_factual = any(kw in query_lower for kw in FACTUAL_KEYWORDS)
        
        return (is_creative or is_novel_but_not_complex) and not is_factual
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            **self.stats,
            "available": self.available,
            "consecutive_failures": self.failure_count,
            "last_error": self.last_failure,
            "diy_api_base": DIY_API_BASE,
            "diy_api_status": "DOWN (HTTP 410 Gone)" if not DIY_API_AVAILABLE else "OK",
            "browser_automation": "BLOCKED BY CLOUDFLARE" if not BROWSER_AUTOMATION_AVAILABLE else "ENABLED (Playwright)",
            "notes": "Perchance uses Cloudflare bot protection. Automated access not feasible.",
        }
    
    def reset_availability(self):
        """Reset availability after failures (call when retrying)."""
        if self.failure_count < 3:
            self.available = BROWSER_AUTOMATION_AVAILABLE


# Convenience function for sync usage
def perchance_generate(prompt: str, generator: str = None) -> Dict[str, Any]:
    """Synchronous Perchance generation."""
    provider = PerchanceProvider()
    return provider.generate(prompt, generator=generator)


# Test function
def test_perchance():
    """Test Perchance integration."""
    provider = PerchanceProvider()
    
    print("Testing Perchance AI (Browser Automation)...")
    print("=" * 60)
    print(f"Status: {'AVAILABLE' if provider.available else 'UNAVAILABLE'}")
    print(f"Browser Automation: {'ENABLED' if BROWSER_AUTOMATION_AVAILABLE else 'DISABLED'}")
    print(f"DIY API: {DIY_API_BASE} (DOWN)")
    print("=" * 60)
    
    tests = [
        ("Creative", "Write a short story about a dragon"),
        ("Character", "Describe a fantasy warrior character"),
        ("Name", "Generate a fantasy city name"),
        ("Default", "Hello, how are you?"),
    ]
    
    for test_name, prompt in tests:
        print(f"\n{test_name}: \"{prompt}\"")
        result = provider.generate(prompt)
        
        if result["error"]:
            print(f"  [ERROR] {result['error']}")
        else:
            print(f"  [OK] Success ({result['latency_ms']:.0f}ms, generator={result['generator']})")
            print(f"  Response: {result['response'][:150]}...")
    
    print("\n" + "=" * 60)
    print(f"Stats: {provider.get_stats()}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python perchance_provider.py <prompt>")
        print("       python perchance_provider.py --test")
        print()
        print("Perchance AI - Free unlimited creative generation")
        print()
        print("STATUS: UNAVAILABLE (Cloudflare blocks automated access)")
        print("Router will use SMART path (local LLM) for creative queries")
        sys.exit(1)
    
    if sys.argv[1] == "--test":
        test_perchance()
    else:
        prompt = " ".join(sys.argv[1:])
        result = perchance_generate(prompt)
        print(json.dumps(result, indent=2, ensure_ascii=False))
