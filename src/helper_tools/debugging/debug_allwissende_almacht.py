#!/usr/bin/env python3
"""
Debug Allwissende Almacht Tool
==============================

Debug version to check why icons aren't loading.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from TirganachReloaded.cff_editor.data_model import CFFDataModel


def main():
    """Debug the icon loading"""
    print("=== Allwissende Almacht Debug ===")
    
    # Create data model
    data_model = CFFDataModel()
    
    print(f"Icons root: {data_model.icons_root}")
    print(f"Icons root exists: {data_model.icons_root.exists()}")
    
    print(f"Icon index keys: {list(data_model.icon_index.keys())}")
    print(f"Icon index type: {type(data_model.icon_index)}")
    
    if 'icons' in data_model.icon_index:
        icons = data_model.icon_index['icons']
        print(f"Total icons in index: {len(icons)}")
        
        # Show first few icons
        icon_keys = list(icons.keys())[:5]
        print(f"First 5 icon keys: {icon_keys}")
        
        for key in icon_keys:
            icon_info = icons[key]
            print(f"  {key}: {icon_info}")
            
            # Check if file exists
            icon_path = data_model.icons_root / icon_info['path']
            print(f"    Path: {icon_path}")
            print(f"    Exists: {icon_path.exists()}")
    else:
        print("No 'icons' key in icon_index!")
        print(f"Icon index content: {data_model.icon_index}")
    
    # Test the get_all_icons method from Allwissende Almacht
    print("\n=== Testing get_all_icons logic ===")
    
    # Get item icons
    if hasattr(data_model, 'icon_index') and data_model.icon_index:
        icon_entries = data_model.icon_index.get('icons', {})
        print(f"Icon entries count: {len(icon_entries)}")
        
        count = 0
        for icon_key, icon_info in icon_entries.items():
            if not icon_info.get('is_empty', False):
                icon_data = {
                    'name': icon_info.get('name', icon_key),
                    'handle': icon_info.get('handle', ''),
                    'category': icon_info.get('category', 'item'),
                    'path': icon_info.get('path', ''),
                    'atlas': icon_info.get('atlas', ''),
                    'index': icon_info.get('index', 0)
                }
                count += 1
                if count <= 3:  # Show first 3
                    print(f"  Icon {count}: {icon_data}")
                    
                    # Test file existence only (skip QPixmap for now)
                    icon_path = data_model.icons_root / icon_data.get('path', '')
                    if icon_path.exists():
                        file_size = icon_path.stat().st_size
                        print(f"    File exists: {icon_path} ({file_size} bytes)")
                    else:
                        print(f"    File does not exist: {icon_path}")
        
        print(f"Total non-empty icons: {count}")
    else:
        print("No icon_index available!")


if __name__ == "__main__":
    main()