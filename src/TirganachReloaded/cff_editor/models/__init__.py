"""
SpellForce Spell Creation System - Models Package
"""

# Import enums first (no dependencies)
from .spell_enums import MagicSchool, SpellType, TargetType, ScalingMode, ValidationError

# Import basic classes
from .spell_level import SpellLevel

# Import complex classes that depend on others
from .spell_creation_data import SpellCreationData

__all__ = [
    "MagicSchool",
    "SpellType",
    "TargetType",
    "ScalingMode",
    "ValidationError",
    "SpellLevel",
    "SpellCreationData",
]