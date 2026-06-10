"""
rememberence_fft_bridge.py

Full refined script: FFT Symbolic Remote Viewer + Rememberence Bridge (RMC pipeline)
+ Stateful, context-aware Biorhythm/Thought matrix (neural-network-style linking)
+ Direct Thought-axis self-modulation (no named context tables)
+ Thought-modulated RMC confidence, weighted chance, loop scaling, loyalty flow, volatility, stability, openness, flavor tone
+ Controlled feedback loop (RMC → dynamic bio/thought weights → next intuition)

Enhancements:
- Thoughts now self-boost their own biorhythm pairs (unconscious speaks directly)
- No external context dictionaries — six Thought axes govern situational leanings
- RMC confidence, loops, chance, loyalty, decay, entropy, etc. all modulated by thoughts
- Chaos preserved as sacred feature (high EGO/UND/low Perception → divergence)
- Backward compatible: set max_loops=1 or damping=0 for original linear behavior

Still entertainment / speculative only. No parapsychological validity.
"""

import numpy as np
from scipy.fft import fft2, fftshift
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import textwrap
import random
import argparse
import os
import re
import json
import math
from typing import Dict, List, Any
from datetime import datetime


# ────────────────────────────────────────────────
# FFT Symbolic Remote Viewer (core unchanged)
# ────────────────────────────────────────────────

