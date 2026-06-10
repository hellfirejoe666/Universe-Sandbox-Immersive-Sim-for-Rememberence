#!/usr/bin/env python3
"""
Hybrid Router v2 - With Token Optimization and RMC Meta-Cognition

Integrates:
1. AIML pattern matching (FAST path, zero tokens)
2. FFT novelty detection (spectral analysis)
3. Token optimization (compression, semantic cache, auto-learning)
4. LLM classification (hybrid-router model)
5. Response caching
6. Cloud escape hatch (qwen3.5:cloud)
7. RMC meta-cognition (explainable routing, confidence calibration)

Makes routing decisions using all signals together while minimizing token usage.
"""

import sys
import json
import subprocess
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Import modules
sys.path.insert(0, str(Path(__file__).parent))
from fft_novelty import FFTNoveltyDetector, rmc_confidence_adjustment
from token_optimizer import TokenOptimizer
from localgen_provider import LocalGenProvider
from rmc_meta_cognition import RMC_META_COGNITION

ROUTER_MODEL = "hybrid-router"
SMART_MODEL = "qwen2.5:7b"
CLOUD_MODEL = "qwen3.5:cloud"
LOCALGEN_GENERATOR = "ai-character-chat"  # Default generator

# Aggressive cloud avoidance thresholds
FAST_THRESHOLD = 0.35   # Lower = more queries to fast path
CLOUD_THRESHOLD = 0.90  # Higher = only very novel queries to cloud

WORKSPACE = Path("D:/Ollama/OpenClaw/workspace")
ROUTER_DIR = WORKSPACE / "hybrid-router"


