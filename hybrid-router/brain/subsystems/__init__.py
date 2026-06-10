"""
Neural Router Subsystems

Each subsystem simulates a brain region with specialized function.
"""

from .executive import ExecutiveSystem
from .arousal import ArousalSystem
from .attention import AttentionSystem
from .memory import MemorySystem
from .habits import HabitSystem
from .language import LanguageSystem
from .reasoning import ReasoningSystem
from .salience import SalienceSystem
from .quality import QualitySystem
from .default_mode import DefaultModeNetwork

__all__ = [
    'ExecutiveSystem',
    'ArousalSystem',
    'AttentionSystem',
    'MemorySystem',
    'HabitSystem',
    'LanguageSystem',
    'ReasoningSystem',
    'SalienceSystem',
    'QualitySystem',
    'DefaultModeNetwork'
]
