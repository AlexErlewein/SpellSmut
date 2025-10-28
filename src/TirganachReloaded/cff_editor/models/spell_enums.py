"""
SpellForce Spell Creation System - Enums and Constants
"""

from enum import Enum


class MagicSchool(Enum):
    """SpellForce magic schools"""
    WHITE = 0    # Holy/Life magic
    FIRE = 1     # Fire elemental
    ICE = 2      # Ice elemental
    BLACK = 3    # Necromancy/Dark magic
    MENTAL = 4   # Mind/Illusion magic
    EARTH = 5    # Earth elemental


class SpellType(Enum):
    """Types of spells in SpellForce"""
    ATTACK = "attack"      # Direct damage spells
    HEAL = "heal"          # Healing spells
    BUFF = "buff"          # Beneficial status effects
    DEBUFF = "debuff"      # Harmful status effects
    SUMMON = "summon"      # Creature summoning
    AOE = "aoe"           # Area of effect spells
    UTILITY = "utility"    # Utility spells (teleport, etc.)


class TargetType(Enum):
    """How spells target enemies/areas"""
    SINGLE = "single"      # Single target
    AOE = "aoe"           # Area around point
    SELF = "self"         # Self-cast
    CONE = "cone"         # Cone-shaped area
    CHAIN = "chain"       # Chain between targets


class ScalingMode(Enum):
    """How spell stats scale with level"""
    LINEAR = "linear"           # Same increase per level
    EXPONENTIAL = "exponential"  # Accelerating growth
    LOGARITHMIC = "logarithmic"  # Diminishing returns
    CUSTOM = "custom"           # Manual per-level editing


class ValidationError:
    """Represents a validation error or warning"""

    def __init__(self, message: str, severity: str = "error"):
        self.message = message
        self.severity = severity  # "error" or "warning"

    def __str__(self):
        return f"[{self.severity.upper()}] {self.message}"