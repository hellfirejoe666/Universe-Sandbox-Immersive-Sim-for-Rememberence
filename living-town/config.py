"""
Configuration with Auto-Detection for Older Machines

Optimizes settings based on available hardware.
Conservative defaults for older systems.
"""

import os
import multiprocessing
from pathlib import Path
from typing import Dict, Any


class SystemDetector:
    """Detects system capabilities for optimization."""
    
    @staticmethod
    def get_cpu_cores() -> int:
        """Get available CPU cores (conservative estimate)."""
        logical = multiprocessing.cpu_count()
        physical = logical // 2 if logical > 2 else logical
        
        # Use physical cores, cap at 4 for older machines
        return min(physical, 4)
    
    @staticmethod
    def get_memory_gb() -> float:
        """Estimate available memory (conservative)."""
        try:
            # Windows
            if os.name == 'nt':
                import ctypes
                kernel32 = ctypes.windll.kernel32
                c_ulonglong = ctypes.c_ulonglong
                
                class MEMORYSTATUS(ctypes.Structure):
                    _fields_ = [
                        ('dwLength', ctypes.c_ulong),
                        ('dwMemoryLoad', ctypes.c_ulong),
                        ('ullTotalPhys', c_ulonglong),
                        ('ullAvailPhys', c_ulonglong),
                    ]
                
                memory = MEMORYSTATUS()
                memory.dwLength = ctypes.sizeof(MEMORYSTATUS)
                kernel32.GlobalMemoryStatusEx(ctypes.byref(memory))
                
                return memory.ullTotalPhys / (1024 ** 3)
        except:
            pass
        
        # Fallback: assume 4GB for older machines
        return 4.0
    
    @staticmethod
    def get_optimization_profile() -> str:
        """Determine optimization profile based on hardware."""
        cores = SystemDetector.get_cpu_cores()
        memory = SystemDetector.get_memory_gb()
        
        if cores >= 4 and memory >= 8:
            return "standard"
        elif cores >= 2 and memory >= 4:
            return "conservative"
        else:
            return "minimal"


# ────────────────────────────────────────────────
# Configuration Profiles
# ────────────────────────────────────────────────

CONFIG_PROFILES = {
    "minimal": {
        "description": "For very old machines (2 cores, <4GB RAM)",
        "max_parallel_tasks": 1,  # No parallelization
        "cache_size_mb": 64,
        "batch_save_size": 50,  # Save every 50 entities
        "async_saves": False,  # Synchronous to avoid overhead
        "ai_call_batch_size": 1,  # No batching
        "max_active_layers": 1,  # Only one layer active at a time
        "aggressive_caching": True,
        "update_interval_multiplier": 2.0,  # Slower updates
    },
    
    "conservative": {
        "description": "For older machines (2-4 cores, 4-8GB RAM)",
        "max_parallel_tasks": 2,  # Light parallelization
        "cache_size_mb": 128,
        "batch_save_size": 100,
        "async_saves": True,
        "ai_call_batch_size": 2,
        "max_active_layers": 2,
        "aggressive_caching": True,
        "update_interval_multiplier": 1.0,  # Normal speed
    },
    
    "standard": {
        "description": "For modern machines (4+ cores, 8+GB RAM)",
        "max_parallel_tasks": 4,
        "cache_size_mb": 256,
        "batch_save_size": 200,
        "async_saves": True,
        "ai_call_batch_size": 5,
        "max_active_layers": 3,
        "aggressive_caching": False,
        "update_interval_multiplier": 0.5,  # Faster updates
    }
}


# ────────────────────────────────────────────────
# Global Configuration
# ────────────────────────────────────────────────

class Config:
    """Global configuration with auto-detection."""
    
    def __init__(self):
        self.profile_name = SystemDetector.get_optimization_profile()
        self.profile = CONFIG_PROFILES[self.profile_name]
        self.system_info = {
            'cpu_cores': SystemDetector.get_cpu_cores(),
            'memory_gb': SystemDetector.get_memory_gb(),
            'profile': self.profile_name
        }
        
        # Time-scale separation settings
        self.timescales = {
            'npc_days': 1,      # NPCs update daily
            'faction_weeks': 7, # Factions update weekly
            'world_months': 30, # Worlds update monthly
            'system_years': 365, # Systems update yearly
            'galaxy_decades': 3650, # Galaxies update decadal
        }
        
        # Apply multiplier for older machines
        multiplier = self.profile.get('update_interval_multiplier', 1.0)
        for key in self.timescales:
            self.timescales[key] = int(self.timescales[key] * multiplier)
    
    def get_setting(self, key: str) -> Any:
        """Get configuration setting."""
        return self.profile.get(key)
    
    def get_timescale(self, layer: str) -> int:
        """Get update interval for layer."""
        return self.timescales.get(layer, 1)
    
    def should_parallelize(self, task_count: int) -> bool:
        """Determine if task should be parallelized."""
        max_parallel = self.profile.get('max_parallel_tasks', 1)
        return task_count > 10 and max_parallel > 1
    
    def get_parallel_count(self, task_count: int) -> int:
        """Get number of parallel workers to use."""
        max_parallel = self.profile.get('max_parallel_tasks', 1)
        return min(max_parallel, task_count)
    
    def print_info(self):
        """Print configuration info."""
        print("=" * 60)
        print("SYSTEM CONFIGURATION")
        print("=" * 60)
        print(f"CPU Cores: {self.system_info['cpu_cores']}")
        print(f"Memory: {self.system_info['memory_gb']:.1f} GB")
        print(f"Profile: {self.system_info['profile']}")
        print(f"\n{self.profile['description']}")
        print(f"\nSettings:")
        print(f"  Parallel Tasks: {self.profile['max_parallel_tasks']}")
        print(f"  Cache Size: {self.profile['cache_size_mb']} MB")
        print(f"  Batch Save: every {self.profile['batch_save_size']} entities")
        print(f"  Async Saves: {self.profile['async_saves']}")
        print(f"  AI Batch Size: {self.profile['ai_call_batch_size']}")
        print(f"  Max Active Layers: {self.profile['max_active_layers']}")
        print(f"  Aggressive Caching: {self.profile['aggressive_caching']}")
        print("=" * 60)


# Global config instance
config = Config()
