#!/usr/bin/env python3
"""
Parse SpellForce item MSB (mesh) files to extract item icon mappings.

Items use the same MSB structure as spells:
- Filename = item handle (e.g., ui_item_equip_weapon_sword_flame.msb)
- Embedded texture reference = atlas number (e.g., ui_item25)
- UV coordinates = grid position

Item atlases use a 16x16 grid of 16x16 pixel icons (vs spell's 4x4 grid of 64x64).
Some items (weapons) span multiple grid cells.
"""

import struct
import re
import json
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional
from collections import defaultdict


@dataclass
class ItemIconMapping:
    """Mapping from item handle to icon file."""
    item_handle: str        # e.g., "ui_item_equip_weapon_sword_flame"
    atlas_number: int       # e.g., 25 (from "ui_item25")
    grid_row: int          # 0-15
    grid_col: int          # 0-15
    icon_number: int       # 0-255 (0-indexed for items)
    icon_path: str         # e.g., "itm/atlas_25/item_042.png"
    item_type: str         # weapon, armor, ring, rune, consumable, etc.
    item_subtype: str      # sword, chest, helmet, etc.
    source_file: str       # Original MSB file
    width_cells: int = 1   # Width in grid cells (1-4, weapons often 2-4)
    height_cells: int = 1  # Height in grid cells (usually 1)


def extract_atlas_reference(msb_data: bytes) -> Optional[str]:
    """Extract the atlas texture reference from MSB file data."""
    pattern = rb'ui_item(\d+)'
    match = re.search(pattern, msb_data)
    if match:
        return match.group(0).decode('ascii')
    return None


def classify_item(handle: str) -> tuple[str, str]:
    """
    Classify item by type and subtype based on handle name.

    Returns: (item_type, item_subtype)
    """
    handle_lower = handle.lower()

    # Equipment types
    if 'equip_weapon' in handle_lower or 'weapon_' in handle_lower:
        # Weapon subtypes
        if 'sword' in handle_lower:
            return ('weapon', 'sword')
        elif 'axe' in handle_lower:
            return ('weapon', 'axe')
        elif 'mace' in handle_lower or 'hammer' in handle_lower:
            return ('weapon', 'mace')
        elif 'staff' in handle_lower:
            return ('weapon', 'staff')
        elif 'bow' in handle_lower:
            return ('weapon', 'bow')
        elif 'crossbow' in handle_lower:
            return ('weapon', 'crossbow')
        elif 'dagger' in handle_lower:
            return ('weapon', 'dagger')
        elif 'spear' in handle_lower or 'lance' in handle_lower:
            return ('weapon', 'spear')
        elif 'halberd' in handle_lower:
            return ('weapon', 'halberd')
        else:
            return ('weapon', 'other')

    elif 'equip_chest' in handle_lower or 'breastplate' in handle_lower:
        return ('armor', 'chest')
    elif 'equip_helmet' in handle_lower or 'equip_head' in handle_lower:
        return ('armor', 'helmet')
    elif 'equip_leg' in handle_lower or 'equip_pants' in handle_lower:
        return ('armor', 'legs')
    elif 'equip_gloves' in handle_lower or 'equip_hand' in handle_lower:
        return ('armor', 'gloves')
    elif 'equip_boots' in handle_lower or 'equip_feet' in handle_lower:
        return ('armor', 'boots')
    elif 'equip_shield' in handle_lower:
        return ('armor', 'shield')
    elif 'equip_shoulder' in handle_lower:
        return ('armor', 'shoulders')

    elif 'ring' in handle_lower:
        return ('accessory', 'ring')
    elif 'amulet' in handle_lower or 'necklace' in handle_lower:
        return ('accessory', 'amulet')

    elif 'rune' in handle_lower:
        if 'hero' in handle_lower:
            return ('rune', 'hero')
        elif 'worker' in handle_lower:
            return ('rune', 'worker')
        else:
            return ('rune', 'other')

    elif 'scroll' in handle_lower or 'spellscroll' in handle_lower:
        return ('consumable', 'scroll')
    elif 'potion' in handle_lower:
        return ('consumable', 'potion')
    elif 'food' in handle_lower:
        return ('consumable', 'food')

    elif 'equip_' in handle_lower:
        return ('equipment', 'other')

    else:
        return ('misc', 'other')


