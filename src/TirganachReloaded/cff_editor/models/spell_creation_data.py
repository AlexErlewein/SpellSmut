"""
SpellForce Spell Creation System - Main Spell Data Model
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from .spell_enums import MagicSchool, SpellType, TargetType, ScalingMode
from .spell_level import SpellLevel


@dataclass
class SpellCreationData:
    """Complete spell definition for the Spell Creation Wizard"""

    # Step 1: Basics
    spell_name: str = ""  # "Inferno Blast"
    internal_name: str = ""  # "InfernoBlast" (no spaces)
    magic_school: MagicSchool = MagicSchool.FIRE
    spell_type: SpellType = SpellType.ATTACK
    description: str = ""

    # Step 2: Mechanics
    target_type: TargetType = TargetType.SINGLE
    has_projectile: bool = False
    base_range: float = 20.0
    aoe_radius: float = 0.0
    duration: float = 0.0  # seconds (for buffs/debuffs/summons)
    special_effects: List[str] = field(default_factory=list)  # ["stun", "burn", etc.]

    # Step 3: Level Progression
    num_levels: int = 15  # 1-15
    levels: List[SpellLevel] = field(default_factory=list)  # One for each level
    scaling_mode: ScalingMode = ScalingMode.LINEAR

    # Step 4: Visual Effects
    vfx_cast: str = ""  # Effect name or template
    vfx_projectile: str = ""
    vfx_resolve: str = ""
    vfx_target: str = ""
    vfx_overtime: str = ""

    # Step 5: Sound Effects
    sfx_cast: str = ""  # Sound file name
    sfx_projectile: str = ""
    sfx_resolve: str = ""
    sfx_hit: str = ""

    # Metadata
    spell_line_id: int = 300  # Auto-assigned (300+ range for custom spells)
    created_date: str = ""
    author: str = ""

    def __post_init__(self):
        """Validate and initialize spell data"""
        # Set creation date if not provided
        if not self.created_date:
            self.created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Auto-generate internal name if not provided
        if not self.internal_name and self.spell_name:
            self.internal_name = "".join(c for c in self.spell_name if c.isalnum() or c in " _-").replace(" ", "")

        # Validate internal name (no spaces)
        if " " in self.internal_name:
            raise ValueError(f"Internal name cannot contain spaces: '{self.internal_name}'")

        # Validate level count
        if not 1 <= self.num_levels <= 15:
            raise ValueError(f"Number of levels must be between 1-15, got {self.num_levels}")

        # Initialize levels if empty
        if not self.levels:
            self.initialize_levels()

        # Ensure we have the right number of levels
        if len(self.levels) != self.num_levels:
            self.initialize_levels()

    def initialize_levels(self):
        """Initialize spell levels with default values"""
        self.levels = []
        for level in range(1, self.num_levels + 1):
            self.levels.append(SpellLevel(level=level))

    def apply_scaling(self, scaling_mode: Optional[ScalingMode] = None):
        """Apply scaling formula to all levels"""
        if scaling_mode:
            self.scaling_mode = scaling_mode

        if self.scaling_mode == ScalingMode.CUSTOM:
            return  # Don't auto-scale custom levels

        # Get base stats from level 1
        if not self.levels:
            return

        base_level = self.levels[0]

        for i, level in enumerate(self.levels):
            if i == 0:  # Skip level 1
                continue

            level_num = i + 1

            if self.scaling_mode == ScalingMode.LINEAR:
                # Linear scaling: same increase per level
                level.damage_min = base_level.damage_min + (level_num - 1) * 10
                level.damage_max = base_level.damage_max + (level_num - 1) * 12
                level.mana_cost = base_level.mana_cost + (level_num - 1) * 3
                level.cooldown = max(1.0, base_level.cooldown - (level_num - 1) * 0.1)
                level.range = base_level.range + (level_num - 1) * 0.5

            elif self.scaling_mode == ScalingMode.EXPONENTIAL:
                # Exponential scaling: accelerating growth
                factor = 1.15 ** (level_num - 1)
                level.damage_min = int(base_level.damage_min * factor)
                level.damage_max = int(base_level.damage_max * factor)
                level.mana_cost = int(base_level.mana_cost * (1.12 ** (level_num - 1)))
                level.cooldown = max(1.0, base_level.cooldown * (0.95 ** (level_num - 1)))
                level.range = base_level.range * (1.02 ** (level_num - 1))

            elif self.scaling_mode == ScalingMode.LOGARITHMIC:
                # Logarithmic scaling: diminishing returns
                import math
                factor = 1 + math.log(level_num) / 2
                level.damage_min = int(base_level.damage_min * factor)
                level.damage_max = int(base_level.damage_max * factor)
                level.mana_cost = int(base_level.mana_cost * factor)
                level.cooldown = base_level.cooldown
                level.range = base_level.range + (level_num - 1) * 0.3

    def get_balance_metrics(self) -> dict:
        """Calculate balance metrics for the spell"""
        if not self.levels:
            return {}

        # Use highest level for balance calculation
        max_level = self.levels[-1]

        metrics = {
            "damage_per_mana": max_level.damage_per_mana,
            "damage_per_second": max_level.dps,
            "effective_cast_time": max_level.effective_cast_time,
            "power_rating": 0.0,
            "balance_category": "Unknown"
        }

        # Calculate power rating (arbitrary scale)
        dpm_score = metrics["damage_per_mana"] * 10
        dps_score = metrics["damage_per_second"] * 5
        metrics["power_rating"] = (dpm_score + dps_score) / 2

        # Categorize power level
        if metrics["power_rating"] < 20:
            metrics["balance_category"] = "Weak"
        elif metrics["power_rating"] < 40:
            metrics["balance_category"] = "Balanced"
        elif metrics["power_rating"] < 60:
            metrics["balance_category"] = "Strong"
        else:
            metrics["balance_category"] = "Overpowered"

        return metrics

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "spell_name": self.spell_name,
            "internal_name": self.internal_name,
            "magic_school": self.magic_school.value,
            "spell_type": self.spell_type.value,
            "description": self.description,
            "target_type": self.target_type.value,
            "has_projectile": self.has_projectile,
            "base_range": self.base_range,
            "aoe_radius": self.aoe_radius,
            "duration": self.duration,
            "special_effects": self.special_effects,
            "num_levels": self.num_levels,
            "levels": [level.to_dict() for level in self.levels],
            "scaling_mode": self.scaling_mode.value,
            "vfx_cast": self.vfx_cast,
            "vfx_projectile": self.vfx_projectile,
            "vfx_resolve": self.vfx_resolve,
            "vfx_target": self.vfx_target,
            "vfx_overtime": self.vfx_overtime,
            "sfx_cast": self.sfx_cast,
            "sfx_projectile": self.sfx_projectile,
            "sfx_resolve": self.sfx_resolve,
            "sfx_hit": self.sfx_hit,
            "spell_line_id": self.spell_line_id,
            "created_date": self.created_date,
            "author": self.author,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SpellCreationData':
        """Create from dictionary"""
        # Convert enum values back
        magic_school = MagicSchool(data.get("magic_school", 1))
        spell_type = SpellType(data.get("spell_type", "attack"))
        target_type = TargetType(data.get("target_type", "single"))
        scaling_mode = ScalingMode(data.get("scaling_mode", "linear"))

        # Convert levels
        levels_data = data.get("levels", [])
        levels = [SpellLevel.from_dict(level_data) for level_data in levels_data]

        return cls(
            spell_name=data.get("spell_name", ""),
            internal_name=data.get("internal_name", ""),
            magic_school=magic_school,
            spell_type=spell_type,
            description=data.get("description", ""),
            target_type=target_type,
            has_projectile=data.get("has_projectile", False),
            base_range=data.get("base_range", 20.0),
            aoe_radius=data.get("aoe_radius", 0.0),
            duration=data.get("duration", 0.0),
            special_effects=data.get("special_effects", []),
            num_levels=data.get("num_levels", 15),
            levels=levels,
            scaling_mode=scaling_mode,
            vfx_cast=data.get("vfx_cast", ""),
            vfx_projectile=data.get("vfx_projectile", ""),
            vfx_resolve=data.get("vfx_resolve", ""),
            vfx_target=data.get("vfx_target", ""),
            vfx_overtime=data.get("vfx_overtime", ""),
            sfx_cast=data.get("sfx_cast", ""),
            sfx_projectile=data.get("sfx_projectile", ""),
            sfx_resolve=data.get("sfx_resolve", ""),
            sfx_hit=data.get("sfx_hit", ""),
            spell_line_id=data.get("spell_line_id", 300),
            created_date=data.get("created_date", ""),
            author=data.get("author", ""),
        )

    def __str__(self) -> str:
        """String representation for debugging"""
        return f"SpellCreationData(name='{self.spell_name}', school={self.magic_school.name}, type={self.spell_type.value}, levels={self.num_levels})"