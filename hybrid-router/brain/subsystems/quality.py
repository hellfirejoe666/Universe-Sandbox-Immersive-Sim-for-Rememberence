"""
Quality System (Cerebellum)

Output prediction, error correction, coherence checking.
"""

from typing import Dict, Any


class QualitySystem:
    """
    Validates output quality before sending to user.
    Like the cerebellum fine-tuning motor output.
    """
    
    def __init__(self):
        self.quality_threshold = 0.6
        self.coherence_threshold = 0.5
    
    def assess(self, response: Dict, query: str, context: Dict) -> Dict[str, Any]:
        """
        Assess response quality.
        
        Returns:
            Dict with:
            - acceptable: bool (can this be sent to user?)
            - score: float (0.0 to 1.0)
            - issues: List[str] (quality problems detected)
            - suggestions: List[str] (how to improve)
        """
        content = response.get('content', '')
        issues = []
        suggestions = []
        
        # Check for empty response
        if not content or len(content) < 5:
            issues.append("empty_or_too_short")
            suggestions.append("Generate more substantive response")
        
        # Check for coherence (basic heuristics)
        coherence = self._check_coherence(content)
        if coherence < self.coherence_threshold:
            issues.append("low_coherence")
            suggestions.append("Response may be incoherent or fragmented")
        
        # Check for error indicators
        error_indicators = ['error:', 'failed', 'unable to', 'sorry, i cannot']
        if any(ind in content.lower() for ind in error_indicators):
            issues.append("error_indicators")
            suggestions.append("Response contains error language")
        
        # Check for relevance to query
        relevance = self._check_relevance(content, query)
        if relevance < 0.3:
            issues.append("low_relevance")
            suggestions.append("Response may not address the query")
        
        # Calculate overall score
        score = 1.0
        score -= len(issues) * 0.2
        score = max(0.0, min(1.0, score))
        
        acceptable = score >= self.quality_threshold and len(issues) < 3
        
        return {
            'acceptable': acceptable,
            'score': score,
            'coherence': coherence,
            'relevance': relevance,
            'issues': issues,
            'suggestions': suggestions
        }
    
    def _check_coherence(self, content: str) -> float:
        """Check if content is coherent (basic heuristics)."""
        # Very basic: check for sentence structure
        sentences = content.split('.')
        if len(sentences) < 1:
            return 0.0
        
        # Check for reasonable word lengths
        words = content.split()
        if not words:
            return 0.0
        
        avg_word_len = sum(len(w) for w in words) / len(words)
        
        # Reasonable avg word length is 4-8 characters
        if avg_word_len < 3 or avg_word_len > 12:
            return 0.3
        
        return 0.7  # Default to acceptable
    
    def _check_relevance(self, content: str, query: str) -> float:
        """Check if content is relevant to query."""
        # Very basic: check for keyword overlap
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        overlap = query_words & content_words
        if not overlap:
            return 0.0
        
        return min(1.0, len(overlap) / len(query_words))
    
    def predict_quality(self, query: str, path: str, context: Dict) -> float:
        """
        Predict quality before generating response.
        
        Used for path selection.
        """
        # Heuristics based on path and query
        base_quality = {
            'fast': 0.7,
            'smart': 0.8,
            'cloud': 0.9
        }
        
        # Adjust for query complexity
        if len(query) > 200:
            base_quality['fast'] -= 0.2
            base_quality['smart'] -= 0.1
        
        return base_quality.get(path, 0.5)
    
    def set_threshold(self, threshold: float):
        """Set quality threshold for acceptance."""
        self.quality_threshold = max(0.0, min(1.0, threshold))
