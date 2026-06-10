#!/usr/bin/env python3
"""
OpenClaw Hybrid Router Tool

Provides a simple interface for OpenClaw to route requests through
FAST (patterns), SMART (local LLM), or CLOUD (cloud LLM) paths.

Usage:
    python openclaw_router.py route "query text"
    python openclaw_router.py learn "pattern" "response"
    python openclaw_router.py stats
    python openclaw_router.py classify "query text"
"""

import sys
import json
import subprocess
from pathlib import Path

ROUTER_SCRIPT = Path(__file__).parent / "router.py"

def run_router(args: list) -> dict:
    """Run the router script and parse output."""
    cmd = [sys.executable, str(ROUTER_SCRIPT)] + args
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            encoding='utf-8'
        )
        
        output = result.stdout.strip()
        
        # Parse [PATH] (XXXms, cached=X) line
        import re
        header_match = re.match(r'\[(\w+)\]\s+\((\d+)ms,\s+cached=(\w+)\)', output)
        
        if header_match:
            path = header_match.group(1)
            latency = int(header_match.group(2))
            cached = header_match.group(3) == 'True'
            response = output[header_match.end():].strip()
            
            return {
                "success": True,
                "path": path.lower(),
                "latency_ms": latency,
                "cached": cached,
                "response": response
            }
        else:
            # Stats or other output
            return {
                "success": True,
                "output": output
            }
            
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def route(query: str, force: str = None) -> dict:
    """Route a query through the hybrid router."""
    args = [query]
    if force:
        args.extend(["--force", force])
    return run_router(args)


def learn(pattern: str, response: str) -> dict:
    """Learn a new pattern."""
    args = ["--learn", pattern, response]
    result = run_router(args)
    if result["success"]:
        return {"success": True, "message": f"Learned pattern: {pattern}"}
    return result


def stats() -> dict:
    """Get routing statistics."""
    return run_router(["--stats"])


def classify(query: str) -> dict:
    """Just classify a query without executing."""
    # Use the router model directly
    from subprocess import run
    
    try:
        result = run(
            ["ollama", "run", "hybrid-router", f"Classify: {query}"],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8'
        )
        
        import re
        json_match = re.search(r'\{[^}]+\}', result.stdout, re.DOTALL)
        if json_match:
            classification = json.loads(json_match.group())
            return {"success": True, **classification}
        
        return {"success": False, "error": "Could not parse classification"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    if len(sys.argv) < 2:
        print("Usage: python openclaw_router.py <command> [args]")
        print("Commands: route, learn, stats, classify")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "route":
        if len(sys.argv) < 3:
            print("Usage: route <query> [--force path]")
            sys.exit(1)
        query = sys.argv[2]
        force = sys.argv[3] if len(sys.argv) > 3 else None
        result = route(query, force)
        
    elif command == "learn":
        if len(sys.argv) < 4:
            print("Usage: learn <pattern> <response>")
            sys.exit(1)
        result = learn(sys.argv[2], sys.argv[3])
        
    elif command == "stats":
        result = stats()
        
    elif command == "classify":
        if len(sys.argv) < 3:
            print("Usage: classify <query>")
            sys.exit(1)
        result = classify(sys.argv[2])
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
    
    # Output as JSON for OpenClaw
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
