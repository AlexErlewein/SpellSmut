#!/usr/bin/env python3
"""
Test script to verify icon mapping integration
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "TirganachReloaded"))

from cff_editor.data_model import CFFDataModel

def test_icon_mapping():
    """Test that icon mapping is working correctly"""
    
    # Initialize data model
    data_model = CFFDataModel()
    
    print("=== Icon Mapping Test ===")
    print(f"Icon mapping loaded: {len(data_model.icon_mapping.get('item_to_icons', {}))} items")
    print(f"Icon index loaded: {len(data_model.icon_index.get('icons', {}))} icons")
    print(f"Verified mappings: {len(getattr(data_model, 'verified_mappings', {}))} items")
    
    # Test specific armor items
    armor_items = [
        ("armor", 22),   # Should have icon
        ("armor", 100),  # Should have icon
        ("armor", 500),  # Should have icon
    ]
    
    print("\n=== Testing Armor Icons ===")
    for category, item_id in armor_items:
        # Create a mock armor object
        class MockArmor:
            def __init__(self, item_id):
                self.item_id = item_id
        
        armor = MockArmor(item_id)
        icon_path = data_model.get_icon_path(category, armor)
        
        if icon_path:
            print(f"✓ Item {item_id}: {icon_path}")
            # Check if file exists
            if Path(icon_path).exists():
                print(f"  File exists: YES")
            else:
                print(f"  File exists: NO")
        else:
            print(f"✗ Item {item_id}: No icon found")
    
    # Test ITM category specifically
    print("\n=== Testing ITM Category Icons ===")
    itm_files = list(Path("ExtractedAssets/UI/icons_extracted/itm").glob("**/*.png"))
    print(f"ITM icons extracted: {len(itm_files)}")
    
    if itm_files:
        print(f"Sample ITM icons:")
        for i, icon_file in enumerate(itm_files[:5]):
            print(f"  {icon_file}")
    
    # Test icon resolution for ITM handles
    print("\n=== Testing ITM Handle Resolution ===")
    if 'item_to_icons' in data_model.icon_mapping:
        itm_items = [k for k, v in data_model.icon_mapping['item_to_icons'].items() 
                    if any(icon.get('handle', '').startswith('ui_item_') for icon in v)]
        print(f"Items with ui_item_ handles: {len(itm_items)}")
        
        if itm_items:
            sample_items = itm_items[:3]
            for item_id in sample_items:
                icons = data_model.icon_mapping['item_to_icons'][item_id]
                itm_icons = [icon for icon in icons if icon.get('handle', '').startswith('ui_item_')]
                if itm_icons:
                    icon = itm_icons[0]
                    print(f"  Item {item_id}: {icon['handle']} (index {icon['index']})")

if __name__ == "__main__":
    test_icon_mapping()