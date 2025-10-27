#!/usr/bin/env python3
"""
Test script to check what fields are available for weapons in GameData
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_weapon_fields():
    """Test weapon field availability"""
    print("Testing weapon field availability...")

    try:
        from TirganachReloaded.tirganach import GameData
        print("✓ GameData imported")
    except ImportError as e:
        print(f"✗ GameData import failed: {e}")
        return

    # Load GameData
    print("Loading GameData.cff...")
    try:
        game_data = GameData("OriginalGameFiles/data/GameData.cff")
        print("✓ GameData loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load GameData: {e}")
        return

    # Get weapons table
    weapons_table = None
    for table_name, table_type in game_data.table_info().items():
        if table_name == "weapons":
            weapons_table = getattr(game_data, table_name)
            break

    if not weapons_table:
        print("✗ No weapons table found")
        return

    print(f"Found {len(weapons_table)} weapons")

    # Check first few weapons
    for i, weapon in enumerate(weapons_table[:5]):
        print(f"\nWeapon {i+1}:")
        print(f"  item_id: {getattr(weapon, 'item_id', 'N/A')}")

        # Check name-related fields
        name_fields = ['name', 'item_name', 'weapon_name']
        for field in name_fields:
            if hasattr(weapon, field):
                value = getattr(weapon, field)
                if value:
                    print(f"  {field}: '{value}'")
                else:
                    print(f"  {field}: (empty)")
            else:
                print(f"  {field}: (field not found)")

        # Show all available fields
        print(f"  Available fields: {list(weapon._fields.keys())}")

    print("\nWeapon field analysis complete!")

if __name__ == "__main__":
    test_weapon_fields()