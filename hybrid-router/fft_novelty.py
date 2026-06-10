#!/usr/bin/env python3
"""
FFT Novelty Detection for Hybrid Router

Uses Fast Fourier Transform to analyze query complexity and detect novelty.
High-frequency components = novel/unexpected input
Low-frequency components = familiar/pattern-matched input

This is adapted from the Rememberence FFT bridge (rememberence_bridge.py).
"""

import numpy as np
from scipy.fft import fft2, fftshift
from typing import Dict, Any, List
import hashlib


class FFTNoveltyDetector:
    """
    Analyzes text using FFT-based spectral analysis to detect novelty.
    
    The core idea: familiar patterns have regular, predictable structure
    (low entropy, high symmetry in frequency domain). Novel queries have
    irregular structure (high entropy, asymmetry).
    
    Learns baselines from common queries to improve accuracy over time.
    """
    
    def __init__(self, image_size: tuple = (128, 128)):
        self.image_size = image_size
        # Baseline signatures for common patterns
        self.baseline_signatures: Dict[str, np.ndarray] = {}
        # Learned baselines from user's common queries
        self.user_baselines: List[Dict[str, float]] = []
        self.max_baselines = 50  # Keep last 50 common queries
    
    def text_to_spectral(self, text: str) -> np.ndarray:
        """Convert text to a 2D spectral representation."""
        # Create a 2D representation of the text
        img = np.zeros(self.image_size, dtype=np.float32)
        
        # Map characters to positions with intensity
        for i, char in enumerate(text[:256]):  # Limit length
            x = i % self.image_size[1]
            y = i // self.image_size[1]
            if y < self.image_size[0]:
                # Use ASCII value for intensity modulation
                intensity = ord(char) / 255.0
                img[y, x] = intensity
        
        # Apply FFT
        f = fftshift(fft2(img))
        magnitude = np.abs(f)
        
        return magnitude
    
    def compute_signature(self, text: str) -> Dict[str, float]:
        """Compute a signature vector for the text."""
        magnitude = self.text_to_spectral(text)
        
        # Extract features from frequency domain
        center_y, center_x = self.image_size[0] // 2, self.image_size[1] // 2
        
        # Center energy (low-frequency content = familiar patterns)
        center_energy = magnitude[center_y, center_x]
        
        # High-frequency energy (novel content)
        high_freq_mask = np.ones_like(magnitude)
        high_freq_mask[center_y-16:center_y+16, center_x-16:center_x+16] = 0
        high_freq_energy = np.sum(magnitude * high_freq_mask)
        
        # Total energy
        total_energy = np.sum(magnitude) + 1e-10
        
        # Entropy (disorder measure)
        normalized = magnitude / (np.sum(magnitude) + 1e-10)
        entropy = -np.sum(normalized * np.log(normalized + 1e-10))
        
        # Symmetry score (familiar patterns are more symmetric)
        symmetry_score = np.mean(np.abs(magnitude - np.flip(magnitude)))
        
        # Radial distribution (how spread out the energy is)
        y, x = np.ogrid[:self.image_size[0], :self.image_size[1]]
        radius = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        radial_weighted = np.sum(magnitude * radius) / (total_energy + 1e-10)
        
        return {
            "center_energy": float(center_energy),
            "high_freq_energy": float(high_freq_energy),
            "total_energy": float(total_energy),
            "entropy": float(entropy),
            "symmetry_score": float(symmetry_score),
            "radial_distribution": float(radial_weighted),
            "novelty_score": 0.0  # Computed below
        }
    
    def compute_novelty(self, signature: Dict[str, float], text_length: int = 0, text: str = "") -> float:
        """
        Compute novelty score from signature with multiple signals.
        
        Combines:
        1. FFT spectral analysis (good for long/complex text)
        2. Simple heuristics (good for short text)
        3. Pattern indicators (question words, common phrases)
        
        High novelty = complex, unique, abstract
        Low novelty = simple, common, concrete
        """
        # === SIGNAL 1: Simple Heuristics (weighted heavily for short text) ===
        heuristic_novelty = self._compute_heuristic_novelty(text, text_length)
        
        # === SIGNAL 2: FFT Spectral Analysis (weighted for longer text) ===
        entropy_norm = min(signature["entropy"] / 10.0, 1.0)
        high_freq_ratio = signature["high_freq_energy"] / signature["total_energy"]
        high_freq_norm = min(high_freq_ratio * 2, 1.0)
        symmetry_norm = 1.0 - min(signature["symmetry_score"] / 1000.0, 1.0)
        radial_norm = min(signature["radial_distribution"] / 50.0, 1.0)
        
        fft_novelty = (
            0.30 * entropy_norm +
            0.35 * high_freq_norm +
            0.20 * symmetry_norm +
            0.15 * radial_norm
        )
        
        # === SIGNAL 3: Blend based on text length ===
        # Short text (<20 chars): trust heuristics more
        # Long text (>50 chars): trust FFT more
        if text_length < 20:
            weight_heuristic = 0.8
            weight_fft = 0.2
        elif text_length < 50:
            weight_heuristic = 0.5
            weight_fft = 0.5
        else:
            weight_heuristic = 0.2
            weight_fft = 0.8
        
        novelty = (weight_heuristic * heuristic_novelty) + (weight_fft * fft_novelty)
        
        return round(novelty, 3)
    
    def _compute_heuristic_novelty(self, text: str, text_length: int) -> float:
        """
        Compute novelty using simple heuristics that work well for short text.
        
        Returns 0.0-1.0 where lower = more familiar/common
        """
        if not text:
            return 0.5
        
        text_lower = text.lower().strip()
        novelty = 0.5  # Start neutral
        
        # === Familiar patterns (reduce novelty) ===
        familiar_patterns = [
            # Greetings
            "hello", "hi", "hey", "good morning", "good evening",
            # Status checks
            "status", "running", "working", "alive", "gateway",
            # Common questions
            "what is", "who are", "your name", "can you",
            "help", "thank", "please",
            # Commands
            "list", "show", "get", "check",
            # Math (simple)
            " + ", " - ", " * ", " / ",
            # Time
            "time", "date", "today", "what time",
        ]
        
        for pattern in familiar_patterns:
            if pattern in text_lower:
                novelty -= 0.15
        
        # === Novel indicators (increase novelty) ===
        novel_indicators = [
            # Complex question words
            "why does", "how would", "what if", "explain the",
            # Creative/abstract
            "imagine", "create", "design", "invent", "theorize",
            # Multi-step reasoning
            "compare", "analyze", "evaluate", "synthesize",
            # Technical depth
            "algorithm", "architecture", "implementation", "optimization",
        ]
        
        for indicator in novel_indicators:
            if indicator in text_lower:
                novelty += 0.15
        
        # === Length factor ===
        # Very short (<10 chars): usually simple
        if text_length < 10:
            novelty -= 0.15
        # Very long (>100 chars): usually complex
        elif text_length > 100:
            novelty += 0.15
        
        # === Question complexity ===
        # Multiple question marks or long questions = more novel
        question_count = text.count('?')
        if question_count > 1:
            novelty += 0.1
        
        # === Unique word ratio ===
        words = text_lower.split()
        if len(words) > 3:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio > 0.9:  # Many unique words = more novel
                novelty += 0.1
        
        # Clamp to 0-1 range
        return max(0.0, min(1.0, novelty))
    
    def analyze(self, text: str, baseline_text: str = None, learn: bool = False) -> Dict[str, Any]:
        """
        Analyze text for novelty.
        
        Args:
            text: The text to analyze
            baseline_text: Optional baseline for comparison
            learn: If True, add this to user baselines (for familiar queries)
        
        Returns:
            Dict with novelty_score (0-1), classification, and features
        """
        signature = self.compute_signature(text)
        novelty = self.compute_novelty(signature, len(text), text)
        signature["novelty_score"] = novelty
        
        # Get adaptive threshold based on user's patterns
        adaptive_threshold = self.get_user_novelty_threshold()
        
        # Classify based on novelty (using adaptive threshold)
        if novelty < adaptive_threshold:
            classification = "familiar"
            recommendation = "fast"
            # Learn this as a familiar pattern
            if learn:
                self.learn_user_baseline(text)
        elif novelty < adaptive_threshold + 0.25:
            classification = "moderate"
            recommendation = "localgen"  # Speech center for language tasks
        elif novelty < adaptive_threshold + 0.50:
            classification = "novel"
            recommendation = "smart"  # Local reasoning
        else:
            classification = "very_novel"
            recommendation = "cloud"  # Complex abstract reasoning
        
        signature["classification"] = classification
        signature["recommendation"] = recommendation
        signature["adaptive_threshold"] = round(adaptive_threshold, 3)
        
        return signature
    
    def compare_to_baseline(self, text: str, baseline_name: str) -> Dict[str, Any]:
        """Compare text to a stored baseline."""
        if baseline_name not in self.baseline_signatures:
            # Create baseline
            self.baseline_signatures[baseline_name] = self.compute_signature(text)
            return {
                "baseline_created": baseline_name,
                "novelty_score": 0.0,
                "deviation": 0.0
            }
        
        baseline = self.baseline_signatures[baseline_name]
        current = self.compute_signature(text)
        
        # Compute deviation from baseline
        keys = ["center_energy", "high_freq_energy", "entropy", "symmetry_score", "radial_distribution"]
        deviations = []
        for key in keys:
            if baseline[key] > 0:
                dev = abs(current[key] - baseline[key]) / baseline[key]
                deviations.append(min(dev, 1.0))
        
        avg_deviation = np.mean(deviations) if deviations else 0.0
        
        return {
            "baseline_name": baseline_name,
            "novelty_score": current["novelty_score"],
            "deviation": round(float(avg_deviation), 3),
            "is_novel": avg_deviation > 0.5
        }
    
    def learn_user_baseline(self, text: str):
        """
        Learn a baseline from a common user query.
        Call this for queries that are determined to be "familiar" after the fact.
        """
        signature = self.compute_signature(text)
        self.user_baselines.append(signature)
        
        # Keep only recent baselines
        if len(self.user_baselines) > self.max_baselines:
            self.user_baselines = self.user_baselines[-self.max_baselines:]
    
    def get_user_novelty_threshold(self) -> float:
        """
        Get adaptive novelty threshold based on user's query patterns.
        Returns a threshold where queries below are considered "familiar".
        """
        if len(self.user_baselines) < 5:
            return 0.25  # Default threshold
        
        # Calculate average novelty of user's common queries
        avg_novelty = np.mean([b["novelty_score"] for b in self.user_baselines])
        std_novelty = np.std([b["novelty_score"] for b in self.user_baselines])
        
        # Threshold = mean + 1 std (captures 84% of familiar queries)
        threshold = avg_novelty + std_novelty
        
        # Clamp to reasonable range
        return max(0.15, min(0.40, threshold))


