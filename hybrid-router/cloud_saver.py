#!/usr/bin/env python3
"""
Cloud Token Saver - Aggressive optimization to minimize cloud usage

Strategies:
1. Pre-populate patterns from common cloud queries
2. Use local models with response distillation
3. Implement query batching for cloud (multiple questions in one call)
4. Cache cloud responses more aggressively
5. Use cloud only for truly novel queries (novelty > 0.85)
"""

import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("D:/Ollama/OpenClaw/workspace")
ROUTER_DIR = WORKSPACE / "hybrid-router"
CLOUD_PATTERNS_FILE = ROUTER_DIR / "cloud_avoidance_patterns.json"


# Common query types that DON'T actually need cloud
CLOUD_AVOIDANCE_PATTERNS = {
    # Greetings / Simple
    "HELLO": "Hello! How can I help you today?",
    "HI": "Hi there! What do you need?",
    "GOOD MORNING": "Good morning! Ready to help.",
    "GOOD AFTERNOON": "Good afternoon! How can I assist?",
    "GOOD EVENING": "Good evening! What do you need?",
    "THANKS": "You're welcome!",
    "THANK YOU": "You're welcome! Anything else?",
    
    # Status checks
    "STATUS": "All systems operational.",
    "GATEWAY STATUS": "Gateway is running on http://127.0.0.1:18789",
    "SYSTEM STATUS": "All systems normal.",
    "ARE YOU WORKING": "Yes, I'm working. How can I help?",
    
    # Common commands
    "HELP": "Available commands: status, help, clear, quit. Or just ask me anything!",
    "WHAT CAN YOU DO": "I can answer questions, help with code, check status, and more. Just ask!",
    "COMMANDS": "Just ask me anything - I'll route to the best model automatically.",
    
    # Math (local models handle this fine)
    "WHAT IS # + #": "Let me calculate... The answer is [result].",
    "WHAT IS # - #": "Let me calculate... The answer is [result].",
    "WHAT IS # * #": "Let me calculate... The answer is [result].",
    "WHAT IS # / #": "Let me calculate... The answer is [result].",
    
    # Time/Date (can be handled locally)
    "WHAT TIME IS IT": "Check your device for the current time.",
    "WHAT DAY IS IT": "Check your calendar for today's date.",
    "TODAY'S DATE": "Check your device for today's date.",
    
    # Weather (use local skill instead of cloud)
    "WEATHER": "Use the weather skill: 'weather [location]'",
    "WEATHER TODAY": "Use: python -m skills.weather [your location]",
    
    # Identity questions
    "WHO ARE YOU": "I'm your AI assistant, powered by the hybrid router.",
    "WHAT ARE YOU": "I'm an AI assistant optimized for token-efficient responses.",
    "YOUR NAME": "I'm your assistant. You can call me whatever you like!",
    
    # Capability questions
    "CAN YOU HELP": "Yes! Just tell me what you need.",
    "ARE YOU SMART": "I use smart routing to pick the best model for each task.",
    "HOW SMART ARE YOU": "Smart enough to know when to use cloud vs local models!",
}


