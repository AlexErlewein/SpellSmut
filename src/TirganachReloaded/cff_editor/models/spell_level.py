"""
SpellForce Spell Creation System - Spell Level Data Model
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SpellLevel:
    """Stats for a single spell level (1-15)"""

    level: int  # 1-15
    damage_min: int = 0
    damage_max: int = 0
    mana_cost: int = 10
    cooldown: float = 3.0  # seconds
    cast_time: float = 1.5  # seconds
    range: float = 20.0
    aoe_radius: float = 0.0  # 0 if not AOE
    duration: float = 0.0  # seconds (for buffs/debuffs/summons)

    def __post_init__(self):
        """Validate level data after initialization"""
        if not 1 <= self.level <= 15:
            raise ValueError(f"Spell level must be between 1-15, got {self.level}")

        if self.damage_min < 0:
            raise ValueError(f"Damage min cannot be negative: {self.damage_min}")

        if self.damage_max < self.damage_min:
            raise ValueError(f"Damage max ({self.damage_max}) cannot be less than damage min ({self.damage_min})")

        if self.mana_cost < 0:
            raise ValueError(f"Mana cost cannot be negative: {self.mana_cost}")

        if self.cooldown < 0:
            raise ValueError(f"Cooldown cannot be negative: {self.cooldown}")

        if self.cast_time < 0:
            raise ValueError(f"Cast time cannot be negative: {self.cast_time}")

        if self.range < 0:
            raise ValueError(f"Range cannot be negative: {self.range}")

        if self.aoe_radius < 0:
            raise ValueError(f"AOE radius cannot be negative: {self.aoe_radius}")

        if self.duration < 0:
            raise ValueError(f"Duration cannot be negative: {self.duration}")

    @property
    def average_damage(self) -> float:
        """Calculate average damage for this level"""
        if self.damage_min == 0 and self.damage_max == 0:
            return 0.0
        return (self.damage_min + self.damage_max) / 2.0

    @property
    def damage_per_mana(self) -> float:
        """Calculate damage efficiency (damage per mana point)"""
        if self.mana_cost == 0:
            return 0.0
        return self.average_damage / self.mana_cost

    @property
    def effective_cast_time(self) -> float:
        """Total time to cast (cast time + cooldown)"""
        return self.cast_time + self.cooldown

    @property
    def dps(self) -> float:
        """Calculate damage per second (accounting for cast time)"""
        if self.effective_cast_time == 0:
            return 0.0
        return self.average_damage / self.effective_cast_time

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "level": self.level,
            "damage_min": self.damage_min,
            "damage_max": self.damage_max,
            "mana_cost": self.mana_cost,
            "cooldown": self.cooldown,
            "cast_time": self.cast_time,
            "range": self.range,
            "aoe_radius": self.aoe_radius,
            "duration": self.duration,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SpellLevel':
        """Create from dictionary"""
        return cls(
            level=data["level"],
            damage_min=data.get("damage_min", 0),
            damage_max=data.get("damage_max", 0),
            mana_cost=data.get("mana_cost", 10),
            cooldown=data.get("cooldown", 3.0),
            cast_time=data.get("cast_time", 1.5),
            range=data.get("range", 20.0),
            aoe_radius=data.get("aoe_radius", 0.0),
            duration=data.get("duration", 0.0),
        )