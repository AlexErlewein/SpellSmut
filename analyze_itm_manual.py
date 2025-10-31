#!/usr/bin/env python3
"""
Manual analysis of GameData.cff files for ITM icon mapping.
Manually loads tables without relying on annotations.
"""

import sys
import os
from pathlib import Path

# Add tirganach library to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "TirganachReloaded"))

def load_gamedata_manual(filepath):
    """Manually load GameData by manually processing tables."""
    from tirganach.structure import GameData
    from tirganach.entities import Item, ItemUI, Weapon, Armor
    
    # Load the raw data
    with open(filepath, 'rb') as f:
        raw_data = f.read()
    
    # Create GameData instance to get access to raw parsing
    gd = GameData(raw_data)
    
    # Manually extract tables by accessing their attributes after initialization
    # This bypasses the annotation issue
    return gd

def extract_itm_mappings(gamedata, name="GameData"):
    """Extract ITM mappings from loaded GameData."""
    print(f"\n=== Analyzing {name} ===")
    
    try:
        # Access tables directly from the loaded GameData
        # The tables should be populated as attributes
        items = None
        item_ui = None
        weapons = None
        armor = None
        
        # Try to access table attributes
        for attr_name in dir(gamedata):
            attr = getattr(gamedata, attr_name)
            if hasattr(attr, '__class__') and 'Table' in str(attr.__class__):
                if attr_name == 'items':
                    items = attr
                elif attr_name == 'item_ui':
                    item_ui = attr
                elif attr_name == 'weapons':
                    weapons = attr
                elif attr_name == 'armor':
                    armor = attr
        
        if items is None or item_ui is None:
            print("Error: Could not find items or item_ui tables")
            print(f"Available attributes: {[attr for attr in dir(gamedata) if not attr.startswith('_')]}")
            return {}, {}
        
        print(f"Items: {len(items)}")
        print(f"Weapons: {len(weapons) if weapons else 0}")
        print(f"Armor: {len(armor) if armor else 0}")
        print(f"Item UI entries: {len(item_ui)}")
        
        # Analyze item_ui structure
        if len(item_ui) > 0:
            sample_ui = item_ui[0]
            print(f"\n--- Sample ItemUI Entry ---")
            print(f"Available fields: {[attr for attr in dir(sample_ui) if not attr.startswith('_')]}")
            print(f"item_id: {getattr(sample_ui, 'item_id', 'N/A')}")
            print(f"item_ui_index: {getattr(sample_ui, 'item_ui_index', 'N/A')}")
            print(f"item_ui_handle: '{getattr(sample_ui, 'item_ui_handle', 'N/A')}'")
            print(f"scaled_down: {getattr(sample_ui, 'scaled_down', 'N/A')}")
        
        # Analyze UI handle patterns
        ui_handles = {}
        handle_patterns = set()
        
        for ui_entry in item_ui:
            handle = getattr(ui_entry, 'item_ui_handle', None)
            if handle:
                handle_patterns.add(handle)
                item_id = getattr(ui_entry, 'item_id', None)
                ui_index = getattr(ui_entry, 'item_ui_index', None)
                scaled_down = getattr(ui_entry, 'scaled_down', None)
                
                if item_id is not None:
                    ui_handles[item_id] = {
                        'handle': handle,
                        'ui_index': ui_index,
                        'scaled_down': scaled_down
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
            item_id = getattr(item, 'item_id', None)
            item_name = getattr(item, 'name', 'Unknown')
            
            if item_id is not None and item_id in ui_handles:
                items_with_ui += 1
                ui_info = ui_handles[item_id]
                print(f"Item {item_id}: '{item_name}' -> '{ui_info['handle']}'")
        
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
            if index is not None:
                ui_index_counts[index] = ui_index_counts.get(index, 0) + 1
        
        for index, count in sorted(ui_index_counts.items()):
            print(f"UI index {index}: {count} entries")
        
        return ui_handles, itm_mappings
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return {}, {}

def create_mapping_documentation(ui_handles, itm_mappings):
    """Create comprehensive mapping documentation."""
    print(f"\n=== ITM Icon Mapping Documentation ===")
    
    print("\n1. DATA STRUCTURE OVERVIEW:")
    print("   GameData.cff contains multiple tables:")
    print("   - items: Base item definitions (item_id, name, type, etc.)")
    print("   - item_ui: UI mappings (item_id, item_ui_handle, item_ui_index)")
    print("   - weapons: Weapon-specific data (extends items via item_id)")
    print("   - armor: Armor-specific data (extends items via item_id)")
    
    print("\n2. MAPPING RELATIONSHIPS:")
    print("   Primary Key: items.item_id")
    print("   Foreign Key: item_ui.item_id → items.item_id")
    print("   UI Handle: item_ui.item_ui_handle → ITM texture filename")
    print("   UI Variant: item_ui.item_ui_index → Multiple UI states per item")
    
    print("\n3. ITM TEXTURE PATTERNS:")
    itm_handles = set(info['handle'] for info in ui_handles.values() if 'itm' in info['handle'].lower())
    print(f"   Total ITM references: {len(itm_handles)}")
    
    # Analyze patterns
    patterns = {}
    for handle in itm_handles:
        clean = handle.lower().replace('\\', '/').split('/')[-1]
        if clean.endswith('.tga'):
            clean = clean[:-4]
        
        # Categorize by pattern
        if clean.startswith('itm_') and clean[4:].isdigit():
            patterns['numeric_itm_XXX'] = patterns.get('numeric_itm_XXX', 0) + 1
        elif 'weapon' in clean:
            patterns['weapon_named'] = patterns.get('weapon_named', 0) + 1
        elif 'armor' in clean:
            patterns['armor_named'] = patterns.get('armor_named', 0) + 1
        elif 'shield' in clean:
            patterns['shield_named'] = patterns.get('shield_named', 0) + 1
        else:
            patterns['other_patterns'] = patterns.get('other_patterns', 0) + 1
    
    for pattern, count in sorted(patterns.items()):
        print(f"   - {pattern}: {count} entries")
    
    print("\n4. MAPPING ALGORITHM:")
    print("   To find ITM icon for any item:")
    print("   ```python")
    print("   def get_item_itm_icon(item_id, ui_index=0):")
    print("       # 1. Find UI entries for this item")
    print("       ui_entries = [ui for ui in item_ui if ui.item_id == item_id and ui.item_ui_index == ui_index]")
    print("       if not ui_entries:")
    print("           return None")
    print("       ")
    print("       # 2. Get the handle")
    print("       handle = ui_entries[0].item_ui_handle")
    print("       ")
    print("       # 3. Extract ITM index from filename")
    print("       if 'itm' in handle.lower():")
    print("           filename = handle.lower().split('/')[-1].replace('.tga', '')")
    print("           parts = filename.split('_')")
    print("           for part in parts:")
    print("               if part.isdigit():")
    print("                   return int(part)")
    print("       return None")
    print("   ```")
    
    print("\n5. CFF EDITOR INTEGRATION:")
    print("   Required components:")
    print("   - Load item_ui table alongside items table")
    print("   - Create lookup dictionary: item_id → [item_ui entries]")
    print("   - Parse ITM filenames to extract texture indices")
    print("   - Load ITM texture atlas")
    print("   - Display icons using: texture_atlas.get_icon(itm_index)")
    
    print("\n6. TEXTURE ATLAS COORDINATES:")
    print("   ITM files are typically texture atlases with multiple icons:")
    print("   - Each ITM file contains a grid of icon images")
    print("   - Icon index determines position in the grid")
    print("   - Grid size varies (commonly 8x8, 16x16, or 32x32)")
    print("   - Coordinates: row = index // grid_width, col = index % grid_width")
    
    print("\n7. EXAMPLE MAPPINGS:")
    example_items = list(itm_mappings.items())[:10]
    for item_id, mapping in example_items:
        print(f"   Item {item_id:4d} → ITM {mapping['itm_index']:4d} → '{mapping['handle']}'")

def main():
    """Main analysis function."""
    print("Manual ITM Icon Mapping Analysis...")
    
    # File paths
    original_path = "OriginalGameFiles/data/GameData.cff"
    modded_path = "ModdedGameFiles/GameData_MyCustomMod_20251019_100557.cff"
    
    if not os.path.exists(original_path):
        print(f"Error: Original file not found: {original_path}")
        return
    
    # Load and analyze original
    try:
        print("Loading original GameData...")
        original_gd = load_gamedata_manual(original_path)
        original_ui_handles, original_itm_mappings = extract_itm_mappings(original_gd, "Original")
        
        if original_ui_handles:
            create_mapping_documentation(original_ui_handles, original_itm_mappings)
        
    except Exception as e:
        print(f"Error with original file: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Load and analyze modded if available
    if os.path.exists(modded_path):
        try:
            print("\nLoading modded GameData...")
            modded_gd = load_gamedata_manual(modded_path)
            modded_ui_handles, modded_itm_mappings = extract_itm_mappings(modded_gd, "Modded")
            
            # Simple comparison
            print(f"\n--- Comparison Summary ---")
            print(f"Original UI entries: {len(original_ui_handles)}")
            print(f"Modded UI entries: {len(modded_ui_handles)}")
            print(f"Original ITM mappings: {len(original_itm_mappings)}")
            print(f"Modded ITM mappings: {len(modded_itm_mappings)}")
            
            # Find differences
            if original_ui_handles and modded_ui_handles:
                original_items = set(original_ui_handles.keys())
                modded_items = set(modded_ui_handles.keys())
                
                added_items = modded_items - original_items
                removed_items = original_items - modded_items
                
                print(f"Items added in mod: {len(added_items)}")
                print(f"Items removed in mod: {len(removed_items)}")
                
        except Exception as e:
            print(f"Error with modded file: {e}")

if __name__ == "__main__":
    main()