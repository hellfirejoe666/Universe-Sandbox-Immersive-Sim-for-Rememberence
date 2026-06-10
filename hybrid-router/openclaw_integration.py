#!/usr/bin/env python3
"""
Hybrid Router - OpenClaw Integration

Integrates the hybrid router into OpenClaw's message flow:
1. Pre-process incoming messages (compress, cache check, route)
2. Summarize heartbeat responses
3. Token accounting for OpenClaw sessions
4. Pattern learning from successful interactions

Usage:
- As a pre-processor before OpenClaw agent runs
- For heartbeat summarization
- For token optimization across all agent interactions
"""

import sys
import json
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))
from router_v2 import HybridRouterV2
from token_optimizer import TokenOptimizer

WORKSPACE = Path("D:/Ollama/OpenClaw/workspace")
ROUTER_DIR = WORKSPACE / "hybrid-router"
OPENCLAW_CACHE_FILE = ROUTER_DIR / "openclaw_cache.json"


class OpenClawHybridIntegration:
    """
    Integrates hybrid router with OpenClaw message flow.
    
    Use cases:
    1. Pre-process incoming messages before agent sees them
    2. Summarize heartbeat responses to reduce token usage
    3. Cache common OpenClaw commands/responses
    4. Learn patterns from successful interactions
    """
    
    def __init__(self):
        self.router = HybridRouterV2()
        self.token_optimizer = TokenOptimizer()
        self.openclaw_cache = self._load_openclaw_cache()
        
        # Pre-learned OpenClaw patterns
        self._load_openclaw_patterns()
    
    def _load_openclaw_cache(self) -> Dict[str, Any]:
        if OPENCLAW_CACHE_FILE.exists():
            try:
                return json.loads(OPENCLAW_CACHE_FILE.read_text(encoding='utf-8'))
            except:
                pass
        return {}
    
    def _save_openclaw_cache(self):
        OPENCLAW_CACHE_FILE.write_text(json.dumps(self.openclaw_cache, indent=2), encoding='utf-8')
    
    def _load_openclaw_patterns(self):
        """Pre-load common OpenClaw patterns for instant responses."""
        openclaw_patterns = {
            # Gateway commands
            "GATEWAY STATUS": "Gateway is running on http://127.0.0.1:18789",
            "GATEWAY RESTART": "Restarting Gateway...",
            "OPENCLAW STATUS": "OpenClaw is operational",
            
            # Common questions
            "WHAT IS OPENCLAW": "OpenClaw is a self-hosted AI gateway connecting chat apps to coding agents",
            "WHAT MODELS AVAILABLE": "Available models: qwen3.5:cloud, qwen2.5:7b, phi3:mini, hybrid-router",
            "HOW TO INSTALL": "npm install -g openclaw@latest && openclaw onboard",
            
            # Heartbeat patterns
            "HEARTBEAT OK": "✓",
            "NOTHING NEEDS ATTENTION": "✓ All systems normal",
            "NO URGENT TASKS": "✓ No urgent tasks",
        }
        
        for pattern, response in openclaw_patterns.items():
            if pattern not in self.token_optimizer.pattern_learner.patterns:
                self.token_optimizer.pattern_learner.patterns[pattern] = response
        
        self.token_optimizer.pattern_learner.save_patterns()
    
    def preprocess_message(self, message: str) -> Dict[str, Any]:
        """
        Pre-process an incoming message before the agent sees it.
        
        Returns routing decision with optional early response.
        """
        result = self.router.route(message, use_fft=True, use_optimization=True)
        
        # If we got a cached or pattern response, return it immediately
        if result["path"] in ["cached", "fast"]:
            return {
                "action": "respond_early",
                "response": result["response"],
                "path": result["path"],
                "tokens_saved": result.get("tokens_saved", 0),
                "latency_ms": result.get("latency_ms", 0)
            }
        
        # Otherwise, let the agent handle it with optimization metadata
        return {
            "action": "forward_to_agent",
            "optimized_query": result.get("optimization", {}).get("compressed_query", message),
            "routing_path": result["path"],
            "fft_novelty": result.get("fft", {}).get("novelty_score", 0),
            "tokens_estimated": result.get("tokens_used", 0)
        }
    
    def summarize_heartbeat(self, heartbeat_response: str) -> str:
        """
        Summarize a heartbeat response to reduce token usage.
        
        Long heartbeat responses get condensed while preserving key info.
        """
        # Check if it's just an OK response
        if "HEARTBEAT_OK" in heartbeat_response or len(heartbeat_response) < 100:
            return heartbeat_response.strip()
        
        # For longer responses, use the router to summarize
        summary_prompt = f"Summarize this heartbeat checkup in 1-2 sentences, keep only urgent items:\n\n{heartbeat_response}"
        
        try:
            result = subprocess.run(
                ["ollama", "run", "phi3:mini", summary_prompt],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='ignore'
            )
            
            summary = result.stdout.strip()
            
            # Cache the summary
            cache_key = hashlib.sha256(heartbeat_response.encode()).hexdigest()[:16]
            self.openclaw_cache[cache_key] = {
                "original": heartbeat_response[:200],
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }
            self._save_openclaw_cache()
            
            return summary
            
        except:
            # Fallback: just truncate
            return heartbeat_response[:200] + "..." if len(heartbeat_response) > 200 else heartbeat_response
    
    def learn_from_interaction(self, query: str, response: str, was_helpful: bool = True):
        """
        Learn from a completed interaction.
        
        Call this after the agent responds to build up pattern cache.
        """
        if was_helpful:
            learned_pattern = self.token_optimizer.pattern_learner.learn(query, response)
            if learned_pattern:
                print(f"[LEARNED] Pattern: {learned_pattern}")
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get comprehensive stats for OpenClaw integration."""
        router_stats = self.router.get_stats()
        
        return {
            "openclaw_integration": {
                "cache_entries": len(self.openclaw_cache),
                "pre_learned_patterns": len(self.token_optimizer.pattern_learner.patterns),
            },
            **router_stats
        }
    
    def export_for_openclaw_skill(self) -> str:
        """
        Export integration as an OpenClaw skill.
        
        This creates a SKILL.md that can be loaded by OpenClaw agents.
        """
        skill_content = '''# Hybrid Router Skill

Use the hybrid router to optimize token usage and route messages efficiently.

## Commands

```bash
# Pre-process a message
python hybrid-router/openclaw_integration.py preprocess "user message here"

# Summarize heartbeat response
python hybrid-router/openclaw_integration.py summarize "heartbeat response text"

# Get integration stats
python hybrid-router/openclaw_integration.py stats

# Learn from interaction
python hybrid-router/openclaw_integration.py learn "query" "response"
```

## Integration Points

1. **Message Pre-processing**: Run before agent sees message to check cache/patterns
2. **Heartbeat Summarization**: Condense long heartbeat responses
3. **Pattern Learning**: Automatically learn from successful interactions
4. **Token Accounting**: Track tokens saved vs used

## Example Flow

```
User Message → Pre-process → [Cache Hit? Return Early] → [No? Forward to Agent]
Agent Response → Learn Pattern → Update Cache
```
'''
        
        skill_path = WORKSPACE / "skills" / "hybrid-router" / "SKILL.md"
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(skill_content, encoding='utf-8')
        
        return str(skill_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python openclaw_integration.py <command> [args]")
        print("Commands:")
        print("  preprocess <message>  - Pre-process a message")
        print("  summarize <text>      - Summarize heartbeat response")
        print("  learn <query> <resp>  - Learn from interaction")
        print("  stats                 - Show integration stats")
        print("  export-skill          - Export as OpenClaw skill")
        sys.exit(1)
    
    integration = OpenClawHybridIntegration()
    cmd = sys.argv[1].lower()
    
    if cmd == "preprocess":
        message = " ".join(sys.argv[2:])
        result = integration.preprocess_message(message)
        print(json.dumps(result, indent=2))
        
    elif cmd == "summarize":
        text = " ".join(sys.argv[2:])
        summary = integration.summarize_heartbeat(text)
        print(f"Summary: {summary}")
        
    elif cmd == "learn":
        if len(sys.argv) < 4:
            print("Usage: learn <query> <response>")
            sys.exit(1)
        integration.learn_from_interaction(sys.argv[2], sys.argv[3])
        
    elif cmd == "stats":
        stats = integration.get_integration_stats()
        print(json.dumps(stats, indent=2))
        
    elif cmd == "export-skill":
        skill_path = integration.export_for_openclaw_skill()
        print(f"Exported skill to: {skill_path}")
        
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
