"""
Queue Manager for AIR-AI Oracle
Handles rate-limited API operations with local-first fallback
"""

import json
import os
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import hashlib


class QueueManager:
    """
    Simple JSON-based queue for rate-limited operations.
    
    Features:
    - Persistent queue (survives restarts)
    - Priority levels (high, normal, low)
    - Rate limit tracking per API/service
    - Automatic retry with backoff
    - Local-first fallback support
    """
    
    def __init__(self, queue_dir: str = None, rate_limits: Dict[str, Dict] = None):
        self.queue_dir = Path(queue_dir) if queue_dir else Path(__file__).parent.parent / "queue"
        self.queue_dir.mkdir(exist_ok=True)
        
        self.queue_file = self.queue_dir / "job_queue.json"
        self.state_file = self.queue_dir / "queue_state.json"
        
        # Default rate limits (requests per minute, per hour)
        self.rate_limits = rate_limits or {
            "ollama": {"per_minute": 10, "per_hour": 60},
            "openai": {"per_minute": 3, "per_hour": 60},
            "perchance": {"per_minute": 10, "per_hour": 100},  # Perchance API limits
            "default": {"per_minute": 10, "per_hour": 100}
        }
        
        # In-memory state
        self.jobs: List[Dict] = []
        self.rate_state: Dict[str, Dict] = {}
        self.processing = False
        self.lock = threading.Lock()
        
        # Load persistent state
        self._load_state()
    
    def _load_state(self):
        """Load queue and rate limit state from disk"""
        # Load jobs
        if self.queue_file.exists():
            try:
                with open(self.queue_file, 'r') as f:
                    self.jobs = json.load(f)
                print(f"Loaded {len(self.jobs)} queued jobs")
            except json.JSONDecodeError:
                print("Queue file corrupted, starting fresh")
                self.jobs = []
        
        # Load rate state
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    self.rate_state = json.load(f)
            except json.JSONDecodeError:
                self.rate_state = {}
    
    def _save_state(self):
        """Save queue and rate state to disk"""
        with open(self.queue_file, 'w') as f:
            json.dump(self.jobs, f, indent=2)
        
        with open(self.state_file, 'w') as f:
            json.dump(self.rate_state, f, indent=2)
    
    def _check_rate_limit(self, service: str) -> tuple[bool, float]:
        """
        Check if we can make a request to the service.
        Returns (allowed, wait_seconds)
        """
        now = time.time()
        limits = self.rate_limits.get(service, self.rate_limits["default"])
        
        if service not in self.rate_state:
            self.rate_state[service] = {
                "minute_count": 0,
                "minute_reset": now + 60,
                "hour_count": 0,
                "hour_reset": now + 3600
            }
        
        state = self.rate_state[service]
        
        # Reset counters if window expired
        if now >= state["minute_reset"]:
            state["minute_count"] = 0
            state["minute_reset"] = now + 60
        
        if now >= state["hour_reset"]:
            state["hour_count"] = 0
            state["hour_reset"] = now + 3600
        
        # Check limits
        if state["minute_count"] >= limits["per_minute"]:
            wait = state["minute_reset"] - now
            return False, max(0, wait)
        
        if state["hour_count"] >= limits["per_hour"]:
            wait = state["hour_reset"] - now
            return False, max(0, wait)
        
        # Increment counters
        state["minute_count"] += 1
        state["hour_count"] += 1
        self._save_state()
        
        return True, 0
    
    def add_job(self, job_type: str, service: str, params: Dict, 
                priority: str = "normal", fallback_local: bool = True,
                callback_url: str = None) -> str:
        """
        Add a job to the queue.
        
        Args:
            job_type: Type of operation (e.g., "llm_generate", "oracle_enrich")
            service: API service name (e.g., "ollama", "openai")
            params: Parameters for the operation
            priority: "high", "normal", or "low"
            fallback_local: If True, return local result immediately when rate-limited
            callback_url: Optional webhook/callback URL when complete
        
        Returns:
            job_id: Unique job identifier
        """
        job_id = hashlib.md5(f"{time.time()}{job_type}{json.dumps(params)}".encode()).hexdigest()[:12]
        
        job = {
            "id": job_id,
            "type": job_type,
            "service": service,
            "params": params,
            "priority": priority,
            "fallback_local": fallback_local,
            "callback_url": callback_url,
            "created": datetime.now().isoformat(),
            "attempts": 0,
            "status": "pending",  # pending, processing, completed, failed, fallback
            "result": None,
            "error": None
        }
        
        with self.lock:
            self.jobs.append(job)
            self._save_state()
        
        print(f"Queued job {job_id} ({job_type}, priority={priority})")
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get status of a specific job"""
        with self.lock:
            for job in self.jobs:
                if job["id"] == job_id:
                    return job.copy()
        return None
    
    def get_queue_status(self) -> Dict:
        """Get overall queue status"""
        with self.lock:
            pending = len([j for j in self.jobs if j["status"] == "pending"])
            completed = len([j for j in self.jobs if j["status"] == "completed"])
            failed = len([j for j in self.jobs if j["status"] == "failed"])
            fallback = len([j for j in self.jobs if j["status"] == "fallback"])
        
        return {
            "pending": pending,
            "completed": completed,
            "failed": failed,
            "fallback": fallback,
            "total": len(self.jobs),
            "processing": self.processing
        }
    
    def process_queue(self, executor: Callable = None) -> List[Dict]:
        """
        Process pending jobs in priority order.
        
        Args:
            executor: Function to execute the job. Should accept (job_type, params)
                     and return (success, result_or_error)
        
        Returns:
            List of processed job results
        """
        if self.processing:
            return []  # Already processing
        
        results = []
        
        with self.lock:
            self.processing = True
        
        try:
            # Sort by priority (high > normal > low), then by creation time
            priority_order = {"high": 0, "normal": 1, "low": 2}
            pending_jobs = sorted(
                [j for j in self.jobs if j["status"] == "pending"],
                key=lambda j: (priority_order.get(j["priority"], 1), j["created"])
            )
            
            for job in pending_jobs:
                job_id = job["id"]
                service = job["service"]
                
                # Check rate limit
                allowed, wait_time = self._check_rate_limit(service)
                
                if not allowed:
                    # Rate limited - use fallback if enabled
                    if job["fallback_local"]:
                        job["status"] = "fallback"
                        job["result"] = {
                            "fallback": True,
                            "reason": f"Rate limited, wait {wait_time:.0f}s",
                            "retry_after": wait_time
                        }
                        job["completed"] = datetime.now().isoformat()
                        results.append(job.copy())
                        print(f"Job {job_id} -> fallback (rate limited)")
                    else:
                        # Keep pending, will retry later
                        pass
                    continue
                
                # Execute the job
                job["status"] = "processing"
                job["attempts"] += 1
                self._save_state()
                
                if executor:
                    try:
                        success, result = executor(job["type"], job["params"])
                        
                        if success:
                            job["status"] = "completed"
                            job["result"] = result
                            print(f"Job {job_id} -> completed")
                        else:
                            job["status"] = "failed"
                            job["error"] = str(result)
                            print(f"Job {job_id} -> failed: {result}")
                        
                        job["completed"] = datetime.now().isoformat()
                        results.append(job.copy())
                        
                    except Exception as e:
                        job["status"] = "failed"
                        job["error"] = str(e)
                        job["completed"] = datetime.now().isoformat()
                        results.append(job.copy())
                        print(f"Job {job_id} -> exception: {e}")
                else:
                    # No executor - handle Perchance jobs specially
                    if job["type"] == "perchance_generate":
                        try:
                            from perchance_router import get_perchance_router
                            router = get_perchance_router()
                            result = router.generate(
                                element_type=job["params"].get("element_type"),
                                context=job["params"].get("context"),
                                fallback_local=job["fallback_local"]
                            )
                            job["status"] = "completed" if result["success"] else "failed"
                            job["result"] = result.get("result")
                            if not result["success"]:
                                job["error"] = result.get("error")
                            job["completed"] = datetime.now().isoformat()
                            results.append(job.copy())
                        except Exception as e:
                            job["status"] = "failed"
                            job["error"] = str(e)
                            job["completed"] = datetime.now().isoformat()
                            results.append(job.copy())
                    else:
                        # No executor - just mark as completed (for testing)
                        job["status"] = "completed"
                        job["result"] = {"mock": True, "message": "No executor configured"}
                        job["completed"] = datetime.now().isoformat()
                        results.append(job.copy())
            
            # Clean up old completed jobs (keep last 50)
            with self.lock:
                completed_jobs = [j for j in self.jobs if j["status"] in ["completed", "failed", "fallback"]]
                if len(completed_jobs) > 50:
                    # Remove oldest
                    completed_jobs.sort(key=lambda j: j.get("completed", ""))
                    to_remove = completed_jobs[:-50]
                    self.jobs = [j for j in self.jobs if j not in to_remove]
                
                self._save_state()
        
        finally:
            with self.lock:
                self.processing = False
        
        return results
    
    def clear_queue(self, status_filter: str = None):
        """Clear jobs from queue, optionally filtered by status"""
        with self.lock:
            if status_filter:
                self.jobs = [j for j in self.jobs if j["status"] != status_filter]
            else:
                self.jobs = []
            self._save_state()
        print(f"Queue cleared (filter={status_filter})")
    
    def retry_failed(self) -> int:
        """Reset failed jobs to pending for retry"""
        count = 0
        with self.lock:
            for job in self.jobs:
                if job["status"] == "failed":
                    job["status"] = "pending"
                    job["error"] = None
                    count += 1
            self._save_state()
        print(f"Retrying {count} failed jobs")
        return count


# Background processor thread
class QueueProcessor(threading.Thread):
    """Background thread to process queue periodically"""
    
    def __init__(self, queue_manager: QueueManager, executor: Callable = None, 
                 interval: int = 10):
        super().__init__(daemon=True)
        self.queue = queue_manager
        self.executor = executor
        self.interval = interval
        self.running = False
    
    def run(self):
        self.running = True
        while self.running:
            try:
                self.queue.process_queue(self.executor)
            except Exception as e:
                print(f"Queue processor error: {e}")
            time.sleep(self.interval)
    
    def stop(self):
        self.running = False


# Global instance (for Flask app integration)
_queue_manager: Optional[QueueManager] = None
_processor: Optional[QueueProcessor] = None


def get_queue_manager() -> QueueManager:
    """Get or create global queue manager instance"""
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = QueueManager()
    return _queue_manager


def start_background_processor(executor: Callable = None, interval: int = 10):
    """Start background queue processor"""
    global _processor, _queue_manager
    if _queue_manager is None:
        _queue_manager = QueueManager()
    
    if _processor is None:
        _processor = QueueProcessor(_queue_manager, executor, interval)
        _processor.start()
        print("Queue background processor started")


def stop_background_processor():
    """Stop background queue processor"""
    global _processor
    if _processor:
        _processor.stop()
        _processor = None
