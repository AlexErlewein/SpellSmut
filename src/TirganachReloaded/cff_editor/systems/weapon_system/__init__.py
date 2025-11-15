"""
Weapon System

This package re-exports weapon-related functionality for the CFF editor
from their actual module locations (widgets/models/exporters).
"""

# Widgets
from ...widgets.weapon_forge_wizard import WeaponForgeWizard
from ...widgets.weapon_validation import WeaponValidator

# Models
from ...models.weapon_creation_data import WeaponCreationData, WeaponRequirements, SchoolRequirement

# Exporters / Loaders
from ...exporters.weapon_cff_exporter import WeaponCFFExporter
from ...exporters.weapon_loader import WeaponLoader

__all__ = [
    'WeaponForgeWizard',
    'WeaponValidator',
    'WeaponCreationData',
    'WeaponRequirements',
    'SchoolRequirement',
    'WeaponCFFExporter',
    'WeaponLoader',
]