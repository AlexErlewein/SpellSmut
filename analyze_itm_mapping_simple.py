#!/usr/bin/env python3
"""
Simple analysis of GameData.cff files for ITM icon mapping.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def analyze_gamedata_simple(gamedata, name="GameData"):
    """Simple analysis without relying on annotations."""
    print(f"\n=== Analyzing {name} ===")
    
    # Access tables directly
    try:
        items = gamedata.items
        item_ui = gamedata.item_ui
        weapons = gamedata.weapons
        armor = gamedata.armor
        
        print(f"Items: {len(items)}")
        print(f"Weapons: {len(weapons)}")
        print(f"Armor: {len(armor)}")
        print(f"Item UI entries: {len(item_ui)}")
        
        # Analyze item_ui structure
        if len(item_ui) > 0:
            sample_ui = item_ui[0]
            print(f"\n--- Sample ItemUI Entry ---")
            print(f"item_id: {sample_ui.item_id}")
            print(f"item_ui_index: {sample_ui.item_ui_index}")
            print(f"item_ui_handle: '{sample_ui.item_ui_handle}'")
            print(f"scaled_down: {sample_ui.scaled_down}")
        
        # Analyze UI handle patterns
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
        
        print(f"\n--- UI Handle Analysis ---")
        print(f"Unique handle patterns: {len(handle_patterns)}")
        
        # Show ITM-related patterns
        itm_handles = [h for h in handle_patterns if 'itm' in h.lower()]
        print(f"Handles containing 'itm': {len(itm_handles)}")
        
        for handle in sorted(itm_handles)[:15]:
            print(f"  '{handle}'")
        
        # Map some items to UI
        print(f"\n--- Item to UI Mapping (Sample) ---")
        items_with_ui = 0
        for item in items[:30]:  # First 30 items
            if item.item_id in ui_handles:
                items_with_ui += 1
                ui_info = ui_handles[item.item_id]
                print(f"Item {item.item_id}: '{item.name}' -> '{ui_info['handle']}'")
        
        print(f"Items with UI (in sample): {items_with_ui}")
        
        # Extract ITM index mappings
        print(f"\n--- ITM Index Extraction ---")
        itm_mappings = {}
        
        for item_id, ui_info in ui_handles.items():
            handle = ui_info['handle']
            
            if 'itm' in handle.lower():
                # Try to extract numeric index
                clean_handle = handle.lower().replace('\\', '/').split('/')[-1]
                if clean_handle.endswith('.tga'):
                    clean_handle = clean_handle[:-4]
                
                # Extract numeric parts
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
        
        for item_id, mapping in list(itm_mappings.items())[:15]:
            print(f"Item {item_id} -> ITM {mapping['itm_index']} ('{mapping['handle']}')")
        
        return ui_handles, itm_mappings
        
    except AttributeError as e:
        print(f"Error accessing tables: {e}")
        return {}, {}

def main():
    """Main analysis function."""
    print("Simple ITM Icon Mapping Analysis...")
    
    # File paths
    original_path = "OriginalGameFiles/data/GameData.cff"
    modded_path = "ModdedGameFiles/GameData_MyCustomMod_20251019_100557.cff"
    
    if not os.path.exists(original_path):
        print(f"Error: Original file not found: {original_path}")
        return
    
    # Load and analyze original
    try:
        from TirganachReloaded.tirganach import GameData
        
        print("Loading original GameData...")
        original_gd = GameData(original_path)
        original_ui_handles, original_itm_mappings = analyze_gamedata_simple(original_gd, "Original")
        
    except Exception as e:
        print(f"Error with original file: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Load and analyze modded if available
    if os.path.exists(modded_path):
        try:
            print("\nLoading modded GameData...")
            modded_gd = GameData(modded_path)
            modded_ui_handles, modded_itm_mappings = analyze_gamedata_simple(modded_gd, "Modded")
            
            # Simple comparison
            print(f"\n--- Comparison ---")
            print(f"Original UI entries: {len(original_ui_handles)}")
            print(f"Modded UI entries: {len(modded_ui_handles)}")
            print(f"Original ITM mappings: {len(original_itm_mappings)}")
            print(f"Modded ITM mappings: {len(modded_itm_mappings)}")
            
        except Exception as e:
            print(f"Error with modded file: {e}")
    
    print(f"\n=== Key Findings ===")
    print("1. ItemUI table links items to visual representations")
    print("2. item_ui_handle contains texture paths (often ITM files)")
    print("3. item_ui_index allows multiple UI entries per item")
    print("4. ITM texture names often contain numeric indices")
    print("5. Mapping: item_id -> item_ui_handle -> ITM texture index")

if __name__ == "__main__":
    main()