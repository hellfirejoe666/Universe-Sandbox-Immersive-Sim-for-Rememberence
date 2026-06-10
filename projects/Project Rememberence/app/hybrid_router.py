"""
AIR-AI Hybrid Router for Rememberence
Intelligently routes AI requests between Perchance.org and local GPT4All models

Features:
- Smart routing based on request type, complexity, and availability
- Automatic fallback when services are rate-limited or unavailable
- Caching layer for common requests
- Integration with existing queue_manager and perchance_router
- Support for iterative storytelling, character management, and game master functions
"""

import json
import time
from typing import Dict, List, Any, Optional, Tuple, Callable
from pathlib import Path
from datetime import datetime
from enum import Enum
import hashlib


class AIProvider(Enum):
    """Available AI providers"""
    PERCHANCE = "perchance"
    GPT4ALL_LOCAL = "gpt4all_local"
    OLLAMA = "ollama"
    FALLBACK = "fallback"


class RequestType(Enum):
    """Types of AI requests"""
    CHARACTER_NAME = "character_name"
    CHARACTER_DESCRIPTION = "character_description"
    NPC_DIALOGUE = "npc_dialogue"
    QUEST_GENERATION = "quest_generation"
    NARRATIVE_ELEMENT = "narrative_element"
    WORLD_BUILDING = "world_building"
    SPECIES_TRAIT = "species_trait"
    COMBAT_DESCRIPTION = "combat_description"
    ITEM_GENERATION = "item_generation"
    STORY_ITERATION = "story_iteration"
    GAME_MASTER_ADVICE = "game_master_advice"
    SAVE_LOAD = "save_load"
    PLAYER_CHOICE_MANAGEMENT = "player_choice_management"


