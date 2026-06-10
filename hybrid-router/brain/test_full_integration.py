#!/usr/bin/env python3
"""
Full Integration Test for Neural Router

Tests all path executors with real queries.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from brain.neural_router import NeuralRouter


def main():
    print("=" * 70)
    print("NEURAL ROUTER - FULL INTEGRATION TEST")
    print("=" * 70)
    print()
    
    router = NeuralRouter()
    
    # Test queries designed to hit different paths
    test_cases = [
        # FAST path tests (pattern-matched)
        ("Hello!", {"user_state": "chatting"}, "fast"),
        ("Hi there", {"user_state": "social"}, "fast"),
        ("Thanks!", {"user_state": "chatting"}, "fast"),
        
        # SMART path tests (local LLM - llama3.2)
        ("What is the capital of France?", {"user_state": "learning"}, "smart"),
        ("Explain quantum computing in simple terms", {"user_state": "learning"}, "smart"),
        
        # CLOUD path tests (novel/complex)
        ("Write a detailed analysis of climate change impacts on agriculture", 
         {"user_state": "research"}, "cloud"),
        
        # Salience override test
        ("URGENT: Everything is broken!!!", {"user_state": "crisis"}, "cloud"),
    ]
    
    print("Running test queries...\n")
    
    results = {
        'fast': 0,
        'smart': 0,
        'cloud': 0,
        'total': 0
    }
    
    for query, context, expected_path in test_cases:
        results['total'] += 1
        print(f"[{results['total']}] Query: {query[:60]}{'...' if len(query) > 60 else ''}")
        print(f"    Expected: {expected_path}")
        
        try:
            response = router.route(query, context)
            meta = response.get('metadata', {})
            actual_path = meta.get('path', 'unknown')
            
            results[actual_path] = results.get(actual_path, 0) + 1
            
            # Check if matched expected
            match = "[OK]" if actual_path == expected_path else "[FAIL]"
            print(f"    {match} Actual: {actual_path} ({meta.get('reason', 'unknown')})")
            print(f"    Quality: {meta.get('quality_score', 0):.2f} | Time: {meta.get('elapsed_ms', 0)}ms")
            print(f"    Response: {response.get('content', '')[:80]}{'...' if len(response.get('content', '')) > 80 else ''}")
            
        except Exception as e:
            print(f"    [ERROR] {e}")
        
        print()
    
    # Statistics
    print("=" * 70)
    print("ROUTING STATISTICS")
    print("=" * 70)
    
    stats = router.get_stats()
    print(f"Total requests: {stats['requests_processed']}")
    print(f"Fast path:  {stats.get('fast_pct', 0):5.1f}%  ({stats['fast_path']} requests)")
    print(f"Smart path: {stats.get('smart_pct', 0):5.1f}%  ({stats['smart_path']} requests)")
    print(f"Cloud path: {stats.get('cloud_pct', 0):5.1f}%  ({stats['cloud_path']} requests)")
    print(f"Quality rejections: {stats.get('quality_rejections', 0)}")
    print(f"Salience overrides: {stats.get('salience_overrides', 0)}")
    print()
    
    # Memory stats
    print("MEMORY STATS")
    print("-" * 70)
    mem_stats = router.memory.get_stats()
    print(f"Episodes stored: {mem_stats['total_episodes']}")
    print(f"Categories: {mem_stats['categories']}")
    print()
    
    # Habit stats
    print("HABIT STATS")
    print("-" * 70)
    habit_stats = router.habits.get_learning_stats()
    print(f"Categories tracked: {habit_stats['categories']}")
    print(f"Recent outcomes: {habit_stats['recent_outcomes']}")
    print()
    
    # Run idle processing
    print("=" * 70)
    print("DEFAULT MODE NETWORK - IDLE PROCESSING")
    print("=" * 70)
    router.idle()
    
    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