def parse_item_msb(msb_path: Path) -> Optional[ItemIconMapping]:
    """
    Parse a single item MSB file and extract icon mapping.

    Item icons use 16x16 grid (256 icons per atlas).
    """
    try:
        with open(msb_path, 'rb') as f:
            data = f.read()

        # Extract item handle from filename
        item_handle = msb_path.stem

        # Extract atlas reference
        atlas_ref = extract_atlas_reference(data)
        if not atlas_ref:
            return None

        match = re.search(r'ui_item(\d+)', atlas_ref)
        if not match:
            return None
        atlas_number = int(match.group(1))

        # Parse UV coordinates from known offsets
        uv_offset_pairs = [
            (0x2C, 0x30),
            (0x54, 0x58),
            (0x7C, 0x80),
            (0xA4, 0xA8),
        ]

        uvs = []
        for u_off, v_off in uv_offset_pairs:
            if v_off + 4 <= len(data):
                try:
                    u = struct.unpack_from('<f', data, u_off)[0]
                    v = struct.unpack_from('<f', data, v_off)[0]
                    if -0.01 <= u <= 1.01 and -0.01 <= v <= 1.01:
                        uvs.append((u, v))
                except struct.error:
                    pass

        # Calculate grid position and dimensions (16x16 grid for items)
        width_cells = 1
        height_cells = 1
        if uvs:
            min_u = min(uv[0] for uv in uvs)
            min_v = min(uv[1] for uv in uvs)
            max_u = max(uv[0] for uv in uvs)
            max_v = max(uv[1] for uv in uvs)

            # 16x16 grid
            col = int(min_u * 16) if min_u < 1.0 else 15
            row = int(min_v * 16) if min_v < 1.0 else 15

            # Calculate width and height in cells
            # UV range * 16 = number of cells
            width_cells = max(1, round((max_u - min_u) * 16))
            height_cells = max(1, round((max_v - min_v) * 16))
        else:
            row, col = 0, 0

        col = max(0, min(15, col))
        row = max(0, min(15, row))

        # Calculate icon number (0-indexed for items, row-major order)
        icon_number = row * 16 + col

        # Classify item
        item_type, item_subtype = classify_item(item_handle)

        # Build icon path (item icons use 0-indexed naming: item_000.png)
        icon_path = f"itm/atlas_{atlas_number}/item_{icon_number:03d}.png"

        return ItemIconMapping(
            item_handle=item_handle,
            atlas_number=atlas_number,
            grid_row=row,
            grid_col=col,
            icon_number=icon_number,
            icon_path=icon_path,
            item_type=item_type,
            item_subtype=item_subtype,
            source_file=msb_path.name,
            width_cells=width_cells,
            height_cells=height_cells
        )

    except Exception as e:
        print(f"  Error parsing {msb_path.name}: {e}")
        return None


