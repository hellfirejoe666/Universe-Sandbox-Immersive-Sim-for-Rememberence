"""
Layer 5: Factions (Procedural Groups/Collectives)

Factions are collective entities with shared identity, purpose, and memory.
Generated as unified groups, not aggregations of individuals.
"""

import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


# ────────────────────────────────────────────────
# Faction Types
# ────────────────────────────────────────────────

class FactionType(Enum):
    """Collective types in Rememberence."""
    ARCHIVE = "Archive"              # Memory preservation collective
    FORGETTERS = "Forgetting Order"  # Liberation through release
    WALKERS = "Thread Walkers"       # Fate navigators
    ARTIFICERS = "Memory Artificers" # Construct creators
    MERCHANTS = "Trade Collective"   # Commerce guild
    WARRIORS = "Warrior Band"        # Protection collective
    SCHOLARS = "Knowledge Circle"    # Learning collective


class CollectiveStructure(Enum):
    """How the faction organizes itself."""
    HIERARCHY = "Hierarchy"      # Clear leadership structure
    COLLECTIVE = "Collective"    # Shared decision-making
    CELL = "Cell Network"        # Decentralized cells
    CULT = "Cult"                # Charismatic leader
    GUILD = "Guild"              # Professional organization


# ────────────────────────────────────────────────
# Data Classes
# ────────────────────────────────────────────────

@dataclass
class Faction:
    """
    A faction as a collective entity led by a single leader.
    
    The faction leader's Species (Material) and Type (Materia) define:
    - All faction constructs (6 tiers: Novice → Deity)
    - Faction equipment and weapons
    - Faction traits and abilities
    - Production economy
    
    Factions are unified groups with:
    - Leader (defines Material/Materia)
    - Shared identity (name, symbols, colors)
    - Collective purpose (ideology, goals)
    - Construct hierarchy (6 tiers)
    - Shared resources (treasury, artifacts)
    """
    
    # Core Identity
    id: str
    name: str
    faction_type: FactionType
    structure: CollectiveStructure
    
    # Faction Leader (defines Material/Materia for entire faction)
    leader_id: str = ""
    leader_name: str = ""
    leader_material: str = ""  # Species (Material)
    leader_materia: str = ""   # Type (Materia)
    
    # Collective Identity
    ideology: str = ""
    purpose: str = ""
    symbols: List[str] = field(default_factory=list)
    colors: List[str] = field(default_factory=list)
    motto: str = ""
    
    # Faction Constructs (6 tiers, defined by leader's Species/Type)
    constructs: Dict[str, Any] = field(default_factory=dict)  # tier -> construct data
    
    # Collective Memory
    founding_story: str = ""
    traditions: List[str] = field(default_factory=list)
    taboos: List[str] = field(default_factory=list)
    
    # Group Resources
    shared_treasury: int = 0
    artifacts: List[str] = field(default_factory=list)
    strongholds: List[str] = field(default_factory=list)
    
    # Membership (as a collective)
    member_count: int = 0
    recruitment_method: str = ""
    initiation_ritual: str = ""
    
    # Relations with other collectives
    alliances: List[str] = field(default_factory=list)
    enemies: List[str] = field(default_factory=list)
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'type': self.faction_type.value,
            'structure': self.structure.value,
            'leader': {
                'id': self.leader_id,
                'name': self.leader_name,
                'material': self.leader_material,
                'materia': self.leader_materia,
            },
            'ideology': self.ideology,
            'purpose': self.purpose,
            'symbols': self.symbols,
            'colors': self.colors,
            'motto': self.motto,
            'constructs': self.constructs,
            'founding_story': self.founding_story,
            'traditions': self.traditions,
            'taboos': self.taboos,
            'shared_treasury': self.shared_treasury,
            'artifacts': self.artifacts,
            'strongholds': self.strongholds,
            'member_count': self.member_count,
            'recruitment_method': self.recruitment_method,
            'alliances': self.alliances,
            'enemies': self.enemies
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Faction':
        leader_data = data.get('leader', {})
        return cls(
            id=data['id'],
            name=data['name'],
            faction_type=FactionType(data['type']),
            structure=CollectiveStructure(data.get('structure', 'Collective')),
            leader_id=leader_data.get('id', ''),
            leader_name=leader_data.get('name', ''),
            leader_material=leader_data.get('material', ''),
            leader_materia=leader_data.get('materia', ''),
            ideology=data['ideology'],
            purpose=data['purpose'],
            symbols=data.get('symbols', []),
            colors=data.get('colors', []),
            motto=data.get('motto', ''),
            constructs=data.get('constructs', {}),
            founding_story=data.get('founding_story', ''),
            traditions=data.get('traditions', []),
            taboos=data.get('taboos', []),
            shared_treasury=data.get('shared_treasury', 0),
            artifacts=data.get('artifacts', []),
            strongholds=data.get('strongholds', []),
            member_count=data.get('member_count', 0),
            recruitment_method=data.get('recruitment_method', ''),
            alliances=data.get('alliances', []),
            enemies=data.get('enemies', [])
        )


