"""
Attention System (Thalamus)

Context filtering, signal amplification, relevance gating.
"""

from typing import Dict, Any, List


class AttentionSystem:
    """
    Filters and amplifies relevant signals.
    Like the thalamus gating sensory input to relevant brain regions.
    """
    
    def __init__(self):
        # Context relevance weights
        self.context_weights = {
            'coding': ['code', 'function', 'debug', 'error', 'bug', 'fix', 'python', 'javascript'],
            'social': ['hello', 'how are you', 'chat', 'talk', 'friend', 'feel'],
            'learning': ['explain', 'teach', 'learn', 'understand', 'what is', 'how does'],
            'creative': ['story', 'write', 'imagine', 'create', 'poem', 'fiction'],
            'technical': ['server', 'api', 'database', 'network', 'config', 'deploy']
        }
    
    def filter(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter context to amplify relevant signals.
        
        Returns focused context with amplified relevant fields.
        """
        user_state = context.get('user_state', 'general')
        
        # Get relevant keywords for this state
        relevant_keywords = self.context_weights.get(user_state, [])
        
        # Score query relevance to each context type
        query_lower = query.lower()
        relevance_scores = {}
        
        for state, keywords in self.context_weights.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            relevance_scores[state] = score
        
        # Determine primary focus
        primary_focus = max(relevance_scores.keys(), 
                          key=lambda k: relevance_scores[k])
        
        # Build focused context
        focused = {
            **context,
            'primary_focus': primary_focus,
            'relevance_scores': relevance_scores,
            'amplified_fields': self._get_amplified_fields(primary_focus)
        }
        
        return focused
    
    def _get_amplified_fields(self, focus: str) -> List[str]:
        """Get which context fields to amplify for this focus."""
        amplification_map = {
            'coding': ['code_context', 'error_messages', 'file_paths'],
            'social': ['user_mood', 'conversation_history', 'personal_context'],
            'learning': ['knowledge_level', 'learning_goals', 'previous_topics'],
            'creative': ['style_preferences', 'genre', 'tone'],
            'technical': ['system_info', 'logs', 'config_details']
        }
        
        return amplification_map.get(focus, [])
    
    def gate(self, query: str, context: Dict, active_modules: List[str]) -> List[str]:
        """
        Gate which modules should receive this signal.
        
        Returns list of module names that should process this query.
        """
        focus = context.get('primary_focus', 'general')
        
        # Module relevance by focus
        module_relevance = {
            'coding': ['language', 'reasoning'],
            'social': ['language', 'memory'],
            'learning': ['language', 'memory', 'reasoning'],
            'creative': ['language'],
            'technical': ['reasoning', 'language'],
            'general': ['language', 'memory']
        }
        
        relevant_modules = module_relevance.get(focus, ['language'])
        
        # Filter to only active modules
        return [m for m in relevant_modules if m in active_modules]
    
    def amplify(self, query: str, focus: str) -> str:
        """
        Amplify relevant aspects of a query.
        
        Returns query with relevant context emphasized.
        """
        # For now, just return the query as-is
        # Future: could add emphasis markers or context prefixes
        return query
    
    def get_focus(self, query: str, context: Dict) -> str:
        """Quick focus detection without full filtering."""
        result = self.filter(query, context)
        return result['primary_focus']
