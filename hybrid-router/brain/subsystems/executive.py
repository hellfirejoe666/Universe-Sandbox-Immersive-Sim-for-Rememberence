"""
Executive System (Prefrontal Cortex)

Strategic planning, metacognition, resource allocation, session type inference.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ExecutiveSystem:
    """
    The CEO of the brain. Oversees all subsystems and makes strategic decisions.
    """
    
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.state_file = state_dir / 'executive_state.json'
        
        # Load or initialize state
        self.state = self._load_state()
        
        # Current strategic context
        self.current_context = {}
        self.current_strategy = {}
    
    def _load_state(self) -> Dict:
        """Load executive state from file."""
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except:
                pass
        
        # Default state
        return {
            'session_type': 'general',
            'optimization_strategy': 'balanced',
            'performance_metrics': {
                'avg_latency_ms': 0,
                'success_rate': 1.0,
                'user_satisfaction': 0.8
            },
            'resource_quotas': {
                'cloud_daily': 100,
                'cloud_used': 0,
                'smart_concurrent': 3,
                'smart_active': 0
            },
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_state(self):
        """Save executive state to file."""
        self.state['last_updated'] = datetime.now().isoformat()
        self.state_file.write_text(json.dumps(self.state, indent=2))
    
    def update_context(self, query: str, context: Dict[str, Any]):
        """
        Update strategic context based on query and user context.
        
        Infers session type, user intent, and optimization strategy.
        """
        self.current_context = {
            'query': query,
            'user_state': context.get('user_state', 'unknown'),
            'session_type': context.get('session_type', 'general'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Infer session type from context
        self._infer_session_type()
        
        # Select optimization strategy
        self._select_strategy()
    
    def _infer_session_type(self):
        """Infer what kind of session the user is in."""
        user_state = self.current_context.get('user_state', '')
        
        # Session type heuristics
        if user_state in ['coding', 'debugging', 'development']:
            self.state['session_type'] = 'development'
        elif user_state in ['chatting', 'casual', 'social']:
            self.state['session_type'] = 'social'
        elif user_state in ['learning', 'studying', 'research']:
            self.state['session_type'] = 'learning'
        elif user_state in ['frustrated', 'urgent', 'stressed']:
            self.state['session_type'] = 'crisis'
        else:
            self.state['session_type'] = 'general'
    
    def _select_strategy(self):
        """Select optimization strategy based on session type."""
        session = self.state['session_type']
        
        strategies = {
            'development': {
                'priority': 'accuracy',
                'cloud_willingness': 0.7,
                'quality_threshold': 0.8
            },
            'social': {
                'priority': 'speed',
                'cloud_willingness': 0.3,
                'quality_threshold': 0.6
            },
            'learning': {
                'priority': 'clarity',
                'cloud_willingness': 0.5,
                'quality_threshold': 0.75
            },
            'crisis': {
                'priority': 'reliability',
                'cloud_willingness': 0.9,
                'quality_threshold': 0.9
            },
            'general': {
                'priority': 'balanced',
                'cloud_willingness': 0.5,
                'quality_threshold': 0.7
            }
        }
        
        self.current_strategy = strategies.get(session, strategies['general'])
    
    def get_strategy(self) -> Dict[str, Any]:
        """Get current strategic strategy."""
        return self.current_strategy
    
    def get_context(self) -> Dict[str, Any]:
        """Get current strategic context."""
        return self.current_context
    
    def update_metrics(self, latency_ms: float, success: bool, satisfaction: float = None):
        """Update performance metrics."""
        metrics = self.state['performance_metrics']
        
        # Exponential moving average
        alpha = 0.1
        metrics['avg_latency_ms'] = (1 - alpha) * metrics['avg_latency_ms'] + alpha * latency_ms
        metrics['success_rate'] = (1 - alpha) * metrics['success_rate'] + alpha * (1.0 if success else 0.0)
        
        if satisfaction is not None:
            metrics['user_satisfaction'] = (1 - alpha) * metrics['user_satisfaction'] + alpha * satisfaction
        
        self._save_state()
    
    def check_quota(self, resource: str) -> bool:
        """Check if resource quota allows usage."""
        quotas = self.state['resource_quotas']
        
        if resource == 'cloud':
            return quotas['cloud_used'] < quotas['cloud_daily']
        elif resource == 'smart':
            return quotas['smart_active'] < quotas['smart_concurrent']
        
        return True
    
    def allocate_resource(self, resource: str):
        """Allocate a resource (increment usage counter)."""
        quotas = self.state['resource_quotas']
        
        if resource == 'cloud':
            quotas['cloud_used'] += 1
        elif resource == 'smart':
            quotas['smart_active'] += 1
        
        self._save_state()
    
    def release_resource(self, resource: str):
        """Release a resource (decrement usage counter)."""
        quotas = self.state['resource_quotas']
        
        if resource == 'smart' and quotas['smart_active'] > 0:
            quotas['smart_active'] -= 1
        
        self._save_state()
    
    def get_session_type(self) -> str:
        """Get current inferred session type."""
        return self.state['session_type']
    
    def reset_quotas(self):
        """Reset daily quotas (call at midnight)."""
        self.state['resource_quotas']['cloud_used'] = 0
        self._save_state()