# ────────────────────────────────────────────────
# Faction Generator (Procedural Groups)
# ────────────────────────────────────────────────

class FactionGenerator:
    """
    Procedural faction generator for collective groups.
    
    Generates factions where the leader's Species (Material) and Type (Materia)
    define all faction constructs, equipment, and abilities.
    
    36 Species × 24 Types = 864 faction archetypes
    """
    
    # Faction tiers (from Null.txt template)
    FACTION_TIERS = [
        ('Novice', 'Icon', 1),
        ('Beginner', 'Unit', 10),
        ('Mediate', 'World', 100),
        ('Advanced', 'System', 1000),
        ('Master', 'Galaxy', 10000),
        ('Deity', 'Universe', 100000),
    ]
    
    # Construct names by tier
    CONSTRUCT_NAMES = {
        'Novice': ['Drones', 'Scouts', 'Initiates', 'Servitors'],
        'Beginner': ['Mech Suit', 'Enforcers', 'Adepts', 'Guardians'],
        'Mediate': ['Shuttle', 'Vessel', 'Carrier', 'Temple'],
        'Advanced': ['Cruiser', 'Battleship', 'Fortress', 'Cathedral'],
        'Master': ['Flagship', 'Dreadnought', 'Citadel', 'Sanctum'],
        'Deity': ['Source', 'Genesis', 'Origin', 'Prime'],
    }
    
    # Collective identity tables
    IDENTITY_PREFIXES = [
        "Eternal", "Shattered", "Silent", "Luminous", "Forgotten",
        "Void", "Crystal", "Thread", "Echo", "Sacred"
    ]
    
    IDENTITY_ROOTS = [
        "Archive", "Collective", "Order", "Circle", "Brotherhood",
        "Sisterhood", "Court", "Council", "Keepers", "Weavers"
    ]
    
    IDENTITY_SUFFIXES = [
        "of Memory", "of Echoes", "of the Void", "of Light",
        "of the Shattered", "Eternal", "", ""
    ]
    
    # Collective ideologies (group-minded, not individual)
    IDEOLOGIES = [
        "We preserve what others would forget.",
        "Liberation comes through shared release.",
        "The threads connect us all.",
        "Memory is a burden we carry together.",
        "Individual minds are limited; collective is infinite.",
        "Some truths are too heavy for one soul.",
        "The past shapes our shared future.",
        "Forgetting is a gift we give each other."
    ]
    
    # Collective purposes
    PURPOSES = [
        "Maintain the Great Archive together",
        "Guide seekers through pivotal moments",
        "Create sanctuaries of peaceful forgetting",
        "Perfect the art of memory crafting",
        "Protect the weak from memory thieves",
        "Trade knowledge across the realms",
        "Study the nature of consciousness",
        "Preserve the old ways"
    ]
    
    # Group structures
    STRUCTURES = {
        FactionType.ARCHIVE: CollectiveStructure.HIERARCHY,
        FactionType.FORGETTERS: CollectiveStructure.CELL,
        FactionType.WALKERS: CollectiveStructure.COLLECTIVE,
        FactionType.ARTIFICERS: CollectiveStructure.GUILD,
        FactionType.MERCHANTS: CollectiveStructure.GUILD,
        FactionType.WARRIORS: CollectiveStructure.HIERARCHY,
        FactionType.SCHOLARS: CollectiveStructure.COLLECTIVE,
    }
    
    # Symbols by type
    SYMBOLS = {
        FactionType.ARCHIVE: ["Open Book", "Crystal Shard", "Eye"],
        FactionType.FORGETTERS: ["Empty Vessel", "Broken Chain", "White Flame"],
        FactionType.WALKERS: ["Woven Thread", "Compass", "Star Map"],
        FactionType.ARTIFICERS: ["Hammer & Anvil", "Gear", "Spark"],
        FactionType.MERCHANTS: ["Scales", "Coin", "Handshake"],
        FactionType.WARRIORS: ["Shield", "Sword", "Wolf"],
        FactionType.SCHOLARS: ["Lantern", "Scroll", "Owl"],
    }
    
    # Colors by type
    COLORS = {
        FactionType.ARCHIVE: ["Deep Blue", "Silver"],
        FactionType.FORGETTERS: ["White", "Pale Grey"],
        FactionType.WALKERS: ["Purple", "Gold"],
        FactionType.ARTIFICERS: ["Bronze", "Orange"],
        FactionType.MERCHANTS: ["Green", "Gold"],
        FactionType.WARRIORS: ["Red", "Black"],
        FactionType.SCHOLARS: ["Blue", "White"],
    }
    
    # Founding story templates
    FOUNDING_STORIES = [
        "Founded by {founder} who {action} at {location}.",
        "Born from the {event} when {group} came together.",
        "Established after {founder} discovered {artifact}.",
        "Formed in response to the {crisis} that threatened all."
    ]
    
    FOUNDERS = ["a group of seekers", "twelve survivors", "the first Rememberers",
                "exiles from the Hollow Court", "wandering scholars"]
    ACTIONS = ["found the First Archive", "heard the Call", "wove the First Thread",
               "shared the Great Secret"]
    LOCATIONS = ["the Shattered Fields", "Mount Mnemos", "the City of Recursive Dreams",
                 "the Echo-Deep"]
    EVENTS = ["Great Forgetting", "Thread Convergence", "Memory Plague", "Void Incursion"]
    GROUPS = ["like-minded souls", "the scattered remnants", "those who remembered"]
    ARTIFACTS = ["the Codex of Unspeaking", "the First Echo", "a Core Shard"]
    CRISES = ["the Lethean Purge", "the Memory Wars", "the Great Unraveling"]
    
    # Traditions
    TRADITIONS = [
        "The nightly recitation of names",
        "The sharing of memories at dawn",
        "The ritual of release",
        "The binding of threads",
        "The forging of new artifacts"
    ]
    
    # Taboos
    TABOOS = [
        "Never forget a brother's name",
        "Never sell memory for gold",
        "Never walk the threads alone",
        "Never craft false memories",
        "Never speak the Unspoken"
    ]
    
    def __init__(self):
        self.faction_counter = 0
    
    def generate_id(self) -> str:
        self.faction_counter += 1
        return f"fct_{self.faction_counter:03d}"
    
    def generate_faction(self, faction_type: FactionType = None,
                        leader: Any = None) -> Faction:
        """Generate a procedural faction with leader-driven Material/Materia.
        
        Args:
            faction_type: Type of faction
            leader: Optional leader entity (from Layer 3). If None, generates minimal leader data.
        """
        
        if faction_type is None:
            faction_type = random.choice(list(FactionType))
        
        # Get leader's Species/Type (defines faction's Material/Materia)
        if leader:
            leader_material = leader.material if hasattr(leader, 'material') else leader.species
            leader_materia = leader.materia if hasattr(leader, 'materia') else leader.type
            leader_name = leader.name
            leader_id = leader.id
        else:
            # Generate minimal leader data
            from data_loader import get_loader
            loader = get_loader()
            species_list = list(loader.get_all_species().keys())
            types_list = list(loader.get_all_types().keys())
            leader_material = random.choice(species_list)
            leader_materia = random.choice(types_list)
            leader_name = f"Leader of {leader_material}"
            leader_id = "leader_auto"
        
        # Generate collective identity
        name = self._generate_name()
        ideology = random.choice(self.IDEOLOGIES)
        purpose = random.choice(self.PURPOSES)
        structure = self.STRUCTURES.get(faction_type, CollectiveStructure.COLLECTIVE)
        
        # Generate symbols and colors
        symbols = random.sample(self.SYMBOLS.get(faction_type, ["Unknown"]), 
                               random.randint(1, 2))
        colors = self.COLORS.get(faction_type, ["Grey", "Black"])
        
        # Generate motto
        motto = self._generate_motto(ideology)
        
        # Generate founding story
        founding = self._generate_founding_story()
        
        # Generate traditions and taboos
        traditions = random.sample(self.TRADITIONS, random.randint(1, 3))
        taboos = random.sample(self.TABOOS, random.randint(1, 2))
        
        # Generate faction constructs (6 tiers) from leader's Species/Type
        constructs = self._generate_faction_constructs(leader_material, leader_materia)
        
        # Generate resources
        treasury = random.randint(2000, 8000)
        artifacts = self._generate_artifacts(faction_type)
        member_count = random.randint(20, 200)
        
        # Generate recruitment
        recruitment = random.choice([
            "Open to all who share our purpose",
            "By invitation only",
            "After proving worth through trials",
            "Born into the collective"
        ])
        
        return Faction(
            id=self.generate_id(),
            name=name,
            faction_type=faction_type,
            structure=structure,
            leader_id=leader_id,
            leader_name=leader_name,
            leader_material=leader_material,
            leader_materia=leader_materia,
            ideology=ideology,
            purpose=purpose,
            symbols=symbols,
            colors=colors,
            motto=motto,
            constructs=constructs,
            founding_story=founding,
            traditions=traditions,
            taboos=taboos,
            shared_treasury=treasury,
            artifacts=artifacts,
            member_count=member_count,
            recruitment_method=recruitment
        )
    
    def _generate_name(self) -> str:
        prefix = random.choice(self.IDENTITY_PREFIXES)
        root = random.choice(self.IDENTITY_ROOTS)
        suffix = random.choice(self.IDENTITY_SUFFIXES)
        
        if suffix:
            return f"{prefix} {root} {suffix}"
        return f"{prefix} {root}"
    
    def _generate_motto(self, ideology: str) -> str:
        """Generate a short motto from ideology."""
        # Extract key concept from ideology
        if "preserve" in ideology.lower():
            return "Remember All"
        elif "forget" in ideology.lower() or "release" in ideology.lower():
            return "Let Go, Be Free"
        elif "thread" in ideology.lower():
            return "All Paths Connected"
        elif "collective" in ideology.lower():
            return "Together, Infinite"
        else:
            return "Unity Through Purpose"
    
    def _generate_founding_story(self) -> str:
        """Generate a founding story for the collective."""
        template = random.choice(self.FOUNDING_STORIES)
        
        return template.format(
            founder=random.choice(self.FOUNDERS),
            action=random.choice(self.ACTIONS),
            location=random.choice(self.LOCATIONS),
            event=random.choice(self.EVENTS),
            group=random.choice(self.GROUPS),
            artifact=random.choice(self.ARTIFACTS),
            crisis=random.choice(self.CRISES)
        )
    
    def _generate_artifacts(self, faction_type: FactionType) -> List[str]:
        """Generate collective artifacts."""
        artifact_lists = {
            FactionType.ARCHIVE: ["Memory Crystals", "Echo Chains", "The First Codex"],
            FactionType.FORGETTERS: ["Vials of Lethe", "Blank Scrolls", "Silence Bells"],
            FactionType.WALKERS: ["Thread Compass", "Fate Maps", "Oracle Shards"],
            FactionType.ARTIFICERS: ["Memory Forges", "Crafting Tools", "Prototype Implants"],
            FactionType.MERCHANTS: ["Trade Agreements", "Gold Reserves", "Merchant Fleet"],
            FactionType.WARRIORS: ["Ancestral Weapons", "Battle Standards", "Armor of Heroes"],
            FactionType.SCHOLARS: ["Ancient Tomes", "Research Notes", "Truth Crystals"],
        }
        
        available = artifact_lists.get(faction_type, ["Mysterious Relic"])
        return random.sample(available, min(2, len(available)))
    
    def _generate_faction_constructs(self, material: str, materia: str) -> Dict[str, Any]:
        """
        Generate 6-tier construct hierarchy from leader's Species (Material) + Type (Materia).
        
        Tiers: Novice → Beginner → Mediate → Advanced → Master → Deity
        Each construct inherits material/materia from leader.
        """
        from data_loader import get_loader
        loader = get_loader()
        
        # Get canonical data for material/materia
        material_data = loader.get_species(material)
        materia_data = loader.get_type(materia)
        
        # Get base stats from material (Species)
        base_hp = material_data.get('HP', 20) if isinstance(material_data, dict) else 20
        base_atk = material_data.get('ATK', 10) if isinstance(material_data, dict) else 10
        base_def = material_data.get('DEF', 15) if isinstance(material_data, dict) else 15
        base_spd = material_data.get('SPD', 5) if isinstance(material_data, dict) else 5
        base_mp = material_data.get('MP', 30) if isinstance(material_data, dict) else 30
        
        # Get traits from material and materia
        traits = []
        if material_data and isinstance(material_data, dict):
            mat_traits = material_data.get('traits', {}).get('active', [])
            traits.extend(mat_traits[:2])
        if materia_data and isinstance(materia_data, dict):
            mat_traits = materia_data.get('traits', {}).get('active', [])
            traits.extend(mat_traits[:2])
        
        # Generate constructs for each tier
        constructs = {}
        
        for tier_name, tier_label, level in self.FACTION_TIERS:
            # Scale multipliers by tier
            tier_mult = level  # Direct scaling (1, 10, 100, 1k, 10k, 100k)
            
            # Calculate stats (base + biorhythm-like scaling)
            # Using FND, SEX, DIV, BEU, SPL as pseudo-biorhythms
            fnd = tier_mult * 2
            sex = tier_mult // 2
            div = tier_mult // 2
            beu = tier_mult // 5
            spl = tier_mult
            
            hp = base_hp + fnd
            atk = base_atk + sex
            def_val = base_def + div
            spd = base_spd + beu
            mp = base_mp + spl
            
            # Production scales with tier
            production = tier_mult // 5
            
            # Recipe cost (from Null.txt pattern)
            recipe_cost = 22840 * (tier_mult // 10 + 1) * (tier_mult // 10 + 1)
            sell_value = recipe_cost // 10
            
            # Select construct name
            construct_name = random.choice(self.CONSTRUCT_NAMES.get(tier_name, ['Construct']))
            
            constructs[tier_name] = {
                'name': construct_name,
                'level': level,
                'tier': f"{tier_name}I",
                'material': material,
                'materia': materia,
                'stats': {
                    'HP': hp,
                    'ATK': atk,
                    'DEF': def_val,
                    'SPD': spd,
                    'MP': mp,
                },
                'biorhythms': {
                    'FND': fnd,
                    'SEX': sex,
                    'DIV': div,
                    'BEU': beu,
                    'SPL': spl,
                },
                'production': f"{production}/Turn",
                'recipe_cost': f"${recipe_cost:,}",
                'sell_value': f"${sell_value:,}",
                'move': 'Omni',
                'attack': 'Corner Diag',
                'traits': traits,
            }
        
        return constructs


# ────────────────────────────────────────────────
# Faction Manager
# ────────────────────────────────────────────────

class FactionManager:
    """Manages all factions."""
    
    def __init__(self, count: int = 2):
        """
        Initialize faction manager.
        
        Args:
            count: Number of factions to generate (default 2 for fast tests)
        """
        self.factions: Dict[str, Faction] = {}
        self.generator = FactionGenerator()
        
        # Generate minimal factions for testing
        self._generate_factions(count)
    
    def _generate_factions(self, count: int):
        """Generate specified number of factions."""
        print(f"[Factions] Generating {count} procedural factions...")
        
        for _ in range(count):
            faction = self.generator.generate_faction()
            self.factions[faction.id] = faction
        
        print(f"  Created {len(self.factions)} factions")
    
    def add_faction(self, faction: Faction):
        """Add a faction."""
        self.factions[faction.id] = faction
    
    def get_faction(self, faction_id: str) -> Optional[Faction]:
        return self.factions.get(faction_id)
    
    def get_all_factions(self) -> List[Faction]:
        return list(self.factions.values())
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'total': len(self.factions),
            'factions': [{
                'name': f.name,
                'type': f.faction_type.value,
                'members': f.member_count,
                'treasury': f.shared_treasury
            } for f in self.factions.values()]
        }


