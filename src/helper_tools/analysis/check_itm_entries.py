#!/usr/bin/env python3
"""
Check all ITM-related entries in ItemUI
"""

import sys
import os
import re
from pathlib import Path

# Add the src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from TirganachReloaded.tirganach.structure import GameData
    from TirganachReloaded.tirganach.entities import Item, ItemUI
except ImportError as e:
    print(f"Error importing tirganach library: {e}")
    sys.exit(1)

def check_itm_entries(gamedata, label):
    """Check all ITM-related entries"""
    print(f"\n=== {label} ITM Entries ===")
    
    items = gamedata.items
    item_ui = gamedata.item_ui
    
    # Create item_id to item mapping
    item_by_id = {}
    for item in items:
        if hasattr(item, 'item_id'):
            item_by_id[item.item_id] = item
    
    # Find all ITM-related entries
    itm_entries = []
    equip_entries = []
    
    for ui_entry in item_ui:
        handle = ui_entry.item_ui_handle.lower() if ui_entry.item_ui_handle else ""
        
        if 'itm' in handle:
            itm_entries.append(ui_entry)
        
        if 'equip' in handle:
            equip_entries.append(ui_entry)
    
    print(f"Total UI entries: {len(item_ui)}")
    print(f"Entries with 'itm' in handle: {len(itm_entries)}")
    print(f"Entries with 'equip' in handle: {len(equip_entries)}")
    
    # Show ITM entries
    if itm_entries:
        print(f"\n--- ITM Entries ---")
        for ui_entry in itm_entries:
            item = item_by_id.get(ui_entry.item_id)
            item_name = getattr(item, 'name', 'Unknown') if item else 'Not Found'
            print(f"Item {ui_entry.item_id:4d}: '{item_name}'")
            print(f"  UI[{ui_entry.item_ui_index}]: '{ui_entry.item_ui_handle}'")
            print(f"  Scaled: {ui_entry.scaled_down}")
            
            # Try to extract index
            handle = ui_entry.item_ui_handle
            patterns = [
                (r'ui_itm_equip_(\d+)', 'ui_itm_equip_XXXX'),
                (r'itm_(\d+)', 'itm_XXXX'),
                (r'equip.*?(\d{4})', 'equip_XXXX'),
                (r'(\d{4})', 'any_4digit')
            ]
            
            print(f"  Pattern matches:")
            for pattern, desc in patterns:
                match = re.search(pattern, handle)
                if match:
                    print(f"    {desc}: {match.group(1)}")
            print()
    
    # Show some equip entries with numbers
    print(f"\n--- Equip Entries with Numbers (first 10) ---")
    numeric_equip = []
    for ui_entry in equip_entries:
        handle = ui_entry.item_ui_handle
        if re.search(r'\d{4}', handle):
            numeric_equip.append(ui_entry)
    
    for ui_entry in numeric_equip[:10]:
        item = item_by_id.get(ui_entry.item_id)
        item_name = getattr(item, 'name', 'Unknown') if item else 'Not Found'
        handle = ui_entry.item_ui_handle
        
        # Extract 4-digit numbers
        numbers = re.findall(r'\d{4}', handle)
        
        print(f"Item {ui_entry.item_id:4d}: '{item_name}'")
        print(f"  UI[{ui_entry.item_ui_index}]: '{handle}'")
        print(f"  Numbers: {numbers}")
        print()

def main():
    print("Checking ITM Entries...")
    
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
    
    check_itm_entries(original_gamedata, "Original")

if __name__ == "__main__":
    main()