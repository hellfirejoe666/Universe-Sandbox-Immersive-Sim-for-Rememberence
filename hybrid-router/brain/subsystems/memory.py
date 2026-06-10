"""
Memory System (Hippocampus)

Episodic memory storage, contextual retrieval, similarity matching.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from difflib import SequenceMatcher


class MemorySystem:
    """
    Stores and retrieves episodic memories.
    Like the hippocampus forming and recalling memory episodes.
    """
    
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.episodes_file = state_dir / 'episodic_memory.json'
        self.index_file = state_dir / 'memory_index.json'
        
        # In-memory episode store
        self.episodes: List[Dict] = []
        self.index: Dict[str, List[int]] = {}  # Category → episode indices
        
        # Load existing memories
        self._load_memories()
    
    def _load_memories(self):
        """Load memories from file."""
        if self.episodes_file.exists():
            try:
                data = json.loads(self.episodes_file.read_text())
                self.episodes = data.get('episodes', [])
                self.index = data.get('index', {})
            except:
                pass
    
    def _save_memories(self):
        """Save memories to file."""
        data = {
            'episodes': self.episodes[-1000:],  # Keep last 1000
            'index': self.index
        }
        self.episodes_file.write_text(json.dumps(data, indent=2))
    
    def store_episode(self, episode: Dict):
        """
        Store a new episodic memory.
        
        Args:
            episode: Dict with query, path, response, outcome, etc.
        """
        # Add metadata
        episode['id'] = len(self.episodes)
        episode['stored_at'] = datetime.now().isoformat()
        
        # Categorize for indexing
        category = self._categorize_episode(episode)
        episode['category'] = category
        
        # Store
        self.episodes.append(episode)
        
        # Update index
        if category not in self.index:
            self.index[category] = []
        self.index[category].append(episode['id'])
        
        # Save periodically
        if len(self.episodes) % 50 == 0:
            self._save_memories()
    
    def _categorize_episode(self, episode: Dict) -> str:
        """Categorize an episode for indexing."""
        query = episode.get('query', '').lower()
        
        if any(kw in query for kw in ['hello', 'hi', 'hey']):
            return 'greeting'
        elif any(kw in query for kw in ['code', 'function', 'debug']):
            return 'coding'
        elif any(kw in query for kw in ['what', 'why', 'how']):
            return 'question'
        else:
            return 'general'
    
    def find_similar(self, query: str, context: Dict, 
                    limit: int = 5, min_similarity: float = 0.6) -> Optional[Dict]:
        """
        Find similar past episodes.
        
        Returns most similar episode or None if no good match.
        """
        if not self.episodes:
            return None
        
        # Calculate similarity to all episodes
        similarities = []
        for i, episode in enumerate(self.episodes[-500:]):  # Check last 500
            sim = self._calculate_similarity(query, episode)
            if sim >= min_similarity:
                similarities.append((sim, episode))
        
        if not similarities:
            return None
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        # Return best match
        best_sim, best_episode = similarities[0]
        
        return {
            'episode': best_episode,
            'similarity': best_sim,
            'message': f"Found similar episode (similarity: {best_sim:.2f})"
        }
    
    def _calculate_similarity(self, query: str, episode: Dict) -> float:
        """Calculate similarity between query and stored episode."""
        stored_query = episode.get('query', '')
        
        # Text similarity
        text_sim = SequenceMatcher(None, query.lower(), stored_query.lower()).ratio()
        
        # Category bonus
        category = self._categorize_episode({'query': query})
        if episode.get('category') == category:
            text_sim += 0.1
        
        return min(1.0, text_sim)
    
    def get_episodes_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """Get episodes from a specific category."""
        indices = self.index.get(category, [])
        episodes = [self.episodes[i] for i in indices[-limit:] if i < len(self.episodes)]
        return episodes
    
    def consolidate(self):
        """
        Consolidate memories (run during idle time).
        
        Compresses old memories, removes duplicates, strengthens important ones.
        """
        if len(self.episodes) < 100:
            return
        
        # Keep only important recent memories
        recent = self.episodes[-200:]
        
        # Keep older memories that were high-quality
        older_important = [e for e in self.episodes[:-200] 
                         if e.get('quality', {}).get('score', 0) > 0.8]
        
        # Combine
        self.episodes = older_important[-100:] + recent
        
        # Rebuild index
        self._rebuild_index()
        
        # Save
        self._save_memories()
    
    def _rebuild_index(self):
        """Rebuild the category index."""
        self.index = {}
        for i, episode in enumerate(self.episodes):
            category = episode.get('category', 'general')
            if category not in self.index:
                self.index[category] = []
            self.index[category].append(i)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            'total_episodes': len(self.episodes),
            'categories': list(self.index.keys()),
            'episodes_per_category': {k: len(v) for k, v in self.index.items()}
        }
    
    def clear(self):
        """Clear all memories."""
        self.episodes = []
        self.index = {}
        self._save_memories()
