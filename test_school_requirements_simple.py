#!/usr/bin/env python3
"""Test school requirements data without GUI dependencies"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))


def test_weapon_school_requirements():
    """Test weapon school requirements directly from GameData"""
    print("=== Testing Weapon School Requirements ===")

    try:
        from TirganachReloaded.tirganach.structure import GameData

        # Load GameData
        game_data = GameData(None)  # No input file needed for basic structure
        weapons = game_data.items.weapons

        print(f"✓ Loaded {len(weapons)} weapons from GameData")

        # Check for school requirements in weapons
        weapons_with_school_reqs = 0
        sample_weapons = []

        for weapon_id, weapon in list(weapons.items())[:10]:  # Check first 10
            school_requirements = weapon.get("school_requirements", [])
            if school_requirements:
                weapons_with_school_reqs += 1
                sample_weapons.append((weapon_id, weapon, school_requirements))

        print(
            f"✓ Found {weapons_with_school_reqs} weapons with school requirements in sample"
        )

        # Display sample weapons with school requirements
        for weapon_id, weapon, school_reqs in sample_weapons[:3]:
            print(f"\nWeapon {weapon_id} ({weapon.get('name', 'Unknown')}):")
            print(
                f"  Basic requirements: STR={weapon.get('strength', 0)}, DEX={weapon.get('dexterity', 0)}, INT={weapon.get('intelligence', 0)}"
            )
            print(f"  School requirements ({len(school_reqs)}):")
            for req in school_reqs:
                school = req.get("requirement_school", "Unknown")
                level = req.get("level", 0)
                print(f"    - {school} Level {level}")

        return True

    except Exception as e:
        print(f"✗ Error testing weapon school requirements: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_armor_school_requirements():
    """Test armor school requirements directly from GameData"""
    print("\n=== Testing Armor School Requirements ===")

    try:
        from engine.game_data import GameData

        # Load GameData
        game_data = GameData()
        armors = game_data.get_armor()

        print(f"✓ Loaded {len(armors)} armor pieces from GameData")

        # Check for school requirements in armor
        armors_with_school_reqs = 0
        sample_armors = []

        for armor_id, armor in list(armors.items())[:10]:  # Check first 10
            school_requirements = armor.get("school_requirements", [])
            if school_requirements:
                armors_with_school_reqs += 1
                sample_armors.append((armor_id, armor, school_requirements))

        print(
            f"✓ Found {armors_with_school_reqs} armor pieces with school requirements in sample"
        )

        # Display sample armor with school requirements
        for armor_id, armor, school_reqs in sample_armors[:3]:
            print(f"\nArmor {armor_id} ({armor.get('name', 'Unknown')}):")
            print(
                f"  Basic requirements: STR={armor.get('strength', 0)}, DEX={armor.get('dexterity', 0)}, INT={armor.get('intelligence', 0)}"
            )
            print(f"  School requirements ({len(school_reqs)}):")
            for req in school_reqs:
                school = req.get("requirement_school", "Unknown")
                level = req.get("level", 0)
                print(f"    - {school} Level {level}")

        return True

    except Exception as e:
        print(f"✗ Error testing armor school requirements: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_custom_weapon_school_requirements():
    """Test custom weapons with school requirements"""
    print("\n=== Testing Custom Weapon School Requirements ===")

    try:
        # Check custom weapons directory
        custom_weapons_dir = project_root / "src" / "custom_weapons"
        if not custom_weapons_dir.exists():
            print("✗ Custom weapons directory not found")
            return False

        import json

        custom_weapons = list(custom_weapons_dir.glob("weapon_*.json"))
        print(f"✓ Found {len(custom_weapons)} custom weapon files")

        weapons_with_school_reqs = 0

        for weapon_file in custom_weapons[:5]:  # Check first 5
            try:
                with open(weapon_file, "r") as f:
                    weapon_data = json.load(f)

                school_reqs = weapon_data.get("school_requirements", [])
                if school_reqs:
                    weapons_with_school_reqs += 1
                    print(f"\n{weapon_file.name}:")
                    print(f"  Name: {weapon_data.get('name', 'Unknown')}")
                    print(f"  School requirements ({len(school_reqs)}):")
                    for req in school_reqs:
                        school = req.get("requirement_school", "Unknown")
                        level = req.get("level", 0)
                        print(f"    - {school} Level {level}")
                else:
                    print(f"{weapon_file.name}: No school requirements")

            except Exception as e:
                print(f"✗ Error reading {weapon_file.name}: {e}")

        print(
            f"\n✓ Found {weapons_with_school_reqs} custom weapons with school requirements"
        )
        return True

    except Exception as e:
        print(f"✗ Error testing custom weapons: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success1 = test_weapon_school_requirements()
    success2 = test_armor_school_requirements()
    success3 = test_custom_weapon_school_requirements()

    overall_success = success1 and success2 and success3
    print(f"\n{'=' * 50}")
    if overall_success:
        print("✓ All school requirements tests passed!")
    else:
        print("✗ Some tests failed")

    sys.exit(0 if overall_success else 1)
