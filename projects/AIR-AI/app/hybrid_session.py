"""
hybrid_session.py
AIR-AI Oracle Hybrid Session Engine

Combines:
- FFT symbolic remote viewing (spectral analysis of queries)
- RMC (Recursive Meta-Cognition) for explainable routing
- Biorhythm/Thought matrix for character-aware responses
- Rememberence lore integration

Usage:
    from hybrid_session import HybridSessionEngine
    engine = HybridSessionEngine()
    result = engine.run_session("What lies ahead?", character_data)
"""

import numpy as np
from scipy.fft import fft2, fftshift
import random
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# Local imports
from oracle_calculations import calculate_biorhythms, generate_thoughts, roll_d20

# ────────────────────────────────────────────────
# FFT Symbolic Analysis
# ────────────────────────────────────────────────

class FFTSymbolicAnalyzer:
    """Analyze query text using FFT-based spectral methods"""
    
    def __init__(self, size=256):
        self.size = size
    
    def text_to_field(self, text: str) -> np.ndarray:
        """Convert text to 2D symbolic field"""
        field = np.zeros((self.size, self.size))
        
        # Hash text to seed
        seed = sum(ord(c) * (i + 1) for i, c in enumerate(text)) % (2**31)
        np.random.seed(seed)
        
        # Create interference pattern from text
        words = text.upper().split()
        for i, word in enumerate(words):
            angle = (i / len(words)) * 2 * np.pi
            radius = (len(word) / 20) * (self.size / 4)
            cx = self.size // 2 + int(radius * np.cos(angle))
            cy = self.size // 2 + int(radius * np.sin(angle))
            
            # Add gaussian blob for each word
            y, x = np.ogrid[:self.size, :self.size]
            mask = (x - cx)**2 + (y - cy)**2 < (len(word) * 3)**2
            field[mask] += np.random.uniform(0.5, 1.0)
        
        # Add noise layer
        noise = np.random.normal(0, 0.15, (self.size, self.size))
        field = np.clip(field + noise, 0, 1)
        
        return field
    
    def compute_features(self, field: np.ndarray) -> Dict[str, float]:
        """Extract spectral features from field"""
        fft = fft2(field)
        fft_shift = fftshift(fft)
        mag = np.abs(fft_shift)
        
        h, w = mag.shape
        cy, cx = h // 2, w // 2
        
        # Center energy (coherence)
        center = mag[cy-16:cy+16, cx-16:cx+16]
        center_energy = float(np.mean(center))
        
        # Quadrant asymmetry
        q_ul = np.mean(mag[:cy, :cx])
        q_ur = np.mean(mag[:cy, cx:])
        q_ll = np.mean(mag[cy:, :cx])
        q_lr = np.mean(mag[cy:, cx:])
        
        # Radial profile
        y, x = np.ogrid[:h, :w]
        r = np.sqrt((y - cy)**2 + (x - cx)**2) / max(h, w)
        radial = []
        for r_min, r_max in [(0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0)]:
            mask = (r >= r_min) & (r < r_max)
            radial.append(float(np.mean(mag[mask])) if np.any(mask) else 0.0)
        
        # Symmetry
        v_sym = float(np.mean(np.abs(mag[:, :cx] - mag[:, cx:][:, ::-1])))
        h_sym = float(np.mean(np.abs(mag[:cy, :] - mag[cy:, :][::-1, :])))
        
        return {
            'center_energy': center_energy,
            'quad_asymmetry': (q_ul - q_ll, q_ur - q_lr),
            'radial_profile': radial,
            'symmetry_score': (v_sym + h_sym) / 2,
            'entropy': float(self._compute_entropy(mag))
        }
    
    def _compute_entropy(self, mag: np.ndarray) -> float:
        """Compute spectral entropy"""
        p = mag.flatten() / (mag.sum() + 1e-10)
        p = p[p > 0]
        return -np.sum(p * np.log2(p))
    
    def interpret(self, features: Dict, query: str) -> str:
        """Interpret features as oracle impression"""
        impressions = []
        
        ce = features['center_energy']
        if ce > 5.0:
            impressions.append("Intense coherent core — monumental or heavily guarded.")
        elif ce > 2.5:
            impressions.append("Focused harmonic node — precise location or person dominates.")
        else:
            impressions.append("Diffuse atmospheric field — collective or environmental.")
        
        sym = features['symmetry_score']
        if sym < 0.15:
            impressions.append("Remarkable symmetry — balanced, sacred geometry.")
        elif sym > 0.4:
            impressions.append("Chaotic asymmetry — turbulent forces at play.")
        
        ent = features['entropy']
        if ent > 12:
            impressions.append("High entropy — unpredictable, volatile situation.")
        elif ent < 7:
            impressions.append("Low entropy — ordered, predictable pattern.")
        
        radial = features['radial_profile']
        if radial[0] > 1.5 * np.mean(radial[2:]):
            impressions.append("Strong low-frequency foundation — ancient or archetypal.")
        if radial[-1] > 1.3 * np.mean(radial[:-1]):
            impressions.append("High-frequency shimmer — technological or ethereal.")
        
        return "FFT impression: " + " ".join(impressions[:4])


