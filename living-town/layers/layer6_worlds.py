"""
Layer 6: Worlds (Procedural World Generation)

Multiple towns, trade routes, star maps, and regional relationships.
Follows same principles as previous layers: procedural, minimal, fast.
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


# ────────────────────────────────────────────────
# World Types
# ────────────────────────────────────────────────

class WorldType(Enum):
    """Types of worlds in Rememberence."""
    MEMORY_REALM = "Memory Realm"
    DREAMSCAPE = "Dreamscape"
    ECHO_PLANE = "Echo Plane"
    VOID_SPACE = "Void Space"
    THREAD_REALM = "Thread Realm"


class TerrainType(Enum):
    """Terrain types for world maps."""
    PLAINS = "Plains"
    MOUNTAINS = "Mountains"
    FOREST = "Forest"
    WASTELAND = "Wasteland"
    CRYSTAL_FIELDS = "Crystal Fields"
    ECHO_DEEP = "Echo Deep"
    SHATTERED_LANDS = "Shattered Lands"


# ────────────────────────────────────────────────
# Data Classes
# ────────────────────────────────────────────────

@dataclass
class Town:
    """
    A town in the world.
    
    Towns are nodes in the world network, connected by trade routes.
    """
    id: str
    name: str
    x: int  # Map coordinates
    y: int
    population: int
    faction_id: Optional[str] = None
    terrain: TerrainType = TerrainType.PLAINS
    resources: Dict[str, int] = field(default_factory=dict)
    buildings: List[str] = field(default_factory=list)
    
    def distance_to(self, other: 'Town') -> float:
        """Calculate distance to another town."""
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5


@dataclass
class TradeRoute:
    """
    A trade route connecting two towns.
    """
    id: str
    town_a_id: str
    town_b_id: str
    goods: List[str] = field(default_factory=list)
    volume: int = 0  # Trade volume per cycle
    safety: float = 1.0  # 0.0-1.0 safety rating
    established: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class StarMap:
    """
    Celestial navigation map.
    
    Used by Thread-Walkers and travelers.
    """
    constellation_name: str
    stars: List[Tuple[int, int]]  # X,Y coordinates
    significance: str  # What this constellation means
    navigation_bonus: float = 0.0  # Travel speed modifier


@dataclass
class World:
    """
    A complete world with towns, routes, and star maps.
    """
    id: str
    name: str
    world_type: WorldType
    towns: Dict[str, Town] = field(default_factory=dict)
    trade_routes: Dict[str, TradeRoute] = field(default_factory=dict)
    star_maps: List[StarMap] = field(default_factory=list)
    
    # World properties
    width: int = 1000  # Map units
    height: int = 1000
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'type': self.world_type.value,
            'town_count': len(self.towns),
            'route_count': len(self.trade_routes),
            'star_maps': len(self.star_maps)
        }


# ────────────────────────────────────────────────
# World Generator
# ────────────────────────────────────────────────

class WorldGenerator:
    """
    Procedural world generator.
    
    Generates:
    - World with towns
    - Trade routes
    - Star maps
    """
    
    # Town name components
    TOWN_PREFIXES = [
        "Memory", "Echo", "Thread", "Void", "Crystal",
        "Shattered", "Silent", "Luminous", "Forgotten", "Eternal"
    ]
    
    TOWN_SUFFIXES = [
        "hold", "haven", "rest", "watch", "keep",
        "spire", "deep", "field", "crossing", "gate"
    ]
    
    # Terrain by world type
    TERRAIN_BY_WORLD = {
        WorldType.MEMORY_REALM: [TerrainType.PLAINS, TerrainType.CRYSTAL_FIELDS, TerrainType.FOREST],
        WorldType.DREAMSCAPE: [TerrainType.FOREST, TerrainType.PLAINS, TerrainType.ECHO_DEEP],
        WorldType.ECHO_PLANE: [TerrainType.ECHO_DEEP, TerrainType.SHATTERED_LANDS, TerrainType.WASTELAND],
        WorldType.VOID_SPACE: [TerrainType.WASTELAND, TerrainType.SHATTERED_LANDS, TerrainType.CRYSTAL_FIELDS],
        WorldType.THREAD_REALM: [TerrainType.MOUNTAINS, TerrainType.PLAINS, TerrainType.CRYSTAL_FIELDS],
    }
    
    # Constellation names
    CONSTELLATIONS = [
        "The Rememberer", "The Forgotten", "The Thread-Weaver",
        "The Shattered Crown", "The Echo Dragon", "The Void Serpent",
        "The Twin Archives", "The Broken Chain", "The Luminous Path"
    ]
    
    # Trade goods
    TRADE_GOODS = [
        "Memory Crystals", "Echo Chains", "Lethean Water",
        "Oracle Fragments", "Fate Threads", "Ancient Tomes",
        "Crafted Implants", "Truth Crystals", "Void Dust"
    ]
    
    def __init__(self):
        self.world_counter = 0
        self.town_counter = 0
        self.route_counter = 0
    
    def generate_id(self, prefix: str) -> str:
        if prefix == 'world':
            self.world_counter += 1
            return f"wld_{self.world_counter:03d}"
        elif prefix == 'town':
            self.town_counter += 1
            return f"twn_{self.town_counter:03d}"
        elif prefix == 'route':
            self.route_counter += 1
            return f"rt_{self.route_counter:03d}"
        return f"_{random.randint(1000, 9999)}"
    
    def generate_world(self, town_count: int = 3) -> World:
        """
        Generate a complete world.
        
        Args:
            town_count: Number of towns (default 3 for minimal tests)
        """
        world_type = random.choice(list(WorldType))
        name = self._generate_world_name(world_type)
        
        world = World(
            id=self.generate_id('world'),
            name=name,
            world_type=world_type
        )
        
        # Generate towns
        terrains = self.TERRAIN_BY_WORLD.get(world_type, [TerrainType.PLAINS])
        for _ in range(town_count):
            town = self._generate_town(world, terrains)
            world.towns[town.id] = town
        
        # Generate trade routes (connect all towns)
        self._generate_trade_routes(world)
        
        # Generate star maps
        self._generate_star_maps(world)
        
        return world
    
    def _generate_world_name(self, world_type: WorldType) -> str:
        """Generate world name."""
        prefixes = ["The", "Realm of", "Plane of", "Domain of"]
        roots = {
            WorldType.MEMORY_REALM: "Memory",
            WorldType.DREAMSCAPE: "Dreams",
            WorldType.ECHO_PLANE: "Echoes",
            WorldType.VOID_SPACE: "Void",
            WorldType.THREAD_REALM: "Threads"
        }
        
        return f"{random.choice(prefixes)} {roots.get(world_type, 'Unknown')}"
    
    def _generate_town(self, world: World, terrains: List[TerrainType]) -> Town:
        """Generate a town."""
        name = self._generate_town_name()
        
        # Random position
        x = random.randint(50, world.width - 50)
        y = random.randint(50, world.height - 50)
        
        # Random terrain
        terrain = random.choice(terrains)
        
        # Population based on terrain
        pop_mods = {
            TerrainType.PLAINS: 1.0,
            TerrainType.FOREST: 0.8,
            TerrainType.MOUNTAINS: 0.5,
            TerrainType.WASTELAND: 0.3,
            TerrainType.CRYSTAL_FIELDS: 0.7,
            TerrainType.ECHO_DEEP: 0.4,
            TerrainType.SHATTERED_LANDS: 0.2,
        }
        population = int(random.randint(100, 1000) * pop_mods.get(terrain, 1.0))
        
        # Resources based on terrain
        resources = self._generate_town_resources(terrain)
        
        return Town(
            id=self.generate_id('town'),
            name=name,
            x=x,
            y=y,
            population=population,
            terrain=terrain,
            resources=resources
        )
    
    def _generate_town_name(self) -> str:
        """Generate town name."""
        prefix = random.choice(self.TOWN_PREFIXES)
        suffix = random.choice(self.TOWN_SUFFIXES)
        return f"{prefix}{suffix}"
    
    def _generate_town_resources(self, terrain: TerrainType) -> Dict[str, int]:
        """Generate resources based on terrain."""
        resource_map = {
            TerrainType.PLAINS: {'Food': 100, 'Lumber': 50},
            TerrainType.FOREST: {'Lumber': 150, 'Herbs': 75},
            TerrainType.MOUNTAINS: {'Ore': 100, 'Gems': 25},
            TerrainType.WASTELAND: {'Void Dust': 50},
            TerrainType.CRYSTAL_FIELDS: {'Memory Crystals': 100, 'Echo Shards': 50},
            TerrainType.ECHO_DEEP: {'Echo Chains': 75, 'Thought Shards': 40},
            TerrainType.SHATTERED_LANDS: {'Fate Threads': 60, 'Oracle Fragments': 30},
        }
        return resource_map.get(terrain, {'Generic': 50})
    
    def _generate_trade_routes(self, world: World):
        """Generate trade routes connecting towns."""
        town_ids = list(world.towns.keys())
        
        # Connect each town to at least one other
        for i in range(len(town_ids) - 1):
            town_a = world.towns[town_ids[i]]
            town_b = world.towns[town_ids[i + 1]]
            
            # Generate goods
            goods = random.sample(self.TRADE_GOODS, random.randint(2, 4))
            volume = random.randint(10, 100)
            
            # Safety based on distance
            distance = town_a.distance_to(town_b)
            safety = max(0.5, 1.0 - (distance / world.width))
            
            route = TradeRoute(
                id=self.generate_id('route'),
                town_a_id=town_a.id,
                town_b_id=town_b.id,
                goods=goods,
                volume=volume,
                safety=round(safety, 2)
            )
            world.trade_routes[route.id] = route
    
    def _generate_star_maps(self, world: World):
        """Generate star maps for navigation."""
        num_stars = random.randint(3, 7)
        
        for const_name in random.sample(self.CONSTELLATIONS, random.randint(2, 4)):
            stars = [(random.randint(0, 100), random.randint(0, 100)) for _ in range(num_stars)]
            
            significance = random.choice([
                "Guides travelers to safety",
                "Marks the path to the Archive",
                "Warns of void storms",
                "Blesses Thread-Walkers",
                "Reveals hidden truths"
            ])
            
            star_map = StarMap(
                constellation_name=const_name,
                stars=stars,
                significance=significance,
                navigation_bonus=round(random.uniform(0.1, 0.3), 2)
            )
            world.star_maps.append(star_map)


# ────────────────────────────────────────────────
# World Manager
# ────────────────────────────────────────────────

class WorldManager:
    """Manages worlds."""
    
    def __init__(self, world_count: int = 1, towns_per_world: int = 3):
        """
        Initialize world manager.
        
        Args:
            world_count: Number of worlds (default 1)
            towns_per_world: Towns per world (default 3 for minimal tests)
        """
        self.worlds: Dict[str, World] = {}
        self.generator = WorldGenerator()
        
        self._generate_worlds(world_count, towns_per_world)
    
    def _generate_worlds(self, world_count: int, towns_per_world: int):
        """Generate worlds."""
        print(f"[Worlds] Generating {world_count} world(s) with {towns_per_world} towns each...")
        
        for _ in range(world_count):
            world = self.generator.generate_world(town_count=towns_per_world)
            self.worlds[world.id] = world
        
        print(f"  Created {len(self.worlds)} world(s)")
    
    def get_world(self, world_id: str) -> Optional[World]:
        return self.worlds.get(world_id)
    
    def get_all_worlds(self) -> List[World]:
        return list(self.worlds.values())
    
    def get_stats(self) -> Dict[str, Any]:
        total_towns = sum(len(w.towns) for w in self.worlds.values())
        total_routes = sum(len(w.trade_routes) for w in self.worlds.values())
        
        return {
            'total_worlds': len(self.worlds),
            'total_towns': total_towns,
            'total_routes': total_routes,
            'total_starmaps': sum(len(w.star_maps) for w in self.worlds.values())
        }


# ────────────────────────────────────────────────
# Minimal Test (Fast)
# ────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 60)
    print("LAYER 6: WORLDS (MINIMAL TEST)")
    print("=" * 60)
    
    # Generate 1 world with 3 towns (minimal)
    manager = WorldManager(world_count=1, towns_per_world=3)
    
    world = manager.get_all_worlds()[0]
    
    print(f"\nWorld: {world.name} ({world.world_type.value})")
    print(f"Size: {world.width}x{world.height}")
    
    print("\nTowns:")
    for town in world.towns.values():
        print(f"  {town.name} at ({town.x}, {town.y})")
        print(f"    Terrain: {town.terrain.value}")
        print(f"    Population: ~{town.population}")
        print(f"    Resources: {town.resources}")
    
    print("\nTrade Routes:")
    for route in world.trade_routes.values():
        town_a = world.towns[route.town_a_id]
        town_b = world.towns[route.town_b_id]
        print(f"  {town_a.name} <-> {town_b.name}")
        print(f"    Goods: {', '.join(route.goods)}")
        print(f"    Volume: {route.volume}/cycle, Safety: {route.safety}")
    
    print("\nStar Maps:")
    for star_map in world.star_maps:
        print(f"  {star_map.constellation_name}")
        print(f"    Stars: {len(star_map.stars)}")
        print(f"    Significance: {star_map.significance}")
        print(f"    Navigation Bonus: +{star_map.navigation_bonus}")
    
    print("\n" + "=" * 60)
    stats = manager.get_stats()
    print(f"TOTALS:")
    print(f"  Worlds: {stats['total_worlds']}")
    print(f"  Towns: {stats['total_towns']}")
    print(f"  Trade Routes: {stats['total_routes']}")
    print(f"  Star Maps: {stats['total_starmaps']}")
    print("=" * 60)
