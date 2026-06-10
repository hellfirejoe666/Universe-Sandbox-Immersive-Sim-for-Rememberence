#!/usr/bin/env python3
"""
Test script for Neural Router.

Run this to test the brain-inspired routing architecture.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from brain.neural_router import NeuralRouter


def main():
    print("=" * 60)
    print("NEURAL ROUTER TEST - Brain-Inspired Architecture")
    print("=" * 60)
    print()
    
    # Initialize router
    print("[Test] Initializing Neural Router...")
    router = NeuralRouter()
    print("[Test] Router initialized successfully!\n")
    
    # Test queries
    test_cases = [
        ("Hello!", {"user_state": "chatting"}),
        ("What is 2 + 2?", {"user_state": "learning"}),
        ("Write a Python function to sort a list", {"user_state": "coding"}),
        ("URGENT: My code is broken!!!", {"user_state": "frustrated"}),
        ("Tell me a story about a dragon", {"user_state": "creative"}),
    ]
    
    print("=" * 60)
    print("TEST QUERIES")
    print("=" * 60)
    
    for query, context in test_cases:
        print(f"\n[Query] {query}")
        print(f"[Context] {context}")
        
        try:
            response = router.route(query, context)
            meta = response.get('metadata', {})
            
            print(f"[Path] {meta.get('path', 'unknown')} ({meta.get('reason', 'unknown')})")
            print(f"[Quality] {meta.get('quality_score', 0):.2f}")
            print(f"[Time] {meta.get('elapsed_ms', 0)}ms")
            print(f"[Response] {response.get('content', '')[:100]}...")
        except Exception as e:
            print(f"[Error] {e}")
    
    # Show statistics
    print("\n" + "=" * 60)
    print("ROUTING STATISTICS")
    print("=" * 60)
    
    stats = router.get_stats()
    print(json.dumps(stats, indent=2))
    
    # Test idle processing (Default Mode Network)
    print("\n" + "=" * 60)
    print("IDLE PROCESSING (Default Mode Network)")
    print("=" * 60)
    
    router.idle()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
