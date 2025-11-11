#!/usr/bin/env python3
"""Simple test to check weapon loading and school requirements"""

import sys
import os

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from TirganachReloaded.cff_editor.models.weapon_creation_data import (
    WeaponRequirements,
    SchoolRequirement,
)
from TirganachReloaded.cff_editor.exporters.weapon_loader import WeaponLoader


def test_school_requirements():
    """Test school requirements functionality"""
    print("Testing School Requirements...")

    # Test creating school requirements
    school_reqs = [
        SchoolRequirement(school_name="WHITE_MAGIC", level=5),
        SchoolRequirement(school_name="HEAVY_BLADE_WEAPONS", level=3),
    ]

    # Test creating requirements with school requirements
    requirements = WeaponRequirements(
        strength=15,
        dexterity=10,
        intelligence=0,
        level=5,
        school_requirements=school_reqs,
    )

    print(
        f"✓ Created requirements with {len(requirements.school_requirements)} school requirements:"
    )
    for req in requirements.school_requirements:
        print(f"  - {req.school_name} Level {req.level}")

    return True


def test_weapon_loading():
    """Test weapon loading from CFF"""
    print("\nTesting Weapon Loading...")

    try:
        loader = WeaponLoader()

        # Test loading a specific weapon (using IDs we found exist)
        test_weapon_ids = [
            27,
            28,
            100,
        ]  # Try a few different IDs (skip 1 - it's a charm)
        loaded_weapons = []

        for weapon_id in test_weapon_ids:
            try:
                weapon = loader.load_weapon(
                    weapon_id, "OriginalGameFiles/data/GameData.cff"
                )
                if weapon:
                    loaded_weapons.append(weapon)
                    print(f"✓ Loaded weapon {weapon_id}: {weapon.weapon_name}")
                    break  # Stop at the first successful load
            except Exception as e:
                print(f"  Could not load weapon {weapon_id}: {e}")
                continue

        if loaded_weapons:
            weapon = loaded_weapons[0]
            print(f"\nTesting weapon: {weapon.weapon_name}")
            print(f"  ID: {weapon.weapon_id}")
            print(f"  Damage: {weapon.min_damage}-{weapon.max_damage}")
            print(
                f"  School Requirements: {len(weapon.requirements.school_requirements)}"
            )
            for req in weapon.requirements.school_requirements:
                print(f"    - {req.school_name} Level {req.level}")

            # Check if damage values are loaded (not defaults)
            if weapon.min_damage > 0 or weapon.max_damage > 0:
                print(f"  ✓ Damage values loaded from CFF")
            else:
                print(f"  ⚠ Damage values appear to be defaults")

        else:
            print(
                "⚠ No weapons loaded - CFF file may be missing or weapon IDs incorrect"
            )

    except Exception as e:
        print(f"✗ Error loading weapons: {e}")
        return False

    return True


if __name__ == "__main__":
    print("=== Weapon Forge School Requirements Test ===")

    # Test school requirements
    test_school_requirements()

    # Test weapon loading
    test_weapon_loading()

    print("\n=== Test Complete ===")
