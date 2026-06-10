"""
Neural Router - Main Orchestrator

Coordinates all brain subsystems for intelligent request routing.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# Import subsystems
from .subsystems.executive import ExecutiveSystem
from .subsystems.arousal import ArousalSystem
from .subsystems.attention import AttentionSystem
from .subsystems.memory import MemorySystem
from .subsystems.habits import HabitSystem
from .subsystems.language import LanguageSystem
from .subsystems.reasoning import ReasoningSystem
from .subsystems.salience import SalienceSystem
from .subsystems.quality import QualitySystem
from .subsystems.default_mode import DefaultModeNetwork


class NeuralRouter:
    """
    Brain-inspired AI request router.
    
    Coordinates specialized subsystems to route requests intelligently,
    learn from outcomes, and improve continuously.
    """
    
    def __init__(self, workspace_path: str = None):
        """Initialize all brain subsystems."""
        
        # Set workspace path
        if workspace_path is None:
            workspace_path = "D:/Ollama/OpenClaw/workspace"
        self.workspace = Path(workspace_path)
        
        # State directory
        self.state_dir = self.workspace / "hybrid-router" / "brain" / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize subsystems
        print("[NeuralRouter] Initializing brain subsystems...")
        
        self.executive = ExecutiveSystem(self.state_dir)
        self.arousal = ArousalSystem(self.state_dir)
        self.attention = AttentionSystem()
        self.memory = MemorySystem(self.state_dir)
        self.habits = HabitSystem(self.state_dir)
        self.language = LanguageSystem()
        self.reasoning = ReasoningSystem()
        self.salience = SalienceSystem()
        self.quality = QualitySystem()
        self.default_mode = DefaultModeNetwork(self.state_dir, self)
        
        # Statistics
        self.stats = {
            'requests_processed': 0,
            'fast_path': 0,
            'smart_path': 0,
            'cloud_path': 0,
            'quality_rejections': 0,
            'salience_overrides': 0,
            'start_time': datetime.now().isoformat()
        }
        
        # Load stats from file
        self._load_stats()
        
        print("[NeuralRouter] All subsystems initialized")
        print(f"[NeuralRouter] Ready to process requests (mode: {self.arousal.get_mode()})")
    
    # ────────────────────────────────────────────────
    # Main Routing Method
    # ────────────────────────────────────────────────
    
    def route(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Route a request through the neural architecture.
        
        Args:
            query: User's input text
            context: Optional context dict (user_state, session_type, etc.)
        
        Returns:
            Response dict with content, path_used, metadata
        """
        start_time = time.time()
        context = context or {}
        
        # 1. Executive sets strategic context
        self.executive.update_context(query, context)
        strategy = self.executive.get_strategy()
        
        # 2. Arousal checks system state
        arousal_state = self.arousal.get_state()
        resource_budget = self.arousal.get_resource_budget()
        
        # 3. Attention filters and amplifies
        focused_context = self.attention.filter(query, context)
        
        # 4. Check Salience (can override normal routing)
        salience_result = self.salience.assess(query, context)
        if salience_result['override']:
            self.stats['salience_overrides'] += 1
            path = salience_result['forced_path']
            reason = "salience_override"
        else:
            # 5. Normal routing: Memory/Habits → Language → Reasoning
            path, reason = self._select_path(query, focused_context, resource_budget)
        
        # 6. Execute selected path
        response = self._execute_path(path, query, focused_context, strategy)
        
        # 7. Quality gate (catch bad outputs)
        quality_result = self.quality.assess(response, query, context)
        if not quality_result['acceptable']:
            self.stats['quality_rejections'] += 1
            # Re-route with higher-quality path
            path = 'cloud'  # Escalate to best available
            response = self._execute_path(path, query, focused_context, strategy)
        
        # 8. Record outcome for learning
        elapsed = time.time() - start_time
        self._record_outcome(query, path, response, elapsed, quality_result)
        
        # 9. Update statistics
        self.stats['requests_processed'] += 1
        self.stats[f'{path}_path'] += 1
        
        # 10. Add metadata
        response['metadata'] = {
            'path': path,
            'reason': reason,
            'elapsed_ms': int(elapsed * 1000),
            'arousal_mode': arousal_state['mode'],
            'quality_score': quality_result.get('score', 0),
            'timestamp': datetime.now().isoformat()
        }
        
        return response
    
    def _select_path(self, query: str, context: Dict, budget: float) -> Tuple[str, str]:
        """Select routing path based on novelty, habits, and resources."""
        
        # Check Memory (episodic similarity)
        memory_match = self.memory.find_similar(query, context)
        if memory_match and memory_match['similarity'] > 0.85:
            return 'fast', 'memory_match'
        
        # Check Habits (learned preferences)
        habit_path = self.habits.get_preferred_path(query, context)
        if habit_path and self.habits.get_confidence(habit_path) > 0.8:
            return habit_path, 'habit'
        
        # Check FFT novelty (is this familiar or novel?)
        novelty = self._calculate_novelty(query, context)
        
        if novelty < 0.3 and budget > 0.3:
            return 'fast', 'low_novelty'
        elif novelty < 0.7 and budget > 0.5:
            return 'smart', 'medium_novelty'
        else:
            return 'cloud', 'high_novelty'
    
    def _calculate_novelty(self, query: str, context: Dict) -> float:
        """
        Calculate novelty score (0.0 = familiar, 1.0 = completely novel).
        
        Uses pattern matching + semantic heuristics.
        """
        # Check if query matches known patterns (familiar)
        query_lower = query.lower()
        
        # Familiar patterns (should route FAST)
        familiar_keywords = [
            'hello', 'hi', 'hey', 'thanks', 'thank you',
            'what is 2', '1 + 1', '2 + 2',  # Simple math
            'how are you', 'whats up', 'good morning'
        ]
        
        familiar_count = sum(1 for kw in familiar_keywords if kw in query_lower)
        if familiar_count > 0:
            return 0.2  # Low novelty
        
        # Medium novelty: common question patterns
        common_patterns = [
            query_lower.startswith('what '),
            query_lower.startswith('how '),
            query_lower.startswith('why '),
            query_lower.startswith('explain '),
            query_lower.startswith('write '),
            'function' in query_lower,
            'code' in query_lower,
        ]
        
        if sum(common_patterns) >= 2:
            return 0.5  # Medium novelty
        
        # Long, complex queries are usually novel
        if len(query) > 150:
            return 0.8
        
        # Very long queries (>100 chars) should lean cloud
        if len(query) > 100:
            return 0.7
        
        # Default: moderate novelty
        return 0.5
    
    def _execute_path(self, path: str, query: str, context: Dict, strategy: Dict) -> Dict:
        """Execute the selected routing path."""
        
        if path == 'fast':
            return self.language.fast_response(query, context)
        elif path == 'smart':
            return self.language.smart_response(query, context)
        elif path == 'cloud':
            return self.reasoning.cloud_response(query, context)
        else:
            return {'content': 'Unknown path', 'path': path}
    
    def _record_outcome(self, query: str, path: str, response: Dict, 
                       elapsed: float, quality: Dict):
        """Record outcome for habit learning and memory."""
        
        # Update habits (reinforce successful paths)
        success = quality.get('acceptable', True)
        self.habits.record_outcome(query, path, success, elapsed, quality)
        
        # Store in episodic memory
        self.memory.store_episode({
            'query': query,
            'path': path,
            'response': response.get('content', '')[:500],  # Truncate
            'elapsed': elapsed,
            'quality': quality,
            'timestamp': datetime.now().isoformat()
        })
    
    # ────────────────────────────────────────────────
    # Statistics & State
    # ────────────────────────────────────────────────
    
    def get_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        total = self.stats['requests_processed']
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            'fast_pct': round(self.stats['fast_path'] / total * 100, 1),
            'smart_pct': round(self.stats['smart_path'] / total * 100, 1),
            'cloud_pct': round(self.stats['cloud_path'] / total * 100, 1),
            'uptime_minutes': (datetime.now() - datetime.fromisoformat(self.stats['start_time'])).total_seconds() / 60
        }
    
    def _load_stats(self):
        """Load statistics from file."""
        stats_file = self.state_dir / 'router_stats.json'
        if stats_file.exists():
            try:
                saved = json.loads(stats_file.read_text())
                self.stats.update(saved)
            except:
                pass
    
    def _save_stats(self):
        """Save statistics to file."""
        stats_file = self.state_dir / 'router_stats.json'
        stats_file.write_text(json.dumps(self.stats, indent=2))
    
    # ────────────────────────────────────────────────
    # Lifecycle
    # ────────────────────────────────────────────────
    
    def idle(self):
        """Trigger idle processing (Default Mode Network)."""
        self.default_mode.process_idle()
    
    def shutdown(self):
        """Graceful shutdown."""
        print("[NeuralRouter] Shutting down...")
        self._save_stats()
        self.memory.consolidate()
        print("[NeuralRouter] Shutdown complete")


# ────────────────────────────────────────────────
# Test/Demo
# ────────────────────────────────────────────────

if __name__ == '__main__':
    print("=== Neural Router Test ===\n")
    
    router = NeuralRouter()
    
    # Test queries
    test_queries = [
        ("Hello!", {"user_state": "chatting"}),
        ("What is 2 + 2?", {"user_state": "learning"}),
        ("Write a Python function to sort a list", {"user_state": "coding"}),
        ("URGENT: My code is broken!!!", {"user_state": "frustrated"}),
    ]
    
    for query, context in test_queries:
        print(f"\nQuery: {query}")
        response = router.route(query, context)
        print(f"Path: {response['metadata']['path']} ({response['metadata']['reason']})")
        print(f"Quality: {response['metadata']['quality_score']}")
        print(f"Time: {response['metadata']['elapsed_ms']}ms")
    
    print(f"\n=== Stats ===")
    print(json.dumps(router.get_stats(), indent=2))