# ────────────────────────────────────────────────
# RMC (Recursive Meta-Cognition) Engine
# ────────────────────────────────────────────────

class RMCEngine:
    """Recursive Meta-Cognition for explainable routing"""
    
    def __init__(self, confidence_threshold=0.75, max_depth=3):
        self.confidence_threshold = confidence_threshold
        self.max_depth = max_depth
    
    def decompose(self, data: Any) -> List[Dict]:
        """Break input into sub-components"""
        if isinstance(data, dict):
            return [{k: v} for k, v in data.items()]
        elif isinstance(data, list):
            return [{f"item_{i}": item} for i, item in enumerate(data)]
        return [{"input": data}]
    
    def estimate_confidence(self, result: Any, fft_features: Dict = None) -> float:
        """Estimate confidence in result"""
        score = 0.8  # Base confidence
        
        if isinstance(result, dict):
            # Penalize negative values
            if any(v < 0 for v in result.values() if isinstance(v, (int, float))):
                score -= 0.2
            # Reward completeness
            if len(result) >= 3:
                score += 0.1
        
        if fft_features:
            # Symmetry boosts confidence
            sym = fft_features.get('symmetry_score', 0.5)
            score += (0.5 - sym) * 0.3
            # High entropy penalizes
            ent = fft_features.get('entropy', 8)
            score -= (ent - 8) * 0.02
        
        return max(0.0, min(1.0, round(score, 2)))
    
    def process(self, compute_func, input_data: Any, depth=0) -> Dict:
        """Run RMC loop"""
        if depth > self.max_depth:
            return {"result": None, "confidence": 0.0, "caveats": ["Max depth exceeded"]}
        
        sub_inputs = self.decompose(input_data)
        sub_results = []
        
        for sub in sub_inputs:
            try:
                sub_res = compute_func(sub)
                conf = self.estimate_confidence(sub_res)
                sub_results.append({"result": sub_res, "confidence": conf})
            except Exception as e:
                sub_results.append({"result": None, "confidence": 0.0, "error": str(e)})
        
        # Synthesize
        valid = [r for r in sub_results if r['confidence'] > 0.3]
        if not valid:
            # Retry with refined input
            return self.process(compute_func, input_data, depth + 1)
        
        avg_conf = sum(r['confidence'] for r in valid) / len(valid)
        best_result = max(valid, key=lambda x: x['confidence'])['result']
        
        return {
            "result": best_result,
            "confidence": avg_conf,
            "sub_results": len(sub_results),
            "depth": depth
        }


# ────────────────────────────────────────────────
# Biorhythm/Thought Matrix
# ────────────────────────────────────────────────

def build_biorhythm_matrix(bios: Dict[str, int], state: float) -> np.ndarray:
    """Build 12×12 biorhythm interaction matrix"""
    bio_list = np.array([bios.get(k, 0) for k in [
        'MNF', 'SPL', 'BEU', 'STR', 'FND', 'KNO',
        'UND', 'WIS', 'VIT', 'SEX', 'DIV', 'EGO'
    ]])
    
    # Outer product creates interaction matrix
    mat = np.outer(bio_list, bio_list) / 100.0
    
    # Scale by state
    mat *= (1 + state / 50.0)
    
    return mat


