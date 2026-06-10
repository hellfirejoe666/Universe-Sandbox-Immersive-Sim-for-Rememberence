"""
Reasoning System (Prefrontal Cortex / Cloud)

Complex reasoning, novel queries, cloud-based processing.
"""

import subprocess
from datetime import datetime
from typing import Dict, Any


class ReasoningSystem:
    """
    Handles complex reasoning and novel queries.
    Uses cloud models (qwen3.5:cloud) for heavy computation.
    """
    
    def __init__(self):
        self.cloud_model = 'qwen3.5:cloud'
    
    def cloud_response(self, query: str, context: Dict) -> Dict[str, Any]:
        """
        Generate response using cloud model.
        
        Used for novel, complex, or high-stakes queries.
        """
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                ["ollama", "run", self.cloud_model, query],
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )
            
            latency = (datetime.now() - start_time).total_seconds() * 1000
            content = result.stdout.strip() if result.stdout else "[Empty response from cloud model]"
            
            return {
                'content': content,
                'path': 'cloud',
                'model': self.cloud_model,
                'latency_ms': latency,
                'cached': False
            }
        
        except subprocess.TimeoutExpired:
            return {
                'content': "[TIMEOUT] Cloud model unavailable. Try again later.",
                'path': 'cloud',
                'model': self.cloud_model,
                'latency_ms': 60000,
                'cached': False
            }
        except Exception as e:
            return {
                'content': f"[ERROR] Cloud request failed: {str(e)}",
                'path': 'cloud',
                'model': self.cloud_model,
                'latency_ms': 0,
                'cached': False
            }
    
    def complex_reasoning(self, query: str, context: Dict, 
                         require_citations: bool = False) -> Dict[str, Any]:
        """
        Handle complex reasoning tasks with structured output.
        """
        # Add reasoning prompt prefix
        reasoning_prompt = f"""Analyze this carefully and provide a well-reasoned response:

{query}

Think step-by-step and explain your reasoning."""
        
        return self.cloud_response(reasoning_prompt, context)
    
    def novel_query_handling(self, query: str, context: Dict) -> Dict[str, Any]:
        """
        Handle truly novel queries (never seen before).
        
        Uses cloud model with maximum creativity/adaptability.
        """
        # Add creativity prompt
        creativity_prompt = f"""This is a novel question that requires creative thinking:

{query}

Provide a thoughtful, creative response that addresses the unique aspects of this query."""
        
        return self.cloud_response(creativity_prompt, context)
    
    def escalate_from_smart(self, query: str, smart_response: str, 
                           quality_score: float) -> Dict[str, Any]:
        """
        Escalate to cloud when smart path quality is insufficient.
        """
        escalation_prompt = f"""The following response was inadequate (quality: {quality_score}):

Query: {query}
Previous response: {smart_response}

Please provide a better, more comprehensive answer."""
        
        return self.cloud_response(escalation_prompt, {})