# ────────────────────────────────────────────────
# Faction Actions (Civ-Style Decision Engine)
# ────────────────────────────────────────────────

class ActionCategory(Enum):
    """Categories of faction actions."""
    EXPANSION = "Expansion"
    DIPLOMACY = "Diplomacy"
    WAR = "War"
    RESEARCH = "Research"
    INFRASTRUCTURE = "Infrastructure"
    RECRUITMENT = "Recruitment"
    ESPIONAGE = "Espionage"
    CONSOLIDATION = "Consolidation"


@dataclass
class FactionAction:
    """A faction action (Civ-style)."""
    id: str
    category: ActionCategory
    name: str
    description: str
    target_id: Optional[str] = None
    success_chance: float = 0.5
    impact: Dict[str, Any] = field(default_factory=dict)
    completed: bool = False


class FactionDecisionMatrix:
    """
    Maps leader biorhythms to faction actions.
    Weekly turns driven by leader state.
    """
    
    HIGH_THRESHOLD = 15
    LOW_THRESHOLD = 5
    
    ACTION_WEIGHTS = {
        'VIT': {ActionCategory.WAR: 0.3, ActionCategory.EXPANSION: 0.2},
        'STR': {ActionCategory.WAR: 0.4, ActionCategory.EXPANSION: 0.2},
        'BEU': {ActionCategory.DIPLOMACY: 0.4, ActionCategory.RECRUITMENT: 0.2},
        'DIV': {ActionCategory.DIPLOMACY: 0.3, ActionCategory.CONSOLIDATION: 0.2},
        'KNO': {ActionCategory.RESEARCH: 0.4, ActionCategory.INFRASTRUCTURE: 0.2},
        'WIS': {ActionCategory.RESEARCH: 0.3, ActionCategory.INFRASTRUCTURE: 0.2},
        'FND': {ActionCategory.INFRASTRUCTURE: 0.3, ActionCategory.CONSOLIDATION: 0.3},
        'EGO': {ActionCategory.CONSOLIDATION: 0.3, ActionCategory.INFRASTRUCTURE: 0.2},
        'MNF': {ActionCategory.EXPANSION: 0.3, ActionCategory.ESPIONAGE: 0.2},
        'SPL': {ActionCategory.ESPIONAGE: 0.3, ActionCategory.EXPANSION: 0.2},
        'UND': {ActionCategory.ESPIONAGE: 0.3, ActionCategory.RESEARCH: 0.2},
        'SEX': {ActionCategory.RECRUITMENT: 0.3, ActionCategory.DIPLOMACY: 0.2},
    }
    
    ACTIONS_BY_CATEGORY = {
        ActionCategory.EXPANSION: [("Found New Town", "Establish settlement"), ("Claim Territory", "Expand borders")],
        ActionCategory.DIPLOMACY: [("Propose Alliance", "Seek defense pact"), ("Trade Agreement", "Establish trade")],
        ActionCategory.WAR: [("Declare War", "Open conflict"), ("Raid Outpost", "Strike resources")],
        ActionCategory.RESEARCH: [("Discover Technique", "New method"), ("Craft Artifact", "Create item")],
        ActionCategory.INFRASTRUCTURE: [("Build Stronghold", "Fortify base"), ("Establish Archive", "Store knowledge")],
        ActionCategory.RECRUITMENT: [("Recruit Members", "Attract followers"), ("Convert Town", "Persuade settlement")],
        ActionCategory.ESPIONAGE: [("Steal Resources", "Acquire supplies"), ("Gather Intelligence", "Learn plans")],
        ActionCategory.CONSOLIDATION: [("Defend Borders", "Strengthen defenses"), ("Stockpile Resources", "Build reserves")],
    }
    
    @classmethod
    def decide_action(cls, biorhythms: Dict[str, int], targets: List[str] = None) -> FactionAction:
        """Decide faction action based on leader biorhythms."""
        # Calculate weights
        weights = {cat: 0.0 for cat in ActionCategory}
        for bio_key, bio_value in biorhythms.items():
            if bio_key in cls.ACTION_WEIGHTS:
                for cat, weight in cls.ACTION_WEIGHTS[bio_key].items():
                    if bio_value >= cls.HIGH_THRESHOLD:
                        weights[cat] += weight * (bio_value / 10)
                    elif bio_value <= cls.LOW_THRESHOLD:
                        weights[cat] -= weight * 0.5
        
        # Select category
        total = sum(max(0, w) for w in weights.values())
        if total > 0:
            weights = {k: v/total for k, v in weights.items()}
        
        items = list(weights.keys())
        vals = [max(0, weights[i]) for i in items]
        category = random.choices(items, weights=vals, k=1)[0] if sum(vals) > 0 else random.choice(items)
        
        # Select action
        action_name, action_desc = random.choice(cls.ACTIONS_BY_CATEGORY.get(category, cls.ACTIONS_BY_CATEGORY[ActionCategory.CONSOLIDATION]))
        target = random.choice(targets) if targets else None
        
        # Success chance
        relevant = {
            ActionCategory.WAR: ['VIT', 'STR'], ActionCategory.DIPLOMACY: ['BEU', 'DIV'],
            ActionCategory.RESEARCH: ['KNO', 'WIS'], ActionCategory.INFRASTRUCTURE: ['FND', 'EGO'],
        }
        bio_keys = relevant.get(category, ['FND'])
        avg = sum(biorhythms.get(k, 10) for k in bio_keys) / len(bio_keys)
        chance = max(0.1, min(0.95, 0.5 + (avg - 10) / 20))
        
        return FactionAction(
            id=f"act_{random.randint(1000, 9999)}",
            category=category,
            name=action_name,
            description=action_desc,
            target_id=target,
            success_chance=chance
        )


