#!/usr/bin/env python3
"""
Parse SpellForce MSB (mesh) files to extract spell icon mappings.

MSB files contain:
1. The spell handle (from filename): ui_spell_wm_life_healing.msb
2. The atlas reference (embedded string): ui_spell5
3. UV coordinates that indicate grid position within the 4x4 atlas

This script extracts this data to create a complete spell handle -> icon file mapping.
"""

import struct
import re
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class SpellIconMapping:
    """Mapping from spell handle to icon file."""
    spell_handle: str       # e.g., "ui_spell_wm_life_healing"
    atlas_number: int       # e.g., 5 (from "ui_spell5")
    grid_row: int          # 0-3
    grid_col: int          # 0-3
    icon_number: int       # 1-16 (1-indexed)
    icon_path: str         # e.g., "spell/atlas_5/icon_003.png"
    source_file: str       # Original MSB file


def extract_atlas_reference(msb_data: bytes) -> Optional[str]:
    """
    Extract the atlas texture reference from MSB file data.

    The atlas reference (e.g., "ui_spell13") is typically found
    around offset 0xD0 as a null-terminated string.
    """
    # Search for ui_spell followed by digits
    pattern = rb'ui_spell(\d+)'
    match = re.search(pattern, msb_data)
    if match:
        return match.group(0).decode('ascii')
    return None


def extract_uv_coordinates(msb_data: bytes) -> list[tuple[float, float]]:
    """
    Extract UV coordinates from MSB vertex data.

    MSB files contain vertex data with position, normal, and UV coordinates.
    The UV coordinates help determine which cell in the 4x4 grid the icon is in.
    """
    uvs = []

    # MSB vertex structure appears to be:
    # - 4 bytes: flags/type
    # - 4 bytes: count
    # - Then vertex data...

    # Look for float pairs that could be UVs (values between 0 and 1)
    # UVs are typically stored as 32-bit floats

    # Skip header (first 16 bytes based on hex dump analysis)
    offset = 16

    while offset + 8 <= len(msb_data) - 50:  # Leave room for texture string at end
        try:
            u = struct.unpack_from('<f', msb_data, offset)[0]
            v = struct.unpack_from('<f', msb_data, offset + 4)[0]

            # Valid UV coordinates should be in 0-1 range (or slightly outside for tiling)
            if 0.0 <= u <= 1.0 and 0.0 <= v <= 1.0:
                uvs.append((u, v))
        except struct.error:
            pass

        offset += 4  # Move by 4 bytes to check next potential position

    return uvs


def calculate_grid_position(uvs: list[tuple[float, float]]) -> tuple[int, int]:
    """
    Calculate grid position from UV coordinates.

    For a 4x4 grid:
    - UV (0.0-0.25, 0.0-0.25) = cell (0, 0) = icon 1
    - UV (0.25-0.5, 0.0-0.25) = cell (1, 0) = icon 2
    etc.
    """
    if not uvs:
        return (0, 0)

    # Take the average or most common UV range
    # For spell icons, look for UVs that map to specific cells

    # Find minimum U and V (top-left corner of the icon)
    min_u = min(uv[0] for uv in uvs)
    min_v = min(uv[1] for uv in uvs)

    # Calculate grid position (0-3 range for 4x4 grid)
    col = int(min_u * 4)
    row = int(min_v * 4)

    # Clamp to valid range
    col = max(0, min(3, col))
    row = max(0, min(3, row))

    return (row, col)


def parse_msb_file(msb_path: Path) -> Optional[SpellIconMapping]:
    """
    Parse a single MSB file and extract spell icon mapping.
    """
    try:
        with open(msb_path, 'rb') as f:
            data = f.read()

        # Extract spell handle from filename
        spell_handle = msb_path.stem  # e.g., "ui_spell_wm_life_healing"

        # Extract atlas reference
        atlas_ref = extract_atlas_reference(data)
        if not atlas_ref:
            return None

        # Parse atlas number
        match = re.search(r'ui_spell(\d+)', atlas_ref)
        if not match:
            return None
        atlas_number = int(match.group(1))

        # Extract UV coordinates and calculate grid position
        uvs = extract_uv_coordinates(data)
        row, col = calculate_grid_position(uvs)

        # Calculate icon number (1-indexed, row-major order)
        icon_number = row * 4 + col + 1

        # Build icon path
        icon_path = f"spell/atlas_{atlas_number}/icon_{icon_number:03d}.png"

        return SpellIconMapping(
            spell_handle=spell_handle,
            atlas_number=atlas_number,
            grid_row=row,
            grid_col=col,
            icon_number=icon_number,
            icon_path=icon_path,
            source_file=msb_path.name
        )

    except Exception as e:
        print(f"  Error parsing {msb_path.name}: {e}")
        return None


