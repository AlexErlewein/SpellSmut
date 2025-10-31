#!/usr/bin/env python3
"""
Final ITM Icon Mapping Analysis
Complete analysis with proper mapping and ITM index extraction
"""

import sys
import os
import re
from pathlib import Path

# Add the tirganach library to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "TirganachReloaded"))

try:
    from tirganach.structure import GameData
    from tirganach.entities import Item, ItemUI
except ImportError as e:
    print(f"Error importing tirganach library: {e}")
    sys.exit(1)

def extract_itm_index_from_handle(handle):
    """Extract ITM texture index from UI handle"""
    if not handle:
        return None
    
    handle = handle.lower()
    
    # Pattern 1: ui_itm_equip_XXXX_...
    match = re.search(r'ui_itm_equip_(\d+)', handle)
    if match:
        return int(match.group(1))
    
    # Pattern 2: itm_XXXX in any position
    match = re.search(r'itm_(\d+)', handle)
    if match:
        return int(match.group(1))
    
    # Pattern 3: Just numbers in equip handles (4 digits)
    if 'equip' in handle:
        match = re.search(r'(\d{4})', handle)
        if match:
            return int(match.group(1))
    
    return None

def final_itm_analysis(gamedata, label):
    """Final comprehensive ITM analysis"""
    print(f"\n=== {label} Final ITM Analysis ===")
    
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
    
    # Find all ITM-related entries and extract indices
    itm_mappings = {}
    equip_with_numbers = []
    
    for ui_entry in item_ui:
        handle = ui_entry.item_ui_handle
        if not handle:
            continue
            
        # Get item
        item = item_by_id.get(ui_entry.item_id)
        item_name = getattr(item, 'name', 'Unknown') if item else 'Not Found'
        
        # Extract ITM index
        itm_index = extract_itm_index_from_handle(handle)
        
        if itm_index is not None:
            itm_mappings[ui_entry.item_id] = {
                'item_id': ui_entry.item_id,
                'item_name': item_name,
                'ui_handle': handle,
                'itm_index': itm_index,
                'ui_index': ui_entry.item_ui_index,
                'scaled_down': ui_entry.scaled_down,
                'found_item': item is not None
            }
        
        # Also track equip entries with 4-digit numbers
        if 'equip' in handle.lower() and re.search(r'\d{4}', handle):
            equip_with_numbers.append({
                'item_id': ui_entry.item_id,
                'item_name': item_name,
                'ui_handle': handle,
                'numbers': re.findall(r'\d{4}', handle),
                'ui_index': ui_entry.item_ui_index,
                'found_item': item is not None
            })
    
    print(f"Items with ITM mapping: {len(itm_mappings)}")
    print(f"Equip entries with 4-digit numbers: {len(equip_with_numbers)}")
    
    # Show ITM mappings
    if itm_mappings:
        print(f"\n--- ITM Mappings ---")
        for item_id, mapping in sorted(itm_mappings.items()):
            status = "✓" if mapping['found_item'] else "✗"
            print(f"{status} Item {item_id:4d}: '{mapping['item_name']}' -> ITM {mapping['itm_index']:4d}")
            print(f"    Handle: {mapping['ui_handle']}")
            print(f"    UI Index: {mapping['ui_index']}, Scaled: {mapping['scaled_down']}")
            print()
    
    # Show equip entries with numbers (potential ITM candidates)
    if equip_with_numbers:
        print(f"\n--- Equip Entries with 4-Digit Numbers (ITM Candidates) ---")
        for entry in equip_with_numbers[:20]:  # Show first 20
            status = "✓" if entry['found_item'] else "✗"
            print(f"{status} Item {entry['item_id']:4d}: '{entry['item_name']}'")
            print(f"    Handle: {entry['ui_handle']}")
            print(f"    Numbers: {entry['numbers']}")
            print(f"    UI Index: {entry['ui_index']}")
            print()
        
        if len(equip_with_numbers) > 20:
            print(f"... and {len(equip_with_numbers) - 20} more equip entries with numbers")
    
    # Analyze ITM index range
    if itm_mappings:
        itm_indices = [m['itm_index'] for m in itm_mappings.values()]
        print(f"\n--- ITM Index Analysis ---")
        print(f"ITM index range: {min(itm_indices)} - {max(itm_indices)}")
        print(f"Unique ITM indices: {len(set(itm_indices))}")
        print(f"ITM indices: {sorted(set(itm_indices))}")
    
    return itm_mappings, equip_with_numbers

