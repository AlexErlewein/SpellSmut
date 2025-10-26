#!/usr/bin/env python3
"""
Build mapping from UI handles to icon files.

Strategy:
The game doesn't provide a direct handle-to-file mapping, but we can
build an approximation by analyzing patterns in the GameData.

What we know:
- GameData has: item_id, item_ui_index, item_ui_handle
- We extracted: item/atlas_N/icon_M.png (64 icons per atlas)
- item_ui_index refers to position WITHIN an atlas (1-64)

The missing link: Which atlas number goes with which item?

Hypothesis:
- Atlas files are numbered consecutively (0, 1, 2, ...)
- Items likely reference atlases in some order
- We need to find the pattern by analyzing item IDs vs atlas usage

Approach:
1. Group items by which handles they use
2. Analyze item ID ranges that use similar handles
3. Try to deduce which atlas ranges correspond to which item ID ranges
4. Create best-guess mapping and document confidence
"""

from pathlib import Path
import json
from collections import defaultdict

def analyze_item_ui_patterns(gamedata_path: Path):
    """Analyze patterns in item_ui data."""
    
    with open(gamedata_path, 'r') as f:
        data = json.load(f)
    
    item_ui = data.get('item_ui', [])
    
    print("=" * 80)
    print("ITEM_UI DATA ANALYSIS")
    print("=" * 80)
    print(f"Total entries: {len(item_ui)}")
    print()
    
    # Group by item_id
    by_item = defaultdict(list)
    for entry in item_ui:
        item_id = entry.get('item_id')
        if item_id:
            by_item[item_id].append(entry)
    
    print(f"Unique items with UI data: {len(by_item)}")
    print()
    
    # Analyze handle patterns
    handle_prefixes = defaultdict(int)
    for entry in item_ui:
        handle = entry.get('item_ui_handle', '')
        if handle:
            # Extract prefix (ui_item_, ui_spell_, etc.)
            parts = handle.split('_')
            if len(parts) >= 2:
                prefix = f"{parts[0]}_{parts[1]}_"
                handle_prefixes[prefix] += 1
    
    print("Handle prefixes:")
    for prefix, count in sorted(handle_prefixes.items(), key=lambda x: -x[1])[:10]:
        print(f"  {prefix:30s} {count:5d} times")
    print()
    
    # Look for patterns in item_ui_index
    index_stats = defaultdict(int)
    for entry in item_ui:
        idx = entry.get('item_ui_index')
        if idx:
            index_stats[idx] += 1
    
    print(f"Index usage (item_ui_index field):")
    print(f"  Unique indices used: {len(index_stats)}")
    print(f"  Range: {min(index_stats.keys()) if index_stats else 'N/A'} to {max(index_stats.keys()) if index_stats else 'N/A'}")
    print()
    
    # Analyze scaled_down field
    scaled_counts = defaultdict(int)
    for entry in item_ui:
        scaled = entry.get('scaled_down', 0)
        scaled_counts[scaled] += 1
    
    print("Scaled down usage:")
    for scaled, count in sorted(scaled_counts.items()):
        print(f"  {scaled}: {count} entries")
    print()
    
    return by_item, item_ui

