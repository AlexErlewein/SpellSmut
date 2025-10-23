#!/usr/bin/env python3
"""
Test script to verify element name extraction with weapon names
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from cff_editor.data_model import CFFDataModel

class MockElementTable:
    """Mock element table for testing name extraction"""
    def __init__(self, data_model):
        self.data_model = data_model

    def _get_element_name(self, element) -> str:
        """Extract name from element, trying common name fields"""
        # Special handling for weapons - check mapping first
        if self.data_model.current_category == "weapons":
            if hasattr(element, 'item_id'):
                weapon_name = self.data_model.get_weapon_name(element.item_id)
                if weapon_name:
                    return weapon_name

        # Try common name fields in order of preference
        name_fields = ['name', 'item_name', 'spell_name', 'creature_name', 'building_name']

        for field_name in name_fields:
            if hasattr(element, field_name):
                name_value = getattr(element, field_name)
                if name_value:
                    return str(name_value)

        # Fallback: try to construct a name from ID fields
        id_fields = ['item_id', 'spell_id', 'creature_id', 'building_id']
        for field_name in id_fields:
            if hasattr(element, field_name):
                id_value = getattr(element, field_name)
                if id_value is not None:
                    return f"{field_name.replace('_id', '').title()} {id_value}"

        # Last resort
        return "Unknown"

def test_element_name_extraction():
    """Test that element name extraction works with weapon mapping"""

    # Load real data model to get weapon mappings
    real_data_model = CFFDataModel()
    real_data_model._load_weapon_names()

    # Create mock element table for testing
    table = MockElementTable(real_data_model)

    # Create mock weapon elements
    class MockWeapon:
        def __init__(self, item_id):
            self.item_id = item_id

    # Test weapon name extraction
    real_data_model.current_category = "weapons"
    test_weapons = [
        MockWeapon(27),  # Flameblade Dagger
        MockWeapon(28),  # Flameblade Sword
        MockWeapon(999), # Non-existent weapon
    ]

    print("Testing weapon name extraction:")
    for weapon in test_weapons:
        name = table._get_element_name(weapon)
        print(f"  Weapon item_id={weapon.item_id}: '{name}'")

    # Test with non-weapon category
    real_data_model.current_category = "items"
    print("\nTesting with 'items' category (should not use weapon mapping):")
    for weapon in test_weapons[:2]:  # Only test first 2
        name = table._get_element_name(weapon)
        print(f"  Item item_id={weapon.item_id}: '{name}'")

if __name__ == "__main__":
    test_element_name_extraction()