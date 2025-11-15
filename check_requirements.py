#!/usr/bin/env python3
"""Check for weapons with school requirements in the game data"""

import sys

sys.path.append("src")

from TirganachReloaded.tirganach import GameData


def check_weapons_with_requirements():
    """Check all weapons for school requirements"""

    # Load GameData.cff
    gd = GameData("OriginalGameFiles/data/GameData.cff")
    print(f"✓ Loaded GameData.cff")

    weapons_with_requirements = []
    weapons_checked = 0

    # Check all weapons
    for weapon in gd.weapons:
        weapons_checked += 1
        item = weapon.item

        if hasattr(item, "requirements") and item.requirements is not None:
            weapons_with_requirements.append(
                (weapon.item_id, item.name, item.requirements)
            )
            print(
                f"Weapon {weapon.item_id} ({item.name}): requirements = {item.requirements}"
            )

    print(f"\nChecked {weapons_checked} weapons")
    print(f"Found {len(weapons_with_requirements)} weapons with requirements")

    if not weapons_with_requirements:
        print("\nNo weapons have requirements in the original game data!")
        print("This means school requirements were not used in SpellForce")

        # Let's check what the requirements structure looks like for non-weapon items
        print("\nChecking non-weapon items for requirements...")
        items_checked = 0
        items_with_requirements = []

        for item in gd.items:
            items_checked += 1
            if hasattr(item, "requirements") and item.requirements is not None:
                items_with_requirements.append(
                    (item.item_id, item.name, item.requirements)
                )
                if len(items_with_requirements) <= 5:  # Show first 5 examples
                    print(
                        f"Item {item.item_id} ({item.name}): requirements = {item.requirements}"
                    )

        print(f"\nChecked {items_checked} items")
        print(f"Found {len(items_with_requirements)} items with requirements")


if __name__ == "__main__":
    check_weapons_with_requirements()
