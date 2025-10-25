#!/usr/bin/env python3
"""
Test script specifically for ui_item_ icon resolution
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "TirganachReloaded"))

from cff_editor.data_model import CFFDataModel

def test_ui_item_icons():
    """Test ui_item_ icon resolution"""
    
    data_model = CFFDataModel()
    
    print("=== Testing ui_item_ Icon Resolution ===")
    
    # Test items that have ui_item_ handles
    test_items = [25, 26, 27, 28, 31]  # These have ui_item_ handles from debug output
    
    for item_id in test_items:
        # Create a mock item object
        class MockItem:
            def __init__(self, item_id):
                self.item_id = item_id
        
        item = MockItem(item_id)
        icon_path = data_model.get_icon_path("armor", item)  # Try armor category first
        
        print(f"\n--- Item {item_id} ---")
        
        # Show what mappings we have
        item_id_str = str(item_id)
        if item_id_str in data_model.icon_mapping.get('item_to_icons', {}):
            icons = data_model.icon_mapping['item_to_icons'][item_id_str]
            for icon in icons:
                handle = icon.get('handle', '')
                print(f"  Handle: {handle}")
                print(f"  Index: {icon.get('index')}")
                print(f"  Scaled: {icon.get('scaled')}")
        
        if icon_path:
            print(f"✓ Icon found: {icon_path}")
            if Path(icon_path).exists():
                print(f"  File exists: YES")
                size = Path(icon_path).stat().st_size
                print(f"  File size: {size} bytes")
            else:
                print(f"  File exists: NO")
        else:
            print(f"✗ No icon found")
            
        # Try with different categories
        for category in ['items', 'weapons', 'item']:
            icon_path_cat = data_model.get_icon_path(category, item)
            if icon_path_cat:
                print(f"  Found in {category}: {icon_path_cat}")
                break

if __name__ == "__main__":
    test_ui_item_icons()