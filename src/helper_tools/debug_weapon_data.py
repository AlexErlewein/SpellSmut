#!/usr/bin/env python3
"""Debug test to check weapon data from GameData.cff"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def debug_weapon_data():
    """Debug weapon data to see what's actually loaded"""
    print("=== Debug Weapon Data ===")

    try:
        from TirganachReloaded.tirganach import GameData

        # Load game data
        cff_path = os.path.join(
            os.path.dirname(__file__), "OriginalGameFiles", "data", "GameData.cff"
        )
        gd = GameData(cff_path)
        print("✓ Loaded GameData.cff")

        # Get weapon with ID 27 (Flameblade Dagger)
        weapons = gd.weapons.where(item_id=27)
        if weapons:
            weapon = weapons[0]
            print(f"\n✓ Found weapon: {weapon.item_id}")
            print(f"  Raw weapon entity fields:")
            print(f"    item_id: {weapon.item_id}")
            print(f"    min_damage: {weapon.min_damage}")
            print(f"    max_damage: {weapon.max_damage}")
            print(f"    min_range: {weapon.min_range}")
            print(f"    max_range: {weapon.max_range}")
            print(f"    speed: {weapon.speed}")
            print(f"    weapon_type: {weapon.weapon_type}")
            print(f"    material: {weapon.material}")

            # Check if item data is available
            if hasattr(weapon, "item") and weapon.item:
                item = weapon.item
                print(f"\n  Related item data:")
                print(f"    name: {getattr(item, 'name', 'N/A')}")
                print(f"    selling_price: {getattr(item, 'selling_price', 'N/A')}")
                print(f"    buying_price: {getattr(item, 'buying_price', 'N/A')}")
                print(f"    item_set_id: {getattr(item, 'item_set_id', 'N/A')}")

                # Check for requirements
                if hasattr(item, "requirements") and item.requirements:
                    print(f"    requirements: {len(item.requirements)} requirement(s)")
                    for i, req in enumerate(item.requirements):
                        print(f"      Req {i}: {req}")
                        if (
                            hasattr(req, "requirement_school")
                            and req.requirement_school
                        ):
                            print(
                                f"        School: {req.requirement_school.name}, Level: {req.level}"
                            )
                        else:
                            print(f"        No school requirement")
                else:
                    print(f"    requirements: None")
            else:
                print(f"\n  No related item data found")

        else:
            print("✗ Weapon with ID 27 not found")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_weapon_data()
