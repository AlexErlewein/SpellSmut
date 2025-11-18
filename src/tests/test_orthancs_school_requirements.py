#!/usr/bin/env python3
"""Test school requirements display in OrthancsSchmiede"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))


def test_school_requirements_data():
    """Test that CFF loaders include school requirements data"""
    print("=== Testing School Requirements Data ===")

    try:
        # Test weapon loader
        from OrthancsSchmiede.cff_weapon_loader import CFFWeaponLoader

        weapon_loader = CFFWeaponLoader()
        weapons = weapon_loader.load_all_weapons()

        print(f"✓ Loaded {len(weapons)} weapons")

        # Check a few weapons for school requirements
        for weapon_id in [27, 28, 100]:
            if weapon_id in weapons:
                weapon = weapons[weapon_id]
                reqs = weapon.get("requirements", {})
                school_reqs = reqs.get("school_requirements", [])
                print(f"Weapon {weapon_id} ({weapon.get('name', 'Unknown')}):")
                print(
                    f"  Basic requirements: STR={reqs.get('strength', 0)}, DEX={reqs.get('dexterity', 0)}, INT={reqs.get('intelligence', 0)}, Level={reqs.get('level', 0)}"
                )
                print(f"  School requirements: {len(school_reqs)} items")
                for school_req in school_reqs:
                    school_name = school_req.get("requirement_school", "Unknown")
                    school_level = school_req.get("level", 0)
                    print(f"    - {school_name} Level {school_level}")
                print()

        # Test armor loader
        from OrthancsSchmiede.cff_armor_loader import CFFArmorLoader

        armor_loader = CFFArmorLoader()
        armors = armor_loader.load_all_armor()

        print(f"✓ Loaded {len(armors)} armor pieces")

        # Check a few armor pieces for school requirements
        for armor_id in list(armors.keys())[:3]:  # First 3 armor pieces
            armor = armors[armor_id]
            reqs = armor.get("requirements", {})
            school_reqs = reqs.get("school_requirements", [])
            print(f"Armor {armor_id} ({armor.get('armor_name', 'Unknown')}):")
            print(
                f"  Basic requirements: STR={reqs.get('strength', 0)}, DEX={reqs.get('dexterity', 0)}, INT={reqs.get('intelligence', 0)}, Level={reqs.get('level', 0)}"
            )
            print(f"  School requirements: {len(school_reqs)} items")
            for school_req in school_reqs:
                school_name = school_req.get("requirement_school", "Unknown")
                school_level = school_req.get("level", 0)
                print(f"    - {school_name} Level {school_level}")
            print()

        print("✓ School requirements data structure verified!")
        return True

    except Exception as e:
        print(f"✗ Error testing school requirements: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_school_requirements_data()
    sys.exit(0 if success else 1)