def detect_novelty(text: str) -> Dict[str, Any]:
    """Convenience function for novelty detection."""
    detector = FFTNoveltyDetector()
    return detector.analyze(text)


# ────────────────────────────────────────────────
# Integration with RMC (Recursive Meta-Cognition)
# ────────────────────────────────────────────────

def rmc_confidence_adjustment(novelty_result: Dict[str, Any], base_confidence: float) -> float:
    """
    Adjust RMC confidence based on FFT novelty detection.
    
    High novelty → lower confidence (model may be out of distribution)
    Low novelty → higher confidence (pattern is familiar)
    """
    novelty = novelty_result.get("novelty_score", 0.5)
    
    # Adjust confidence inversely to novelty
    adjustment = (0.5 - novelty) * 0.3  # Max ±0.15 adjustment
    adjusted = base_confidence + adjustment
    
    return round(max(0.1, min(0.95, adjusted)), 3)


# ────────────────────────────────────────────────
# CLI Interface
# ────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python fft_novelty.py <text>")
        print("       python fft_novelty.py --compare <baseline_name> <text>")
        sys.exit(1)
    
    detector = FFTNoveltyDetector()
    
    if sys.argv[1] == "--compare" and len(sys.argv) >= 4:
        baseline_name = sys.argv[2]
        text = sys.argv[3]
        result = detector.compare_to_baseline(text, baseline_name)
    else:
        text = " ".join(sys.argv[1:])
        result = detector.analyze(text)
    
    print(json.dumps(result, indent=2))
