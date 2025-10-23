#!/usr/bin/env python3
"""
Test script to verify weapon name display functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cff_editor.data_model import CFFDataModel
from pathlib import Path

def test_weapon_names():
    """Test that weapon names are loaded and displayed correctly"""

    # Initialize data model
    data_model = CFFDataModel()

    # Load weapon names
    data_model._load_weapon_names()

    print(f"Loaded {len(data_model.weapon_name_mapping)} weapon names")

    # Test some known weapon IDs
    test_ids = [27, 28, 29, 31, 58]
    for item_id in test_ids:
        name = data_model.get_weapon_name(item_id)
        print(f"Item ID {item_id}: {name}")

    # Load a CFF file to test full functionality
    cff_path = data_model.get_default_file_path()
    print(f"\nLoading CFF file: {cff_path}")

    if data_model.load_file(str(cff_path)):
        print("CFF file loaded successfully")

        # Get weapons table
        weapons_table = data_model.get_table("weapons")
        if weapons_table:
            print(f"Weapons table has {len(weapons_table)} entries")

            # Test first few weapons
            for i, weapon in enumerate(weapons_table[:5]):
                if hasattr(weapon, 'item_id'):
                    item_id = weapon.item_id
                    mapped_name = data_model.get_weapon_name(item_id)
                    print(f"Weapon {i+1}: item_id={item_id}, mapped_name='{mapped_name}'")
        else:
            print("Weapons table not found")
    else:
        print("Failed to load CFF file")

if __name__ == "__main__":
    test_weapon_names()