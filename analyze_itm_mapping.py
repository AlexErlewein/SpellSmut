#!/usr/bin/env python3
"""
Analyze GameData.cff files to understand ITM icon mapping structure.
Focus on understanding how item_ui entries connect to items and ITM texture atlases.
"""

import sys
import os
from pathlib import Path

# Add the tirganach library to the path
sys.path.insert(0, str(Path(__file__).parent / "src" / "TirganachReloaded"))

from tirganach import GameData

def analyze_item_ui_mapping(gamedata, name="GameData"):
    """Analyze the item_ui table and its relationship to items."""
    print(f"\n=== Analyzing {name} ===")
    
    # Get basic table info
    items = gamedata.items
    item_ui = gamedata.item_ui
    weapons = gamedata.weapons
    armor = gamedata.armor
    
    print(f"Items: {len(items)}")
    print(f"Weapons: {len(weapons)}")
    print(f"Armor: {len(armor)}")
    print(f"Item UI entries: {len(item_ui)}")
    
    # Analyze item_ui structure
    print(f"\n--- ItemUI Structure ---")
    if len(item_ui) > 0:
        sample_ui = item_ui[0]
        print(f"Sample ItemUI fields: {sample_ui.__dict__.keys()}")
        print(f"Sample ItemUI: item_id={sample_ui.item_id}, item_ui_index={sample_ui.item_ui_index}, item_ui_handle='{sample_ui.item_ui_handle}'")
    
    # Analyze item_ui_handle patterns
    ui_handles = {}
    handle_patterns = set()
    
    for ui_entry in item_ui:
        handle = ui_entry.item_ui_handle
        if handle:
            handle_patterns.add(handle)
            ui_handles[ui_entry.item_id] = {
                'handle': handle,
                'ui_index': ui_entry.item_ui_index,
                'scaled_down': ui_entry.scaled_down
            }
    
    print(f"\n--- ItemUI Handle Analysis ---")
    print(f"Unique handle patterns: {len(handle_patterns)}")
    
    # Show some handle patterns
    pattern_samples = sorted(list(handle_patterns))[:20]
    for pattern in pattern_samples:
        print(f"  '{pattern}'")
    
    # Analyze ITM patterns in handles
    itm_handles = [h for h in handle_patterns if 'itm' in h.lower()]
    print(f"\nHandles containing 'itm': {len(itm_handles)}")
    for handle in sorted(itm_handles)[:10]:
        print(f"  '{handle}'")
    
    # Map items to UI handles
    print(f"\n--- Item to UI Mapping ---")
    items_with_ui = 0
    items_without_ui = 0
    
    for item in items[:50]:  # Sample first 50 items
        if item.item_id in ui_handles:
            items_with_ui += 1
            ui_info = ui_handles[item.item_id]
            print(f"Item {item.item_id}: '{item.name}' -> UI: '{ui_info['handle']}' (index: {ui_info['ui_index']})")
        else:
            items_without_ui += 1
    
    print(f"\nItems with UI (sample): {items_with_ui}")
    print(f"Items without UI (sample): {items_without_ui}")
    
    return ui_handles, handle_patterns

def analyze_weapon_armor_mapping(gamedata):
    """Analyze how weapons and armor map to item_ui entries."""
    print(f"\n--- Weapon/Armor UI Mapping ---")
    
    weapons = gamedata.weapons
    armor = gamedata.armor
    item_ui = gamedata.item_ui
    items = gamedata.items
    
    # Create lookup for item_ui by item_id
    ui_lookup = {ui.item_id: ui for ui in item_ui}
    
    # Check weapons
    weapons_with_ui = 0
    for weapon in weapons[:20]:  # Sample first 20
        if weapon.item_id in ui_lookup:
            weapons_with_ui += 1
            ui = ui_lookup[weapon.item_id]
            item = items.where(item_id=weapon.item_id)
            item_name = item[0].name if item else "Unknown"
            print(f"Weapon {weapon.item_id}: '{item_name}' -> UI: '{ui.item_ui_handle}'")
    
    # Check armor
    armor_with_ui = 0
    for armor_piece in armor[:20]:  # Sample first 20
        if armor_piece.item_id in ui_lookup:
            armor_with_ui += 1
            ui = ui_lookup[armor_piece.item_id]
            item = items.where(item_id=armor_piece.item_id)
            item_name = item[0].name if item else "Unknown"
            print(f"Armor {armor_piece.item_id}: '{item_name}' -> UI: '{ui.item_ui_handle}'")
    
    print(f"Weapons with UI (sample): {weapons_with_ui}")
    print(f"Armor with UI (sample): {armor_with_ui}")