class HybridRouter:
    """
    Intelligent router for AIR-AI Oracle.
    
    Routes requests to the most appropriate AI provider based on:
    - Request type and complexity
    - Provider availability and rate limits
    - Cache hits
    - Performance requirements
    """
    
    # Routing rules: request_type -> preferred providers (in order)
    ROUTING_RULES = {
        RequestType.CHARACTER_NAME: [AIProvider.PERCHANCE, AIProvider.GPT4ALL_LOCAL, AIProvider.FALLBACK],
        RequestType.CHARACTER_DESCRIPTION: [AIProvider.PERCHANCE, AIProvider.GPT4ALL_LOCAL, AIProvider.FALLBACK],
        RequestType.NPC_DIALOGUE: [AIProvider.PERCHANCE, AIProvider.OLLAMA, AIProvider.GPT4ALL_LOCAL, AIProvider.FALLBACK],
        RequestType.QUEST_GENERATION: [AIProvider.PERCHANCE, AIProvider.GPT4ALL_LOCAL, AIProvider.FALLBACK],
        RequestType.NARRATIVE_ELEMENT: [AIProvider.GPT4ALL_LOCAL, AIProvider.PERCHANCE, AIProvider.FALLBACK],
        RequestType.WORLD_BUILDING: [AIProvider.GPT4ALL_LOCAL, AIProvider.PERCHANCE, AIProvider.FALLBACK],
        RequestType.SPECIES_TRAIT: [AIProvider.PERCHANCE, AIProvider.GPT4ALL_LOCAL, AIProvider.FALLBACK],
        RequestType.COMBAT_DESCRIPTION: [AIProvider.GPT4ALL_LOCAL, AIProvider.OLLAMA, AIProvider.FALLBACK],
        RequestType.ITEM_GENERATION: [AIProvider.PERCHANCE, AIProvider.GPT4ALL_LOCAL, AIProvider.FALLBACK],
        RequestType.STORY_ITERATION: [AIProvider.GPT4ALL_LOCAL, AIProvider.OLLAMA, AIProvider.FALLBACK],
        RequestType.GAME_MASTER_ADVICE: [AIProvider.GPT4ALL_LOCAL, AIProvider.OLLAMA, AIProvider.FALLBACK],
        RequestType.SAVE_LOAD: [AIProvider.FALLBACK],  # Local only
        RequestType.PLAYER_CHOICE_MANAGEMENT: [AIProvider.GPT4ALL_LOCAL, AIProvider.FALLBACK],
    }
    
    # Perchance element type mapping
    PERCHANCE_ELEMENT_MAP = {
        RequestType.CHARACTER_NAME: "character_name",
        RequestType.CHARACTER_DESCRIPTION: "character_description",
        RequestType.NPC_DIALOGUE: "npc_dialogue",
        RequestType.QUEST_GENERATION: "quest_idea",
        RequestType.SPECIES_TRAIT: "species_trait",
        RequestType.ITEM_GENERATION: "item_name",
        RequestType.WORLD_BUILDING: "place_name",
    }
    
    def __init__(self, config: Dict = None):
        """
        Initialize hybrid router.
        
        Args:
            config: Router configuration
        """
        self.config = config or {}
        
        # Provider status tracking
        self.provider_status = {
            AIProvider.PERCHANCE: {"available": True, "last_check": 0, "failures": 0},
            AIProvider.GPT4ALL_LOCAL: {"available": True, "last_check": 0, "failures": 0},
            AIProvider.OLLAMA: {"available": True, "last_check": 0, "failures": 0},
            AIProvider.FALLBACK: {"available": True, "last_check": 0, "failures": 0},
        }
        
        # Cache
        self.cache_dir = Path(__file__).parent.parent / "cache" / "hybrid_router"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "router_cache.json"
        self.cache: Dict[str, Any] = {}
        self._load_cache()
        
        # Performance metrics
        self.metrics = {
            "requests": 0,
            "cache_hits": 0,
            "perchance_calls": 0,
            "local_calls": 0,
            "fallback_calls": 0,
            "avg_response_time": 0.0,
            "errors": 0
        }
        
        # Initialize providers
        self.perchance_router = None
        self._init_providers()
    
    def _init_providers(self):
        """Initialize AI provider connections"""
        try:
            from perchance_router import get_perchance_router
            self.perchance_router = get_perchance_router()
            print("HybridRouter: Perchance router initialized")
        except Exception as e:
            print(f"HybridRouter: Failed to initialize Perchance router: {e}")
            self.provider_status[AIProvider.PERCHANCE]["available"] = False
    
    def _load_cache(self):
        """Load router cache from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                # Clean old entries
                self._clean_cache()
                print(f"HybridRouter cache loaded with {len(self.cache)} entries")
            except json.JSONDecodeError:
                print("HybridRouter cache corrupted, starting fresh")
                self.cache = {}
    
    def _save_cache(self):
        """Save router cache to disk"""
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
    
    def _get_cache_key(self, request_type: RequestType, params: Dict) -> str:
        """Generate cache key"""
        key_str = f"{request_type.value}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _check_cache(self, request_type: RequestType, params: Dict) -> Optional[Dict]:
        """Check if request is cached"""
        cache_key = self._get_cache_key(request_type, params)
        
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if cached.get('expires', 0) > time.time():
                self.metrics["cache_hits"] += 1
                return cached['result']
        
        return None
    
    def _cache_result(self, request_type: RequestType, params: Dict, result: Dict, ttl: int = 3600):
        """Cache a result"""
        cache_key = self._get_cache_key(request_type, params)
        self.cache[cache_key] = {
            'result': result,
            'created': datetime.now().isoformat(),
            'expires': time.time() + ttl
        }
        self._save_cache()
    
    def _select_provider(self, request_type: RequestType, context: Dict = None) -> AIProvider:
        """
        Select the best AI provider for a request.
        
        Args:
            request_type: Type of request
            context: Additional context
        
        Returns:
            Selected AIProvider
        """
        preferred_providers = self.ROUTING_RULES.get(request_type, [AIProvider.FALLBACK])
        
        for provider in preferred_providers:
            status = self.provider_status.get(provider, {})
            
            # Check if provider is available
            if not status.get("available", False):
                continue
            
            # Special handling for Perchance - check rate limits
            if provider == AIProvider.PERCHANCE:
                if self.perchance_router:
                    allowed, _ = self.perchance_router._check_rate_limit()
                    if not allowed:
                        continue
            
            return provider
        
        # Fallback to fallback provider
        return AIProvider.FALLBACK
    
    def _execute_perchance(self, request_type: RequestType, params: Dict) -> Tuple[bool, Dict]:
        """Execute request via Perchance"""
        if not self.perchance_router:
            return False, {"error": "Perchance router not available"}
        
        element_type = self.PERCHANCE_ELEMENT_MAP.get(request_type)
        if not element_type:
            return False, {"error": f"No Perchance mapping for {request_type}"}
        
        try:
            context = params.get("context", {})
            result = self.perchance_router.generate(
                element_type=element_type,
                context=context,
                use_cache=True,
                fallback_local=True
            )
            
            self.metrics["perchance_calls"] += 1
            
            if result["success"]:
                return True, {
                    "content": result["result"],
                    "provider": "perchance",
                    "metadata": result.get("metadata", {})
                }
            else:
                return False, {"error": result.get("error", "Perchance generation failed")}
        
        except Exception as e:
            self.metrics["errors"] += 1
            return False, {"error": str(e)}
    
    def _execute_local(self, request_type: RequestType, params: Dict) -> Tuple[bool, Dict]:
        """Execute request via local GPT4All model"""
        # Placeholder - integrate with actual GPT4All model
        # This would call your local LLM with appropriate prompts
        
        prompt = self._build_local_prompt(request_type, params)
        
        # TODO: Integrate with actual GPT4All inference
        # For now, return a placeholder
        result = {
            "content": f"[Local GPT4All] Generated {request_type.value} for: {params}",
            "provider": "gpt4all_local",
            "metadata": {
                "prompt_length": len(prompt),
                "model": "placeholder"
            }
        }
        
        self.metrics["local_calls"] += 1
        return True, result
    
    def _execute_ollama(self, request_type: RequestType, params: Dict) -> Tuple[bool, Dict]:
        """Execute request via Ollama"""
        # Placeholder - integrate with Ollama API
        result = {
            "content": f"[Ollama] Generated {request_type.value} for: {params}",
            "provider": "ollama",
            "metadata": {}
        }
        
        self.metrics["local_calls"] += 1
        return True, result
    
    def _execute_fallback(self, request_type: RequestType, params: Dict) -> Tuple[bool, Dict]:
        """Execute request via fallback (simple templates)"""
        result = self._generate_fallback(request_type, params)
        self.metrics["fallback_calls"] += 1
        return True, result
    
    def _build_local_prompt(self, request_type: RequestType, params: Dict) -> str:
        """Build prompt for local LLM based on request type"""
        base_prompts = {
            RequestType.CHARACTER_NAME: "Generate a unique fantasy character name:",
            RequestType.CHARACTER_DESCRIPTION: "Create a detailed character description:",
            RequestType.NPC_DIALOGUE: "Write NPC dialogue in character:",
            RequestType.QUEST_GENERATION: "Generate an engaging quest idea:",
            RequestType.SPECIES_TRAIT: "Describe a unique species trait for Rememberence:",
        }
        
        base = base_prompts.get(request_type, "Generate content:")
        context = params.get("context", {})
        
        prompt = f"{base}\n"
        if "species" in context:
            prompt += f"Species: {context['species']}\n"
        if "tone" in context:
            prompt += f"Tone: {context['tone']}\n"
        if "context" in context:
            prompt += f"Context: {context['context']}\n"
        
        return prompt
    
    def _generate_fallback(self, request_type: RequestType, params: Dict) -> Dict:
        """Generate fallback content using templates"""
        fallbacks = {
            RequestType.CHARACTER_NAME: {
                "content": f"Traveler-{int(time.time()) % 10000}",
                "provider": "fallback",
                "metadata": {"template": "simple"}
            },
            RequestType.SPECIES_TRAIT: {
                "content": f"Innate {params.get('context', {}).get('species', 'being')} ability manifests",
                "provider": "fallback",
                "metadata": {"template": "species_trait"}
            },
            RequestType.QUEST_GENERATION: {
                "content": "Discover the source of the mysterious disturbances",
                "provider": "fallback",
                "metadata": {"template": "quest_basic"}
            }
        }
        
        return fallbacks.get(request_type, {
            "content": f"Generated content for {request_type.value}",
            "provider": "fallback",
            "metadata": {}
        })
    
    def route_request(self, request_type: RequestType, params: Dict, 
                     use_cache: bool = True, timeout: float = 30.0) -> Dict[str, Any]:
        """
        Route an AI request to the appropriate provider.
        
        Args:
            request_type: Type of request
            params: Request parameters
            use_cache: Whether to use cached results
            timeout: Request timeout in seconds
        
        Returns:
            Dict with 'success', 'result', 'provider', 'metadata'
        """
        start_time = time.time()
        self.metrics["requests"] += 1
        
        # Check cache first
        if use_cache:
            cached = self._check_cache(request_type, params)
            if cached:
                return {
                    "success": True,
                    "result": cached,
                    "provider": "cache",
                    "metadata": {"cached": True}
                }
        
        # Select provider
        provider = self._select_provider(request_type, params.get("context", {}))
        
        # Execute request
        try:
            if provider == AIProvider.PERCHANCE:
                success, result = self._execute_perchance(request_type, params)
            elif provider == AIProvider.GPT4ALL_LOCAL:
                success, result = self._execute_local(request_type, params)
            elif provider == AIProvider.OLLAMA:
                success, result = self._execute_ollama(request_type, params)
            else:  # FALLBACK
                success, result = self._execute_fallback(request_type, params)
            
            # Update metrics
            elapsed = time.time() - start_time
            self._update_metrics(elapsed, success)
            
            if success:
                # Cache successful result
                if use_cache and provider != AIProvider.FALLBACK:
                    self._cache_result(request_type, params, result)
                
                return {
                    "success": True,
                    "result": result.get("content"),
                    "provider": provider.value,
                    "metadata": {
                        "response_time": elapsed,
                        **result.get("metadata", {})
                    }
                }
            else:
                # Provider failed - try fallback
                if provider != AIProvider.FALLBACK:
                    self.provider_status[provider]["failures"] += 1
                    return self.route_request(request_type, params, use_cache=False)
                
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "provider": provider.value,
                    "metadata": {}
                }
        
        except Exception as e:
            self.metrics["errors"] += 1
            return {
                "success": False,
                "error": str(e),
                "provider": "error",
                "metadata": {}
            }
    
    def _update_metrics(self, elapsed: float, success: bool):
        """Update performance metrics"""
        # Update average response time
        total = self.metrics["requests"]
        avg = self.metrics["avg_response_time"]
        self.metrics["avg_response_time"] = ((avg * (total - 1)) + elapsed) / total
        
        if not success:
            self.metrics["errors"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get router performance metrics"""
        return {
            **self.metrics,
            "cache_size": len(self.cache),
            "provider_status": self.provider_status
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive stats including Perchance cache"""
        stats = self.get_metrics()
        
        if self.perchance_router:
            stats["perchance_cache"] = self.perchance_router.get_cache_stats()
        
        return stats
    
    def clear_cache(self, request_type: RequestType = None):
        """Clear router cache"""
        if request_type:
            # Clear specific type
            keys_to_remove = [
                k for k in self.cache.keys() 
                if k.startswith(request_type.value)
            ]
            for k in keys_to_remove:
                del self.cache[k]
        else:
            self.cache = {}
        
        self._save_cache()
        
        # Also clear Perchance cache
        if self.perchance_router:
            self.perchance_router.clear_cache()


# Convenience functions for Rememberence integration
def generate_character_name(species: str = None, context: Dict = None) -> Dict:
    """Generate a character name"""
    router = HybridRouter()
    params = {"context": {"species": species, **(context or {})}}
    return router.route_request(RequestType.CHARACTER_NAME, params)


def generate_quest(context: Dict = None) -> Dict:
    """Generate a quest idea"""
    router = HybridRouter()
    params = {"context": context or {}}
    return router.route_request(RequestType.QUEST_GENERATION, params)


def generate_species_trait(species: str, context: Dict = None) -> Dict:
    """Generate a species-specific trait"""
    router = HybridRouter()
    params = {"context": {"species": species, **(context or {})}}
    return router.route_request(RequestType.SPECIES_TRAIT, params)


# Global instance
_hybrid_router: Optional[HybridRouter] = None


def get_hybrid_router() -> HybridRouter:
    """Get or create global hybrid router instance"""
    global _hybrid_router
    if _hybrid_router is None:
        _hybrid_router = HybridRouter()
    return _hybrid_router
