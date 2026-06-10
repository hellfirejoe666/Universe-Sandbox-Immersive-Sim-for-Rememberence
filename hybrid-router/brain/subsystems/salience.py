"""
Salience System (Amygdala)

Urgency detection, priority override, safety checks.
"""

import re
from typing import Dict, Any, List


class SalienceSystem:
    """
    Detects emotionally salient or urgent content.
    Can override normal routing for high-priority items.
    Like the amygdala's threat detection and priority signaling.
    """
    
    def __init__(self):
        # Urgency indicators
        self.urgency_patterns = [
            r'\b(urgent|emergency|critical|asap|immediately)\b',
            r'\b(broken|crash|error|fail|dead)\b',
            r'!!!+',
            r'\bHELP\b',
            r'\b(please|need|must|have to)\b.*\b(now|fast|quick)\b',
        ]
        
        # Safety-critical keywords
        self.safety_patterns = [
            r'\b(suicide|harm|hurt|kill|danger)\b',
            r'\b(medical|doctor|hospital|poison)\b',
            r'\b(legal|lawyer|arrest|court)\b',
            r'\b(financial|bankrupt|money.*lost)\b',
        ]
        
        # Frustration indicators
        self.frustration_patterns = [
            r'\b(why|wont|doesnt|cant|impossible)\b',
            r'\b(stupid|dumb|useless|waste)\b',
            r'\b(angry|frustrated|annoyed)\b',
            r'(?i)\b(fuck|shit|damn|hell)\b',
        ]
    
    def assess(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess salience of a query.
        
        Returns:
            Dict with:
            - override: bool (should normal routing be overridden?)
            - forced_path: str (which path to force, if any)
            - priority: str (low/normal/high/critical)
            - salience_score: float (0.0 to 1.0)
            - reasons: List[str] (why this assessment was made)
        """
        reasons = []
        salience_score = 0.0
        priority = 'normal'
        forced_path = None
        
        query_lower = query.lower()
        
        # Check urgency
        urgency_matches = sum(1 for pattern in self.urgency_patterns 
                             if re.search(pattern, query_lower))
        if urgency_matches > 0:
            salience_score += 0.3 * urgency_matches
            reasons.append(f"urgency_detected ({urgency_matches} indicators)")
            priority = 'high'
            forced_path = 'cloud'  # Route to best available
        
        # Check safety
        safety_matches = sum(1 for pattern in self.safety_patterns 
                            if re.search(pattern, query_lower))
        if safety_matches > 0:
            salience_score += 0.4 * safety_matches
            reasons.append(f"safety_critical ({safety_matches} indicators)")
            priority = 'critical'
            forced_path = 'cloud'  # Always use best path for safety
        
        # Check frustration
        frustration_matches = sum(1 for pattern in self.frustration_patterns 
                                 if re.search(pattern, query_lower))
        if frustration_matches > 0:
            salience_score += 0.2 * frustration_matches
            reasons.append(f"frustration_detected ({frustration_matches} indicators)")
            if priority == 'normal':
                priority = 'high'
        
        # Check context for user state
        user_state = context.get('user_state', '')
        if user_state in ['frustrated', 'urgent', 'stressed', 'crisis']:
            salience_score += 0.3
            reasons.append(f"user_state ({user_state})")
            priority = 'high'
            if not forced_path:
                forced_path = 'cloud'
        
        # Check caps (shouting)
        if query.isupper() and len(query) > 10:
            salience_score += 0.1
            reasons.append("caps_detected (possible shouting)")
        
        # Normalize score
        salience_score = min(1.0, salience_score)
        
        # Determine if override is needed
        override = salience_score > 0.5
        
        return {
            'override': override,
            'forced_path': forced_path,
            'priority': priority,
            'salience_score': salience_score,
            'reasons': reasons
        }
    
    def is_safety_critical(self, query: str) -> bool:
        """Check if query involves safety-critical content."""
        query_lower = query.lower()
        return any(re.search(pattern, query_lower) 
                  for pattern in self.safety_patterns)
    
    def get_priority(self, query: str, context: Dict) -> str:
        """Get priority level without full assessment."""
        result = self.assess(query, context)
        return result['priority']