def extract_itm_index_mapping(ui_handles, handle_patterns):
    """Extract ITM icon index mapping from item_ui handles."""
    print(f"\n--- ITM Index Mapping ---")
    
    itm_mappings = {}
    
    # Look for patterns like "itm_XXXX" where XXXX might be the index
    for item_id, ui_info in ui_handles.items():
        handle = ui_info['handle']
        
        # Try to extract ITM index from handle
        if 'itm' in handle.lower():
            # Remove extension and path
            clean_handle = handle.lower().replace('\\', '/').split('/')[-1]
            if clean_handle.endswith('.tga'):
                clean_handle = clean_handle[:-4]
            
            # Try to extract numeric part
            parts = clean_handle.split('_')
            for part in parts:
                if part.isdigit():
                    itm_mappings[item_id] = {
                        'itm_index': int(part),
                        'handle': handle,
                        'ui_index': ui_info['ui_index']
                    }
                    break
    
    print(f"Items with ITM index mapping: {len(itm_mappings)}")
    
    # Show some mappings
    for item_id, mapping in list(itm_mappings.items())[:20]:
        print(f"Item {item_id} -> ITM index {mapping['itm_index']} ('{mapping['handle']}')")
    
    return itm_mappings

def compare_gamedata_files(original_ui_handles, modded_ui_handles):
    """Compare original and modded GameData files."""
    print(f"\n--- Comparing Original vs Modded ---")
    
    original_items = set(original_ui_handles.keys())
    modded_items = set(modded_ui_handles.keys())
    
    print(f"Original items with UI: {len(original_items)}")
    print(f"Modded items with UI: {len(modded_items)}")
    
    # Find differences
    added_items = modded_items - original_items
    removed_items = original_items - modded_items
    common_items = original_items & modded_items
    
    print(f"Added items: {len(added_items)}")
    print(f"Removed items: {len(removed_items)}")
    print(f"Common items: {len(common_items)}")
    
    # Check for handle changes in common items
    handle_changes = 0
    for item_id in list(common_items)[:50]:  # Sample first 50
        if original_ui_handles[item_id]['handle'] != modded_ui_handles[item_id]['handle']:
            handle_changes += 1
            print(f"Item {item_id}: '{original_ui_handles[item_id]['handle']}' -> '{modded_ui_handles[item_id]['handle']}'")
    
    print(f"Handle changes (sample): {handle_changes}")

def main():
    """Main analysis function."""
    print("Analyzing GameData.cff files for ITM icon mapping...")
    
    # File paths
    original_path = "OriginalGameFiles/data/GameData.cff"
    modded_path = "ModdedGameFiles/GameData_MyCustomMod_20251019_100557.cff"
    
    if not os.path.exists(original_path):
        print(f"Error: Original file not found: {original_path}")
        return
    
    # Load original GameData
    try:
        print("Loading original GameData...")
        original_gd = GameData(original_path)
        original_ui_handles, original_patterns = analyze_item_ui_mapping(original_gd, "Original GameData")
        analyze_weapon_armor_mapping(original_gd)
        original_itm_mapping = extract_itm_index_mapping(original_ui_handles, original_patterns)
    except Exception as e:
        print(f"Error loading original GameData: {e}")
        return
    
    # Load modded GameData if available
    if os.path.exists(modded_path):
        try:
            print("\nLoading modded GameData...")
            modded_gd = GameData(modded_path)
            modded_ui_handles, modded_patterns = analyze_item_ui_mapping(modded_gd, "Modded GameData")
            analyze_weapon_armor_mapping(modded_gd)
            modded_itm_mapping = extract_itm_index_mapping(modded_ui_handles, modded_patterns)
            
            # Compare files
            compare_gamedata_files(original_ui_handles, modded_ui_handles)
        except Exception as e:
            print(f"Error loading modded GameData: {e}")
    else:
        print(f"Modded file not found: {modded_path}")
    
    print(f"\n=== Summary ===")
    print("1. ItemUI table contains item_ui_handle fields that reference ITM texture files")
    print("2. Each item can have multiple UI entries (item_ui_index)")
    print("3. item_ui_handle typically contains paths like 'itm_XXXX.tga' where XXXX is the icon index")
    print("4. The mapping connects item_id -> item_ui_handle -> ITM texture atlas index")
    print("5. Weapons and armor use the same item_ui table through their item_id")

if __name__ == "__main__":
    main()