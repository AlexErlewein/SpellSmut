#!/usr/bin/env python3
"""
Direct analysis of GameData.cff files for ITM icon mapping.
Bypasses annotation issues by accessing tables directly.
"""

import sys
import os
from pathlib import Path

# Add tirganach library to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "TirganachReloaded"))

def analyze_gamedata_direct(gamedata, name="GameData"):
    """Direct analysis by accessing table attributes."""
    print(f"\n=== Analyzing {name} ===")
    
    try:
        # Access tables directly - they should be populated after initialization
        items = getattr(gamedata, 'items', None)
        item_ui = getattr(gamedata, 'item_ui', None)
        weapons = getattr(gamedata, 'weapons', None)
        armor = getattr(gamedata, 'armor', None)
        
        if items is None or item_ui is None:
            print("Error: Could not access items or item_ui tables")
            return {}, {}
        
        print(f"Items: {len(items)}")
        print(f"Weapons: {len(weapons) if weapons else 0}")
        print(f"Armor: {len(armor) if armor else 0}")
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
        
        # Show some non-ITM patterns for comparison
        non_itm_handles = [h for h in handle_patterns if 'itm' not in h.lower() and h]
        print(f"Other handles: {len(non_itm_handles)}")
        for handle in sorted(non_itm_handles)[:10]:
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
        
        # Analyze UI index distribution
        print(f"\n--- UI Index Distribution ---")
        ui_index_counts = {}
        for ui_info in ui_handles.values():
            index = ui_info['ui_index']
            ui_index_counts[index] = ui_index_counts.get(index, 0) + 1
        
        for index, count in sorted(ui_index_counts.items()):
            print(f"UI index {index}: {count} entries")
        
        return ui_handles, itm_mappings
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return {}, {}

def create_mapping_summary(ui_handles, itm_mappings):
    """Create a summary of the mapping structure."""
    print(f"\n=== ITM Icon Mapping Summary ===")
    print("1. DATA STRUCTURE:")
    print("   - items table: Contains item definitions with item_id as primary key")
    print("   - item_ui table: Links items to UI representations")
    print("   - weapons/armor tables: Extend items with specific properties")
    
    print("\n2. MAPPING RELATIONSHIPS:")
    print("   - item_ui.item_id → items.item_id (many-to-one)")
    print("   - item_ui.item_ui_handle → ITM texture filename")
    print("   - item_ui.item_ui_index → Multiple UI variants per item")
    
    print("\n3. ITM TEXTURE PATTERNS:")
    itm_handles = set(info['handle'] for info in ui_handles.values() if 'itm' in info['handle'].lower())
    print(f"   - Found {len(itm_handles)} ITM texture references")
    
    # Analyze patterns
    patterns = {}
    for handle in itm_handles:
        clean = handle.lower().replace('\\', '/').split('/')[-1]
        if clean.endswith('.tga'):
            clean = clean[:-4]
        
        # Categorize by pattern
        if clean.startswith('itm_') and clean[4:].isdigit():
            patterns['numeric'] = patterns.get('numeric', 0) + 1
        elif 'weapon' in clean:
            patterns['weapon'] = patterns.get('weapon', 0) + 1
        elif 'armor' in clean:
            patterns['armor'] = patterns.get('armor', 0) + 1
        else:
            patterns['other'] = patterns.get('other', 0) + 1
    
    for pattern, count in patterns.items():
        print(f"   - {pattern}: {count} entries")
    
    print("\n4. MAPPING ALGORITHM:")
    print("   To find ITM icon for an item:")
    print("   1. Look up item_id in item_ui table")
    print("   2. Get item_ui_handle for desired item_ui_index (usually 0)")
    print("   3. Extract ITM index from handle filename")
    print("   4. Use ITM index to reference texture atlas")
    
    print("\n5. CFF EDITOR INTEGRATION:")
    print("   - Load item_ui table alongside items table")
    print("   - Create lookup: item_id → [item_ui entries]")
    print("   - Parse ITM filenames to extract texture indices")
    print("   - Display icons using ITM texture atlas + index")

def main():
    """Main analysis function."""
    print("Direct ITM Icon Mapping Analysis...")
    
    # File paths
    original_path = "OriginalGameFiles/data/GameData.cff"
    modded_path = "ModdedGameFiles/GameData_MyCustomMod_20251019_100557.cff"
    
    if not os.path.exists(original_path):
        print(f"Error: Original file not found: {original_path}")
        return
    
    # Load and analyze original
    try:
        # Import GameData directly
        from tirganach.structure import GameData
        
        print("Loading original GameData...")
        original_gd = GameData(original_path)
        original_ui_handles, original_itm_mappings = analyze_gamedata_direct(original_gd, "Original")
        
        if original_ui_handles:
            create_mapping_summary(original_ui_handles, original_itm_mappings)
        
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
            modded_ui_handles, modded_itm_mappings = analyze_gamedata_direct(modded_gd, "Modded")
            
            # Simple comparison
            print(f"\n--- Comparison ---")
            print(f"Original UI entries: {len(original_ui_handles)}")
            print(f"Modded UI entries: {len(modded_ui_handles)}")
            print(f"Original ITM mappings: {len(original_itm_mappings)}")
            print(f"Modded ITM mappings: {len(modded_itm_mappings)}")
            
        except Exception as e:
            print(f"Error with modded file: {e}")

if __name__ == "__main__":
    main()