class FactionTurnManager:
    """Manages weekly faction turns."""
    
    def __init__(self):
        self.week = 0
        self.action_log: List[Dict] = []
        self.matrix = FactionDecisionMatrix()
    
    def process_week(self, factions: List[Faction], leaders: Dict[str, Any]) -> List[FactionAction]:
        """Process one week of faction turns."""
        self.week += 1
        actions = []
        
        print(f"\n{'='*60}")
        print(f"WEEK {self.week}: FACTION TURNS")
        print(f"{'='*60}")
        
        for faction in factions:
            leader = leaders.get(faction.id)
            if not leader:
                continue
            
            biorhythms = leader.biorhythms.to_dict()
            targets = [f.id for f in factions if f.id != faction.id]
            action = self.matrix.decide_action(biorhythms, targets)
            
            print(f"\n  {faction.name} ({leader.name})")
            print(f"    Action: {action.name} ({action.category.value})")
            print(f"    Success: {action.success_chance:.0%}")
            
            actions.append(action)
            self.action_log.append({
                'week': self.week,
                'faction': faction.name,
                'leader': leader.name,
                'action': action.name,
                'category': action.category.value,
                'success_chance': action.success_chance
            })
        
        return actions
    
    def resolve_actions(self, actions: List[FactionAction]) -> List[Dict]:
        """Resolve action outcomes."""
        events = []
        print(f"\n{'='*60}")
        print("ACTION RESOLUTION")
        print(f"{'='*60}")
        
        for action in actions:
            success = random.random() < action.success_chance
            status = "[OK]" if success else "[FAIL]"
            print(f"  {status} {action.name} - {'SUCCESS' if success else 'FAILED'}")
            
            events.append({
                'week': self.week,
                'action': action.name,
                'category': action.category.value,
                'success': success
            })
        
        return events
    
    def get_story_log(self) -> List[Dict]:
        """Get emergent story log."""
        return self.action_log


