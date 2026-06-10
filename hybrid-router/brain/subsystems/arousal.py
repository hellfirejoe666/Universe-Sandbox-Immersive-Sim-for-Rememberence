"""
Arousal System (Reticular Activating System)

System load monitoring, adaptive resource allocation, alertness levels.
"""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class ArousalSystem:
    """
    Monitors system state and adjusts resource allocation accordingly.
    Like the brain's arousal system that regulates alertness and energy.
    """
    
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.state_file = state_dir / 'arousal_state.json'
        
        # Load or initialize state
        self.state = self._load_state()
        
        # Current mode
        self.mode = self._calculate_mode()
    
    def _load_state(self) -> Dict:
        """Load arousal state from file."""
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except:
                pass
        
        return {
            'mode': 'normal',
            'cpu_threshold': 70,
            'memory_threshold': 80,
            'resource_budget': 1.0,
            'last_check': datetime.now().isoformat()
        }
    
    def _save_state(self):
        """Save arousal state to file."""
        self.state['last_check'] = datetime.now().isoformat()
        self.state_file.write_text(json.dumps(self.state, indent=2))
    
    def _calculate_mode(self) -> str:
        """Calculate current arousal mode based on system load."""
        if PSUTIL_AVAILABLE:
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory_percent = psutil.virtual_memory().percent
            except:
                cpu_percent = 50
                memory_percent = 50
        else:
            # Fallback if psutil unavailable
            cpu_percent = 50
            memory_percent = 50
        
        # Determine mode
        if cpu_percent > 90 or memory_percent > 90:
            mode = 'critical'
            budget = 0.3  # Very conservative
        elif cpu_percent > self.state['cpu_threshold'] or memory_percent > self.state['memory_threshold']:
            mode = 'high'
            budget = 0.5  # Conservative
        elif cpu_percent < 30 and memory_percent < 50:
            mode = 'low'
            budget = 1.0  # Full resources available
        else:
            mode = 'normal'
            budget = 0.8  # Standard allocation
        
        self.state['mode'] = mode
        self.state['resource_budget'] = budget
        self.state['cpu_load'] = cpu_percent
        self.state['memory_load'] = memory_percent
        self._save_state()
        
        return mode
    
    def get_state(self) -> Dict[str, Any]:
        """Get current arousal state."""
        self.mode = self._calculate_mode()
        return {
            'mode': self.mode,
            'cpu_load': self.state.get('cpu_load', 0),
            'memory_load': self.state.get('memory_load', 0),
            'resource_budget': self.state['resource_budget']
        }
    
    def get_mode(self) -> str:
        """Get current arousal mode."""
        return self.mode
    
    def get_resource_budget(self) -> float:
        """
        Get resource budget (0.0 to 1.0).
        
        Determines how "expensive" a routing path we can afford.
        """
        self.mode = self._calculate_mode()
        return self.state['resource_budget']
    
    def can_afford_path(self, path: str) -> bool:
        """Check if current budget allows a specific path."""
        budget = self.get_resource_budget()
        
        path_costs = {
            'fast': 0.1,    # Almost free
            'smart': 0.5,   # Moderate (local LLM)
            'cloud': 0.9    # Expensive (rate-limited)
        }
        
        return budget >= path_costs.get(path, 1.0)
    
    def adjust_thresholds(self, cpu: int = None, memory: int = None):
        """Adjust CPU/memory thresholds for mode calculation."""
        if cpu is not None:
            self.state['cpu_threshold'] = max(30, min(90, cpu))
        if memory is not None:
            self.state['memory_threshold'] = max(30, min(95, memory))
        self._save_state()
    
    def enter_sleep_mode(self):
        """Enter low-power sleep mode (for idle periods)."""
        self.state['mode'] = 'sleep'
        self.state['resource_budget'] = 0.1
        self._save_state()
    
    def wake(self):
        """Wake from sleep mode."""
        self.mode = self._calculate_mode()
