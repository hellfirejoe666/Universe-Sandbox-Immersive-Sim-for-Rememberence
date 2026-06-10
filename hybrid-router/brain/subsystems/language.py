"""
Language System (Language Centers)

llama3.2 + Pattern matching + Donjon-style procedural generation.
Integrates with existing Hybrid Router infrastructure.
"""

import subprocess
import json
import re
import random
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


# Paths from existing Hybrid Router
WORKSPACE = Path("D:/Ollama/OpenClaw/workspace")
ROUTER_DIR = WORKSPACE / "hybrid-router"
AIML_DIR = Path("D:/GPT4All/AIPlus/alice/DATA")
PATTERNS_FILE = ROUTER_DIR / "learned_patterns.json"
CACHE_FILE = ROUTER_DIR / "response_cache.json"

# Models
FAST_MODEL = "phi3:mini"
SMART_MODEL = "llama3.2"  # Updated from qwen2.5:7b


class PatternMatcher:
    """AIML-style pattern matching with wildcard support."""
    
    def __init__(self):
        self.patterns = []
        self.learned_patterns = {}
        self.load_learned_patterns()
    
    def load_learned_patterns(self):
        """Load previously learned patterns."""
        if PATTERNS_FILE.exists():
            try:
                self.learned_patterns = json.loads(PATTERNS_FILE.read_text())
            except:
                self.learned_patterns = {}
    
    def match(self, text: str) -> Optional[str]:
        """Try to match input against patterns. Returns response or None."""
        text_upper = text.upper().strip()
        
        # Check learned patterns first
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
        
        return None
    
    def add_pattern(self, pattern: str, response: str):
        """Add a learned pattern."""
        self.learned_patterns[pattern] = response
        PATTERNS_FILE.write_text(json.dumps(self.learned_patterns, indent=2))


class ResponseCache:
    """Cache LLM responses by content hash."""
    
    def __init__(self):
        self.cache = {}
        self.load_cache()
    
    def load_cache(self):
        if CACHE_FILE.exists():
            try:
                self.cache = json.loads(CACHE_FILE.read_text())
            except:
                self.cache = {}
    
    def save_cache(self):
        CACHE_FILE.write_text(json.dumps(self.cache, indent=2))
    
    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    def get(self, text: str) -> Optional[Any]:
        key = self._hash(text)
        return self.cache.get(key)
    
    def set(self, text: str, response: Any):
        key = self._hash(text)
        self.cache[key] = {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "uses": 0
        }
        self.save_cache()


class LanguageSystem:
    """
    Generates language responses using hybrid approach.
    Integrates pattern matching, caching, and LLM calls.
    """
    
    def __init__(self):
        self.matcher = PatternMatcher()
        self.cache = ResponseCache()
        
        # Procedural templates for common responses
        self.templates = {
            'greeting': [
                "Hello! How can I help you today?",
                "Hey there! What's on your mind?",
                "Greetings! Ready to assist.",
            ],
            'acknowledgment': [
                "Got it!",
                "Understood.",
                "I see. Let me help with that.",
            ],
            'thanks': [
                "You're welcome!",
                "Happy to help!",
                "Anytime!",
            ]
        }
    
    def fast_response(self, query: str, context: Dict) -> Dict[str, Any]:
        """
        Generate fast response (pattern-matched or cached).
        
        Used for familiar queries where speed matters.
        """
        start_time = datetime.now()
        
        # 1. Check cache first
        cached = self.cache.get(query)
        if cached:
            return {
                'content': cached['response'],
                'path': 'fast',
                'generator': 'cache',
                'latency_ms': 0,
                'cached': True
            }
        
        # 2. Check pattern matching
        pattern_response = self.matcher.match(query)
        if pattern_response:
            return {
                'content': pattern_response,
                'path': 'fast',
                'generator': 'pattern',
                'latency_ms': 0,
                'cached': False
            }
        
        # 3. Check procedural templates
        query_lower = query.lower()
        
        if any(g in query_lower for g in ['hello', 'hi', 'hey', 'greetings']):
            response = random.choice(self.templates['greeting'])
            self.cache.set(query, response)
            return {
                'content': response,
                'path': 'fast',
                'generator': 'procedural',
                'latency_ms': 0,
                'cached': False
            }
        
        if 'thank' in query_lower or 'thanks' in query_lower:
            response = random.choice(self.templates['thanks'])
            self.cache.set(query, response)
            return {
                'content': response,
                'path': 'fast',
                'generator': 'procedural',
                'latency_ms': 0,
                'cached': False
            }
        
        # 4. Fall back to SMART path
        return self.smart_response(query, context)
    
    def smart_response(self, query: str, context: Dict) -> Dict[str, Any]:
        """
        Generate smart response using llama3.2 (local LLM).
        
        Used for semi-familiar queries requiring reasoning.
        """
        start_time = datetime.now()
        
        # Check cache first
        cached = self.cache.get(query)
        if cached:
            return {
                'content': cached['response'],
                'path': 'smart',
                'generator': 'llama3.2',
                'latency_ms': 0,
                'cached': True
            }
        
        try:
            # Run llama3.2 via Ollama
            result = subprocess.run(
                ["ollama", "run", SMART_MODEL, query],
                capture_output=True,
                text=True,
                timeout=45,
                encoding='utf-8',
                errors='replace'
            )
            
            latency = (datetime.now() - start_time).total_seconds() * 1000
            response = result.stdout.strip()
            
            # Cache the response
            self.cache.set(query, response)
            
            return {
                'content': response,
                'path': 'smart',
                'generator': 'llama3.2',
                'latency_ms': latency,
                'cached': False
            }
        
        except subprocess.TimeoutExpired:
            return {
                'content': "[TIMEOUT] Local model took too long.",
                'path': 'smart',
                'generator': 'llama3.2',
                'latency_ms': 45000,
                'cached': False
            }
        except Exception as e:
            return {
                'content': f"[ERROR] {e}",
                'path': 'smart',
                'generator': 'llama3.2',
                'latency_ms': 0,
                'cached': False
            }
    
    def blend_response(self, query: str, context: Dict, 
                      llm_output: str, procedural_variants: list,
                      blend_weight: float = 0.6) -> Dict[str, Any]:
        """
        Blend LLM output with procedural variants.
        
        For future implementation when we have Donjon-style generators.
        """
        # For now, just use LLM output
        return {
            'content': llm_output,
            'path': 'smart',
            'generator': 'blended',
            'blend_weight': blend_weight
        }
    
    def get_response_style(self, context: Dict) -> str:
        """Determine response style based on context."""
        user_state = context.get('user_state', 'neutral')
        
        styles = {
            'coding': 'technical',
            'social': 'friendly',
            'learning': 'educational',
            'creative': 'expressive',
            'frustrated': 'supportive',
            'urgent': 'direct'
        }
        
        return styles.get(user_state, 'neutral')
    
    def learn_pattern(self, pattern: str, response: str):
        """Learn a new pattern-response pair."""
        self.matcher.add_pattern(pattern, response)
        print(f"[Language] Learned pattern: {pattern}")
