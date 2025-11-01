#!/usr/bin/env python3
"""
Debug ItemUI mapping to understand the structure
"""

import sys
import os
from pathlib import Path

# Add the tirganach library to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "TirganachReloaded"))

try:
    from tirganach.structure import GameData
    from tirganach.entities import Item, ItemUI
except ImportError as e:
    print(f"Error importing tirganach library: {e}")
    sys.exit(1)

def debug_item_ui_structure(gamedata, label):
    """Debug the ItemUI structure"""
    print(f"\n=== {label} Debug ===")
    
    items = gamedata.items
    item_ui = gamedata.item_ui
    
    print(f"Items: {len(items)}")
    print(f"Item UI entries: {len(item_ui)}")
    
    # Check first few ItemUI entries
    print(f"\n--- First 5 ItemUI entries ---")
    for i, ui_entry in enumerate(item_ui[:5]):
        print(f"UI Entry {i}:")
        print(f"  item_id: {ui_entry.item_id}")
        print(f"  item_ui_index: {ui_entry.item_ui_index}")
        print(f"  item_ui_handle: '{ui_entry.item_ui_handle}'")
        print(f"  scaled_down: {ui_entry.scaled_down}")
        
        # Try to find matching item
        if ui_entry.item_id < len(items):
            item = items[ui_entry.item_id]
            print(f"  -> Found item: '{getattr(item, 'name', 'Unknown')}'")
        else:
            print(f"  -> No item found for ID {ui_entry.item_id}")
        print()
    
    # Check item_id range
    item_ids = [ui.item_id for ui in item_ui]
    print(f"Item ID range: {min(item_ids)} - {max(item_ids)}")
    print(f"Items length: {len(items)}")
    
    # Check some sample mappings
    print(f"\n--- Sample ID mappings ---")
    sample_ids = [22, 25, 26, 27, 28]  # From previous analysis
    for item_id in sample_ids:
        if item_id < len(items):
            item = items[item_id]
            print(f"Item {item_id}: '{getattr(item, 'name', 'Unknown')}'")
            
            # Find UI entries
            ui_entries = [ui for ui in item_ui if ui.item_id == item_id]
            for ui in ui_entries:
                print(f"  -> UI: '{ui.item_ui_handle}' (index {ui.item_ui_index})")
        else:
            print(f"Item {item_id}: Not found in items array")
        print()

def main():
    print("Debug ItemUI Mapping...")
    
    # Load original GameData
    print("\nLoading original GameData...")
    original_path = "OriginalGameFiles/data/GameData.cff"
    if not os.path.exists(original_path):
        print(f"Original GameData not found at {original_path}")
        return
    
    try:
        original_gamedata = GameData(original_path)
        print("Original GameData loaded successfully")
    except Exception as e:
        print(f"Error loading original GameData: {e}")
        return
    
    debug_item_ui_structure(original_gamedata, "Original")

if __name__ == "__main__":
    main()