def main():
    """Main function to parse all item MSB files and generate mapping."""
    print("SpellForce Item Icon MSB Parser")
    print("=" * 60)

    project_root = Path(__file__).parent.parent.parent.parent

    # Find MSB files
    msb_search_dir = project_root / "ExtractedAssets" / "UI" / "raw_reextraction"

    print(f"Searching for item MSB files in: {msb_search_dir}")

    # Use sf35 as primary source
    msb_files = []
    sf35_mesh = msb_search_dir / "sf35" / "mesh"
    if sf35_mesh.exists():
        msb_files = list(sf35_mesh.glob("ui_item_*.msb"))
        print(f"Using MSB files from: sf35 (primary source)")

    if not msb_files:
        for sf_dir in sorted(msb_search_dir.glob("sf*"), reverse=True):
            mesh_dir = sf_dir / "mesh"
            if mesh_dir.exists():
                item_msbs = list(mesh_dir.glob("ui_item_*.msb"))
                if item_msbs:
                    msb_files = item_msbs
                    print(f"Using MSB files from: {sf_dir.name}")
                    break

    if not msb_files:
        print("No item MSB files found!")
        return

    print(f"Found {len(msb_files)} item MSB files")
    print()

    # Parse all MSB files
    mappings = []
    errors = 0

    for msb_file in sorted(msb_files):
        mapping = parse_item_msb(msb_file)
        if mapping:
            mappings.append(mapping)
        else:
            errors += 1

    print(f"\nParsed {len(mappings)} item mappings ({errors} errors)")

    # Analyze results
    print("\n" + "=" * 60)
    print("ITEM TYPE DISTRIBUTION")
    print("=" * 60)

    type_counts = defaultdict(lambda: defaultdict(int))
    for m in mappings:
        type_counts[m.item_type][m.item_subtype] += 1

    for item_type in sorted(type_counts.keys()):
        subtypes = type_counts[item_type]
        total = sum(subtypes.values())
        print(f"\n{item_type.upper()} ({total} total):")
        for subtype, count in sorted(subtypes.items()):
            print(f"    {subtype}: {count}")

    # Atlas distribution
    print("\n" + "=" * 60)
    print("ATLAS DISTRIBUTION")
    print("=" * 60)

    atlas_counts = {}
    for m in mappings:
        atlas_counts[m.atlas_number] = atlas_counts.get(m.atlas_number, 0) + 1

    for atlas in sorted(atlas_counts.keys()):
        print(f"  Atlas {atlas:2d}: {atlas_counts[atlas]:3d} items")

    # Sample mappings
    print("\n" + "=" * 60)
    print("SAMPLE MAPPINGS")
    print("=" * 60)

    # Show samples by category
    categories = ['weapon', 'armor', 'accessory', 'rune', 'consumable']
    for cat in categories:
        samples = [m for m in mappings if m.item_type == cat][:3]
        if samples:
            print(f"\n{cat.upper()}:")
            for m in samples:
                print(f"  {m.item_handle}")
                print(f"    → {m.icon_path} ({m.item_subtype})")

    # Save mapping to JSON
    output_path = project_root / "src" / "TirganachReloaded" / "data" / "item_icon_mapping.json"

    mapping_dict = {
        "description": "Item handle to icon file mapping extracted from MSB mesh files",
        "total_mappings": len(mappings),
        "atlases_used": sorted(atlas_counts.keys()),
        "type_summary": {t: dict(st) for t, st in type_counts.items()},
        "mappings": {m.item_handle: asdict(m) for m in mappings}
    }

    # Simple handle → path lookup
    simple_mapping = {m.item_handle: m.icon_path for m in mappings}
    mapping_dict["handle_to_path"] = simple_mapping

    # Handle → display info (for AllwissendeAlmacht)
    display_mapping = {
        m.item_handle: {
            "name": m.item_handle.replace("ui_item_equip_", "").replace("ui_item_", "").replace("_", " ").title(),
            "path": m.icon_path,
            "type": m.item_type,
            "subtype": m.item_subtype,
            "width_cells": m.width_cells,
            "height_cells": m.height_cells
        }
        for m in mappings
    }
    mapping_dict["display_info"] = display_mapping

    # Icon size statistics
    print("\n" + "=" * 60)
    print("ICON SIZE DISTRIBUTION")
    print("=" * 60)

    size_counts = defaultdict(int)
    for m in mappings:
        size_key = f"{m.width_cells}x{m.height_cells}"
        size_counts[size_key] += 1

    for size, count in sorted(size_counts.items()):
        print(f"  {size}: {count} items")

    # Multi-cell examples
    multi_cell = [m for m in mappings if m.width_cells > 1 or m.height_cells > 1]
    if multi_cell:
        print(f"\nMulti-cell icons ({len(multi_cell)} total):")
        for m in multi_cell[:10]:
            print(f"  {m.item_handle}: {m.width_cells}x{m.height_cells} cells")

    with open(output_path, 'w') as f:
        json.dump(mapping_dict, f, indent=2)

    print(f"\n✓ Saved mapping to: {output_path}")

    # Verify against extracted icons
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)

    icons_dir = project_root / "ExtractedAssets" / "UI" / "icons_extracted"
    verified = 0
    missing = 0

    for m in mappings[:100]:
        icon_path = icons_dir / m.icon_path
        if icon_path.exists():
            verified += 1
        else:
            missing += 1
            if missing <= 5:
                print(f"  Missing: {m.icon_path}")

    print(f"\n  Verified: {verified}/100 icons exist")
    if missing > 0:
        print(f"  Missing: {missing} icons")

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
