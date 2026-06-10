"""
Habit System (Basal Ganglia)

Habit learning through reinforcement, reward-based routing preferences.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict


class HabitSystem:
    """
    Learns routing preferences through reinforcement.
    Like the basal ganglia forming habits based on reward history.
    """
    
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.weights_file = state_dir / 'habit_weights.json'
        
        # Initialize weights
        self.weights: Dict[str, Dict[str, float]] = defaultdict(lambda: {
            'fast': 0.5,
            'smart': 0.5,
            'cloud': 0.5
        })
        
        # Load existing weights
        self._load_weights()
        
        # Recent outcomes for learning
        self.recent_outcomes: List[Dict] = []
    
    def _load_weights(self):
        """Load habit weights from file."""
        if self.weights_file.exists():
            try:
                data = json.loads(self.weights_file.read_text())
                self.weights = defaultdict(lambda: {'fast': 0.5, 'smart': 0.5, 'cloud': 0.5}, data)
            except:
                pass
    
    def _save_weights(self):
        """Save habit weights to file."""
        # Convert defaultdict to regular dict for JSON
        data = {k: dict(v) for k, v in self.weights.items()}
        self.weights_file.write_text(json.dumps(data, indent=2))
    
    def _categorize_query(self, query: str) -> str:
        """Categorize query for habit tracking."""
        query_lower = query.lower()
        
        # Simple categorization
        if any(kw in query_lower for kw in ['hello', 'hi', 'hey', 'thanks']):
            return 'greeting'
        elif any(kw in query_lower for kw in ['code', 'function', 'write', 'debug']):
            return 'coding'
        elif any(kw in query_lower for kw in ['what', 'why', 'how', 'explain']):
            return 'question'
        elif any(kw in query_lower for kw in ['story', 'write', 'creative']):
            return 'creative'
        else:
            return 'general'
    
    def record_outcome(self, query: str, path: str, success: bool, 
                      elapsed: float, quality: Dict):
        """
        Record outcome for habit learning.
        
        Args:
            query: The original query
            path: Which path was used (fast/smart/cloud)
            success: Whether the outcome was successful
            elapsed: Time taken in seconds
            quality: Quality assessment dict
        """
        category = self._categorize_query(query)
        
        # Calculate reward
        reward = 0.0
        if success:
            reward += 0.5
        reward += quality.get('score', 0.5) * 0.3
        reward += max(0, (1.0 - elapsed / 10.0)) * 0.2  # Faster = better
        
        # Update weight for this path
        current_weight = self.weights[category][path]
        
        # Reinforcement learning update
        learning_rate = 0.1
        if success:
            new_weight = current_weight + learning_rate * (1.0 - current_weight)
        else:
            new_weight = current_weight - learning_rate * current_weight
        
        self.weights[category][path] = max(0.0, min(1.0, new_weight))
        
        # Store recent outcome
        self.recent_outcomes.append({
            'category': category,
            'path': path,
            'success': success,
            'elapsed': elapsed,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only recent outcomes
        if len(self.recent_outcomes) > 100:
            self.recent_outcomes = self.recent_outcomes[-100:]
        
        # Save periodically
        if len(self.recent_outcomes) % 10 == 0:
            self._save_weights()
    
    def get_preferred_path(self, query: str, context: Dict) -> Optional[str]:
        """
        Get preferred path based on learned habits.
        
        Returns path name or None if no strong preference.
        """
        category = self._categorize_query(query)
        weights = self.weights[category]
        
        # Find highest weight
        best_path = max(weights.keys(), key=lambda k: weights[k])
        best_weight = weights[best_path]
        
        # Only return if confidence is high enough
        if best_weight > 0.7:
            return best_path
        
        return None
    
    def get_confidence(self, path: str, category: str = None) -> float:
        """Get confidence level for a path (optionally in a category)."""
        if category:
            return self.weights[category].get(path, 0.5)
        
        # Average across all categories
        all_weights = [self.weights[cat].get(path, 0.5) 
                      for cat in self.weights.keys()]
        return sum(all_weights) / len(all_weights) if all_weights else 0.5
    
    def get_weights(self, category: str) -> Dict[str, float]:
        """Get all weights for a category."""
        return dict(self.weights[category])
    
    def reset_habits(self):
        """Reset all learned habits."""
        self.weights = defaultdict(lambda: {'fast': 0.5, 'smart': 0.5, 'cloud': 0.5})
        self.recent_outcomes = []
        self._save_weights()
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about learned habits."""
        return {
            'categories': len(self.weights),
            'recent_outcomes': len(self.recent_outcomes),
            'weights': {cat: dict(w) for cat, w in self.weights.items()}
        }
