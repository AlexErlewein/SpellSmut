#!/usr/bin/env python3
"""
Test script to verify armor name display functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cff_editor.data_model import CFFDataModel

def test_armor_names():
    """Test that armor names are loaded and displayed correctly"""

    # Initialize data model
    data_model = CFFDataModel()

    # Load armor names
    data_model._load_armor_names()

    print(f"Loaded {len(data_model.armor_name_mapping)} armor names")

    # Test some known armor IDs
    test_ids = [72, 73, 74, 80, 343]
    for item_id in test_ids:
        name = data_model.get_armor_name(item_id)
        print(f"Item ID {item_id}: {name}")

    # Load a CFF file to test full functionality
    from pathlib import Path
    cff_path = data_model.get_default_file_path()
    print(f"\nLoading CFF file: {cff_path}")

    if data_model.load_file(str(cff_path)):
        print("CFF file loaded successfully")

        # Get armor table
        armor_table = data_model.get_table("armor")
        if armor_table:
            print(f"Armor table has {len(armor_table)} entries")

            # Test first few armor pieces
            for i, armor in enumerate(armor_table[:5]):
                if hasattr(armor, 'item_id'):
                    item_id = armor.item_id
                    mapped_name = data_model.get_armor_name(item_id)
                    print(f"Armor {i+1}: item_id={item_id}, mapped_name='{mapped_name}'")
        else:
            print("Armor table not found")
    else:
        print("Failed to load CFF file")

if __name__ == "__main__":
    test_armor_names()