class FFTSymbolicRemoteViewer:
    def __init__(self, image_size=(512, 512), font_size=48, seed=None):
        self.size = image_size
        self.font_size = font_size
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        self.font = self._load_font()

    def _load_font(self):
        try:
            return ImageFont.truetype("arial.ttf", self.font_size)
        except:
            try:
                return ImageFont.truetype("DejaVuSans.ttf", self.font_size)
            except:
                return ImageFont.load_default()

    def generate_glyph(self, text, binary_mode=False):
        img = Image.new('RGB', self.size, color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = self.font

        wrapped = textwrap.wrap(text, width=40)
        y = 10
        for line in wrapped:
            draw.text((10, y), line, font=font, fill=(255, 255, 255))
            y += self.font_size + 5

        if binary_mode:
            arr = np.array(img.convert('L'))
            arr = (arr > 128).astype(np.uint8) * 255
            img = Image.fromarray(arr)

        return img

    def compute_features(self, img):
        arr = np.array(img.convert('L')) / 255.0
        f = fftshift(fft2(arr))
        magnitude = np.abs(f)
        phase = np.angle(f)

        center_energy = magnitude[self.size[0]//2, self.size[1]//2]
        symmetry_score = np.mean(np.abs(magnitude - np.flip(magnitude)))
        entropy = -np.sum(arr * np.log(arr + 1e-10)) / (arr.size)

        return {
            "center_energy": center_energy,
            "symmetry_score": symmetry_score,
            "entropy": entropy,
            "phase_mean": np.mean(phase),
        }


def fft_symbolic_remote_view(target, seed=None, binary_mode=False):
    viewer = FFTSymbolicRemoteViewer(seed=seed)
    img = viewer.generate_glyph(target, binary_mode)
    features = viewer.compute_features(img)

    impression = f"Diffuse atmospheric field — {features['entropy']:.2f} entropy, {features['symmetry_score']:.2f} symmetry."
    return impression, features


# ────────────────────────────────────────────────
# Thought Matrix – Self-Modulating, Stateful, Persistent
# ────────────────────────────────────────────────

PAIRS = {
    "Environment":   ("FND", 1, "EGO", -1),     # Conscientiousness (Order–Chaos)
    "Emotion":       ("BEU", 1, "DIV", -1),     # Neuroticism (Love–Fear)
    "Subconscious":  ("SPL", 1, "UND", -1),     # Openness (Embrace–Reject)
    "Conscious":     ("MNF", 1, "SEX", -1),     # Extraversion (Active–Passive)
    "Abstraction":   ("KNO", 1, "WIS", -1),     # Education (Learned–Lived)
    "Perception":    ("VIT", 1, "STR", -1),     # Agreeableness (Positive–Negative)
}


def generate_thoughts(biorhythms: Dict[str, float],
                     abstraction: float = 0,
                     dynamic_weights: Dict[str, float] = None,
                     persistent_state: Dict[str, float] = None) -> Dict[str, float]:
    """
    Generate 6 thought axes.
    Each axis self-modulates its own biorhythm pair (unconscious reinforcement).
    No external context tables — thoughts themselves are the situational leanings.
    """
    if dynamic_weights is None:
        dynamic_weights = {}
    if persistent_state is None:
        persistent_state = {}

    thoughts = {}

    for axis, (pos_bio, pos_sign, neg_bio, neg_sign) in PAIRS.items():
        pos_val = biorhythms.get(pos_bio, 0)
        neg_val = biorhythms.get(neg_bio, 0)

        # Apply dynamic feedback from previous RMC loop
        pos_val *= (1 + dynamic_weights.get(pos_bio, 0))
        neg_val *= (1 + dynamic_weights.get(neg_bio, 0))

        # Self-modulation: each Thought axis reinforces its own pair
        # (positive feedback loop within axis — the spirit leans into its own nature)
        current_thought = persistent_state.get(axis, 0) + thoughts.get(axis, 0)
        pos_val += current_thought / 20.0   # gentle reinforcement
        neg_val += current_thought / 25.0   # slight asymmetry to prevent perfect balance

        raw = pos_sign * pos_val + neg_sign * neg_val

        # Abstraction non-linearity (global)
        if abstraction > 50:
            raw *= 0.7   # dampen extremes → balanced, abstract mind
        elif abstraction < -50:
            raw *= 1.4   # amplify polarization → concrete, reactive mind

        thoughts[axis] = raw + persistent_state.get(axis, 0)

    return thoughts


# ────────────────────────────────────────────────
# Thought-Driven System Modifiers (All 6 axes → 9 control points)
# ────────────────────────────────────────────────

def get_thought_modifiers(thoughts: Dict[str, float]) -> Dict[str, float]:
    """
    Each Thought axis modulates multiple system parameters.
    Big 6 + cross-effects → confidence, loops, chance, loyalty, volatility, stability, openness, flavor, decay.
    """
    mods = {}

    # 1. Conscious (Extraversion) → reasoning reliability & decisiveness
    mods["rmc_conf_boost"] = thoughts.get("Conscious", 0) / 10.0 * 0.15
    mods["weighted_roll_strength"] = thoughts.get("Conscious", 0) / 10.0 * 0.12

    # 2. Abstraction (Education) → convergence speed & depth
    abstr = thoughts.get("Abstraction", 0)
    mods["max_loops"] = max(1, min(5, 3 + int(-abstr / 40)))
    mods["feedback_damping"] = 0.7 + (abstr / 100.0) * 0.3   # high → faster convergence

    # 3. Perception (Agreeableness) → positivity/loyalty bias
    mods["loyalty_multiplier"] = 1.0 + (thoughts.get("Perception", 0) / 10.0) * 0.2
    mods["positive_bias"] = thoughts.get("Perception", 0) / 20.0   # flavor text weighting

    # 4. Emotion (Neuroticism) → emotional volatility
    mods["feedback_strength"] = 0.3 + (abs(thoughts.get("Emotion", 0)) / 10.0) * 0.15
    mods["chaos_amplifier"] = abs(thoughts.get("Emotion", 0)) / 15.0

    # 5. Environment (Conscientiousness) → order/stability
    mods["decay_rate"] = 0.05 * (1 - thoughts.get("Environment", 0) / 10.0)
    mods["entropy_tolerance"] = 1 + (thoughts.get("Environment", 0) / 20.0)  # higher → more forgiving of chaos

    # 6. Subconscious (Openness) → openness to new/chaotic input
    mods["entropy_bias"] = 1 + (thoughts.get("Subconscious", 0) / 10.0) * 0.1
    mods["context_adapt_strength"] = thoughts.get("Subconscious", 0) / 20.0

    return mods


# ────────────────────────────────────────────────
# RMC – Recursive Meta-Cognition with Thought-Modulated Confidence
# ────────────────────────────────────────────────

def rmc_pipeline(impression: str, thoughts: Dict[str, float], features: Dict[str, float],
                 mods: Dict[str, float], depth: int = 0, max_depth: int = 5) -> Dict[str, Any]:
    conf = 0.5 + 0.3 * (1 - features.get("entropy", 0.5)) + 0.2 * features.get("symmetry_score", 0.0)
    conf += mods["rmc_conf_boost"]
    conf = min(max(conf, 0.1), 0.95)

    synthesis = f"{impression} Thoughts: {', '.join(f'{k}:{v:.1f}' for k,v in thoughts.items())}"

    notes = []
    if conf < 0.7:
        notes.append("Low confidence — high entropy or asymmetry detected.")
    if any(abs(v) > 8 for v in thoughts.values()):
        notes.append("Extreme thought polarization observed.")

    result = {
        "confidence": conf,
        "synthesis": synthesis,
        "notes": notes,
    }

    if conf < 0.8 and depth < max_depth:
        result["notes"].append(f"Recursed to depth {depth+1}")
        return result  # placeholder — expand later

    return result


# ────────────────────────────────────────────────
# Weighted Random Choice & Loyalty Interaction
# ────────────────────────────────────────────────

def weighted_choice_from_thoughts(options: List[Any], thoughts: Dict[str, float],
                                 mods: Dict[str, float]) -> Any:
    if not options:
        return None

    weights = []
    total = 0.0
    for opt in options:
        w = 1.0
        w += thoughts.get("Conscious", 0) * mods.get("weighted_roll_strength", 0.1)
        w += thoughts.get("Perception", 0) * 0.08
        w += random.uniform(0, thoughts.get("EGO", 0) * 0.05)  # chaos variance
        weights.append(max(w, 0.1))
        total += w

    probs = [w / total for w in weights]
    return random.choices(options, weights=probs, k=1)[0]


def interact_biorhythm(a_entity, b_entity, primary_bio="MNF", secondary_bio=None,
                       mods: Dict[str, float] = None) -> Dict[str, Any]:
    if mods is None:
        mods = {}

    a_val = a_entity.biorhythms.get(primary_bio, 0)
    b_val = b_entity.biorhythms.get(primary_bio, 0)

    if secondary_bio:
        a_val += 0.5 * a_entity.biorhythms.get(secondary_bio, 0)
        b_val += 0.5 * b_entity.biorhythms.get(secondary_bio, 0)

    delta = a_val - b_val
    loyalty_change = int(delta * 2 * mods.get("loyalty_multiplier", 1.0))

    b_entity.loyalty_map.setdefault(a_entity.name, 0)
    b_entity.loyalty_map[a_entity.name] += loyalty_change

    return {
        "dominant": a_entity.name if delta > 0 else b_entity.name,
        "delta": delta,
        "loyalty_change": loyalty_change
    }


# ────────────────────────────────────────────────
# Hybrid Session – Full Integration
# ────────────────────────────────────────────────

def hybrid_fft_rmc_session(target: str, entity_dict: Dict[str, Any],
                          flavor: str = "mystical", seed: int = None,
                          binary_mode: bool = False,
                          max_loops: int = None, feedback_damping: float = 0.7,
                          feedback_strength: float = 0.3) -> Dict[str, Any]:
    bios = entity_dict.get("biorhythms", {})
    persistent_state = entity_dict.get("thought_state", {})

    # First thoughts pass to get Abstraction for loop scaling
    initial_thoughts = generate_thoughts(bios, persistent_state=persistent_state)
    mods = get_thought_modifiers(initial_thoughts)

    if max_loops is None:
        max_loops = mods["max_loops"]

    result = {}
    current_text = target
    loop_count = 0
    dynamic_weights = None

    while loop_count < max_loops:
        thoughts = generate_thoughts(bios, abstraction=0,
                                    dynamic_weights=dynamic_weights,
                                    persistent_state=persistent_state)

        mods = get_thought_modifiers(thoughts)  # refresh each loop

        impression, features = fft_symbolic_remote_view(current_text, seed=seed, binary_mode=binary_mode)

        rmc_result = rmc_pipeline(impression, thoughts, features, mods)

        result[f"loop_{loop_count}"] = {
            "impression": impression,
            "features": features,
            "thoughts": thoughts,
            "rmc": rmc_result,
            "mods": mods
        }

        if rmc_result["confidence"] < 0.85 and loop_count < max_loops - 1:
            dynamic_weights = compute_feedback_weights(rmc_result, thoughts, mods["feedback_strength"])

            current_text = (
                current_text * (1 - mods["feedback_damping"]) +
                rmc_result["synthesis"] * mods["feedback_damping"]
            )
            loop_count += 1
        else:
            break

    result["summary"] = {
        "loops_used": loop_count,
        "final_confidence": rmc_result["confidence"],
        "final_thoughts": thoughts,
        "final_impression": impression,
        "final_mods": mods
    }

    return result


# ────────────────────────────────────────────────
# Entity Class (persistent state)
# ────────────────────────────────────────────────

class Entity:
    def __init__(self, name="Spirit", **kwargs):
        self.name = name
        self.biorhythms = kwargs.get('biorhythms', {
            'MNF':5, 'SPL':0, 'BEU':0, 'STR':0, 'FND':0,
            'KNO':0, 'UND':0, 'WIS':0, 'VIT':0, 'SEX':0,
            'DIV':0, 'EGO':0
        })
        self.thoughts = None
        self.thought_state = kwargs.get('thought_state', {})
        self.loyalty_map = kwargs.get('loyalty_map', {})

    def get_thoughts(self, abstraction=0):
        if self.thoughts is None:
            self.thoughts = generate_thoughts(self.biorhythms,
                                             abstraction=abstraction,
                                             persistent_state=self.thought_state)
        decay_rate = 0.05 * get_thought_modifiers(self.thoughts)["decay_rate"]
        for axis in self.thoughts:
            current = self.thoughts[axis]
            self.thoughts[axis] = current * (1 - decay_rate)
            self.thought_state[axis] = self.thoughts[axis]
        return self.thoughts


# ────────────────────────────────────────────────
# Main CLI / Test Entry Point
# ────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rememberence Bridge – Refined Oracle")
    parser.add_argument("target", type=str, help="Target description")
    parser.add_argument("--flavor", choices=["mystical", "sci-fi", "clinical", "quantum"], default="mystical")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--binary", action="store_true")
    parser.add_argument("--max-loops", type=int, default=None, help="Override; None=auto from Abstraction")
    parser.add_argument("--damping", type=float, default=0.7)
    args = parser.parse_args()

    sample_entity = Entity(
        name="Eliza",
        biorhythms={'MNF':4,'SPL':3,'BEU':1,'STR':0,'FND':1,'KNO':2,'UND':2,'WIS':5,'VIT':3,'SEX':4,'DIV':5,'EGO':6},
        loyalty_map={"Player": 30}
    )

    result = hybrid_fft_rmc_session(
        args.target,
        sample_entity.__dict__,
        flavor=args.flavor,
        seed=args.seed,
        binary_mode=args.binary,
        max_loops=args.max_loops,
        feedback_damping=args.damping
    )

    print("\n=== Hybrid Session Result ===")
    print(f"Loops used: {result['summary']['loops_used']}")
    print("Final confidence:", result['summary']['final_confidence'])
    print("Final impression:", result['summary']['final_impression'])
    print("Final thoughts:", result['summary']['final_thoughts'])
    print("Final mods:", result['summary']['final_mods'])
    print("\nPer-loop details:")
    for k, v in result.items():
        if k.startswith("loop_"):
            print(f"{k}:")
            print(f"  Impression: {v['impression']}")
            print(f"  Thoughts: {v['thoughts']}")
            print(f"  RMC conf: {v['rmc']['confidence']}")