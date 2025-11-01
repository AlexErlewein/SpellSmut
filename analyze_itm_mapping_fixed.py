#!/usr/bin/env python3
"""
Fixed ITM Icon Mapping Analysis
Correctly maps ItemUI entries to Items using item_id field
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

def extract_itm_index_from_handle(handle):
    """Extract ITM texture index from UI handle"""
    if not handle:
        return None
    
    # Pattern 1: ui_itm_equip_XXXX_...
    match = re.search(r'ui_itm_equip_(\d+)', handle)
    if match:
        return int(match.group(1))
    
    # Pattern 2: itm_XXXX in any position
    match = re.search(r'itm_(\d+)', handle)
    if match:
        return int(match.group(1))
    
    # Pattern 3: Just numbers in equip handles
    if 'equip' in handle.lower():
        match = re.search(r'(\d{4})', handle)
        if match:
            return int(match.group(1))
    
    return None

def analyze_itm_mapping_fixed(gamedata, label):
    """Fixed analysis of ITM mapping"""
    print(f"\n=== {label} Fixed Analysis ===")
    
    # Get all tables
    items = gamedata.items
    item_ui = gamedata.item_ui
    
    print(f"Items: {len(items)}")
    print(f"Item UI entries: {len(item_ui)}")
    
    # Create item_id to item mapping
    item_by_id = {}
    for item in items:
        if hasattr(item, 'item_id'):
            item_by_id[item.item_id] = item
    
    print(f"Items mapped by ID: {len(item_by_id)}")
    
    # Build complete mapping
    item_to_ui = {}
    ui_to_itm = {}
    itm_mappings = {}
    
    # Build item to UI mapping
    for ui_entry in item_ui:
        if ui_entry.item_id in item_by_id:
            item = item_by_id[ui_entry.item_id]
            if ui_entry.item_id not in item_to_ui:
                item_to_ui[ui_entry.item_id] = []
            item_to_ui[ui_entry.item_id].append({
                'ui_index': ui_entry.item_ui_index,
                'handle': ui_entry.item_ui_handle,
                'scaled_down': ui_entry.scaled_down
            })
            
            # Extract ITM index
            itm_index = extract_itm_index_from_handle(ui_entry.item_ui_handle)
            if itm_index is not None:
                ui_to_itm[ui_entry.item_ui_handle] = itm_index
                itm_mappings[ui_entry.item_id] = {
                    'item_id': ui_entry.item_id,
                    'item_name': getattr(item, 'name', 'Unknown'),
                    'ui_handle': ui_entry.item_ui_handle,
                    'itm_index': itm_index,
                    'ui_index': ui_entry.item_ui_index
                }
    
    print(f"Items with UI mapping: {len(item_to_ui)}")
    print(f"UI handles with ITM index: {len(ui_to_itm)}")
    print(f"Items with ITM mapping: {len(itm_mappings)}")
    
    # Analyze ITM index distribution
    if itm_mappings:
        itm_indices = [m['itm_index'] for m in itm_mappings.values()]
        print(f"ITM index range: {min(itm_indices)} - {max(itm_indices)}")
        print(f"Unique ITM indices: {len(set(itm_indices))}")
    
    # Show all ITM mappings
    if itm_mappings:
        print(f"\n--- All ITM Mappings ---")
        for item_id, mapping in sorted(itm_mappings.items()):
            print(f"Item {item_id:4d}: '{mapping['item_name']}' -> ITM {mapping['itm_index']:4d} ({mapping['ui_handle']})")
    
    # Analyze handle patterns
    print(f"\n--- UI Handle Pattern Analysis ---")
    handle_patterns = {}
    for ui_entry in item_ui:
        if ui_entry.item_ui_handle:
            pattern = ui_entry.item_ui_handle.split('_')[0] + '_' + ui_entry.item_ui_handle.split('_')[1] if '_' in ui_entry.item_ui_handle else 'other'
            handle_patterns[pattern] = handle_patterns.get(pattern, 0) + 1
    
    for pattern, count in sorted(handle_patterns.items(), key=lambda x: x[1], reverse=True):
        print(f"{pattern:20s}: {count:4d} entries")
    
    # Show sample mappings
    print(f"\n--- Sample Item to UI Mappings ---")
    sample_count = 0
    for item_id, ui_list in list(item_to_ui.items())[:20]:
        if item_id in item_by_id:
            item = item_by_id[item_id]
            print(f"Item {item_id:4d}: '{getattr(item, 'name', 'Unknown')}'")
            for ui_info in ui_list:
                print(f"  -> UI[{ui_info['ui_index']}]: '{ui_info['handle']}'")
                itm_idx = extract_itm_index_from_handle(ui_info['handle'])
                if itm_idx is not None:
                    print(f"     ITM Index: {itm_idx}")
            sample_count += 1
            if sample_count >= 10:
                break
    
    return itm_mappings, item_to_ui, ui_to_itm

def compare_gamedata(original_mappings, modded_mappings):
    """Compare original and modded GameData"""
    print(f"\n=== Comparison Analysis ===")
    
    original_items = set(original_mappings.keys())
    modded_items = set(modded_mappings.keys())
    
    print(f"Original ITM items: {len(original_items)}")
    print(f"Modded ITM items: {len(modded_items)}")
    
    # Check for differences
    added = modded_items - original_items
    removed = original_items - modded_items
    
    if added:
        print(f"Added ITM mappings: {len(added)}")
        for item_id in sorted(added):
            mapping = modded_mappings[item_id]
            print(f"  + Item {item_id}: '{mapping['item_name']}' -> ITM {mapping['itm_index']}")
    
    if removed:
        print(f"Removed ITM mappings: {len(removed)}")
        for item_id in sorted(removed):
            mapping = original_mappings[item_id]
            print(f"  - Item {item_id}: '{mapping['item_name']}' -> ITM {mapping['itm_index']}")
    
    # Check for changed mappings
    common = original_items & modded_items
    changed = []
    for item_id in common:
        if original_mappings[item_id]['itm_index'] != modded_mappings[item_id]['itm_index']:
            changed.append(item_id)
    
    if changed:
        print(f"Changed ITM mappings: {len(changed)}")
        for item_id in sorted(changed):
            orig = original_mappings[item_id]
            mod = modded_mappings[item_id]
            print(f"  ~ Item {item_id}: ITM {orig['itm_index']} -> ITM {mod['itm_index']}")

def main():
    print("Fixed ITM Icon Mapping Analysis...")
    
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
    
    # Load modded GameData
    print("\nLoading modded GameData...")
    modded_files = list(Path("ModdedGameFiles").glob("GameData_*.cff"))
    if not modded_files:
        print("No modded GameData files found")
        return
    
    modded_path = modded_files[0]
    print(f"Using modded GameData: {modded_path.name}")
    
    try:
        modded_gamedata = GameData(str(modded_path))
        print("Modded GameData loaded successfully")
    except Exception as e:
        print(f"Error loading modded GameData: {e}")
        return
    
    # Analyze both
    original_mappings, _, _ = analyze_itm_mapping_fixed(original_gamedata, "Original")
    modded_mappings, _, _ = analyze_itm_mapping_fixed(modded_gamedata, "Modded")
    
    # Compare
    compare_gamedata(original_mappings, modded_mappings)
    
    # Create integration summary
    print(f"\n=== CFF Editor Integration Summary ===")
    print("1. Load ItemUI table alongside Items table")
    print("2. Create item_id -> Item mapping from Items table")
    print("3. For each ItemUI entry, find matching Item by item_id")
    print("4. Extract ITM index from item_ui_handle using regex patterns:")
    print("   - ui_itm_equip_(\\d+) -> primary pattern")
    print("   - itm_(\\d+) -> fallback pattern")
    print("   - (\\d{4}) in equip handles -> last resort")
    print("5. Use ITM index to calculate texture atlas coordinates")
    print("6. Display icon using extracted coordinates")
    
    if original_mappings:
        sample_mapping = list(original_mappings.values())[0]
        print(f"\nExample mapping:")
        print(f"Item ID: {sample_mapping['item_id']}")
        print(f"Item Name: {sample_mapping['item_name']}")
        print(f"UI Handle: {sample_mapping['ui_handle']}")
        print(f"ITM Index: {sample_mapping['itm_index']}")
        print(f"Texture Coordinates: Calculate from ITM {sample_mapping['itm_index']}")

if __name__ == "__main__":
    main()