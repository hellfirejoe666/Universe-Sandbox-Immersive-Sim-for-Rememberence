#!/usr/bin/env python3
"""
FFT Novelty Detection v2 - Enhanced with User Baselines and Adaptive Thresholds

Enhancements over v1:
1. User-specific baselines (learn what "normal" looks like per user)
2. Multi-dimensional novelty (structural + semantic + temporal)
3. Adaptive thresholds (adjust based on context and history)
4. Better spectral features (more nuanced complexity metrics)
5. Query clustering (group similar queries for better baseline comparison)
6. RMC meta-cognition (track routing decision accuracy over time)
"""

import numpy as np
from scipy.fft import fft2, fftshift, fftfreq
from scipy.ndimage import gaussian_filter
from typing import Dict, Any, List, Optional, Tuple
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import re

WORKSPACE = Path("D:/Ollama/OpenClaw/workspace")
ROUTER_DIR = WORKSPACE / "hybrid-router"
BASELINES_FILE = ROUTER_DIR / "fft_baselines.json"
NOVELTY_HISTORY_FILE = ROUTER_DIR / "novelty_history.json"


class FFTNoveltyDetectorV2:
    """
    Enhanced FFT-based novelty detection with user baselines and adaptive thresholds.
    
    Novelty is now multi-dimensional:
    1. Structural novelty (FFT spectral analysis)
    2. Semantic novelty (query clustering vs baseline)
    3. Temporal novelty (has user asked similar questions recently?)
    4. Contextual novelty (time of day, conversation state)
    """
    
    def __init__(self, image_size: tuple = (64, 64), user_id: str = "default"):
        self.image_size = image_size
        self.user_id = user_id
        self.baselines = self._load_baselines()
        self.history = self._load_history()
        
        # Adaptive threshold parameters
        self.threshold_history = defaultdict(list)  # Track threshold performance
        self.context_weights = {
            "time_of_day": 1.0,
            "conversation_depth": 1.0,
            "recent_novelty_avg": 1.0,
        }
    
    def _load_baselines(self) -> Dict[str, Any]:
        """Load user-specific baselines."""
        if BASELINES_FILE.exists():
            try:
                data = json.loads(BASELINES_FILE.read_text(encoding='utf-8'))
                return data.get(self.user_id, data.get("default", {}))
            except:
                pass
        return {"signatures": [], "clusters": {}, "stats": {}}
    
    def _save_baselines(self):
        """Save user-specific baselines."""
        all_baselines = {}
        if BASELINES_FILE.exists():
            try:
                all_baselines = json.loads(BASELINES_FILE.read_text(encoding='utf-8'))
            except:
                pass
        
        all_baselines[self.user_id] = self.baselines
        BASELINES_FILE.write_text(json.dumps(all_baselines, indent=2), encoding='utf-8')
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load novelty history for adaptive thresholds."""
        if NOVELTY_HISTORY_FILE.exists():
            try:
                return json.loads(NOVELTY_HISTORY_FILE.read_text(encoding='utf-8'))
            except:
                pass
        return []
    
    def _save_history(self):
        """Save novelty history (keep last 1000 entries)."""
        if len(self.history) > 1000:
            self.history = self.history[-500:]
        NOVELTY_HISTORY_FILE.write_text(json.dumps(self.history, indent=2), encoding='utf-8')
    
    def text_to_spectral(self, text: str) -> np.ndarray:
        """Convert text to a 2D spectral representation with enhanced encoding."""
        img = np.zeros(self.image_size, dtype=np.float32)
        
        # Enhanced character mapping with multiple features
        for i, char in enumerate(text[:256]):
            x = i % self.image_size[1]
            y = i // self.image_size[1]
            
            if y < self.image_size[0]:
                # Multiple intensity channels
                ascii_intensity = ord(char) / 255.0
                
                # Add positional modulation
                positional_weight = 1.0 - (i / 256.0)  # Earlier chars weighted more
                
                # Add character type modulation
                if char.isalpha():
                    type_weight = 1.0
                elif char.isdigit():
                    type_weight = 0.8
                elif char.isspace():
                    type_weight = 0.3
                else:
                    type_weight = 0.6
                
                img[y, x] = ascii_intensity * positional_weight * type_weight
        
        # Apply Gaussian smoothing for better spectral properties
        img = gaussian_filter(img, sigma=0.5)
        
        # Apply FFT
        f = fftshift(fft2(img))
        magnitude = np.abs(f)
        
        # Normalize
        magnitude = magnitude / (np.max(magnitude) + 1e-10)
        
        return magnitude
    
    def compute_enhanced_signature(self, text: str) -> Dict[str, float]:
        """
        Compute enhanced signature with multiple spectral features.
        
        Returns comprehensive feature vector for novelty assessment.
        """
        magnitude = self.text_to_spectral(text)
        center_y, center_x = self.image_size[0] // 2, self.image_size[1] // 2
        
        # Compute FFT for frequency-based features
        img = np.zeros(self.image_size, dtype=np.float32)
        for i, char in enumerate(text[:256]):
            x = i % self.image_size[1]
            y = i // self.image_size[1]
            if y < self.image_size[0]:
                ascii_intensity = ord(char) / 255.0
                positional_weight = 1.0 - (i / 256.0)
                if char.isalpha():
                    type_weight = 1.0
                elif char.isdigit():
                    type_weight = 0.8
                elif char.isspace():
                    type_weight = 0.3
                else:
                    type_weight = 0.6
                img[y, x] = ascii_intensity * positional_weight * type_weight
        img = gaussian_filter(img, sigma=0.5)
        f = fftshift(fft2(img))
        
        # 1. Center energy (low-frequency content = familiar patterns)
        center_region = magnitude[center_y-8:center_y+8, center_x-8:center_x+8]
        center_energy = float(np.mean(center_region))
        
        # 2. High-frequency energy (novel content)
        high_freq_mask = np.ones_like(magnitude)
        high_freq_mask[center_y-16:center_y+16, center_x-16:center_x+16] = 0
        high_freq_energy = float(np.sum(magnitude * high_freq_mask))
        
        # 3. Mid-frequency energy (moderate complexity)
        mid_freq_mask = np.zeros_like(magnitude)
        mid_freq_mask[center_y-32:center_y+32, center_x-32:center_x+32] = 1
        mid_freq_mask[center_y-16:center_y+16, center_x-16:center_x+16] = 0
        mid_freq_energy = float(np.sum(magnitude * mid_freq_mask))
        
        # 4. Total energy
        total_energy = float(np.sum(magnitude) + 1e-10)
        
        # 5. Entropy (disorder measure) - enhanced with log base 2
        normalized = magnitude / (np.sum(magnitude) + 1e-10)
        normalized = normalized + 1e-10  # Avoid log(0)
        entropy = float(-np.sum(normalized * np.log2(normalized)))
        
        # 6. Symmetry score (familiar patterns are more symmetric)
        symmetry_horizontal = np.mean(np.abs(magnitude - np.fliplr(magnitude)))
        symmetry_vertical = np.mean(np.abs(magnitude - np.flipud(magnitude)))
        symmetry_score = float((symmetry_horizontal + symmetry_vertical) / 2)
        
        # 7. Radial distribution (how spread out the energy is)
        y, x = np.ogrid[:self.image_size[0], :self.image_size[1]]
        radius = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        radial_weighted = float(np.sum(magnitude * radius) / (total_energy + 1e-10))
        
        # 8. Spectral centroid (center of mass in frequency domain)
        frequencies_x = fftfreq(self.image_size[1])
        frequencies_y = fftfreq(self.image_size[0])
        centroid_x = float(np.sum(np.abs(f) * frequencies_x[np.newaxis, :]) / (np.sum(np.abs(f)) + 1e-10))
        centroid_y = float(np.sum(np.abs(f) * frequencies_y[:, np.newaxis]) / (np.sum(np.abs(f)) + 1e-10))
        spectral_centroid = float(np.sqrt(centroid_x**2 + centroid_y**2))
        
        # 9. Spectral spread (variance around centroid)
        spread = float(np.std(np.abs(f)))
        
        # 10. Peak ratio (ratio of highest peak to average)
        peak_value = np.max(magnitude)
        avg_value = np.mean(magnitude)
        peak_ratio = float(peak_value / (avg_value + 1e-10))
        
        # 11. Directional energy (horizontal vs vertical patterns)
        horizontal_energy = float(np.sum(magnitude[:, :self.image_size[1]//2]))
        vertical_energy = float(np.sum(magnitude[:self.image_size[0]//2, :]))
        directional_ratio = float(horizontal_energy / (vertical_energy + 1e-10))
        
        # 12. Texture complexity (local variance)
        local_variance = float(np.var(gaussian_filter(magnitude, sigma=2)))
        
        return {
            "center_energy": center_energy,
            "high_freq_energy": high_freq_energy,
            "mid_freq_energy": mid_freq_energy,
            "total_energy": total_energy,
            "entropy": entropy,
            "symmetry_score": symmetry_score,
            "radial_distribution": radial_weighted,
            "spectral_centroid": spectral_centroid,
            "spectral_spread": spread,
            "peak_ratio": peak_ratio,
            "directional_ratio": directional_ratio,
            "texture_complexity": local_variance,
            # Computed below
            "structural_novelty": 0.0,
            "semantic_novelty": 0.0,
            "temporal_novelty": 0.0,
            "overall_novelty": 0.0,
        }
    
    def compute_structural_novelty(self, signature: Dict[str, float]) -> float:
        """
        Compute structural novelty from FFT spectral features.
        
        Uses weighted combination of spectral metrics.
        """
        # Normalize each feature to 0-1 range based on typical values
        entropy_norm = min(signature["entropy"] / 12.0, 1.0)  # Max entropy ~12 for 64x64
        high_freq_norm = min(signature["high_freq_energy"] / signature["total_energy"], 1.0)
        symmetry_norm = 1.0 - min(signature["symmetry_score"] / 0.1, 1.0)  # Invert: low symmetry = high novelty
        radial_norm = min(signature["radial_distribution"] / 50.0, 1.0)
        texture_norm = min(signature["texture_complexity"] / 0.01, 1.0)
        peak_norm = 1.0 - min(signature["peak_ratio"] / 100.0, 1.0)  # Low peak ratio = more complex
        
        # Weighted combination (weights sum to 1.0)
        weights = {
            "entropy": 0.25,
            "high_freq": 0.25,
            "symmetry": 0.15,
            "radial": 0.15,
            "texture": 0.10,
            "peak": 0.10,
        }
        
        novelty = (
            weights["entropy"] * entropy_norm +
            weights["high_freq"] * high_freq_norm +
            weights["symmetry"] * symmetry_norm +
            weights["radial"] * radial_norm +
            weights["texture"] * texture_norm +
            weights["peak"] * peak_norm
        )
        
        return round(novelty, 3)
    
    def compute_semantic_novelty(self, text: str, signature: Dict[str, float]) -> float:
        """
        Compute semantic novelty by comparing to baseline clusters.
        
        Queries in known clusters = low semantic novelty
        Queries far from all clusters = high semantic novelty
        """
        if not self.baselines.get("clusters"):
            return 0.5  # No baseline, return neutral
        
        # Create simple text hash for clustering
        text_hash = self._text_hash(text)
        
        # Find closest cluster
        min_distance = float('inf')
        for cluster_id, cluster_sigs in self.baselines["clusters"].items():
            for baseline_sig in cluster_sigs:
                # Compare key features
                distance = 0.0
                for key in ["entropy", "center_energy", "high_freq_energy"]:
                    if key in signature and key in baseline_sig:
                        diff = abs(signature[key] - baseline_sig[key])
                        distance += diff
                
                distance = distance / 3.0  # Normalize
                min_distance = min(min_distance, distance)
        
        # Convert distance to novelty (0 = in cluster, 1 = far from all clusters)
        semantic_novelty = min(1.0, min_distance / 0.5)
        
        return round(semantic_novelty, 3)
    
    def compute_temporal_novelty(self, text: str) -> float:
        """
        Compute temporal novelty based on recent query history.
        
        Similar to recent queries = low temporal novelty
        Different from recent queries = high temporal novelty
        """
        if not self.history:
            return 0.5  # No history, return neutral
        
        # Get recent queries (last 20)
        recent = self.history[-20:]
        
        # Check for similar queries in recent history
        text_lower = text.lower()
        for entry in recent:
            recent_text = entry.get("text", "").lower()
            
            # Simple similarity check (could be enhanced with embeddings)
            if len(text_lower) > 10 and len(recent_text) > 10:
                # Word overlap
                words_text = set(text_lower.split())
                words_recent = set(recent_text.split())
                overlap = len(words_text & words_recent) / max(len(words_text), len(words_recent))
                
                if overlap > 0.6:  # Similar query
                    return 0.2  # Low temporal novelty
        
        return 0.7  # No similar recent queries = moderate novelty
    
    def _text_hash(self, text: str) -> str:
        """Create a hash for text clustering."""
        # Normalize text first
        normalized = text.lower().strip()
        normalized = re.sub(r'\s+', ' ', normalized)
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def update_baseline(self, text: str, signature: Dict[str, Any]):
        """
        Update user baseline with new signature.
        
        Called after successful routing to learn user's patterns.
        """
        # Add to signatures list
        self.baselines.setdefault("signatures", [])
        self.baselines["signatures"].append({
            "text_hash": self._text_hash(text),
            "signature": {k: v for k, v in signature.items() if isinstance(v, (int, float))},
            "timestamp": datetime.now().isoformat(),
        })
        
        # Keep only last 100 signatures
        if len(self.baselines["signatures"]) > 100:
            self.baselines["signatures"] = self.baselines["signatures"][-50:]
        
        # Update clusters (simple clustering by signature similarity)
        self._update_clusters(signature)
        
        # Update stats
        self.baselines.setdefault("stats", {})
        self.baselines["stats"]["total_queries"] = self.baselines["stats"].get("total_queries", 0) + 1
        self.baselines["stats"]["last_updated"] = datetime.now().isoformat()
        
        self._save_baselines()
    
    def _update_clusters(self, signature: Dict[str, Any]):
        """Update query clusters based on signature similarity."""
        # Simple clustering: assign to nearest existing cluster or create new
        assigned = False
        
        for cluster_id, cluster_sigs in self.baselines.setdefault("clusters", {}).items():
            # Compare to first signature in cluster (centroid approximation)
            if cluster_sigs:
                centroid = cluster_sigs[0]
                distance = 0.0
                for key in ["entropy", "center_energy", "high_freq_energy"]:
                    if key in signature and key in centroid:
                        distance += abs(signature[key] - centroid[key])
                
                if distance < 0.3:  # Similar enough to join cluster
                    cluster_sigs.append({k: v for k, v in signature.items() if isinstance(v, (int, float))})
                    assigned = True
                    break
        
        if not assigned:
            # Create new cluster
            cluster_id = f"cluster_{len(self.baselines['clusters'])}"
            self.baselines["clusters"][cluster_id] = [
                {k: v for k, v in signature.items() if isinstance(v, (int, float))}
            ]
    
    def get_adaptive_thresholds(self, context: Dict[str, Any] = None) -> Dict[str, float]:
        """
        Get adaptive thresholds based on context and history.
        
        Returns:
        - fast_threshold: Below this → FAST path
        - cloud_threshold: Above this → CLOUD path
        - context_adjustments: Why thresholds were adjusted
        """
        # Base thresholds
        fast_threshold = 0.4
        cloud_threshold = 0.8
        
        adjustments = []
        
        # 1. Time of day adjustment
        hour = datetime.now().hour
        if 2 <= hour <= 6:  # Late night
            fast_threshold -= 0.1  # More likely to use fast path (simpler queries)
            adjustments.append("late_night")
        elif 9 <= hour <= 17:  # Business hours
            cloud_threshold -= 0.05  # More willing to use cloud for complex work
            adjustments.append("business_hours")
        
        # 2. Recent novelty average
        if self.history:
            recent_novelty = np.mean([h.get("novelty_score", 0.5) for h in self.history[-20:]])
            if recent_novelty < 0.3:  # User has been asking simple questions
                fast_threshold += 0.05  # Raise bar for fast path
                adjustments.append("recent_simple")
            elif recent_novelty > 0.7:  # User has been asking complex questions
                cloud_threshold += 0.05  # More willing to use cloud
                adjustments.append("recent_complex")
        
        # 3. Conversation depth (if provided)
        if context and context.get("conversation_depth", 0) > 10:
            # Deep conversation → user is exploring, expect novelty
            cloud_threshold -= 0.05
            adjustments.append("deep_conversation")
        
        return {
            "fast_threshold": max(0.2, min(0.6, fast_threshold)),
            "cloud_threshold": max(0.7, min(0.95, cloud_threshold)),
            "adjustments": adjustments,
        }
    
    def analyze(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive novelty analysis with all dimensions.
        
        Returns multi-dimensional novelty assessment with routing recommendation.
        """
        # Compute enhanced signature
        signature = self.compute_enhanced_signature(text)
        
        # Compute multi-dimensional novelty
        structural = self.compute_structural_novelty(signature)
        semantic = self.compute_semantic_novelty(text, signature)
        temporal = self.compute_temporal_novelty(text)
        
        # Weighted combination for overall novelty
        # Structural is most reliable, semantic adds context, temporal prevents repetition
        overall = (
            0.5 * structural +
            0.3 * semantic +
            0.2 * temporal
        )
        
        # Update signature with novelty scores
        signature["structural_novelty"] = structural
        signature["semantic_novelty"] = semantic
        signature["temporal_novelty"] = temporal
        signature["overall_novelty"] = round(overall, 3)
        
        # Get adaptive thresholds
        thresholds = self.get_adaptive_thresholds(context)
        
        # Classification and recommendation
        if overall < thresholds["fast_threshold"]:
            classification = "familiar"
            recommendation = "fast"
            confidence = "high"
        elif overall < thresholds["cloud_threshold"]:
            classification = "moderate"
            recommendation = "smart"
            confidence = "medium"
        else:
            classification = "novel"
            recommendation = "cloud"
            confidence = "high"
        
        signature["classification"] = classification
        signature["recommendation"] = recommendation
        signature["confidence"] = confidence
        signature["thresholds_used"] = thresholds
        
        # Record in history for adaptive learning
        self.history.append({
            "text": text[:100],
            "text_hash": self._text_hash(text),
            "novelty_score": overall,
            "classification": classification,
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat(),
        })
        self._save_history()
        
        return signature
    
    def record_routing_outcome(self, text: str, predicted_novelty: float, 
                                actual_path: str, was_optimal: bool = True):
        """
        Record the outcome of a routing decision for learning.
        
        Use this to improve thresholds over time based on actual performance.
        """
        # Find the most recent entry for this text
        text_hash = self._text_hash(text)
        for entry in reversed(self.history):
            if entry.get("text_hash") == text_hash:
                entry["actual_path"] = actual_path
                entry["was_optimal"] = was_optimal
                entry["outcome_recorded"] = True
                break
        
        self._save_history()
        
        # Update baseline if outcome was good
        if was_optimal:
            signature = self.compute_enhanced_signature(text)
            self.update_baseline(text, signature)
    
    def get_baseline_stats(self) -> Dict[str, Any]:
        """Get statistics about user baselines and learning."""
        return {
            "user_id": self.user_id,
            "total_signatures": len(self.baselines.get("signatures", [])),
            "total_clusters": len(self.baselines.get("clusters", {})),
            "total_history": len(self.history),
            "baseline_stats": self.baselines.get("stats", {}),
            "recent_novelty_avg": np.mean([h.get("novelty_score", 0.5) for h in self.history[-20:]]) if self.history else 0.5,
        }