def build_thought_matrix(thoughts: Dict[str, int], state: float) -> np.ndarray:
    """Build 6×6 thought interaction matrix"""
    thought_list = np.array([thoughts.get(k, 0) for k in [
        'Environment', 'Emotion', 'Subconscious',
        'Conscious', 'Abstraction', 'Perception'
    ]])
    
    mat = np.outer(thought_list, thought_list) / 100.0
    mat *= (1 + state / 50.0)
    
    return mat


def link_matrices(bio_mat: np.ndarray, thought_mat: np.ndarray) -> np.ndarray:
    """Project biorhythm matrix onto thought space"""
    # Group biorhythms into thought categories
    groups = [
        (0, 11),  # MNF, EGO → Environment
        (10, 2),  # DIV, BEU → Emotion
        (7, 6),   # WIS, UND → Subconscious (inverted)
        (0, 9),   # MNF, SEX → Conscious
        (5, 7),   # KNO, WIS → Abstraction
        (8, 3),   # VIT, STR → Perception
    ]
    
    proj = np.zeros(6)
    for i, (a, b) in enumerate(groups):
        proj[i] = (bio_mat[a] + bio_mat[b]).mean()
    
    return proj


# ────────────────────────────────────────────────
# Hybrid Session Engine
# ────────────────────────────────────────────────