def parse_msb_with_detailed_uv(msb_path: Path) -> Optional[SpellIconMapping]:
    """
    Parse MSB file with more detailed UV extraction based on file structure analysis.

    Based on hex dump analysis of spell MSB files:
    - Header: 16 bytes
    - 4 vertices, each ~40 bytes
    - Each vertex has: position, padding, color (0xFFFFFFFF), UV pair
    - UV coordinates found at specific offsets within vertex data
    - Texture name is null-terminated string around offset 0xD0
    """
    try:
        with open(msb_path, 'rb') as f:
            data = f.read()

        # Extract spell handle from filename
        spell_handle = msb_path.stem

        # Extract atlas reference
        atlas_ref = extract_atlas_reference(data)
        if not atlas_ref:
            return None

        match = re.search(r'ui_spell(\d+)', atlas_ref)
        if not match:
            return None
        atlas_number = int(match.group(1))

        # Parse UV coordinates from known offsets
        # Based on analysis: UVs appear at these offset pairs within vertex data:
        # Vertex 1: 0x2C, 0x30
        # Vertex 2: 0x54, 0x58
        # Vertex 3: 0x7C, 0x80
        # Vertex 4: 0xA4, 0xA8

        uv_offset_pairs = [
            (0x2C, 0x30),  # Vertex 1
            (0x54, 0x58),  # Vertex 2
            (0x7C, 0x80),  # Vertex 3
            (0xA4, 0xA8),  # Vertex 4
        ]

        uvs = []
        for u_off, v_off in uv_offset_pairs:
            if v_off + 4 <= len(data):
                try:
                    u = struct.unpack_from('<f', data, u_off)[0]
                    v = struct.unpack_from('<f', data, v_off)[0]
                    # Valid UV coordinates in 0-1 range (with small tolerance)
                    if -0.01 <= u <= 1.01 and -0.01 <= v <= 1.01:
                        uvs.append((u, v))
                except struct.error:
                    pass

        # If we couldn't find UVs at expected offsets, scan for them
        if len(uvs) < 2:
            # Scan through file looking for valid UV pairs
            for offset in range(0x20, min(0xB0, len(data) - 8), 4):
                try:
                    val = struct.unpack_from('<f', data, offset)[0]
                    # Look for values in UV range that are close to grid boundaries
                    if 0.0 <= val <= 1.0:
                        # Check if this could be a U coordinate
                        next_val = struct.unpack_from('<f', data, offset + 4)[0]
                        if 0.0 <= next_val <= 1.0:
                            uvs.append((val, next_val))
                except struct.error:
                    pass

        # Calculate grid position from UV coordinates
        # For a 4x4 grid, each cell is 0.25 x 0.25
        if uvs:
            # Get the minimum U and V (top-left corner of the quad)
            min_u = min(uv[0] for uv in uvs)
            min_v = min(uv[1] for uv in uvs)

            # Calculate grid position
            # Column from U: 0.0-0.25 = col 0, 0.25-0.5 = col 1, etc.
            # Row from V: 0.0-0.25 = row 0, 0.25-0.5 = row 1, etc.
            col = int(min_u * 4) if min_u < 1.0 else 3
            row = int(min_v * 4) if min_v < 1.0 else 3
        else:
            # Default to position 1 if we can't determine
            row, col = 0, 0

        # Clamp to valid range
        col = max(0, min(3, col))
        row = max(0, min(3, row))

        # Calculate icon number (1-indexed, row-major order)
        icon_number = row * 4 + col + 1

        icon_path = f"spell/atlas_{atlas_number}/icon_{icon_number:03d}.png"

        return SpellIconMapping(
            spell_handle=spell_handle,
            atlas_number=atlas_number,
            grid_row=row,
            grid_col=col,
            icon_number=icon_number,
            icon_path=icon_path,
            source_file=msb_path.name
        )

    except Exception as e:
        print(f"  Error parsing {msb_path.name}: {e}")
        return None


