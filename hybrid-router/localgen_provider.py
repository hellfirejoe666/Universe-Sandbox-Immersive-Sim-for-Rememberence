#!/usr/bin/env python3
"""
LocalGen Provider - Direct Ollama Integration
Replaces the separate server architecture with direct API calls to Ollama.

Features:
- Zero middleware: No more localhost:5000 server.
- Tiered Models: phi3:mini for fast tasks, qwen2.5:7b for complex creative tasks.
- Generator Emulation: Uses specialized system prompts to mimic Perchance generators.
- GPU Leveraged: Direct interaction with Ollama's GPU-accelerated backend.
"""

import sys
import requests
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Model mapping for performance/quality balance
MODEL_MAP = {
    "fast": "phi3:mini",         # Low VRAM, high speed (Names, Plots, Simple lists)
    "creative": "qwen2.5:7b",   # Higher quality (Stories, Complex Chat)
}

# Generator definitions: (Model Tier, System Prompt)
GENERATOR_CONFIGS = {
    "fantasy-name": (
        "fast", 
        "You are a professional fantasy name generator. Output ONLY the name. No conversational filler, no quotes, no explanations."
    ),
    "character-name": (
        "fast", 
        "You are a character name generator. Output ONLY the name based on the input. No filler."
    ),
    "fantasy-plot": (
        "fast", 
        "You are a fantasy plot hook generator. Output a one-sentence intriguing plot hook. No filler."
    ),
    "city-name": (
        "fast", 
        "You are a fantasy city name generator. Output ONLY the name of the city. No filler."
    ),
    "ai-story-generator": (
        "creative", 
        "You are a master storyteller. Create immersive, evocative, and iterative narratives. Be descriptive and atmospheric."
    ),
    "ai-character-chat": (
        "creative", 
        "You are a versatile AI companion. Engage in natural, creative, and conversational dialogue. Adapt your tone to the user."
    ),
    "explain": (
        "fast", 
        "You are a helpful explainer. Provide a concise, clear, and simple explanation of the concept."
    ),
    "summarize": (
        "fast", 
        "You are a summarization expert. Condense the following text into its most essential points while maintaining clarity."
    ),
    "brainstorm": (
        "creative", 
        "You are a creative brainstorming partner. Provide a diverse list of innovative ideas and possibilities."
    ),
    "default": (
        "creative", 
        "You are a helpful and creative AI assistant."
    ),
}

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