class HybridRouterV2:
    """
    Enhanced router with token optimization and LocalGen integration.
    
    Routing paths:
    1. FAST - Pattern/cache (0 tokens, instant)
    2. SMART - Local LLM qwen2.5:7b (~150 tokens, 5-30s)
    3. LOCALGEN - Self-hosted AI (0 cost, unlimited, 5-15s)
    4. CLOUD - qwen3.5:cloud (~500 tokens, rate limited)
    
    Routing pipeline:
    1. Compress query (remove filler, normalize)
    2. Check semantic cache (fuzzy match)
    3. Check pattern cache (exact match)
    4. FFT novelty analysis
    5. LLM classification (with compressed query)
    6. RMC meta-cognition evaluation
    7. Route with confidence adjustment
    8. Learn from results
    """
    
    def __init__(self):
        self.fft_detector = FFTNoveltyDetector(image_size=(64, 64))
        self.token_optimizer = TokenOptimizer()
        self.localgen = LocalGenProvider()
        self.rmc = RMC_META_COGNITION()  # Meta-cognition layer
        self.stats = {"fast": 0, "smart": 0, "localgen": 0, "cloud": 0, "cached": 0, "total": 0}

    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def get_llm_classification(self, text: str) -> Dict[str, Any]:
        """Get LLM-based classification with timeout protection."""
        # Use compressed text for classification
        compressed = self.token_optimizer.compressor.compress(text)
        prompt = f"Route: {compressed[:100]}"

        try:
            result = subprocess.run(
                ["ollama", "run", ROUTER_MODEL, prompt],
                capture_output=True,
                text=True,
                timeout=15,
                encoding='utf-8',
                errors='ignore'
            )

            json_match = re.search(r'\{[^}]+\}', result.stdout, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass

        return {"path": "smart", "confidence": 0.5, "reason": "default"}

    def route(self, text: str, use_fft: bool = True, use_optimization: bool = True, use_rmc: bool = True) -> Dict[str, Any]:
        """
        Route a request with full token optimization and meta-cognition.

        Returns routing decision with response, metadata, and RMC explanation.
        """
        self.stats["total"] += 1
        start = datetime.now()

        # Step 1: Token optimization (compression + cache check)
        optimization_meta = {}
        if use_optimization:
            optimized_query, opt_meta = self.token_optimizer.optimize_query(text)
            optimization_meta = opt_meta

            # Cache hit? Return immediately
            if opt_meta.get("cache_hit"):
                self.stats["cached"] += 1
                self.token_optimizer.record_cache_hit(opt_meta.get('tokens_saved', 100))
                return {
                    "path": "cached",
                    "source": "semantic_cache",
                    "response": opt_meta["cached_response"],
                    "latency_ms": 0,
                    "tokens_saved": opt_meta.get('tokens_saved', 100),
                    "optimization": opt_meta
                }

            # Use optimized query for rest of pipeline
            query_to_use = optimized_query
        else:
            query_to_use = text

        # Step 2: Pattern match (FAST path, zero tokens)
        pattern_response = self.token_optimizer.pattern_learner.patterns.get(query_to_use.upper().strip())
        if pattern_response:
            self.stats["fast"] += 1
            self.token_optimizer.accountant.record_request("fast", 0)
            return {
                "path": "fast",
                "source": "pattern",
                "response": pattern_response,
                "latency_ms": 0,
                "tokens_saved": 100,  # Would have used LLM
                "optimization": optimization_meta
            }

        # Step 3: FFT novelty analysis
        fft_result = None
        if use_fft:
            fft_result = self.fft_detector.analyze(query_to_use)

        # Step 4: LLM classification
        llm_class = self.get_llm_classification(query_to_use)

        # Step 5: Decision logic with RMC confidence adjustment
        path = "smart"  # Default
        
        if fft_result and llm_class:
            novelty = fft_result["novelty_score"]
            llm_conf = llm_class.get("confidence", 0.5)
            llm_path = llm_class.get("path", "smart")
            
            # Adjust confidence based on FFT novelty
            adjusted_conf = rmc_confidence_adjustment(fft_result, llm_conf)
            
            # Check if LocalGen is suitable (creative, conversational, high novelty but not complex)
            is_creative = self.localgen.is_suitable_for(text, novelty) and self.localgen.available
            
            # Decision matrix with aggressive cloud avoidance and LocalGen integration
            if novelty < FAST_THRESHOLD and llm_path == "fast" and adjusted_conf > 0.7:
                path = "fast"
            elif is_creative and 0.5 < novelty < 0.85 and self.localgen.available:
                path = "localgen"  # Creative tasks → LocalGen (free, unlimited, localhost)
            elif novelty > CLOUD_THRESHOLD:
                path = "cloud"  # Very novel (>0.90) → cloud
            elif llm_path == "cloud" and adjusted_conf > 0.95:
                path = "cloud"  # Only with very high confidence
            else:
                path = "smart"  # Default to local model

        # Step 5b: RMC Meta-Cognition - Evaluate decision BEFORE execution
        rmc_evaluation = None
        if use_rmc and fft_result:
            rmc_evaluation = self.rmc.evaluate_decision(
                query=text,
                novelty_result=fft_result,
                llm_classification=llm_class or {},
                final_path=path,
                latency_ms=0,  # Will be updated
                tokens_used=0  # Will be updated
            )

        # Step 6: Execute routing
        tokens_used = 0
        response = None
        latency_ms = 0
        
        if path == "localgen":
            # Use LocalGen for creative/conversational tasks (free, unlimited, localhost)
            try:
                localgen_result = self.localgen.generate(query_to_use, generator=LOCALGEN_GENERATOR)
                
                if localgen_result.get("error"):
                    # Fallback to smart if LocalGen fails
                    path = "smart"
                else:
                    response = localgen_result["response"]
                    latency_ms = localgen_result.get("latency_ms", 0)
                    
                    self.stats["localgen"] += 1
                    self.token_optimizer.accountant.record_request("localgen", 0)
                    self.token_optimizer.record_response(text, response, "localgen", 0)
                    
                    # Update RMC with actual metrics
                    if rmc_evaluation:
                        rmc_evaluation["decision"]["latency_ms"] = latency_ms
                        rmc_evaluation["decision"]["tokens_used"] = 0
                    
                    return {
                        "path": "localgen",
                        "response": response,
                        "latency_ms": latency_ms,
                        "tokens_used": 0,  # Local = free!
                        "generator": localgen_result.get("generator", LOCALGEN_GENERATOR),
                        "fft": fft_result,
                        "llm": llm_class,
                        "rmc": rmc_evaluation,
                        "optimization": optimization_meta
                    }
            except Exception as e:
                path = "smart"
            
            if path == "smart":
                self.stats["smart"] += 1
        
        if path == "fast":
            self.stats["fast"] += 1
            response = "[No pattern yet - will be learned from response]"
            self.token_optimizer.accountant.record_request("fast", 0)

        elif path == "smart":
            try:
                result = subprocess.run(
                    ["ollama", "run", SMART_MODEL, query_to_use],
                    capture_output=True,
                    text=True,
                    timeout=90,
                    encoding='utf-8',
                    errors='ignore'
                )

                response = result.stdout.strip()
                tokens_used = self.token_optimizer.accountant.estimate_tokens(query_to_use) + \
                             self.token_optimizer.accountant.estimate_tokens(response)
                latency_ms = (datetime.now() - start).total_seconds() * 1000

                self.token_optimizer.record_response(text, response, "smart", tokens_used)
                self.stats["smart"] += 1
                
                # Update RMC with actual metrics
                if rmc_evaluation:
                    rmc_evaluation["decision"]["latency_ms"] = latency_ms
                    rmc_evaluation["decision"]["tokens_used"] = tokens_used
                
                return {
                    "path": "smart",
                    "response": response,
                    "latency_ms": latency_ms,
                    "tokens_used": tokens_used,
                    "fft": fft_result,
                    "llm": llm_class,
                    "rmc": rmc_evaluation,
                    "optimization": optimization_meta
                }
            except subprocess.TimeoutExpired:
                return {
                    "path": "smart",
                    "response": "[TIMEOUT]",
                    "latency_ms": 90000,
                    "error": "Timeout"
                }

        else:  # cloud
            try:
                result = subprocess.run(
                    ["ollama", "run", CLOUD_MODEL, query_to_use],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    encoding='utf-8',
                    errors='ignore'
                )

                response = result.stdout.strip()
                tokens_used = self.token_optimizer.accountant.estimate_tokens(query_to_use) + \
                             self.token_optimizer.accountant.estimate_tokens(response)
                latency_ms = (datetime.now() - start).total_seconds() * 1000

                self.stats["cloud"] += 1
                self.token_optimizer.accountant.record_request("cloud", tokens_used)
                
                # Update RMC with actual metrics
                if rmc_evaluation:
                    rmc_evaluation["decision"]["latency_ms"] = latency_ms
                    rmc_evaluation["decision"]["tokens_used"] = tokens_used

                return {
                    "path": "cloud",
                    "response": response,
                    "latency_ms": latency_ms,
                    "tokens_used": tokens_used,
                    "fft": fft_result,
                    "llm": llm_class,
                    "rmc": rmc_evaluation,
                    "optimization": optimization_meta
                }
            except:
                return {
                    "path": "cloud",
                    "response": "[CLOUD UNAVAILABLE]",
                    "error": "Cloud model unavailable"
                }

        # Final step: Learn from fast path classification
        if path == "fast" and response:
            learned = self.token_optimizer.pattern_learner.learn(text, response)
            latency_ms = (datetime.now() - start).total_seconds() * 1000
            
            if rmc_evaluation:
                rmc_evaluation["decision"]["latency_ms"] = latency_ms
            
            return {
                "path": "fast",
                "source": "classification",
                "response": response,
                "latency_ms": latency_ms,
                "pattern_learned": learned,
                "fft": fft_result,
                "llm": llm_class,
                "rmc": rmc_evaluation,
                "optimization": optimization_meta
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive routing and optimization stats."""
        total = self.stats["total"] or 1
        token_stats = self.token_optimizer.get_full_stats()
        localgen_stats = self.localgen.get_stats()
        rmc_insights = self.rmc.get_routing_insights()

        return {
            "routing": {
                **self.stats,
                "fast_pct": round(self.stats["fast"] / total * 100, 1),
                "smart_pct": round(self.stats["smart"] / total * 100, 1),
                "localgen_pct": round(self.stats["localgen"] / total * 100, 1),
                "cloud_pct": round(self.stats["cloud"] / total * 100, 1),
                "cached_pct": round(self.stats["cached"] / total * 100, 1),
            },
            "optimization": token_stats,
            "localgen": localgen_stats,
            "rmc": rmc_insights
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python router_v2.py <command> [args]")
        print("Commands: route, stats, fft, compress, learn, rmc")
        sys.exit(1)

    router = HybridRouterV2()
    cmd = sys.argv[1].lower()

    if cmd == "route":
        text = " ".join(sys.argv[2:])
        result = router.route(text)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif cmd == "stats":
        stats = router.get_stats()
        print(json.dumps(stats, indent=2))

    elif cmd == "fft":
        text = " ".join(sys.argv[2:])
        result = router.fft_detector.analyze(text)
        print(json.dumps(result, indent=2))

    elif cmd == "compress":
        text = " ".join(sys.argv[2:])
        optimized, meta = router.token_optimizer.optimize_query(text)
        print(f"Original:  {text}")
        print(f"Compressed: {optimized}")
        print(f"Saved: ~{meta.get('compression_savings', 0)} tokens")

    elif cmd == "learn":
        if len(sys.argv) < 4:
            print("Usage: learn <pattern> <response>")
            sys.exit(1)
        router.token_optimizer.pattern_learner.learn(sys.argv[2], sys.argv[3])
        print(f"Learned: {sys.argv[2]} → {sys.argv[3][:50]}...")

    elif cmd == "rmc":
        subcmd = sys.argv[2] if len(sys.argv) > 2 else "insights"
        if subcmd == "insights":
            insights = router.rmc.get_routing_insights()
            print(json.dumps(insights, indent=2))
        elif subcmd == "history":
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            history = router.rmc.get_decision_history(limit)
            print(json.dumps(history, indent=2))
        elif subcmd == "explain":
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
            explanations = router.rmc.explain_recent_decisions(limit)
            for exp in explanations:
                print(exp)
                print("-" * 60)
        else:
            print(f"Unknown RMC command: {subcmd}")

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