# ────────────────────────────────────────────────
# Minimal Test (Fast)
# ────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 60)
    print("LAYER 5: FACTIONS (Material/Materia Integration)")
    print("=" * 60)
    
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from layers.layer3_entities import EntityGenerator
    
    # Generate factions with leader-driven Material/Materia
    generator = FactionGenerator()
    manager = FactionManager(count=0)  # We'll generate manually
    
    # Test specific Material/Materia combinations
    print("\nFACTIONS (Leader's Species/Type defines all constructs):")
    print("-" * 60)
    
    # Generate a leader entity first
    entity_gen = EntityGenerator()
    leader1 = entity_gen.generate_entity(
        material='Mimic',
        materia='Metal',
        level=50,
        role=None
    )
    
    faction1 = generator.generate_faction(
        faction_type=FactionType.ARTIFICERS,
        leader=leader1
    )
    
    print(f"\n  {faction1.name}")
    print(f"    Leader: {faction1.leader_name}")
    print(f"    Material (Species): {faction1.leader_material}")
    print(f"    Materia (Type): {faction1.leader_materia}")
    print(f"    Type: {faction1.faction_type.value}")
    print(f"    Members: ~{faction1.member_count}")
    print(f"\n    Faction Constructs (6 Tiers):")
    
    for tier_name, construct in faction1.constructs.items():
        print(f"\n      [{tier_name}I] {construct['name']}")
        print(f"        Material: {construct['material']} / Materia: {construct['materia']}")
        print(f"        Level: {construct['level']} ({construct['tier']})")
        stats = construct['stats']
        print(f"        HP={stats['HP']}, ATK={stats['ATK']}, DEF={stats['DEF']}, SPD={stats['SPD']}, MP={stats['MP']}")
        print(f"        Product: {construct['production']}")
        print(f"        Recipe: {construct['recipe_cost']} | Sell: {construct['sell_value']}")
        print(f"        Traits: {', '.join(construct['traits'])}")
    
    # Generate another faction with different Material/Materia
    leader2 = entity_gen.generate_entity(
        material='Drakian',
        materia='Thunder',
        level=50,
        role=None
    )
    
    faction2 = generator.generate_faction(
        faction_type=FactionType.WARRIORS,
        leader=leader2
    )
    
    print(f"\n\n  {faction2.name}")
    print(f"    Leader: {faction2.leader_name}")
    print(f"    Material (Species): {faction2.leader_material}")
    print(f"    Materia (Type): {faction2.leader_materia}")
    print(f"    Type: {faction2.faction_type.value}")
    print(f"\n    Sample Constructs:")
    
    # Show first 3 tiers
    for tier_name in ['Novice', 'Mediate', 'Master']:
        construct = faction2.constructs[tier_name]
        print(f"\n      [{tier_name}I] {construct['name']}")
        print(f"        {construct['material']} + {construct['materia']}")
        print(f"        HP={construct['stats']['HP']}, ATK={construct['stats']['ATK']}")
    
    print("\n" + "=" * 60)
    print(f"TOTAL: 864 faction archetypes (36 Species × 24 Types)")
    print("Each faction has 6-tier construct hierarchy")
    print("All constructs inherit leader's Material/Materia")
    print("=" * 60)