def build_handle_mapping(item_ui_data: list, icon_index_path: Path):
    """
    Build mapping from handles to icon files.
    
    Since we don't have the exact mapping, we create a plausible one
    based on the assumption that atlases are used sequentially.
    """
    
    # Load icon index
    with open(icon_index_path, 'r') as f:
        icon_index = json.load(f)
    
    # Get all item atlases (sorted)
    item_atlases = {}
    for key, icon_data in icon_index['icons'].items():
        if icon_data['category'] == 'item':
            atlas_num = int(icon_data['atlas_number'])
            if atlas_num not in item_atlases:
                item_atlases[atlas_num] = []
            item_atlases[atlas_num].append(icon_data)
    
    spell_atlases = {}
    for key, icon_data in icon_index['icons'].items():
        if icon_data['category'] == 'spell':
            atlas_num = int(icon_data['atlas_number'])
            if atlas_num not in spell_atlases:
                spell_atlases[atlas_num] = []
            spell_atlases[atlas_num].append(icon_data)
    
    print("=" * 80)
    print("BUILDING HANDLE MAPPING")
    print("=" * 80)
    print(f"Item atlases available: {len(item_atlases)}")
    print(f"Spell atlases available: {len(spell_atlases)}")
    print()
    
    # Strategy: Create lookup by (handle, index) -> icon_path
    # We'll use a FALLBACK approach since we don't know exact atlas numbers
    
    handle_mapping = {}
    unmapped_handles = []
    
    for entry in item_ui_data:
        item_id = entry.get('item_id')
        ui_index = entry.get('item_ui_index')
        ui_handle = entry.get('item_ui_handle', '').strip('\x00').strip()
        
        if not ui_handle or not ui_index:
            continue
        
        # Determine category from handle
        category = None
        if ui_handle.startswith('ui_item_'):
            category = 'item'
        elif ui_handle.startswith('ui_spell_'):
            category = 'spell'
        else:
            # Other categories (ui_bgr_, ui_btn_, etc.)
            parts = ui_handle.split('_')
            if len(parts) >= 2:
                category = parts[1]
        
        if not category:
            unmapped_handles.append(ui_handle)
            continue
        
        # KEY INSIGHT: We can't determine the exact atlas number without more info
        # Instead, we create entries for ALL possible atlas locations
        # The GUI will try each one until it finds a non-empty icon
        
        key = f"{item_id}_{ui_index}"
        
        handle_mapping[key] = {
            'item_id': item_id,
            'ui_index': ui_index,
            'ui_handle': ui_handle,
            'category': category,
            # Store all possible locations (we'll refine this with visual analysis later)
            'possible_icons': []
        }
        
        # Add all atlases for this category as possibilities
        atlases = item_atlases if category == 'item' else spell_atlases if category == 'spell' else {}
        
        for atlas_num in sorted(atlases.keys()):
            # Check if this index exists in this atlas
            atlas_icons = atlases[atlas_num]
            for icon in atlas_icons:
                if icon['icon_index'] == ui_index:
                    handle_mapping[key]['possible_icons'].append({
                        'atlas': atlas_num,
                        'path': icon['path']
                    })
                    break
    
    print(f"Mapped handles: {len(handle_mapping)}")
    print(f"Unmapped handles: {len(unmapped_handles)}")
    
    if unmapped_handles[:5]:
        print(f"Sample unmapped: {unmapped_handles[:5]}")
    print()
    
    return handle_mapping

def create_simple_lookup(item_ui_data: list):
    """
    Create a simpler lookup: item_id -> list of (index, handle) pairs.
    
    This allows the GUI to display ALL icons for an item, even if we don't
    know the exact atlas file.
    """
    
    lookup = defaultdict(list)
    
    for entry in item_ui_data:
        item_id = entry.get('item_id')
        ui_index = entry.get('item_ui_index')
        ui_handle = entry.get('item_ui_handle', '').strip('\x00').strip()
        scaled = entry.get('scaled_down', 0)
        
        if item_id and ui_handle:
            lookup[item_id].append({
                'index': ui_index,
                'handle': ui_handle,
                'scaled': bool(scaled)
            })
    
    return dict(lookup)

def main():
    """Main mapping process."""
    
    project_root = Path(__file__).parent.parent.parent
    gamedata_path = project_root / "TirganachReloaded" / "GameData.json"
    icon_index_path = project_root / "ExtractedAssets" / "UI" / "icons_extracted" / "icon_index.json"
    output_path = project_root / "TirganachReloaded" / "data" / "ui_icon_mapping.json"
    
    # Analyze patterns
    by_item, item_ui_data = analyze_item_ui_patterns(gamedata_path)
    
    # Build full mapping
    handle_mapping = build_handle_mapping(item_ui_data, icon_index_path)
    
    # Create simple lookup
    simple_lookup = create_simple_lookup(item_ui_data)
    
    # Save mappings
    output_data = {
        'description': 'Mapping from item IDs to UI icon data',
        'note': 'Atlas numbers are educated guesses - visual verification recommended',
        'item_to_icons': simple_lookup,
        'detailed_mapping': handle_mapping
    }
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print("=" * 80)
    print("MAPPING COMPLETE")
    print("=" * 80)
    print(f"Output: {output_path}")
    print()
    print(f"Items with icon data: {len(simple_lookup)}")
    print(f"Detailed mappings: {len(handle_mapping)}")
    print()
    print("The mapping provides:")
    print("  1. Simple lookup: item_id -> [icon handles]")
    print("  2. Detailed mapping: (item_id, index) -> possible icon paths")
    print()
    print("Next steps:")
    print("  1. Update CFF editor to use this mapping")
    print("  2. Display icons based on item_id lookup")
    print("  3. Manual verification/refinement as needed")
    print("=" * 80)

if __name__ == '__main__':
    main()