class HybridSessionEngine:
    """Main hybrid session orchestrator"""
    
    def __init__(self):
        self.fft_analyzer = FFTSymbolicAnalyzer()
        self.rmc_engine = RMCEngine()
        self.lore_cache = {}
    
    def load_lore(self, lore_dir: str = None):
        """Preload lore files"""
        if lore_dir is None:
            # Try multiple paths
            lore_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'Rememberence')
            if not os.path.exists(lore_dir):
                lore_dir = r'D:\Ollama\OpenClaw\workspace\Rememberence'
            if not os.path.exists(lore_dir):
                lore_dir = r'D:\GPT4All\AIPlus\Rememberence'
        
        if not os.path.exists(lore_dir):
            print(f"Lore directory not found: {lore_dir}")
            return
        
        for root, dirs, files in os.walk(lore_dir):
            for file in files:
                if file.endswith('.txt'):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            key = os.path.relpath(path, lore_dir).replace('\\', '/')
                            self.lore_cache[key] = content[:5000]  # Truncate
                    except:
                        pass
        
        print(f"Loaded {len(self.lore_cache)} lore files")
    
    def run_session(self, query: str, character: Dict = None, 
                    flavor: str = "mystical") -> Dict[str, Any]:
        """
        Run a complete hybrid session.
        
        Args:
            query: User's question/request
            character: Character data (animal_sign, star_sign, etc.)
            flavor: Response flavor (mystical, sci-fi, clinical, quantum)
        
        Returns:
            Complete session result with FFT, RMC, matrices, and response
        """
        # 1. FFT Analysis
        fft_field = self.fft_analyzer.text_to_field(query)
        fft_features = self.fft_analyzer.compute_features(fft_field)
        fft_impression = self.fft_analyzer.interpret(fft_features, query)
        
        # 2. Character Biorhythms & Thoughts
        if character:
            animal = character.get('animal_sign', 'Human')
            star = character.get('star_sign', 'Aries')
            bios = calculate_biorhythms(animal, star)
            thoughts = generate_thoughts(bios)
            state = thoughts.get('State', 0)
        else:
            bios = {k: 0 for k in ['MNF', 'SPL', 'BEU', 'STR', 'FND', 'KNO',
                                    'UND', 'WIS', 'VIT', 'SEX', 'DIV', 'EGO']}
            thoughts = {k: 0 for k in ['Environment', 'Emotion', 'Subconscious',
                                        'Conscious', 'Abstraction', 'Perception', 'State']}
            state = 0
        
        # 3. Build Matrices
        bio_matrix = build_biorhythm_matrix(bios, state)
        thought_matrix = build_thought_matrix(thoughts, state)
        projection = link_matrices(bio_matrix, thought_matrix)
        
        # 4. RMC Processing
        def compute_response(data):
            """Generate response based on input data"""
            # Roll for oracle clarity
            roll, total, is_crit, is_fail = roll_d20(int(state / 10))
            
            # Select lore fragment if available
            lore_match = self._find_lore_match(query)
            
            # Build response
            response = self._build_response(roll, total, is_crit, is_fail, 
                                           query, fft_impression, lore_match, flavor)
            
            return {
                'response': response,
                'roll': roll,
                'total': total,
                'lore_match': lore_match
            }
        
        rmc_input = {
            'query': query,
            'character': character,
            'fft_features': fft_features,
            'state': state
        }
        
        rmc_result = self.rmc_engine.process(compute_response, rmc_input)
        
        # 5. Compile Result
        return {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'flavor': flavor,
            'fft': {
                'impression': fft_impression,
                'features': {
                    'center_energy': fft_features['center_energy'],
                    'symmetry_score': fft_features['symmetry_score'],
                    'entropy': fft_features['entropy']
                }
            },
            'matrices': {
                'biorhythm': bio_matrix.tolist(),
                'thought': thought_matrix.tolist(),
                'projection': projection.tolist()
            },
            'rmc': rmc_result,
            'character': {
                'biorhythms': bios,
                'thoughts': thoughts,
                'state': state
            }
        }
    
    def _find_lore_match(self, query: str) -> Optional[str]:
        """Find relevant lore fragment"""
        query_lower = query.lower()
        
        # Simple keyword matching (expand with embeddings later)
        keywords = {
            'species': ['species', 'creature', 'being', 'race'],
            'type': ['type', 'element', 'affinity'],
            'zodiac': ['zodiac', 'sign', 'animal', 'star'],
            'class': ['class', 'skill', 'ability'],
            'rune': ['rune', 'key', 'symbol'],
            'guardian': ['guardian', 'council', 'eternal']
        }
        
        for category, words in keywords.items():
            if any(word in query_lower for word in words):
                # Return lore file path
                for key in self.lore_cache:
                    if category in key.lower():
                        return key
        
        return None
    
    def _build_response(self, roll: int, total: int, is_crit: bool, is_fail: bool,
                       query: str, fft_impression: str, lore_match: Optional[str],
                       flavor: str) -> str:
        """Build final response"""
        
        if is_fail:
            return "The Archive trembles. The threads scream in discord. Ask again when the echoes settle."
        
        if is_crit:
            base = "✨ The Archive opens fully! The threads converge with perfect clarity: "
        elif total >= 16:
            base = "Clear vision emerges: "
        elif total >= 11:
            base = "Moderate clarity: "
        elif total >= 6:
            base = "Vague impression: "
        else:
            base = "Distant echo: "
        
        # Add FFT insight
        if flavor == "mystical":
            insight = f"The spectral field shows {fft_impression.lower()} "
        elif flavor == "sci-fi":
            insight = f"Quantum analysis indicates {fft_impression.lower()} "
        elif flavor == "clinical":
            insight = f"Pattern analysis: {fft_impression} "
        else:
            insight = ""
        
        # Add lore if found
        lore_text = ""
        if lore_match:
            lore_text = f"\n\n[Archive Reference: {lore_match}]"
        
        # Final guidance based on roll
        if total >= 16:
            guidance = "Your path is illuminated. What you seek is closer than you think."
        elif total >= 11:
            guidance = "The answer lies in what you've forgotten, not what you seek."
        elif total >= 6:
            guidance = "Patience. The answer will come in its own time."
        else:
            guidance = "The threads are tangled. Wait for clearer signs."
        
        return f"{base}{guidance} {insight}{lore_text}"


# ────────────────────────────────────────────────
# CLI Demo
# ────────────────────────────────────────────────

if __name__ == '__main__':
    print("=== AIR-AI Hybrid Session Demo ===\n")
    
    engine = HybridSessionEngine()
    engine.load_lore()
    
    # Test session
    character = {
        'animal_sign': 'Dragon',
        'star_sign': 'Scorpio',
        'species': 'Human',
        'type': 'Warrior'
    }
    
    result = engine.run_session(
        "What lies ahead on my journey?",
        character=character,
        flavor="mystical"
    )
    
    print(f"Query: {result['query']}")
    print(f"FFT: {result['fft']['impression']}")
    print(f"RMC Confidence: {result['rmc']['confidence']}")
    print(f"Response: {result['rmc']['result']['response']}")