class LocalGenProvider:
    """
    Hardened LocalGen provider.
    Directly interfaces with Ollama API to eliminate middleware failures.
    """
    
    def __init__(self):
        self.available = True
        self.stats = {
            "requests": 0,
            "success": 0,
            "failures": 0,
            "avg_latency_ms": 0,
        }
        self.last_failure = None
        self.failure_count = 0
    
    def _select_generator(self, prompt: str) -> str:
        """Select the best generator mapping for this prompt."""
        prompt_lower = prompt.lower()
        
        # High-priority simple tasks
        if any(kw in prompt_lower for kw in ["summarize", "summary"]):
            return "summarize"
        if any(kw in prompt_lower for kw in ["explain", "what is"]):
            return "explain"
        if any(kw in prompt_lower for kw in ["ideas", "brainstorm"]):
            return "brainstorm"
        
        # Creative mapping
        for kw in CREATIVE_KEYWORDS:
            if kw in prompt_lower:
                if kw in ["story", "tale", "adventure", "quest", "write", "poem"]:
                    return "ai-story-generator"
                elif kw in ["character", "person", "who"]:
                    return "ai-character-chat"
                elif kw in ["name", "named"]:
                    return "fantasy-name"
        
        return "default"

    def generate(self, prompt: str, max_tokens: int = 2000, 
                 generator: str = None) -> Dict[str, Any]:
        """
        Generate text via Ollama API using generator-specific prompts.
        """
        start = time.time()
        
        if generator is None:
            generator = self._select_generator(prompt)
        
        # Fallback to default if generator isn't in our config
        gen_key = generator if generator in GENERATOR_CONFIGS else "default"
        model_tier, system_prompt = GENERATOR_CONFIGS[gen_key]
        model_name = MODEL_MAP[model_tier]

        try:
            # Construct the payload for Ollama /api/generate
            # We combine system prompt and user prompt for the 'prompt' field in basic generate
            # Or use the 'system' field for better control
            payload = {
                "model": model_name,
                "prompt": prompt if prompt else "Generate a random entry.",
                "system": system_prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7 if model_tier == "creative" else 0.3,
                }
            }

            response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                result_text = data.get("response", "").strip()
                
                if result_text:
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
                        "provider": "localgen",
                        "generator": gen_key,
                        "model": model_name,
                        "latency_ms": latency_ms,
                        "tokens_used": "local", # Unlimited
                        "error": None,
                    }
                else:
                    return self._error_result("Empty response from Ollama", start)
            else:
                return self._error_result(f"Ollama API HTTP {response.status_code}", start)
        
        except requests.exceptions.ConnectionError:
            return self._error_result("Ollama service not reachable", start)
        except Exception as e:
            return self._error_result(f"Unexpected error: {str(e)}", start)

    def _error_result(self, error: str, start: float) -> Dict[str, Any]:
        latency_ms = (time.time() - start) * 1000
        self.stats["requests"] += 1
        self.stats["failures"] += 1
        self.last_failure = error
        self.failure_count += 1
        
        if self.failure_count >= 3:
            self.available = False
        
        return {
            "response": "",
            "provider": "localgen",
            "latency_ms": latency_ms,
            "tokens_used": 0,
            "error": error,
        }

    def is_suitable_for(self, query: str, novelty: float) -> bool:
        if not self.available:
            return False
        
        query_lower = query.lower()
        is_creative = any(kw in query_lower for kw in CREATIVE_KEYWORDS)
        is_novel_but_not_complex = 0.5 < novelty < 0.85
        is_factual = any(kw in query_lower for kw in FACTUAL_KEYWORDS)
        
        return (is_creative or is_novel_but_not_complex) and not is_factual

    def get_stats(self) -> Dict[str, Any]:
        return {
            **self.stats,
            "available": self.available,
            "consecutive_failures": self.failure_count,
            "last_error": self.last_failure,
            "backend": "Ollama API (Direct)",
            "service_status": "ACTIVE" if self.available else "DISABLED",
        }

    def reset_availability(self):
        self.available = True

def localgen_generate(prompt: str, generator: str = None) -> Dict[str, Any]:
    provider = LocalGenProvider()
    return provider.generate(prompt, generator=generator)

def test_localgen():
    provider = LocalGenProvider()
    print("Testing Hardened LocalGen (Direct Ollama API)...")
    print("=" * 60)
    
    tests = [
        ("Fast Name", "fantasy-name", "A dark forest elf"),
        ("Fast Plot", "fantasy-plot", ""),
        ("Creative Chat", "ai-character-chat", "Tell me a riddle about time."),
        ("Creative Story", "ai-story-generator", "Write a 2-sentence story about a clockwork dragon."),
        ("Fast Explain", "explain", "What is a black hole?"),
    ]
    
    for category, gen, prompt in tests:
        print(f"\n{category} [{gen}]: \"{prompt}\"")
        result = provider.generate(prompt, generator=gen)
        if result["error"]:
            print(f"  [ERROR] {result['error']}")
        else:
            print(f"  [OK] {result['model']} | {result['latency_ms']:.0f}ms")
            print(f"  Response: {result['response'][:100]}...")

    print("\n" + "=" * 60)
    print(f"Stats: {provider.get_stats()}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python localgen_provider.py <prompt> or --test")
        sys.exit(1)
    
    if sys.argv[1] == "--test":
        test_localgen()
    else:
        prompt = " ".join(sys.argv[1:])
        result = localgen_generate(prompt)
        print(json.dumps(result, indent=2, ensure_ascii=False))
