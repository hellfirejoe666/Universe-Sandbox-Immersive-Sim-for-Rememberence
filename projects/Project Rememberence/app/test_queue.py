"""
Test script for Queue Manager
"""

import sys
from pathlib import Path

# Add app directory to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'app'))

from queue_manager import QueueManager

def test_queue():
    print("=== Testing Queue Manager ===\n")
    
    # Create queue manager
    queue = QueueManager(queue_dir=str(PROJECT_ROOT / 'queue'))
    
    # Clear any existing jobs
    queue.clear_queue()
    
    # Test 1: Add jobs with different priorities
    print("1. Adding jobs...")
    job1 = queue.add_job(
        job_type="llm_generate",
        service="ollama",
        params={"prompt": "Generate a mystical oracle reading"},
        priority="high"
    )
    print(f"   Job 1 (high): {job1}")
    
    job2 = queue.add_job(
        job_type="llm_generate",
        service="ollama",
        params={"prompt": "Generate NPC dialogue"},
        priority="normal"
    )
    print(f"   Job 2 (normal): {job2}")
    
    job3 = queue.add_job(
        job_type="oracle_enrich",
        service="ollama",
        params={"data": {"reading": "FFT analysis result"}},
        priority="low",
        fallback_local=True
    )
    print(f"   Job 3 (low, fallback): {job3}")
    
    # Test 2: Check queue status
    print("\n2. Queue status:")
    status = queue.get_queue_status()
    print(f"   Pending: {status['pending']}")
    print(f"   Total: {status['total']}")
    
    # Test 3: Process queue (mock executor)
    print("\n3. Processing queue (mock)...")
    
    def mock_executor(job_type, params):
        import time
        time.sleep(0.1)  # Simulate API call
        return True, {"mock_result": True, "type": job_type, "params": params}
    
    results = queue.process_queue(mock_executor)
    print(f"   Processed: {len(results)} jobs")
    
    for result in results:
        print(f"   - {result['id']}: {result['status']}")
    
    # Test 4: Check final status
    print("\n4. Final queue status:")
    status = queue.get_queue_status()
    print(f"   Completed: {status['completed']}")
    print(f"   Fallback: {status['fallback']}")
    print(f"   Failed: {status['failed']}")
    
    # Test 5: Rate limit simulation
    print("\n5. Testing rate limits...")
    queue.clear_queue()
    
    # Set strict rate limit for testing
    queue.rate_limits["test_service"] = {"per_minute": 2, "per_hour": 10}
    
    for i in range(5):
        job = queue.add_job(
            job_type="test",
            service="test_service",
            params={"iteration": i},
            fallback_local=True
        )
    
    results = queue.process_queue(mock_executor)
    
    completed = len([r for r in results if r['status'] == 'completed'])
    fallback = len([r for r in results if r['status'] == 'fallback'])
    
    print(f"   Completed: {completed} (limit was 2/minute)")
    print(f"   Fallback: {fallback} (rate limited)")
    
    print("\n=== Tests Complete ===")

if __name__ == "__main__":
    test_queue()
