"""
Default Mode Network (Idle Learning)

Memory consolidation, performance reflection, self-improvement during idle time.
"""

import json
from pathlib import Path
from typing import TYPE_CHECKING
from datetime import datetime


if TYPE_CHECKING:
    from ..neural_router import NeuralRouter


class DefaultModeNetwork:
    """
    Processes during idle time for continuous improvement.
    Like the brain's default mode network active during rest.
    """
    
    def __init__(self, state_dir: Path, router: 'NeuralRouter' = None):
        self.state_dir = state_dir
        self.router = router
        self.state_file = state_dir / 'dmn_state.json'
        
        # Load state
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        """Load DMN state from file."""
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except:
                pass
        
        return {
            'last_consolidation': None,
            'last_reflection': None,
            'improvements_generated': 0,
            'idle_cycles': 0
        }
    
    def _save_state(self):
        """Save DMN state to file."""
        self.state_file.write_text(json.dumps(self.state, indent=2))
    
    def process_idle(self):
        """
        Run idle processing cycle.
        
        Called when the router is idle (no active requests).
        """
        print("[DMN] Starting idle processing...")
        
        # 1. Consolidate memories
        self.consolidate_memories()
        
        # 2. Reflect on performance
        self.reflect_on_performance()
        
        # 3. Generate improvements
        self.generate_improvements()
        
        # Update state
        self.state['idle_cycles'] += 1
        self._save_state()
        
        print(f"[DMN] Idle processing complete (cycle {self.state['idle_cycles']})")
    
    def consolidate_memories(self):
        """Consolidate recent memories into long-term storage."""
        if self.router and hasattr(self.router, 'memory'):
            print("[DMN] Consolidating memories...")
            self.router.memory.consolidate()
            self.state['last_consolidation'] = datetime.now().isoformat()
    
    def reflect_on_performance(self):
        """Reflect on recent performance and identify patterns."""
        if not self.router:
            return
        
        stats = self.router.get_stats()
        print(f"[DMN] Performance reflection:")
        print(f"  - Total requests: {stats['requests_processed']}")
        print(f"  - Fast path: {stats.get('fast_pct', 0)}%")
        print(f"  - Smart path: {stats.get('smart_pct', 0)}%")
        print(f"  - Cloud path: {stats.get('cloud_pct', 0)}%")
        print(f"  - Quality rejections: {stats.get('quality_rejections', 0)}")
        
        self.state['last_reflection'] = datetime.now().isoformat()
    
    def generate_improvements(self):
        """Generate self-improvement ideas based on recent performance."""
        if not self.router:
            return
        
        improvements = []
        
        # Analyze stats for improvement opportunities
        stats = self.router.get_stats()
        
        # If cloud usage is high, suggest more pattern learning
        if stats.get('cloud_pct', 0) > 30:
            improvements.append({
                'type': 'reduce_cloud',
                'suggestion': 'Cloud usage is high. Consider expanding FAST path patterns.',
                'priority': 'medium'
            })
        
        # If quality rejections are high, suggest threshold adjustment
        if stats.get('quality_rejections', 0) > 10:
            improvements.append({
                'type': 'quality_improvement',
                'suggestion': 'Many quality rejections. Review quality thresholds or path selection.',
                'priority': 'high'
            })
        
        # Store improvements
        if improvements:
            self.state['improvements_generated'] += len(improvements)
            print(f"[DMN] Generated {len(improvements)} improvement suggestions")
            for imp in improvements:
                print(f"  - [{imp['priority']}] {imp['suggestion']}")
    
    def get_state(self) -> dict:
        """Get DMN state."""
        return self.state
    
    def reset(self):
        """Reset DMN state."""
        self.state = {
            'last_consolidation': None,
            'last_reflection': None,
            'improvements_generated': 0,
            'idle_cycles': 0
        }
        self._save_state()
