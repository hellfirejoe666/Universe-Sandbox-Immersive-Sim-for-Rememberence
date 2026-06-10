"""
Layer 0: AIR-AI + UI Framework

AIR-AI uses Hybrid Router for on-demand narrative generation.
Procedural layers (1-6) handle all simulation math/stats.
AI only generates flavor text when player examines something.

Design Philosophy:
- Lazy AI evaluation (only when player looks/interacts)
- Procedural layers run continuously (fast, no AI)
- AI adds narrative layer to pre-computed data
- UI provides Rimworld-style interface
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'hybrid-router'))

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

# Import Hybrid Router
try:
    from brain.neural_router import NeuralRouter
    ROUTER_AVAILABLE = True
except ImportError:
    ROUTER_AVAILABLE = False
    print("[Layer 0] Warning: Hybrid Router not available, using fallback")


# ────────────────────────────────────────────────
# UI Components (Rimworld-Style)
# ────────────────────────────────────────────────

class UIPanel(Enum):
    """UI panel types."""
    INSPECTOR = "Inspector"      # Examine entity/object
    EVENT_LOG = "Event Log"      # Story feed
    FACTION_STATUS = "Factions"  # Faction overview
    WORLD_MAP = "World Map"      # Cosmic/local view
    NPC_LIST = "NPCs"           # Entity roster
    INVENTORY = "Inventory"     # Items/resources


@dataclass
class UIState:
    """Current UI state."""
    active_panel: UIPanel = UIPanel.EVENT_LOG
    selected_entity_id: Optional[str] = None
    selected_faction_id: Optional[str] = None
    selected_system_id: Optional[str] = None
    zoom_level: str = "local"  # local, world, system, galaxy
    paused: bool = False
    speed: int = 1  # 0=paused, 1=normal, 2=fast, 3=max


# ────────────────────────────────────────────────
# AIR-AI Orchestrator
# ────────────────────────────────────────────────

class AIRAIOrchestrator:
    """
    AIR-AI uses Hybrid Router for on-demand narrative.
    
    Key principle: AI only generates text when player examines something.
    Procedural simulation runs independently (fast, no AI calls).
    
    Usage:
    1. Simulation runs (layers 1-6, no AI)
    2. Player examines entity (clicks on NPC, faction, etc.)
    3. AIR-AI fetches pre-computed data from layers
    4. Hybrid Router generates narrative description
    5. UI displays rich text to player
    """
    
    # Narrative templates (fallback if router unavailable)
    NARRATIVE_TEMPLATES = {
        'npc': "{name} is a {animal_sign}/{star_sign} with {bio_summary}.",
        'faction': "{name} is a {structure} focused on {ideology}.",
        'town': "{name} is a {size} settlement with {population} residents.",
        'system': "{name} is a {star_type} system with {worlds} worlds.",
        'event': "In week {week}, {faction} {action}.",
    }
    
    def __init__(self):
        self.router = None
        self.initialized = False
        
        if ROUTER_AVAILABLE:
            try:
                self.router = NeuralRouter()
                self.initialized = True
                print("[Layer 0] AIR-AI: Hybrid Router initialized")
            except Exception as e:
                print(f"[Layer 0] AIR-AI: Router init failed - {e}")
    
    def generate_narrative(self, context_type: str, 
                          data: Dict[str, Any],
                          prompt_override: str = None) -> str:
        """
        Generate narrative description for player.
        
        Args:
            context_type: Type of entity (npc, faction, town, system, event)
            data: Pre-computed data from procedural layers
            prompt_override: Custom prompt if needed
        
        Returns:
            Narrative text for UI display
        """
        # Build prompt from data
        if prompt_override:
            prompt = prompt_override
        else:
            prompt = self._build_prompt(context_type, data)
        
        # Try Hybrid Router
        if self.initialized and self.router:
            try:
                # Use router.route() method
                result = self.router.route(prompt)
                return result.get('response', {}).get('content', self._fallback_narrative(context_type, data))
            except Exception as e:
                print(f"[Layer 0] AIR-AI: Router error - {e}")
                return self._fallback_narrative(context_type, data)
        
        # Fallback to templates
        return self._fallback_narrative(context_type, data)
    
    def _build_prompt(self, context_type: str, data: Dict) -> str:
        """Build AI prompt from procedural data."""
        prompts = {
            'npc': f"Describe this NPC in 2-3 engaging sentences: {data.get('name', 'Unknown')}, "
                   f"{data.get('animal_sign', '')}/{data.get('star_sign', '')}, "
                   f"biorhythms: KNO={data.get('kno', 10)}, WIS={data.get('wis', 10)}, "
                   f"STR={data.get('str', 10)}. Current mood: {data.get('mood', 'neutral')}.",
            
            'faction': f"Describe this faction in 2-3 engaging sentences: {data.get('name', 'Unknown')}, "
                       f"a {data.get('structure', 'collective')} with ideology: '{data.get('ideology', 'unknown')}'. "
                       f"Currently pursuing: {data.get('current_action', 'unknown plans')}.",
            
            'town': f"Describe this town in 2-3 engaging sentences: {data.get('name', 'Unknown')}, "
                    f"population {data.get('population', 0)}, located in {data.get('region', 'unknown')}. "
                    f"Notable features: {data.get('features', 'none')}.",
            
            'system': f"Describe this star system in 2-3 engaging sentences: {data.get('name', 'Unknown')}, "
                      f"a {data.get('star_type', 'unknown')} system with {data.get('worlds', 0)} worlds. "
                      f"Resources: {data.get('resources', 'unknown')}.",
            
            'event': f"Describe this event in 1-2 engaging sentences: Week {data.get('week', '?')}, "
                     f"{data.get('faction', 'Unknown')} {data.get('action', 'did something')}. "
                     f"Outcome: {'success' if data.get('success') else 'failure'}.",
        }
        
        return prompts.get(context_type, f"Describe: {data}")
    
    def _fallback_narrative(self, context_type: str, data: Dict) -> str:
        """Fallback narrative using templates."""
        templates = {
            'npc': f"{data.get('name', 'Unknown')} is a {data.get('animal_sign', '')}/{data.get('star_sign', '')} "
                   f"with distinctive biorhythms.",
            'faction': f"{data.get('name', 'Unknown')} is a {data.get('structure', 'group')} "
                       f"focused on their goals.",
            'town': f"{data.get('name', 'Unknown')} is a settlement with "
                    f"{data.get('population', 0)} residents.",
            'system': f"{data.get('name', 'Unknown')} is a star system "
                      f"with {data.get('worlds', 0)} worlds.",
            'event': f"In week {data.get('week', '?')}, {data.get('faction', 'Unknown')} "
                     f"{data.get('action', 'acted')}.",
        }
        
        return templates.get(context_type, str(data))
    
    def batch_generate(self, items: List[Dict]) -> List[str]:
        """
        Generate narratives for multiple items.
        
        Use sparingly - each call is expensive.
        Better to generate on-demand as player scrolls.
        """
        results = []
        for item in items:
            narrative = self.generate_narrative(
                item.get('type', 'unknown'),
                item.get('data', {})
            )
            results.append(narrative)
        return results


# ────────────────────────────────────────────────
# UI Manager
# ────────────────────────────────────────────────

class UIManager:
    """
    Manages UI panels and player interaction.
    
    Rimworld-style interface:
    - Inspector panel (examine entities)
    - Event log (story feed)
    - Status panels (factions, NPCs, worlds)
    """
    
    def __init__(self, airai: AIRAIOrchestrator = None):
        self.state = UIState()
        self.airai = airai or AIRAIOrchestrator()
        self.event_log: List[Dict] = []
    
    def set_active_panel(self, panel: UIPanel):
        """Switch active UI panel."""
        self.state.active_panel = panel
    
    def select_entity(self, entity_id: str, entity_type: str):
        """Select entity for inspection."""
        self.state.selected_entity_id = entity_id
        
        # Auto-switch to inspector panel
        self.state.active_panel = UIPanel.INSPECTOR
    
    def add_event(self, event: Dict):
        """Add event to log."""
        self.event_log.append({
            'timestamp': datetime.now().isoformat(),
            **event
        })
        
        # Keep log manageable
        if len(self.event_log) > 100:
            self.event_log = self.event_log[-100:]
    
    def get_inspector_data(self, entity_type: str, 
                          entity_data: Dict) -> Dict:
        """
        Get data for inspector panel.
        
        Returns pre-computed data + AI-generated narrative.
        """
        # Generate narrative on-demand
        narrative = self.airai.generate_narrative(entity_type, entity_data)
        
        return {
            'data': entity_data,
            'narrative': narrative,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_event_log(self, limit: int = 20) -> List[Dict]:
        """Get recent events."""
        return self.event_log[-limit:]
    
    def render(self) -> str:
        """
        Render current UI state.
        
        In production, this would be actual UI rendering.
        For now, returns text representation.
        """
        lines = []
        lines.append(f"UI State: {self.state.active_panel.value}")
        lines.append(f"Selected: {self.state.selected_entity_id or 'None'}")
        lines.append(f"Speed: {self.state.speed}x")
        lines.append("")
        
        if self.state.active_panel == UIPanel.EVENT_LOG:
            lines.append("EVENT LOG:")
            for event in self.get_event_log(10):
                lines.append(f"  [{event.get('week', '?')}] {event.get('action', 'Unknown')}")
        
        return "\n".join(lines)


# ────────────────────────────────────────────────
# Layer 0 Integration Test
# ────────────────────────────────────────────────

def test_layer0():
    """Test Layer 0: AIR-AI + UI."""
    print("=" * 60)
    print("LAYER 0: AIR-AI + UI (INTEGRATION TEST)")
    print("=" * 60)
    
    # Initialize AIR-AI
    print("\n[1/4] Initializing AIR-AI...")
    airai = AIRAIOrchestrator()
    print(f"  Router: {'ONLINE' if airai.initialized else 'OFFLINE (using fallback)'}")
    
    # Initialize UI
    print("\n[2/4] Initializing UI...")
    ui = UIManager(airai)
    print(f"  Active Panel: {ui.state.active_panel.value}")
    
    # Test narrative generation
    print("\n[3/4] Testing Narrative Generation...")
    
    test_data = {
        'npc': {
            'name': 'Featherwing',
            'animal_sign': 'Dragon',
            'star_sign': 'Scorpio',
            'kno': 16, 'wis': 14, 'str': 8,
            'mood': 'contemplative'
        },
        'faction': {
            'name': 'Crystal Collective',
            'structure': 'Collective',
            'ideology': 'Memory is a burden we carry together',
            'current_action': 'researching ancient techniques'
        },
        'event': {
            'week': 3,
            'faction': 'Crystal Collective',
            'action': 'discovered new memory technique',
            'success': True
        }
    }
    
    for context_type, data in test_data.items():
        narrative = airai.generate_narrative(context_type, data)
        print(f"\n  {context_type.upper()}:")
        print(f"    {narrative}")
    
    # Test UI
    print("\n[4/4] Testing UI...")
    
    # Add some events
    ui.add_event({'week': 1, 'action': 'Faction founded new town', 'type': 'expansion'})
    ui.add_event({'week': 2, 'action': 'Trade route established', 'type': 'diplomacy'})
    ui.add_event({'week': 3, 'action': 'Research breakthrough', 'type': 'research'})
    
    # Select entity
    ui.select_entity('npc_001', 'npc')
    
    # Render UI
    print("\n" + ui.render())
    
    print("\n" + "=" * 60)
    print("LAYER 0 TEST COMPLETE")
    print("=" * 60)
    print(f"AIR-AI: {'OPERATIONAL' if airai.initialized else 'FALLBACK MODE'}")
    print(f"UI: READY")
    print(f"Narrative Generation: ON-DEMAND (lazy evaluation)")


if __name__ == '__main__':
    test_layer0()