def create_integration_summary(itm_mappings, equip_candidates):
    """Create CFF editor integration summary"""
    print(f"\n=== CFF Editor Integration Guide ===")
    
    print("1. DATA STRUCTURE:")
    print("   - Items table: Contains item definitions with item_id as primary key")
    print("   - ItemUI table: Contains UI mappings linked by item_id")
    print("   - item_ui_handle field: Contains texture reference strings")
    
    print("\n2. MAPPING PROCESS:")
    print("   a) Load Items and ItemUI tables from GameData.cff")
    print("   b) Create item_id -> Item mapping for efficient lookup")
    print("   c) For each ItemUI entry, find matching Item by item_id")
    print("   d) Extract ITM index from item_ui_handle using patterns:")
    
    print("\n3. ITM INDEX EXTRACTION PATTERNS (in order):")
    print("   Pattern 1: ui_itm_equip_(\\d+) -> Direct ITM index")
    print("   Pattern 2: itm_(\\d+) -> Fallback ITM index")  
    print("   Pattern 3: (\\d{4}) in equip handles -> Equipment ITM index")
    
    print("\n4. TEXTURE COORDINATE CALCULATION:")
    print("   - ITM files are texture atlases with numbered icons")
    print("   - Use ITM index to calculate row/column in texture grid")
    print("   - Typical ITM atlas: 16x16 icons (256 icons per file)")
    print("   - Row = ITM_index // 16, Column = ITM_index % 16")
    print("   - Pixel coordinates: (Column * icon_size, Row * icon_size)")
    
    print("\n5. IMPLEMENTATION NOTES:")
    print(f"   - Found {len(itm_mappings)} direct ITM mappings")
    print(f"   - Found {len(equip_candidates)} equipment candidates")
    print("   - Most items use ui_item_xxx or ui_spell_xxx handles")
    print("   - ITM mappings are primarily for equipment items")
    
    if itm_mappings:
        sample = list(itm_mappings.values())[0]
        print(f"\n6. EXAMPLE MAPPING:")
        print(f"   Item ID: {sample['item_id']}")
        print(f"   Item Name: {sample['item_name']}")
        print(f"   UI Handle: {sample['ui_handle']}")
        print(f"   Extracted ITM Index: {sample['itm_index']}")
        print(f"   Texture Coordinates: Row {sample['itm_index']//16}, Col {sample['itm_index']%16}")
        print(f"   Pixel Position: ({(sample['itm_index']%16)*32}, {(sample['itm_index']//16)*32})")

def main():
    print("Final ITM Icon Mapping Analysis...")
    
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
    original_itm, original_equip = final_itm_analysis(original_gamedata, "Original")
    modded_itm, modded_equip = final_itm_analysis(modded_gamedata, "Modded")
    
    # Create integration summary
    create_integration_summary(original_itm, original_equip)
    
    # Comparison
    print(f"\n=== Original vs Modded Comparison ===")
    print(f"Original ITM mappings: {len(original_itm)}")
    print(f"Modded ITM mappings: {len(modded_itm)}")
    print(f"Original equip candidates: {len(original_equip)}")
    print(f"Modded equip candidates: {len(modded_equip)}")
    
    if len(original_itm) != len(modded_itm):
        print("⚠️  ITM mappings differ between original and modded!")
    else:
        print("✓ ITM mappings are identical between original and modded")

if __name__ == "__main__":
    main()