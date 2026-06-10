"""
Layer 6: Stellaris-Scale (Systems, Galaxies, Cosmic Generation)

Procedural generation at cosmic scale:
- Star systems with multiple worlds
- Galactic regions with unique properties
- Trade routes between systems
- Cosmic phenomena (void storms, memory nebulas)

Material/Materia Integration:
- Worlds = Material (physical) + Materia (cosmic essence)
- Stars = Material (stellar substance) + Materia (energy type)
- Galaxies = Material (aggregate matter) + Materia (cosmic purpose)
- Higher scale = Higher level constructs (matching faction tier system)

Follows same modular philosophy as Layers 1-5.
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


# ────────────────────────────────────────────────
# Cosmic Types
# ────────────────────────────────────────────────

class StarType(Enum):
    """Star types for systems."""
    BLUE_SUPERGIANT = "Blue Supergiant"
    WHITE_MAIN = "White Main Sequence"
    YELLOW_MAIN = "Yellow Main Sequence"
    RED_DWARF = "Red Dwarf"
    NEUTRON = "Neutron Star"
    BLACK_HOLE = "Black Hole"
    MEMORY_STAR = "Memory Star"  # Exotic Rememberence star


class SystemType(Enum):
    """Star system types."""
    SINGLE = "Single Star"
    BINARY = "Binary System"
    TRINARY = "Trinary System"
    CLUSTER = "Star Cluster"
    NEBULA = "Nebula System"


class GalaxyRegion(Enum):
    """Galactic regions."""
    CORE_WORLDS = "Core Worlds"
    INNER_RIM = "Inner Rim"
    MID_RIM = "Mid Rim"
    OUTER_RIM = "Outer Rim"
    DEEP_VOID = "Deep Void"
    SHATTERED_BAND = "Shattered Band"


# ────────────────────────────────────────────────
# Data Classes
# ────────────────────────────────────────────────

@dataclass
class StarSystem:
    """
    A star system with worlds.
    
    Material/Materia:
    - Star's material/materia defines system properties
    - Worlds inherit from star's Species/Type
    - Scale levels: Novice (1 world) → Deity (8+ worlds)
    
    Contains:
    - Star(s) with Material/Materia
    - Orbiting worlds (constructs)
    - Stations/outposts
    - Jump points to other systems
    """
    id: str
    name: str
    system_type: SystemType
    star_type: StarType
    age: int  # Millions of years
    
    # Material/Materia (from star)
    material: str = ""  # Species (stellar substance)
    materia: str = ""   # Type (energy essence)
    level: int = 1      # System level (1-100k)
    
    # Worlds in system (constructs)
    worlds: Dict[str, Any] = field(default_factory=dict)
    
    # Position in galaxy
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    # Connections
    jump_routes: List[str] = field(default_factory=list)
    
    # Properties
    stability: float = 1.0  # 0.0-1.0
    resources: Dict[str, int] = field(default_factory=dict)
    stats: Dict[str, int] = field(default_factory=dict)  # HP, ATK, DEF, etc.
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'type': self.system_type.value,
            'star': self.star_type.value,
            'material': self.material,
            'materia': self.materia,
            'level': self.level,
            'worlds': len(self.worlds),
            'position': (self.x, self.y, self.z),
            'connections': len(self.jump_routes),
            'stats': self.stats
        }


@dataclass
class Galaxy:
    """
    A galaxy containing star systems.
    
    Material/Materia:
    - Aggregate of all systems' Material/Materia
    - Dominant material/materia defines galaxy nature
    - Scale levels: Mediate (100 systems) → Omniversal (Deity II)
    
    Contains:
    - Multiple star systems
    - Regional properties
    - Galactic phenomena
    """
    id: str
    name: str
    region_type: GalaxyRegion
    
    # Material/Materia (dominant from systems)
    dominant_material: str = ""  # Most common Species
    dominant_materia: str = ""   # Most common Type
    tier: str = ""  # Novice I → Deity I (or higher)
    
    # Systems in galaxy
    systems: Dict[str, StarSystem] = field(default_factory=dict)
    
    # Galaxy properties
    diameter: int = 100000  # Light years
    system_count: int = 0
    age: int = 0  # Billions of years
    
    # Phenomena
    phenomena: List[str] = field(default_factory=list)
    
    # Cosmic stats (scale-appropriate)
    stats: Dict[str, int] = field(default_factory=dict)
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'region': self.region_type.value,
            'dominant_material': self.dominant_material,
            'dominant_materia': self.dominant_materia,
            'tier': self.tier,
            'systems': len(self.systems),
            'diameter_ly': self.diameter,
            'age_by': self.age,
            'stats': self.stats
        }


# ────────────────────────────────────────────────
# System Generator
# ────────────────────────────────────────────────

class SystemGenerator:
    """
    Procedural star system generator with Material/Materia.
    
    Stars and worlds are constructs at cosmic scale:
    - Star = Material (stellar species) + Materia (energy type)
    - Worlds = Inherit from star's Material/Materia
    - Level = Number of worlds + system age
    """
    
    # Material/Materia mapping for stars
    STAR_MATERIALS = [
        'Drakian', 'Banshee', 'Elf', 'Orc', 'Mimic', 'Human',
        'Angel', 'Demon', 'Dwarf', 'Giant', 'Phoenix', 'Serpent'
    ]
    
    STAR_MATERIA = [
        'Thunder', 'Warrior', 'Pyro', 'Aqua', 'Beast', 'Ghost',
        'Crystal', 'Holy', 'Dark', 'Metal', 'Psychic', 'Vortex'
    ]
    
    # System tiers based on world count
    SYSTEM_TIERS = [
        ('Novice', 1, 1),      # 1 world
        ('Beginner', 2, 10),   # 2-3 worlds
        ('Mediate', 4, 100),   # 4-5 worlds
        ('Advanced', 6, 1000), # 6-7 worlds
        ('Master', 8, 10000),  # 8+ worlds
        ('Deity', 8, 100000),  # 8+ worlds, ancient
    ]
    
    # System name components
    NAME_PREFIXES = [
        "Memory", "Echo", "Thread", "Void", "Crystal",
        "Shattered", "Silent", "Luminous", "Forgotten", "Eternal"
    ]
    
    NAME_SUFFIXES = [
        "Prime", "Major", "Minor", "Central", "Core",
        "Reach", "Expanse", "Rim", "End", "Fall"
    ]
    
    # World types
    WORLD_TYPES = [
        "Terran", "Oceanic", "Desert", "Ice", "Volcanic",
        "Gas Giant", "Memory World", "Echo World", "Void World"
    ]
    
    # Resources by star type
    RESOURCES_BY_STAR = {
        StarType.BLUE_SUPERGIANT: ['Rare Crystals', 'Exotic Matter'],
        StarType.WHITE_MAIN: ['Memory Crystals', 'Common Minerals'],
        StarType.YELLOW_MAIN: ['Life-Supporting', 'Agricultural'],
        StarType.RED_DWARF: ['Mineral-Rich', 'Energy-Poor'],
        StarType.NEUTRON: ['Neutronium', 'Exotic Particles'],
        StarType.BLACK_HOLE: ['Hawking Radiation', 'Temporal Anomalies'],
        StarType.MEMORY_STAR: ['Pure Memory', 'Echo Essence'],
    }
    
    def __init__(self):
        self.system_counter = 0
    
    def generate_id(self) -> str:
        self.system_counter += 1
        return f"sys_{self.system_counter:03d}"
    
    def generate_system(self, system_type: SystemType = None,
                       star_type: StarType = None,
                       material: str = None,
                       materia: str = None) -> StarSystem:
        """Generate a procedural star system with Material/Materia.
        
        Args:
            system_type: Type of system
            star_type: Type of star
            material: Species (stellar substance) - random if None
            materia: Type (energy essence) - random if None
        """
        
        # Random type if not specified
        if system_type is None:
            system_type = random.choice(list(SystemType))
        if star_type is None:
            star_type = random.choice(list(StarType))
        if material is None:
            material = random.choice(self.STAR_MATERIALS)
        if materia is None:
            materia = random.choice(self.STAR_MATERIA)
        
        # Generate name
        name = self._generate_name()
        
        # Generate age
        age = random.randint(100, 10000)  # Millions of years
        
        # Generate position
        x = random.uniform(-50000, 50000)
        y = random.uniform(-50000, 50000)
        z = random.uniform(-1000, 1000)
        
        # Generate resources
        resources = {r: random.randint(10, 100) 
                    for r in self.RESOURCES_BY_STAR.get(star_type, ['Generic'])}
        
        # Create system
        system = StarSystem(
            id=self.generate_id(),
            name=name,
            system_type=system_type,
            star_type=star_type,
            age=age,
            material=material,
            materia=materia,
            x=x,
            y=y,
            z=z,
            resources=resources
        )
        
        # Determine tier from world count
        num_worlds = random.randint(1, 8)
        tier_name, min_worlds, level = self.SYSTEM_TIERS[-1]  # Default to Deity
        for t_name, t_min, t_level in self.SYSTEM_TIERS:
            if num_worlds >= t_min:
                tier_name, min_worlds, level = t_name, t_min, t_level
        
        system.level = level
        
        # Calculate stats from Material/Materia + level
        system.stats = self._calculate_system_stats(material, materia, level, num_worlds)
        
        # Generate worlds (inherit material/materia from star)
        for i in range(num_worlds):
            world = self._generate_world(i, material, materia, level)
            system.worlds[world['id']] = world
        
        return system
    
    def _generate_name(self) -> str:
        prefix = random.choice(self.NAME_PREFIXES)
        suffix = random.choice(self.NAME_SUFFIXES)
        return f"{prefix} {suffix}"
    
    def _calculate_system_stats(self, material: str, materia: str,
                                level: int, num_worlds: int) -> Dict[str, int]:
        """
        Calculate system stats from Material/Materia + level.
        
        Systems are cosmic-scale constructs:
        - HP = System stability/mass
        - ATK = Stellar output/radiation
        - DEF = Gravitational well/magnetic field
        - SPD = Orbital mechanics
        - MP = Memory/echo essence
        """
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from data_loader import get_loader
        loader = get_loader()
        
        # Get canonical data
        material_data = loader.get_species(material)
        materia_data = loader.get_type(materia)
        
        # Base stats from Material (Species)
        base_hp = material_data.get('HP', 100) if isinstance(material_data, dict) else 100
        base_atk = material_data.get('ATK', 50) if isinstance(material_data, dict) else 50
        base_def = material_data.get('DEF', 75) if isinstance(material_data, dict) else 75
        base_spd = material_data.get('SPD', 25) if isinstance(material_data, dict) else 25
        base_mp = material_data.get('MP', 150) if isinstance(material_data, dict) else 150
        
        # Scale by level
        scale = level // 10 + 1
        
        # Add world count bonus
        world_bonus = num_worlds * 10
        
        return {
            'HP': (base_hp * scale) + world_bonus,
            'ATK': base_atk * scale,
            'DEF': base_def * scale,
            'SPD': base_spd * scale,
            'MP': (base_mp * scale) + world_bonus,
        }
    
    def _generate_world(self, index: int, material: str, materia: str, level: int) -> Dict:
        """Generate a world in the system (inherits star's Material/Materia)."""
        world_type = random.choice(self.WORLD_TYPES)
        
        # Distance from star (AU)
        distance = (index + 1) * random.uniform(0.5, 2.0)
        
        # Size
        size = random.choice(['Small', 'Medium', 'Large', 'Giant'])
        
        # World stats scale with system level
        world_stats = {
            'HP': 100 * level // 10,
            'ATK': 10 * level // 10,
            'DEF': 15 * level // 10,
            'SPD': 5 * level // 10,
            'MP': 50 * level // 10,
        }
        
        return {
            'id': f'wld_{index+1}',
            'name': f'World {index+1}',
            'type': world_type,
            'distance_au': round(distance, 2),
            'size': size,
            'habitable': world_type in ['Terran', 'Oceanic'] and distance < 3.0,
            'material': material,  # Inherit from star
            'materia': materia,    # Inherit from star
            'level': level,
            'stats': world_stats,
        }


# ────────────────────────────────────────────────
# Galaxy Generator
# ────────────────────────────────────────────────

class GalaxyGenerator:
    """
    Procedural galaxy generator with Material/Materia.
    """
    
    # Galaxy names
    GALAXY_NAMES = [
        "The Memory Spiral",
        "The Echoing Void",
        "The Shattered Expanse",
        "The Thread Nebula",
        "The Crystal Galaxy",
        "The Forgotten Arm",
        "The Luminous Deep"
    ]
    
    # Phenomena by region
    PHENOMENA_BY_REGION = {
        GalaxyRegion.CORE_WORLDS: ["High Traffic", "Rich Resources", "Political Center"],
        GalaxyRegion.INNER_RIM: ["Established Routes", "Moderate Resources"],
        GalaxyRegion.MID_RIM: ["Expansion Zone", "Frontier Systems"],
        GalaxyRegion.OUTER_RIM: ["Sparse Population", "Unknown Dangers"],
        GalaxyRegion.DEEP_VOID: ["Void Storms", "Isolated Systems"],
        GalaxyRegion.SHATTERED_BAND: ["Reality Instability", "Memory Anomalies"],
    }
    
    def __init__(self):
        self.galaxy_counter = 0
        self.system_gen = SystemGenerator()
    
    def generate_id(self) -> str:
        self.galaxy_counter += 1
        return f"gal_{self.galaxy_counter:02d}"
    
    def generate_galaxy(self, region: GalaxyRegion = None,
                       system_count: int = 10,
                       material: str = None,
                       materia: str = None) -> Galaxy:
        """Generate a procedural galaxy with Material/Materia."""
        
        if region is None:
            region = random.choice(list(GalaxyRegion))
        
        # Generate name
        name = random.choice(self.GALAXY_NAMES)
        
        # Generate age
        age = random.randint(5, 15)  # Billions of years
        
        # Generate phenomena
        phenomena = self.PHENOMENA_BY_REGION.get(region, ["Unknown"])
        
        # Create galaxy
        galaxy = Galaxy(
            id=self.generate_id(),
            name=name,
            region_type=region,
            diameter=random.randint(50000, 150000),
            system_count=system_count,
            age=age,
            phenomena=phenomena
        )
        
        # Generate systems with optional Material/Materia
        material_counts = {}
        materia_counts = {}
        
        for _ in range(system_count):
            system = self.system_gen.generate_system(
                material=material,
                materia=materia
            )
            galaxy.systems[system.id] = system
            
            # Track material/materia frequency
            mat = system.material
            mat_type = system.materia
            material_counts[mat] = material_counts.get(mat, 0) + 1
            materia_counts[mat_type] = materia_counts.get(mat_type, 0) + 1
        
        # Determine dominant material/materia
        if material_counts:
            galaxy.dominant_material = max(material_counts, key=material_counts.get)
        if materia_counts:
            galaxy.dominant_materia = max(materia_counts, key=materia_counts.get)
        
        # Determine tier from system count
        if system_count < 10:
            galaxy.tier = "Novice I"
        elif system_count < 100:
            galaxy.tier = "Beginner I"
        elif system_count < 1000:
            galaxy.tier = "Mediate I"
        elif system_count < 10000:
            galaxy.tier = "Advanced I"
        elif system_count < 100000:
            galaxy.tier = "Master I"
        else:
            galaxy.tier = "Deity I"
        
        # Calculate galaxy stats (aggregate of systems)
        galaxy.stats = self._calculate_galaxy_stats(galaxy)
        
        # Generate jump routes (connect nearby systems)
        self._generate_jump_routes(galaxy)
        
        return galaxy
    
    def _calculate_galaxy_stats(self, galaxy: Galaxy) -> Dict[str, int]:
        """Calculate galaxy stats from constituent systems."""
        total_hp = sum(s.stats.get('HP', 0) for s in galaxy.systems.values())
        total_atk = sum(s.stats.get('ATK', 0) for s in galaxy.systems.values())
        total_def = sum(s.stats.get('DEF', 0) for s in galaxy.systems.values())
        total_spd = sum(s.stats.get('SPD', 0) for s in galaxy.systems.values())
        total_mp = sum(s.stats.get('MP', 0) for s in galaxy.systems.values())
        
        return {
            'HP': total_hp,
            'ATK': total_atk,
            'DEF': total_def,
            'SPD': total_spd,
            'MP': total_mp,
        }
    
    def _generate_jump_routes(self, galaxy: Galaxy):
        """Generate jump routes between systems."""
        system_ids = list(galaxy.systems.keys())
        
        # Each system connects to 1-3 others
        for sys_id in system_ids:
            system = galaxy.systems[sys_id]
            num_connections = random.randint(1, 3)
            
            # Pick random other systems
            others = [s for s in system_ids if s != sys_id]
            connections = random.sample(others, min(num_connections, len(others)))
            
            system.jump_routes = connections


# ────────────────────────────────────────────────
# Cosmic Manager
# ────────────────────────────────────────────────

class CosmicManager:
    """Manages galaxies and systems."""
    
    def __init__(self, galaxy_count: int = 1, systems_per_galaxy: int = 5):
        """
        Initialize cosmic manager.
        
        Args:
            galaxy_count: Number of galaxies (default 1 for minimal tests)
            systems_per_galaxy: Systems per galaxy (default 5 for fast tests)
        """
        self.galaxies: Dict[str, Galaxy] = {}
        self.generator = GalaxyGenerator()
        
        self._generate_galaxies(galaxy_count, systems_per_galaxy)
    
    def _generate_galaxies(self, count: int, systems: int):
        """Generate galaxies."""
        print(f"[Cosmic] Generating {count} galaxy(s) with {systems} systems each...")
        
        for _ in range(count):
            galaxy = self.generator.generate_galaxy(system_count=systems)
            self.galaxies[galaxy.id] = galaxy
        
        print(f"  Created {len(self.galaxies)} galaxy(s)")
    
    def get_galaxy(self, galaxy_id: str) -> Optional[Galaxy]:
        return self.galaxies.get(galaxy_id)
    
    def get_all_galaxies(self) -> List[Galaxy]:
        return list(self.galaxies.values())
    
    def get_stats(self) -> Dict[str, Any]:
        total_systems = sum(len(g.systems) for g in self.galaxies.values())
        total_worlds = sum(
            sum(len(s.worlds) for s in g.systems.values())
            for g in self.galaxies.values()
        )
        
        return {
            'total_galaxies': len(self.galaxies),
            'total_systems': total_systems,
            'total_worlds': total_worlds
        }


# ────────────────────────────────────────────────
# Minimal Test (Fast)
# ────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 60)
    print("LAYER 6: STELLARIS-SCALE (Material/Materia Integration)")
    print("=" * 60)
    
    # Generate 1 galaxy with 5 systems (minimal)
    manager = CosmicManager(galaxy_count=1, systems_per_galaxy=5)
    
    galaxy = manager.get_all_galaxies()[0]
    
    print(f"\nGalaxy: {galaxy.name}")
    print(f"  Region: {galaxy.region_type.value}")
    print(f"  Tier: {galaxy.tier}")
    print(f"  Material (Dominant): {galaxy.dominant_material}")
    print(f"  Materia (Dominant): {galaxy.dominant_materia}")
    print(f"  Diameter: {galaxy.diameter:,} ly")
    print(f"  Age: {galaxy.age} billion years")
    print(f"  Phenomena: {', '.join(galaxy.phenomena)}")
    print(f"  Stats: HP={galaxy.stats.get('HP', 0)}, ATK={galaxy.stats.get('ATK', 0)}")
    
    print(f"\nStar Systems ({len(galaxy.systems)}):")
    for system in galaxy.systems.values():
        print(f"\n  {system.name}")
        print(f"    Material: {system.material} / Materia: {system.materia}")
        print(f"    Level: {system.level} ({'Novice' if system.level < 10 else 'Deity' if system.level >= 100000 else 'Intermediate'})")
        print(f"    Star: {system.star_type.value}")
        print(f"    Worlds: {len(system.worlds)}")
        print(f"    Stats: HP={system.stats.get('HP', 0)}, ATK={system.stats.get('ATK', 0)}, DEF={system.stats.get('DEF', 0)}")
        print(f"    Jump Routes: {len(system.jump_routes)}")
        print(f"    Resources: {list(system.resources.keys())[0]}")
        
        # Show habitable worlds
        habitable = [w for w in system.worlds.values() if w.get('habitable')]
        if habitable:
            print(f"    Habitable: {', '.join([w['name'] for w in habitable])}")
        
        # Show world Material/Materia
        if system.worlds:
            first_world = list(system.worlds.values())[0]
            print(f"    World Example: {first_world['name']}")
            print(f"      Material: {first_world.get('material', 'Unknown')} / Materia: {first_world.get('materia', 'Unknown')}")
            print(f"      Stats: {first_world.get('stats', {})}")
    
    print("\n" + "=" * 60)
    stats = manager.get_stats()
    print(f"TOTALS:")
    print(f"  Galaxies: {stats['total_galaxies']}")
    print(f"  Systems: {stats['total_systems']}")
    print(f"  Worlds: {stats['total_worlds']}")
    print(f"\n  All celestial bodies follow Material/Materia ontology!")
    print("=" * 60)
