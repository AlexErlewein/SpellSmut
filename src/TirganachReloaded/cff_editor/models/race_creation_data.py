"""SpellForce Race Creation System - Race Data Model

This module defines the data structure for representing a complete race
with all required components in SpellForce Platinum Edition.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime


class RaceType(Enum):
    """Types of race archetypes in SpellForce"""
    HUMANOID = "humanoid"      # Humans, Elves, Dwarves
    ORCISH = "orcish"          # Orcs, Trolls
    DARK = "dark"              # Dark Elves
    BEAST = "beast"            # Creatures, animal-like races
    MAGICAL = "magical"        # Magic-based races


class UnitType(Enum):
    """Types of units in SpellForce"""
    WORKER = "worker"
    FIGHTER = "fighter"
    RANGED = "ranged"
    MAGE = "mage"
    SIEGE = "siege"
    TITAN = "titan"
    SWARM = "swarm"
    SPECIAL = "special"


@dataclass
class UnitStats:
    """Base stats for a unit"""
    strength: int = 10
    dexterity: int = 10
    intelligence: int = 10
    resistance_physical: int = 0
    resistance_magic: int = 0
    speed_walk: float = 4.0
    speed_run: float = 6.0


@dataclass
class UnitCombat:
    """Combat stats for a unit"""
    health: int = 100
    health_regeneration: float = 0.0
    mana: int = 50
    mana_regeneration: float = 0.0
    armor: int = 0
    damage_min: int = 10
    damage_max: int = 15
    damage_type: str = "normal"


@dataclass
class UnitAppearance:
    """Appearance settings for a unit"""
    mesh_name: str = ""
    texture_name: str = ""
    shadow_size: float = 1.0
    scale: float = 1.0
    animation_library: str = ""


@dataclass
class UnitData:
    """Complete unit definition"""
    unit_id: int
    unit_type: UnitType
    name: str = ""
    description: str = ""
    stats: UnitStats = field(default_factory=UnitStats)
    combat: UnitCombat = field(default_factory=UnitCombat)
    appearance: UnitAppearance = field(default_factory=UnitAppearance)
    requirements: Dict[str, Any] = field(default_factory=dict)  # For weapon/armor requirements, etc.
    sounds: Dict[str, str] = field(default_factory=dict)  # Combat sounds, work sounds, etc.
    # Additional properties
    base_name: str = ""  # Base name for animations (e.g., "figure_yourrace")
    weapon_types: List[int] = field(default_factory=list)  # IDs of weapons this unit can use
    building_id: Optional[int] = None  # ID of building that produces this unit


@dataclass
class BuildingData:
    """Complete building definition"""
    building_id: int
    building_type: str  # HQ, resource, barracks, etc.
    name: str = ""
    description: str = ""
    hp: int = 500
    costs: Dict[str, int] = field(default_factory=lambda: {"gold": 100, "wood": 50, "stone": 50})
    build_time: int = 30  # in seconds
    mesh_name: str = ""
    texture_name: str = ""
    light_effect: str = ""
    produces_units: List[int] = field(default_factory=list)  # IDs of units this building can produce
    # Additional building properties
    range: int = 0  # Range of influence or effect
    capacity: int = 0  # Resource capacity (for storage buildings)
    resource_type: str = ""  # Type of resource (for resource buildings)


@dataclass
class RaceCreationData:
    """Complete race definition for the Race Creation Wizard"""
    
    # Basic race information
    race_id: int = 7  # New races get ID 7+
    race_name: str = ""
    race_type: RaceType = RaceType.HUMANOID
    description: str = ""
    
    # Race-wide settings
    equipment_scaling: int = 100  # 100-180 percentage for equipment scaling
    shadow_size: float = 1.0     # Race-wide shadow size (0.8-2.0)
    visual_theme: str = ""       # Visual theme (size, color palette, etc.)
    
    # Units (at least 9 required: worker, fighters, ranged, mage, siege, titan, swarm)
    units: List[UnitData] = field(default_factory=list)
    
    # Buildings (at least 8 required: HQ, resource buildings, barracks, etc.)
    buildings: List[BuildingData] = field(default_factory=list)
    
    # Animation and sound libraries
    animation_library: str = ""     # Base name for animations (e.g., "YourRaceAnims")
    sound_prefix: str = ""          # Prefix for all race sounds (e.g., "battle_yourrace")
    
    # Lua script modifications required
    lua_modifications: Dict[str, List[str]] = field(default_factory=dict)  # Files that need modification
    
    # Asset paths
    asset_paths: Dict[str, str] = field(default_factory=dict)  # Paths to 3D models, textures, sounds
    
    # Creation metadata
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_date: str = field(default_factory=lambda: datetime.now().isoformat())
    author: str = "CFF Editor - Race Creator"
    version: int = 1
    
    # For tracking source if in edit/duplicate mode
    source_race_id: Optional[int] = None
    creation_mode: str = "new"  # "new", "edit", or "duplicate"
    
    def __post_init__(self):
        """Validate and initialize race data"""
        if not self.race_name:
            self.race_name = f"Race {self.race_id}"
        
        # Ensure equipment scaling is within reasonable bounds
        if self.equipment_scaling < 100:
            self.equipment_scaling = 100
        elif self.equipment_scaling > 180:
            self.equipment_scaling = 180
            
        # Ensure shadow size is within reasonable bounds
        if self.shadow_size < 0.8:
            self.shadow_size = 0.8
        elif self.shadow_size > 2.0:
            self.shadow_size = 2.0
    
    def add_unit(self, unit: UnitData) -> None:
        """Add a unit to the race"""
        self.units.append(unit)
    
    def add_building(self, building: BuildingData) -> None:
        """Add a building to the race"""
        self.buildings.append(building)
    
    def get_unit_by_type(self, unit_type: UnitType) -> Optional[UnitData]:
        """Find a unit by its type"""
        for unit in self.units:
            if unit.unit_type == unit_type:
                return unit
        return None
    
    def get_building_by_type(self, building_type: str) -> Optional[BuildingData]:
        """Find a building by its type"""
        for building in self.buildings:
            if building.building_type == building_type:
                return building
        return None
    
    def get_worker_unit(self) -> Optional[UnitData]:
        """Get the worker unit for this race"""
        return self.get_unit_by_type(UnitType.WORKER)
    
    def get_hq_building(self) -> Optional[BuildingData]:
        """Get the HQ building for this race"""
        return self.get_building_by_type("HQ")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert race data to dictionary format for export"""
        return {
            "race_id": self.race_id,
            "race_name": self.race_name,
            "race_type": self.race_type.value,
            "description": self.description,
            "equipment_scaling": self.equipment_scaling,
            "shadow_size": self.shadow_size,
            "visual_theme": self.visual_theme,
            "units": [
                {
                    "unit_id": u.unit_id,
                    "unit_type": u.unit_type.value,
                    "name": u.name,
                    "description": u.description,
                    "stats": {
                        "strength": u.stats.strength,
                        "dexterity": u.stats.dexterity,
                        "intelligence": u.stats.intelligence,
                        "resistance_physical": u.stats.resistance_physical,
                        "resistance_magic": u.stats.resistance_magic,
                        "speed_walk": u.stats.speed_walk,
                        "speed_run": u.stats.speed_run
                    },
                    "combat": {
                        "health": u.combat.health,
                        "health_regeneration": u.combat.health_regeneration,
                        "mana": u.combat.mana,
                        "mana_regeneration": u.combat.mana_regeneration,
                        "armor": u.combat.armor,
                        "damage_min": u.combat.damage_min,
                        "damage_max": u.combat.damage_max,
                        "damage_type": u.combat.damage_type
                    },
                    "appearance": {
                        "mesh_name": u.appearance.mesh_name,
                        "texture_name": u.appearance.texture_name,
                        "shadow_size": u.appearance.shadow_size,
                        "scale": u.appearance.scale,
                        "animation_library": u.appearance.animation_library
                    },
                    "requirements": u.requirements,
                    "sounds": u.sounds,
                    "base_name": u.base_name,
                    "weapon_types": u.weapon_types,
                    "building_id": u.building_id
                } for u in self.units
            ],
            "buildings": [
                {
                    "building_id": b.building_id,
                    "building_type": b.building_type,
                    "name": b.name,
                    "description": b.description,
                    "hp": b.hp,
                    "costs": b.costs,
                    "build_time": b.build_time,
                    "mesh_name": b.mesh_name,
                    "texture_name": b.texture_name,
                    "light_effect": b.light_effect,
                    "produces_units": b.produces_units,
                    "range": b.range,
                    "capacity": b.capacity,
                    "resource_type": b.resource_type
                } for b in self.buildings
            ],
            "animation_library": self.animation_library,
            "sound_prefix": self.sound_prefix,
            "lua_modifications": self.lua_modifications,
            "asset_paths": self.asset_paths,
            "created_date": self.created_date,
            "modified_date": self.modified_date,
            "author": self.author,
            "version": self.version,
            "source_race_id": self.source_race_id,
            "creation_mode": self.creation_mode
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RaceCreationData':
        """Create RaceCreationData from dictionary"""
        # Create the main race object
        race = cls(
            race_id=data.get("race_id", 7),
            race_name=data.get("race_name", ""),
            race_type=RaceType(data.get("race_type", "humanoid")),
            description=data.get("description", ""),
            equipment_scaling=data.get("equipment_scaling", 100),
            shadow_size=data.get("shadow_size", 1.0),
            visual_theme=data.get("visual_theme", ""),
            animation_library=data.get("animation_library", ""),
            sound_prefix=data.get("sound_prefix", ""),
            created_date=data.get("created_date", datetime.now().isoformat()),
            modified_date=data.get("modified_date", datetime.now().isoformat()),
            author=data.get("author", "CFF Editor - Race Creator"),
            version=data.get("version", 1),
            source_race_id=data.get("source_race_id"),
            creation_mode=data.get("creation_mode", "new")
        )
        
        # Add units
        for unit_data in data.get("units", []):
            stats = UnitStats(
                strength=unit_data["stats"]["strength"],
                dexterity=unit_data["stats"]["dexterity"],
                intelligence=unit_data["stats"]["intelligence"],
                resistance_physical=unit_data["stats"]["resistance_physical"],
                resistance_magic=unit_data["stats"]["resistance_magic"],
                speed_walk=unit_data["stats"]["speed_walk"],
                speed_run=unit_data["stats"]["speed_run"]
            )
            
            combat = UnitCombat(
                health=unit_data["combat"]["health"],
                health_regeneration=unit_data["combat"]["health_regeneration"],
                mana=unit_data["combat"]["mana"],
                mana_regeneration=unit_data["combat"]["mana_regeneration"],
                armor=unit_data["combat"]["armor"],
                damage_min=unit_data["combat"]["damage_min"],
                damage_max=unit_data["combat"]["damage_max"],
                damage_type=unit_data["combat"]["damage_type"]
            )
            
            appearance = UnitAppearance(
                mesh_name=unit_data["appearance"]["mesh_name"],
                texture_name=unit_data["appearance"]["texture_name"],
                shadow_size=unit_data["appearance"]["shadow_size"],
                scale=unit_data["appearance"]["scale"],
                animation_library=unit_data["appearance"]["animation_library"]
            )
            
            unit = UnitData(
                unit_id=unit_data["unit_id"],
                unit_type=UnitType(unit_data["unit_type"]),
                name=unit_data["name"],
                description=unit_data["description"],
                stats=stats,
                combat=combat,
                appearance=appearance,
                requirements=unit_data.get("requirements", {}),
                sounds=unit_data.get("sounds", {}),
                base_name=unit_data.get("base_name", ""),
                weapon_types=unit_data.get("weapon_types", []),
                building_id=unit_data.get("building_id")
            )
            
            race.add_unit(unit)
        
        # Add buildings
        for building_data in data.get("buildings", []):
            building = BuildingData(
                building_id=building_data["building_id"],
                building_type=building_data["building_type"],
                name=building_data["name"],
                description=building_data["description"],
                hp=building_data["hp"],
                costs=building_data["costs"],
                build_time=building_data["build_time"],
                mesh_name=building_data["mesh_name"],
                texture_name=building_data["texture_name"],
                light_effect=building_data.get("light_effect", ""),
                produces_units=building_data.get("produces_units", []),
                range=building_data.get("range", 0),
                capacity=building_data.get("capacity", 0),
                resource_type=building_data.get("resource_type", "")
            )
            
            race.add_building(building)
        
        # Set additional properties
        race.lua_modifications = data.get("lua_modifications", {})
        race.asset_paths = data.get("asset_paths", {})
        
        return race