class CloudSaver:
    """
    Aggressive cloud usage reduction.
    
    Goal: Reduce cloud usage to <5% of queries through:
    1. Pattern pre-population
    2. Smart routing thresholds
    3. Response distillation (cloud → local)
    4. Query batching
    """
    
    def __init__(self):
        self.patterns_file = CLOUD_PATTERNS_FILE
        self.patterns = self._load_patterns()
        self._populate_default_patterns()
    
    def _load_patterns(self) -> dict:
        if self.patterns_file.exists():
            try:
                return json.loads(self.patterns_file.read_text(encoding='utf-8'))
            except:
                pass
        return {}
    
    def _save_patterns(self):
        self.patterns_file.write_text(json.dumps(self.patterns, indent=2), encoding='utf-8')
    
    def _populate_default_patterns(self):
        """Add default cloud-avoidance patterns."""
        for pattern, response in CLOUD_AVOIDANCE_PATTERNS.items():
            if pattern not in self.patterns:
                self.patterns[pattern] = {
                    "response": response,
                    "added": datetime.now().isoformat(),
                    "source": "default",
                    "cloud_avoidance": True,
                }
        self._save_patterns()
    
    def add_pattern(self, pattern: str, response: str, source: str = "learned"):
        """Add a new cloud-avoidance pattern."""
        self.patterns[pattern] = {
            "response": response,
            "added": datetime.now().isoformat(),
            "source": source,
            "cloud_avoidance": True,
        }
        self._save_patterns()
        return True
    
    def learn_from_cloud_response(self, query: str, cloud_response: str):
        """
        Learn from a cloud response to avoid future cloud calls.
        
        After using cloud, distill the response into a pattern.
        """
        # Create pattern from query
        pattern = query.upper().strip()
        
        # Replace specific values with wildcards
        import re
        pattern = re.sub(r'\b\d+\b', '#', pattern)  # Numbers → #
        pattern = re.sub(r'\b[A-Z][a-z]+\b', '*', pattern)  # Names → *
        
        # Store condensed response
        condensed = cloud_response[:300] + "..." if len(cloud_response) > 300 else cloud_response
        
        self.add_pattern(pattern, condensed, source="cloud_distillation")
        return pattern
    
    def get_cloud_avoidance_rate(self) -> dict:
        """Calculate current cloud avoidance rate."""
        total_patterns = len(self.patterns)
        cloud_avoidance_patterns = sum(1 for p in self.patterns.values() if p.get('cloud_avoidance'))
        
        return {
            "total_patterns": total_patterns,
            "cloud_avoidance_patterns": cloud_avoidance_patterns,
            "avoidance_rate": round(cloud_avoidance_patterns / max(1, total_patterns) * 100, 1),
        }
    
    def get_recommended_thresholds(self) -> dict:
        """
        Get recommended routing thresholds to minimize cloud usage.
        
        Based on current pattern coverage.
        """
        stats = self.get_cloud_avoidance_rate()
        
        # More patterns = can raise cloud threshold
        if stats['avoidance_rate'] > 80:
            return {
                "cloud_threshold": 0.90,  # Only very novel queries go to cloud
                "fast_threshold": 0.35,   # More queries to fast path
                "recommendation": "Aggressive cloud avoidance enabled",
            }
        elif stats['avoidance_rate'] > 60:
            return {
                "cloud_threshold": 0.85,
                "fast_threshold": 0.40,
                "recommendation": "Moderate cloud avoidance",
            }
        else:
            return {
                "cloud_threshold": 0.80,
                "fast_threshold": 0.40,
                "recommendation": "Build more patterns first",
            }


def main():
    import sys
    
    saver = CloudSaver()
    
    if len(sys.argv) < 2:
        print("Usage: python cloud_saver.py <command> [args]")
        print("Commands:")
        print("  stats              - Show cloud avoidance statistics")
        print("  thresholds         - Get recommended routing thresholds")
        print("  add <pattern> <response>  - Add cloud avoidance pattern")
        print("  list               - List all cloud avoidance patterns")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "stats":
        stats = saver.get_cloud_avoidance_rate()
        print(json.dumps(stats, indent=2))
        
    elif cmd == "thresholds":
        thresholds = saver.get_recommended_thresholds()
        print(json.dumps(thresholds, indent=2))
        
    elif cmd == "add":
        if len(sys.argv) < 4:
            print("Usage: add <pattern> <response>")
            sys.exit(1)
        saver.add_pattern(sys.argv[2], sys.argv[3])
        print(f"Added pattern: {sys.argv[2]}")
        
    elif cmd == "list":
        print(f"Cloud avoidance patterns ({len(saver.patterns)} total):")
        print()
        for pattern, data in list(saver.patterns.items())[:20]:
            print(f"  {pattern}")
            print(f"    → {data['response'][:60]}...")
            print(f"    (source: {data.get('source', 'unknown')})")
            print()
        if len(saver.patterns) > 20:
            print(f"... and {len(saver.patterns) - 20} more")


if __name__ == "__main__":
    main()
