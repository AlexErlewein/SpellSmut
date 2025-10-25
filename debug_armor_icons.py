#!/usr/bin/env python3
"""
Debug script to check why armor icons aren't found
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "TirganachReloaded"))

from cff_editor.data_model import CFFDataModel

def debug_armor_icons():
    """Debug armor icon mapping"""
    
    data_model = CFFDataModel()
    
    print("=== Debugging Armor Icons ===")
    
    # Check if armor items exist in mapping
    armor_items = [22, 100, 500]
    
    for item_id in armor_items:
        item_id_str = str(item_id)
        print(f"\n--- Item {item_id} ---")
        
        if item_id_str in data_model.icon_mapping.get('item_to_icons', {}):
            icons = data_model.icon_mapping['item_to_icons'][item_id_str]
            print(f"Found {len(icons)} icon mappings:")
            for i, icon in enumerate(icons):
                print(f"  {i+1}: {icon}")
        else:
            print("No icon mappings found")
        
        # Check if item has ui_item_ handle in item_to_icons
        if item_id_str in data_model.icon_mapping.get('item_to_icons', {}):
            icons = data_model.icon_mapping['item_to_icons'][item_id_str]
            for icon in icons:
                handle = icon.get('handle', '')
                print(f"Handle: {handle}")
                
                # Check if handle starts with ui_item_
                if handle.startswith('ui_item_'):
                    print("✓ Handle starts with ui_item_ - should use ITM category")
                else:
                    print(f"✗ Handle doesn't start with ui_item_: {handle}")
        else:
            print("No handle found")
    
    # Check some items that do have ui_item_ handles
    print("\n=== Items with ui_item_ handles ===")
    item_to_icons = data_model.icon_mapping.get('item_to_icons', {})
    ui_item_items = []
    
    for item_id, icons in item_to_icons.items():
        for icon in icons:
            handle = icon.get('handle', '')
            if handle.startswith('ui_item_'):
                ui_item_items.append((item_id, handle))
                break  # Just need one per item
    
    print(f"Found {len(ui_item_items)} items with ui_item_ handles")
    if ui_item_items:
        print("Sample items:")
        for i, (item_id, handle) in enumerate(ui_item_items[:5]):
            print(f"  Item {item_id}: {handle}")
    
    # Check ITM directory structure
    print("\n=== ITM Directory Structure ===")
    itm_root = Path("ExtractedAssets/UI/icons_extracted/itm")
    if itm_root.exists():
        atlases = sorted([d for d in itm_root.iterdir() if d.is_dir()])
        print(f"Found {len(atlases)} atlases")
        
        for atlas in atlases[:3]:
            icons = sorted(list(atlas.glob("*.png")))
            print(f"  {atlas.name}: {len(icons)} icons")
            if icons:
                print(f"    Sample: {icons[0].name} - {icons[0].stat().st_size} bytes")
    else:
        print("ITM directory not found")

if __name__ == "__main__":
    debug_armor_icons()