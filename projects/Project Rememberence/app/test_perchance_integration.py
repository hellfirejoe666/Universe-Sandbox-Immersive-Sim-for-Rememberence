"""
Test script for Perchance AI integration with Rememberence
Tests the hybrid router, Perchance router, and queue integration
"""

import sys
import json
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from perchance_router import PerchanceRouter, get_perchance_router
from hybrid_router import HybridRouter, RequestType, get_hybrid_router
from queue_manager import QueueManager, get_queue_manager


def test_perchance_router():
    """Test Perchance router directly"""
    print("\n" + "="*60)
    print("Testing Perchance Router")
    print("="*60)
    
    router = get_perchance_router()
    
    # Test character name generation
    print("\n1. Testing character name generation...")
    result = router.generate("character_name", use_cache=True)
    print(f"   Success: {result['success']}")
    print(f"   Source: {result['source']}")
    print(f"   Result: {result.get('result', 'N/A')}")
    
    # Test species trait
    print("\n2. Testing species trait (Avious)...")
    result = router.generate("species_trait", context={"species": "Avious"})
    print(f"   Success: {result['success']}")
    print(f"   Source: {result['source']}")
    print(f"   Result: {result.get('result', 'N/A')}")
    
    # Test quest idea
    print("\n3. Testing quest generation...")
    result = router.generate("quest_idea")
    print(f"   Success: {result['success']}")
    print(f"   Source: {result['source']}")
    print(f"   Result: {result.get('result', 'N/A')}")
    
    # Test batch generation
    print("\n4. Testing batch generation...")
    results = router.generate_batch(["character_name", "place_name", "quest_idea"])
    for element_type, result in results.items():
        print(f"   {element_type}: {result.get('result', 'N/A')[:50]}...")
    
    # Get cache stats
    print("\n5. Cache statistics:")
    stats = router.get_cache_stats()
    print(f"   Total entries: {stats['total_entries']}")
    print(f"   Valid entries: {stats['valid_entries']}")
    print(f"   Rate limit remaining: {stats['rate_limit_remaining']}")
    
    return True


def test_hybrid_router():
    """Test hybrid router"""
    print("\n" + "="*60)
    print("Testing Hybrid Router")
    print("="*60)
    
    router = get_hybrid_router()
    
    # Test character name routing
    print("\n1. Testing character name routing...")
    result = router.route_request(
        RequestType.CHARACTER_NAME,
        {"context": {"species": "Geneshan"}}
    )
    print(f"   Success: {result['success']}")
    print(f"   Provider: {result['provider']}")
    print(f"   Result: {result.get('result', 'N/A')}")
    print(f"   Response time: {result.get('metadata', {}).get('response_time', 'N/A')}s")
    
    # Test quest generation
    print("\n2. Testing quest generation...")
    result = router.route_request(
        RequestType.QUEST_GENERATION,
        {"context": {"tone": "mysterious"}}
    )
    print(f"   Success: {result['success']}")
    print(f"   Provider: {result['provider']}")
    print(f"   Result: {result.get('result', 'N/A')}")
    
    # Test species trait
    print("\n3. Testing species trait (Demon)...")
    result = router.route_request(
        RequestType.SPECIES_TRAIT,
        {"context": {"species": "Demon"}}
    )
    print(f"   Success: {result['success']}")
    print(f"   Provider: {result['provider']}")
    print(f"   Result: {result.get('result', 'N/A')}")
    
    # Get metrics
    print("\n4. Router metrics:")
    metrics = router.get_metrics()
    print(f"   Total requests: {metrics['requests']}")
    print(f"   Cache hits: {metrics['cache_hits']}")
    print(f"   Perchance calls: {metrics['perchance_calls']}")
    print(f"   Local calls: {metrics['local_calls']}")
    print(f"   Fallback calls: {metrics['fallback_calls']}")
    print(f"   Errors: {metrics['errors']}")
    print(f"   Avg response time: {metrics['avg_response_time']:.3f}s")
    
    return True


def test_queue_integration():
    """Test queue manager integration"""
    print("\n" + "="*60)
    print("Testing Queue Integration")
    print("="*60)
    
    queue = get_queue_manager()
    
    # Add Perchance jobs
    print("\n1. Adding Perchance generation jobs to queue...")
    
    job1_id = queue.add_job(
        job_type="perchance_generate",
        service="perchance",
        params={
            "element_type": "character_name",
            "context": {"species": "Wolfin"}
        },
        priority="high"
    )
    print(f"   Job 1 (character_name): {job1_id}")
    
    job2_id = queue.add_job(
        job_type="perchance_generate",
        service="perchance",
        params={
            "element_type": "quest_idea",
            "context": {}
        },
        priority="normal"
    )
    print(f"   Job 2 (quest_idea): {job2_id}")
    
    job3_id = queue.add_job(
        job_type="perchance_generate",
        service="perchance",
        params={
            "element_type": "species_trait",
            "context": {"species": "Pixie"}
        },
        priority="low"
    )
    print(f"   Job 3 (species_trait): {job3_id}")
    
    # Process queue
    print("\n2. Processing queue...")
    results = queue.process_queue()
    
    for result in results:
        print(f"\n   Job {result['id']}:")
        print(f"      Status: {result['status']}")
        print(f"      Type: {result['type']}")
        if result['result']:
            result_str = str(result['result'])
            print(f"      Result: {result_str[:100]}...")
        if result.get('error'):
            print(f"      Error: {result['error']}")
    
    # Get queue status
    print("\n3. Queue status:")
    status = queue.get_queue_status()
    print(f"   Pending: {status['pending']}")
    print(f"   Completed: {status['completed']}")
    print(f"   Failed: {status['failed']}")
    print(f"   Fallback: {status['fallback']}")
    
    return True


def test_rememberence_integration():
    """Test integration with Rememberence species data"""
    print("\n" + "="*60)
    print("Testing Rememberence Integration")
    print("="*60)
    
    # Load species data
    species_file = app_dir.parent / "data" / "species.json"
    
    if not species_file.exists():
        print(f"   Species file not found: {species_file}")
        return False
    
    with open(species_file, 'r') as f:
        species_data = json.load(f)
    
    species_list = list(species_data["species"].keys())[:5]  # Test first 5
    
    router = get_perchance_router()
    
    print(f"\n1. Generating traits for {len(species_list)} species...")
    
    for species in species_list:
        print(f"\n   {species}:")
        result = router.generate("species_trait", context={"species": species})
        
        if result['success']:
            print(f"      Source: {result['source']}")
            print(f"      Trait: {result.get('result', 'N/A')}")
        else:
            print(f"      Error: {result.get('error', 'Unknown error')}")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AIR-AI Perchance Integration Test Suite")
    print("="*60)
    
    tests = [
        ("Perchance Router", test_perchance_router),
        ("Hybrid Router", test_hybrid_router),
        ("Queue Integration", test_queue_integration),
        ("Rememberence Integration", test_rememberence_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"\n❌ {test_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, error in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if error:
            print(f"       Error: {error}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