def main():
    """Main function to parse all spell MSB files and generate mapping."""
    print("SpellForce Spell Icon MSB Parser")
    print("=" * 60)

    project_root = Path(__file__).parent.parent.parent.parent

    # Find MSB files
    msb_search_dir = project_root / "ExtractedAssets" / "UI" / "raw_reextraction"

    print(f"Searching for spell MSB files in: {msb_search_dir}")

    # Find all spell MSB files (prioritize sf35 as it's the latest/most complete)
    msb_files = []

    # First try sf35 explicitly (most complete)
    sf35_mesh = msb_search_dir / "sf35" / "mesh"
    if sf35_mesh.exists():
        spell_msbs = list(sf35_mesh.glob("ui_spell_*.msb"))
        if spell_msbs:
            msb_files = spell_msbs
            print(f"Using MSB files from: sf35 (primary source)")

    # Fallback to other directories if sf35 not available
    if not msb_files:
        for sf_dir in sorted(msb_search_dir.glob("sf*"), reverse=True):
            mesh_dir = sf_dir / "mesh"
            if mesh_dir.exists():
                spell_msbs = list(mesh_dir.glob("ui_spell_*.msb"))
                if spell_msbs:
                    msb_files = spell_msbs
                    print(f"Using MSB files from: {sf_dir.name}")
                    break

    if not msb_files:
        print("No spell MSB files found!")
        return

    print(f"Found {len(msb_files)} spell MSB files")
    print()

    # Parse all MSB files
    mappings = []
    errors = 0

    for msb_file in sorted(msb_files):
        mapping = parse_msb_with_detailed_uv(msb_file)
        if mapping:
            mappings.append(mapping)
        else:
            errors += 1

    print(f"\nParsed {len(mappings)} spell mappings ({errors} errors)")

    # Analyze results
    print("\n" + "=" * 60)
    print("ATLAS DISTRIBUTION")
    print("=" * 60)

    atlas_counts = {}
    for m in mappings:
        atlas_counts[m.atlas_number] = atlas_counts.get(m.atlas_number, 0) + 1

    for atlas in sorted(atlas_counts.keys()):
        print(f"  Atlas {atlas:2d}: {atlas_counts[atlas]:3d} spells")

    # Show sample mappings
    print("\n" + "=" * 60)
    print("SAMPLE MAPPINGS (first 20)")
    print("=" * 60)

    for m in mappings[:20]:
        print(f"  {m.spell_handle}")
        print(f"    → atlas_{m.atlas_number}/icon_{m.icon_number:03d}.png (row={m.grid_row}, col={m.grid_col})")

    # Save mapping to JSON
    output_path = project_root / "src" / "TirganachReloaded" / "data" / "spell_icon_mapping.json"

    mapping_dict = {
        "description": "Spell handle to icon file mapping extracted from MSB mesh files",
        "total_mappings": len(mappings),
        "atlases_used": sorted(atlas_counts.keys()),
        "mappings": {m.spell_handle: asdict(m) for m in mappings}
    }

    # Also create a simple handle -> path lookup
    simple_mapping = {m.spell_handle: m.icon_path for m in mappings}
    mapping_dict["handle_to_path"] = simple_mapping

    with open(output_path, 'w') as f:
        json.dump(mapping_dict, f, indent=2)

    print(f"\n✓ Saved mapping to: {output_path}")

    # Verify some mappings against extracted icons
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)

    icons_dir = project_root / "ExtractedAssets" / "UI" / "icons_extracted"
    verified = 0
    missing = 0

    for m in mappings[:50]:  # Check first 50
        icon_path = icons_dir / m.icon_path
        if icon_path.exists():
            verified += 1
        else:
            missing += 1
            if missing <= 5:
                print(f"  Missing: {m.icon_path}")

    print(f"\n  Verified: {verified}/50 icons exist")
    if missing > 0:
        print(f"  Missing: {missing} icons (may need re-extraction)")

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
