"""
Armor System

This package contains all armor-related functionality for CFF editor,
including creation, modeling, sets, and export capabilities.
"""

from .armor_forge import ArmorForge
from .armor_model import Armor, SLOT_HEAD, SLOT_CHEST, SLOT_LEGS, SLOT_FEET, SLOT_RIGHT_RING, SLOT_LEFT_RING, SLOT_LEFT_HAND
from .armor_sets import ArmorSet, ArmorSetManager
from .cff_armor_export import export_armor_to_cff

__all__ = [
    'ArmorForge',
    'Armor',
    'ArmorSet', 
    'ArmorSetManager',
    'export_armor_to_cff',
    'SLOT_HEAD',
    'SLOT_CHEST', 
    'SLOT_LEGS',
    'SLOT_FEET',
    'SLOT_RIGHT_RING',
    'SLOT_LEFT_RING',
    'SLOT_LEFT_HAND'
]