#!/usr/bin/env python3
"""
Debug icon path resolution step by step
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "TirganachReloaded"))

from cff_editor.data_model import CFFDataModel

def debug_icon_path_resolution():
    """Debug icon path resolution step by step"""
    
    data_model = CFFDataModel()
    
    print("=== Debugging Icon Path Resolution ===")
    
    # Test with item 25 (has ui_item_rune_hero_ocre_default)
    item_id = 25
    item_id_str = str(item_id)
    
    print(f"\nTesting Item {item_id}")
    
    # Check if item exists in mapping
    if item_id_str not in data_model.icon_mapping.get('item_to_icons', {}):
        print("✗ Item not found in mapping")
        return
    
    icons = data_model.icon_mapping['item_to_icons'][item_id_str]
    print(f"Found {len(icons)} icon mappings")
    
    # Find primary icon (index 1)
    primary_icon = None
    for icon in icons:
        if icon.get('index') == 1:
            primary_icon = icon
            break
    
    if not primary_icon:
        print("✗ No primary icon (index 1) found")
        return
    
    print(f"Primary icon: {primary_icon}")
    
    # Get handle and determine category
    handle = primary_icon.get('handle', '')
    print(f"Handle: {handle}")
    
    icon_category = 'itm' if handle.startswith('ui_item_') else \
                   'spell' if handle.startswith('ui_spell_') else 'item'
    print(f"Icon category: {icon_category}")
    
    # Try different atlas numbers
    print(f"\nTrying atlas numbers 0-15:")
    for atlas_num in range(16):  # Try all 16 atlases
        icon_path = data_model.icons_root / icon_category / f"atlas_{atlas_num}" / f"icon_{primary_icon['index']:03d}.png"
        
        print(f"  Atlas {atlas_num}: {icon_path}")
        
        if icon_path.exists():
            print(f"    ✓ File exists")
            
            # Check icon index
            icon_key = f"{icon_category}_{atlas_num}_{primary_icon['index']:03d}"
            print(f"    Icon key: {icon_key}")
            
            if icon_key in data_model.icon_index.get('icons', {}):
                icon_info = data_model.icon_index['icons'][icon_key]
                print(f"    Icon info: {icon_info}")
                
                if not icon_info.get('is_empty', False):
                    print(f"    ✓ SUCCESS: Found non-empty icon")
                    print(f"    Path: {icon_path}")
                    return
                else:
                    print(f"    ✗ Icon is empty")
            else:
                print(f"    ✗ Icon key not found in index")
        else:
            print(f"    ✗ File does not exist")
    
    print(f"\n✗ No valid icon found for item {item_id}")
    
    # Debug: show what ITM icons we actually have
    print(f"\n=== Debug: ITM Directory Structure ===")
    itm_root = data_model.icons_root / "itm"
    if itm_root.exists():
        atlases = sorted([d for d in itm_root.iterdir() if d.is_dir()])
        print(f"Found {len(atlases)} atlases")
        
        # Check first few atlases for icon_001.png
        for atlas in atlases[:3]:
            icon_001 = atlas / "icon_001.png"
            if icon_001.exists():
                size = icon_001.stat().st_size
                print(f"  {atlas.name}/icon_001.png: {size} bytes")
            else:
                print(f"  {atlas.name}/icon_001.png: MISSING")

if __name__ == "__main__":
    debug_icon_path_resolution()