# Convenience function
def detect_novelty_v2(text: str, user_id: str = "default", context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Quick novelty detection with enhanced v2 detector."""
    detector = FFTNoveltyDetectorV2(user_id=user_id)
    return detector.analyze(text, context)


# RMC confidence adjustment (enhanced)
def rmc_confidence_adjustment_v2(novelty_result: Dict[str, Any], 
                                  base_confidence: float,
                                  routing_history: List[Dict] = None) -> float:
    """
    Enhanced RMC confidence adjustment with routing history.
    
    Adjusts confidence based on:
    1. FFT novelty (high novelty → lower confidence)
    2. Routing history (past accuracy for similar novelty levels)
    3. Multi-dimensional novelty breakdown
    """
    novelty = novelty_result.get("overall_novelty", 0.5)
    structural = novelty_result.get("structural_novelty", novelty)
    semantic = novelty_result.get("semantic_novelty", novelty)
    
    # Base adjustment from novelty
    novelty_adjustment = (0.5 - novelty) * 0.3  # Max ±0.15
    
    # Structural vs semantic disagreement penalty
    if abs(structural - semantic) > 0.3:
        # Structural and semantic novelty disagree → reduce confidence
        novelty_adjustment -= 0.1
    
    # Historical adjustment (if history available)
    history_adjustment = 0.0
    if routing_history:
        # Find similar novelty levels in history
        similar = [h for h in routing_history if abs(h.get("novelty_score", 0.5) - novelty) < 0.1]
        if similar:
            accuracy = sum(1 for h in similar if h.get("was_optimal", True)) / len(similar)
            history_adjustment = (accuracy - 0.5) * 0.2  # Max ±0.1
    
    adjusted = base_confidence + novelty_adjustment + history_adjustment
    
    return round(max(0.1, min(0.95, adjusted)), 3)


# CLI Interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python fft_novelty_v2.py <text> [--user USER_ID]")
        print("       python fft_novelty_v2.py --stats [--user USER_ID]")
        print("       python fft_novelty_v2.py --baseline <text>")
        sys.exit(1)
    
    user_id = "default"
    if "--user" in sys.argv:
        idx = sys.argv.index("--user")
        if idx + 1 < len(sys.argv):
            user_id = sys.argv[idx + 1]
    
    detector = FFTNoveltyDetectorV2(user_id=user_id)
    
    if sys.argv[1] == "--stats":
        stats = detector.get_baseline_stats()
        print(json.dumps(stats, indent=2))
    
    elif sys.argv[1] == "--baseline" and len(sys.argv) >= 3:
        text = sys.argv[2]
        signature = detector.compute_enhanced_signature(text)
        detector.update_baseline(text, signature)
        print(f"Added to baseline for user '{user_id}'")
        print(f"Total signatures: {len(detector.baselines.get('signatures', []))}")
    
    else:
        text = " ".join(sys.argv[1:])
        if "--user" in text:
            text = text.split("--user")[0].strip()
        
        result = detector.analyze(text)
        print(json.dumps(result, indent=2))
