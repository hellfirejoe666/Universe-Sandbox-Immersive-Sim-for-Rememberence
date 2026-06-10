#!/usr/bin/env python3
"""
RMC (Recursive Meta-Cognition) Layer for Hybrid Router

Provides self-monitoring, explainable routing decisions, and learning from feedback.

Core Functions:
1. Confidence Calibration - Know when the router is uncertain
2. Decision Explanation - Explain why a path was chosen
3. Feedback Learning - Adjust based on user satisfaction
4. Decision History - Track patterns in routing decisions
5. Anomaly Detection - Notice when routing seems wrong

This is the "metacognitive monitoring" system of the brain-inspired architecture.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import hashlib

WORKSPACE = Path("D:/Ollama/OpenClaw/workspace")
ROUTER_DIR = WORKSPACE / "hybrid-router"
DECISION_LOG_FILE = ROUTER_DIR / "rmc_decision_log.json"
CONFIDENCE_CALIBRATION_FILE = ROUTER_DIR / "rmc_calibration.json"


@dataclass
class RoutingDecision:
    """Records a single routing decision with all context."""
    timestamp: str
    query_hash: str
    query_preview: str
    novelty_score: float
    fft_classification: str
    llm_path: str
    llm_confidence: float
    adjusted_confidence: float
    final_path: str
    reasoning: str
    latency_ms: float
    tokens_used: int
    user_satisfaction: Optional[float] = None  # Filled in later if feedback provided
    feedback_text: Optional[str] = None


class RMC_META_COGNITION:
    """
    Recursive Meta-Cognition layer for the hybrid router.
    
    Monitors routing decisions, explains them, and learns from feedback.
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.decision_history: List[RoutingDecision] = []
        self.calibration_data: Dict[str, List[Dict]] = {
            "fast": [],
            "localgen": [],
            "smart": [],
            "cloud": []
        }
        self.load_calibration()
        
        # Confidence thresholds (learned over time)
        self.path_confidence_thresholds = {
            "fast": 0.7,
            "localgen": 0.5,
            "smart": 0.6,
            "cloud": 0.8
        }
    
    def load_calibration(self):
        """Load calibration data from disk."""
        if CONFIDENCE_CALIBRATION_FILE.exists():
            try:
                with open(CONFIDENCE_CALIBRATION_FILE, 'r') as f:
                    data = json.load(f)
                    self.calibration_data = data.get("calibration", self.calibration_data)
                    self.path_confidence_thresholds = data.get(
                        "thresholds", 
                        self.path_confidence_thresholds
                    )
            except Exception:
                pass
    
    def save_calibration(self):
        """Save calibration data to disk."""
        data = {
            "calibration": self.calibration_data,
            "thresholds": self.path_confidence_thresholds,
            "last_updated": datetime.now().isoformat()
        }
        with open(CONFIDENCE_CALIBRATION_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def evaluate_decision(
        self,
        query: str,
        novelty_result: Dict[str, Any],
        llm_classification: Dict[str, Any],
        final_path: str,
        latency_ms: float,
        tokens_used: int
    ) -> Dict[str, Any]:
        """
        Evaluate and record a routing decision with meta-cognitive analysis.
        
        Returns explanation and confidence metrics.
        """
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
        
        # Extract signals
        novelty = novelty_result.get("novelty_score", 0.5)
        fft_rec = novelty_result.get("recommendation", "smart")
        llm_path = llm_classification.get("path", "smart")
        llm_conf = llm_classification.get("confidence", 0.5)
        
        # Calculate adjusted confidence
        adjusted_conf = self._adjust_confidence(novelty, llm_conf)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            query, novelty, fft_rec, llm_path, llm_conf, adjusted_conf, final_path
        )
        
        # Create decision record
        decision = RoutingDecision(
            timestamp=datetime.now().isoformat(),
            query_hash=query_hash,
            query_preview=query[:100],
            novelty_score=novelty,
            fft_classification=fft_rec,
            llm_path=llm_path,
            llm_confidence=llm_conf,
            adjusted_confidence=adjusted_conf,
            final_path=final_path,
            reasoning=reasoning,
            latency_ms=latency_ms,
            tokens_used=tokens_used
        )
        
        # Record decision
        self.decision_history.append(decision)
        if len(self.decision_history) > self.max_history:
            self.decision_history = self.decision_history[-self.max_history:]
        
        # Record for calibration
        self.calibration_data[final_path].append({
            "novelty": novelty,
            "confidence": adjusted_conf,
            "timestamp": decision.timestamp
        })
        
        # Trim calibration data
        for path in self.calibration_data:
            if len(self.calibration_data[path]) > 500:
                self.calibration_data[path] = self.calibration_data[path][-500:]
        
        # Check for anomalies
        anomaly = self._detect_anomaly(decision)
        
        return {
            "decision": asdict(decision),
            "confidence": adjusted_conf,
            "reasoning": reasoning,
            "anomaly_detected": anomaly,
            "calibration_status": self._get_calibration_status()
        }
    
    def _adjust_confidence(self, novelty: float, base_confidence: float) -> float:
        """
        Adjust confidence based on novelty and calibration data.
        
        High novelty → lower confidence (out of distribution)
        Low novelty → higher confidence (familiar pattern)
        """
        # Base adjustment: inverse relationship with novelty
        novelty_adjustment = (0.5 - novelty) * 0.3  # Max ±0.15
        
        # Calibration adjustment: based on historical success
        # (Would be populated from feedback over time)
        calibration_adjustment = 0.0
        
        adjusted = base_confidence + novelty_adjustment + calibration_adjustment
        
        return round(max(0.1, min(0.95, adjusted)), 3)
    
    def _generate_reasoning(
        self,
        query: str,
        novelty: float,
        fft_rec: str,
        llm_path: str,
        llm_conf: float,
        adjusted_conf: float,
        final_path: str
    ) -> str:
        """Generate human-readable explanation for routing decision."""
        reasons = []
        
        # Novelty-based reasoning
        if novelty < 0.3:
            reasons.append(f"Low novelty ({novelty:.2f}) suggests familiar pattern")
        elif novelty < 0.5:
            reasons.append(f"Moderate novelty ({novelty:.2f}) indicates some complexity")
        elif novelty < 0.75:
            reasons.append(f"High novelty ({novelty:.2f}) requires reasoning")
        else:
            reasons.append(f"Very high novelty ({novelty:.2f}) demands advanced processing")
        
        # FFT recommendation
        if fft_rec == "fast":
            reasons.append("FFT recommends fast path (spectral signature matches patterns)")
        elif fft_rec == "localgen":
            reasons.append("FFT suggests language/creative processing")
        elif fft_rec == "smart":
            reasons.append("FFT indicates analytical reasoning needed")
        elif fft_rec == "cloud":
            reasons.append("FFT detects highly novel structure")
        
        # LLM classification
        if llm_conf > 0.8:
            reasons.append(f"LLM classifier highly confident ({llm_conf:.2f}) in {llm_path} path")
        elif llm_conf > 0.6:
            reasons.append(f"LLM classifier moderately confident ({llm_conf:.2f})")
        else:
            reasons.append(f"LLM classifier uncertain ({llm_conf:.2f}), relying on other signals")
        
        # Agreement/disagreement
        if fft_rec == final_path or llm_path == final_path:
            reasons.append("Multiple signals agree on routing")
        else:
            reasons.append("Signals disagree, using weighted decision matrix")
        
        # Final decision
        reason_str = "; ".join(reasons)
        reason_str += f" → {final_path.upper()} path selected"
        
        return reason_str
    
    def _detect_anomaly(self, decision: RoutingDecision) -> Optional[Dict[str, Any]]:
        """
        Detect anomalies in routing decisions.
        
        Returns anomaly info if detected, None otherwise.
        """
        anomalies = []
        
        # Anomaly 1: High confidence but wrong path (based on feedback)
        if decision.user_satisfaction is not None and decision.user_satisfaction < 0.3:
            if decision.adjusted_confidence > 0.7:
                anomalies.append({
                    "type": "overconfident_misroute",
                    "severity": "high",
                    "description": "High confidence but user dissatisfied"
                })
        
        # Anomaly 2: Very high novelty routed to fast path
        if decision.novelty_score > 0.8 and decision.final_path == "fast":
            anomalies.append({
                "type": "novel_to_fast",
                "severity": "medium",
                "description": f"High novelty ({decision.novelty_score}) routed to FAST"
            })
        
        # Anomaly 3: Very low novelty routed to cloud
        if decision.novelty_score < 0.3 and decision.final_path == "cloud":
            anomalies.append({
                "type": "familiar_to_cloud",
                "severity": "high",
                "description": f"Low novelty ({decision.novelty_score}) routed to CLOUD (wasteful)"
            })
        
        # Anomaly 4: Extreme latency
        if decision.latency_ms > 30000:  # 30 seconds
            anomalies.append({
                "type": "extreme_latency",
                "severity": "medium",
                "description": f"Response took {decision.latency_ms/1000:.1f}s"
            })
        
        return anomalies[0] if anomalies else None
    
    def _get_calibration_status(self) -> Dict[str, Any]:
        """Get current calibration status for each path."""
        status = {}
        for path, data in self.calibration_data.items():
            if len(data) >= 10:
                recent = data[-20:]
                avg_conf = sum(d["confidence"] for d in recent) / len(recent)
                status[path] = {
                    "samples": len(data),
                    "recent_avg_confidence": round(avg_conf, 3),
                    "threshold": self.path_confidence_thresholds[path]
                }
            else:
                status[path] = {
                    "samples": len(data),
                    "status": "collecting_data",
                    "threshold": self.path_confidence_thresholds[path]
                }
        return status
    
    def record_feedback(self, query_hash: str, satisfaction: float, feedback_text: str = None):
        """
        Record user feedback for a decision.
        
        satisfaction: 0.0 (terrible) to 1.0 (perfect)
        feedback_text: Optional explanation
        """
        # Find the decision
        for decision in reversed(self.decision_history):
            if decision.query_hash == query_hash:
                decision.user_satisfaction = satisfaction
                decision.feedback_text = feedback_text
                
                # Update calibration based on feedback
                self._update_calibration(decision, satisfaction)
                return
        
        # Decision not found (might be from previous session)
        print(f"Warning: No decision found for query hash {query_hash}")
    
    def _update_calibration(self, decision: RoutingDecision, satisfaction: float):
        """Update calibration based on feedback."""
        path = decision.final_path
        
        # If satisfaction is low, we may have used wrong path
        if satisfaction < 0.3:
            # Increase threshold for this path (be more selective)
            current_threshold = self.path_confidence_thresholds[path]
            self.path_confidence_thresholds[path] = min(0.95, current_threshold + 0.05)
        
        # If satisfaction is high, reinforce this path
        elif satisfaction > 0.8:
            # Slightly decrease threshold (more willing to use this path)
            current_threshold = self.path_confidence_thresholds[path]
            self.path_confidence_thresholds[path] = max(0.3, current_threshold - 0.02)
        
        # Save calibration
        self.save_calibration()
    
    def get_decision_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent decision history."""
        recent = self.decision_history[-limit:]
        return [asdict(d) for d in recent]
    
    def get_routing_insights(self) -> Dict[str, Any]:
        """
        Generate insights from routing history.
        
        Returns patterns, anomalies, and recommendations.
        """
        if len(self.decision_history) < 10:
            return {"status": "insufficient_data", "decisions_recorded": len(self.decision_history)}
        
        # Analyze path distribution
        path_counts = {}
        for d in self.decision_history:
            path_counts[d.final_path] = path_counts.get(d.final_path, 0) + 1
        
        total = len(self.decision_history)
        distribution = {k: round(v/total*100, 1) for k, v in path_counts.items()}
        
        # Analyze satisfaction by path
        satisfaction_by_path = {}
        for path in ["fast", "localgen", "smart", "cloud"]:
            path_decisions = [d for d in self.decision_history if d.final_path == path and d.user_satisfaction is not None]
            if path_decisions:
                avg_sat = sum(d.user_satisfaction for d in path_decisions) / len(path_decisions)
                satisfaction_by_path[path] = {
                    "avg_satisfaction": round(avg_sat, 3),
                    "feedback_count": len(path_decisions)
                }
        
        # Count anomalies
        anomaly_count = sum(1 for d in self.decision_history if self._detect_anomaly(d))
        
        # Generate recommendations
        recommendations = []
        
        # Check cloud usage
        cloud_pct = distribution.get("cloud", 0)
        if cloud_pct > 10:
            recommendations.append({
                "priority": "high",
                "recommendation": f"Cloud usage at {cloud_pct}% (target <5%). Consider lowering CLOUD_THRESHOLD.",
                "action": "adjust_threshold"
            })
        
        # Check fast path usage
        fast_pct = distribution.get("fast", 0)
        if fast_pct < 30:
            recommendations.append({
                "priority": "medium",
                "recommendation": f"Fast path at {fast_pct}% (target 40-50%). Add more patterns or lower FAST_THRESHOLD.",
                "action": "add_patterns"
            })
        
        # Check satisfaction
        if satisfaction_by_path:
            worst_path = min(satisfaction_by_path.items(), key=lambda x: x[1]["avg_satisfaction"])
            if worst_path[1]["avg_satisfaction"] < 0.6 and worst_path[1]["feedback_count"] >= 5:
                recommendations.append({
                    "priority": "high",
                    "recommendation": f"{worst_path[0].upper()} path has low satisfaction ({worst_path[1]['avg_satisfaction']}). Review routing logic.",
                    "action": "review_routing"
                })
        
        return {
            "total_decisions": total,
            "path_distribution": distribution,
            "satisfaction_by_path": satisfaction_by_path,
            "anomaly_count": anomaly_count,
            "anomaly_rate": round(anomaly_count/total*100, 2),
            "recommendations": recommendations,
            "calibration_status": self._get_calibration_status()
        }
    
    def explain_recent_decisions(self, limit: int = 5) -> List[str]:
        """Get explanations for recent decisions."""
        recent = self.decision_history[-limit:]
        explanations = []
        for d in recent:
            exp = f"[{d.final_path.upper()}] {d.query_preview}...\n  Reasoning: {d.reasoning}"
            if d.user_satisfaction is not None:
                exp += f"\n  User satisfaction: {d.user_satisfaction:.2f}"
            explanations.append(exp)
        return explanations


# Convenience functions
_rmc_instance = None

def get_rmc() -> RMC_META_COGNITION:
    """Get or create RMC singleton instance."""
    global _rmc_instance
    if _rmc_instance is None:
        _rmc_instance = RMC_META_COGNITION()
    return _rmc_instance

def evaluate_routing(query, novelty_result, llm_class, final_path, latency_ms, tokens_used):
    """Convenience function to evaluate a routing decision."""
    rmc = get_rmc()
    return rmc.evaluate_decision(query, novelty_result, llm_class, final_path, latency_ms, tokens_used)

def record_user_feedback(query_hash, satisfaction, feedback_text=None):
    """Convenience function to record user feedback."""
    rmc = get_rmc()
    rmc.record_feedback(query_hash, satisfaction, feedback_text)

def get_insights():
    """Get routing insights."""
    rmc = get_rmc()
    return rmc.get_routing_insights()


# CLI interface
if __name__ == "__main__":
    import sys
    
    rmc = RMC_META_COGNITION()
    
    if len(sys.argv) < 2:
        print("RMC Meta-Cognition Layer")
        print("=" * 60)
        print()
        print("Usage:")
        print("  python rmc_meta_cognition.py insights    - Show routing insights")
        print("  python rmc_meta_cognition.py history     - Show recent decisions")
        print("  python rmc_meta_cognition.py explain     - Explain recent decisions")
        print("  python rmc_meta_cognition.py status      - Show calibration status")
        print()
        sys.exit(0)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "insights":
        insights = rmc.get_routing_insights()
        print(json.dumps(insights, indent=2))
    
    elif cmd == "history":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        history = rmc.get_decision_history(limit)
        print(json.dumps(history, indent=2))
    
    elif cmd == "explain":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        explanations = rmc.explain_recent_decisions(limit)
        for exp in explanations:
            print(exp)
            print("-" * 60)
    
    elif cmd == "status":
        status = rmc._get_calibration_status()
        print(json.dumps(status, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
