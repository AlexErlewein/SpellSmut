#!/usr/bin/env python3
"""
Extract individual icons from UI texture atlases.

SpellForce stores UI icons in 256x256 texture atlases (DDS files).
This script extracts individual icons from these atlases into named PNG files.

The challenge:
- Texture files are numbered (ui_item14.dds, ui_spell5.dds)
- Database has handles (ui_item_equip_weapon_dagger_flame) and indices (1, 2, 3...)
- No direct mapping exists between file numbers and handles

Solution:
- Extract ALL icons from ALL atlases
- Create organized structure: item/atlas_N/icon_M.png
- Build mapping database linking handles to actual files
- Users can then look up icons by handle through the mapping
"""

import json
import subprocess
from pathlib import Path

from PIL import Image


def convert_dds_to_png(dds_path: Path, png_path: Path) -> bool:
    """
    Convert DDS file to PNG using ImageMagick.

    Args:
        dds_path: Path to input DDS file
        png_path: Path to output PNG file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        png_path.parent.mkdir(parents=True, exist_ok=True)

        # Use ImageMagick to convert
        result = subprocess.run(
            ["magick", "convert", str(dds_path), str(png_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0 and png_path.exists():
            return True
        else:
            print(f"  ⚠ Conversion failed for {dds_path.name}: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"  ⚠ Timeout converting {dds_path.name}")
        return False
    except Exception as e:
        print(f"  ⚠ Error converting {dds_path.name}: {e}")
        return False


def extract_icons_from_atlas(
    atlas_png: Path,
    output_dir: Path,
    grid_size: int = 8,
    icon_size: int = 32,
    offset_x: int = 0,
    offset_y: int = 0,
    rotate: int = 0,
) -> list[Path]:
    """
    Extract individual icons from a texture atlas.

    Args:
        atlas_png: Path to atlas PNG file
        output_dir: Directory to save extracted icons
        grid_size: Number of icons per row/column (default 8 for items, 4 for spells)
        icon_size: Size of each icon in pixels (32 for items, 64 for spells)
        offset_x: X offset in pixels (0 for items, 3 for spells)
        offset_y: Y offset in pixels (0 for items, 3 for spells)
        rotate: Rotation angle in degrees (0, 90, 180, 270)

    Returns:
        List of paths to extracted icon files
    """
    try:
        atlas = Image.open(atlas_png)

        if atlas.size[0] != 256 or atlas.size[1] != 256:
            print(f"  ⚠ Unexpected atlas size: {atlas.size} (expected 256x256)")
            # Recalculate grid size
            grid_size = atlas.size[0] // icon_size

        output_dir.mkdir(parents=True, exist_ok=True)
        extracted = []

        for row in range(grid_size):
            for col in range(grid_size):
                # Calculate position in atlas with offset
                x = offset_x + (col * icon_size)
                y = offset_y + (row * icon_size)

                # Check bounds
                if x + icon_size > atlas.size[0] or y + icon_size > atlas.size[1]:
                    continue  # Skip icons that exceed bounds

                # Extract icon
                icon = atlas.crop((x, y, x + icon_size, y + icon_size))

                # Apply rotation if specified
                if rotate != 0:
                    icon = icon.rotate(rotate, expand=False)

                # Calculate index (1-based to match game's item_ui_index)
                index = row * grid_size + col + 1

                # Save icon
                icon_path = output_dir / f"icon_{index:03d}.png"
                icon.save(icon_path)
                extracted.append(icon_path)

        return extracted

    except Exception as e:
        print(f"  ⚠ Error extracting from {atlas_png}: {e}")
        return []


def main():
    """Main extraction process."""

    project_root = Path(__file__).parent.parent.parent
    extracted_ui = project_root / "ExtractedAssets" / "UI" / "extracted"
    output_root = project_root / "ExtractedAssets" / "UI" / "icons_extracted"

    print("=" * 80)
    print("UI ICON ATLAS EXTRACTION")
    print("=" * 80)
    print(f"Input:  {extracted_ui}")
    print(f"Output: {output_root}")
    print()

    # Statistics
    stats = {
        "atlases_found": 0,
        "atlases_converted": 0,
        "icons_extracted": 0,
        "categories": {},
    }

    # Find all UI DDS files
    dds_files = list(extracted_ui.rglob("ui_*.dds"))
    print(f"Found {len(dds_files)} UI texture files")
    print()

    # Group by category (item, spell, bgr, etc.)
    by_category = {}
    for dds in dds_files:
        # Extract category from filename (ui_item14.dds -> item)
        parts = dds.stem.split("_")
        if len(parts) >= 2:
            category = parts[1]
            # Extract number from category (item14 -> item, 14)
            import re

            match = re.match(r"([a-z]+)(\d+)", category)
            if match:
                cat_name = match.group(1)
                cat_num = match.group(2)
                by_category.setdefault(cat_name, []).append((cat_num, dds))

    print(f"Found {len(by_category)} categories:")
    for cat, files in sorted(by_category.items()):
        print(f"  - {cat}: {len(files)} atlases")
        stats["categories"][cat] = len(files)
    print()

    # Process each category
    for cat_name in ["itm"]:  # Focus on itm first
        if cat_name not in by_category:
            print(f"⚠ Category '{cat_name}' not found, skipping")
            continue

        print(f"Processing category: {cat_name.upper()}")
        print("-" * 80)

        cat_files = sorted(by_category[cat_name], key=lambda x: int(x[0]))

        for atlas_num, dds_path in cat_files:
            stats["atlases_found"] += 1

            # Create output directory for this atlas
            atlas_output = output_root / cat_name / f"atlas_{atlas_num}"

            # Convert DDS to PNG first
            temp_png = atlas_output / f"_atlas_{atlas_num}.png"

            print(
                f"  [{cat_name}_{atlas_num}] Converting to PNG...", end=" ", flush=True
            )
            if convert_dds_to_png(dds_path, temp_png):
                print("✓")
                stats["atlases_converted"] += 1

                # Extract icons from atlas with category-specific settings
                print(
                    f"  [{cat_name}_{atlas_num}] Extracting icons...",
                    end=" ",
                    flush=True,
                )

                # Category-specific settings
                if cat_name == "spell":
                    # Spells: 64x64 icons, 4x4 grid, (3,3) offset, rotated 180°
                    extracted = extract_icons_from_atlas(
                        temp_png,
                        atlas_output,
                        grid_size=4,
                        icon_size=64,
                        offset_x=3,
                        offset_y=3,
                        rotate=180,
                    )
                elif cat_name == "itm":
                    # ITM: 16x16 icons, 16x16 grid, no offset
                    extracted = extract_icons_from_atlas(
                        temp_png,
                        atlas_output,
                        grid_size=16,
                        icon_size=16,
                        offset_x=0,
                        offset_y=0,
                    )
                else:
                    # Items and others: 32x32 icons, 8x8 grid, no offset
                    extracted = extract_icons_from_atlas(
                        temp_png,
                        atlas_output,
                        grid_size=8,
                        icon_size=32,
                        offset_x=0,
                        offset_y=0,
                    )

                if extracted:
                    print(f"✓ ({len(extracted)} icons)")
                    stats["icons_extracted"] += len(extracted)
                else:
                    print("✗")
            else:
                print("✗")

        print()

    # Create index of all extracted icons
    print("Creating icon index...")
    index_data = {"stats": stats, "icons": {}}

    for icon_file in output_root.rglob("icon_*.png"):
        # Parse path: icons_extracted/item/atlas_14/icon_003.png
        parts = icon_file.relative_to(output_root).parts
        if len(parts) == 3:
            category = parts[0]  # item
            atlas = parts[1].replace("atlas_", "")  # 14
            icon_num = icon_file.stem.replace("icon_", "")  # 003

            key = f"{category}_{atlas}_{icon_num}"
            index_data["icons"][key] = {
                "category": category,
                "atlas_number": atlas,
                "icon_index": int(icon_num),
                "path": str(icon_file.relative_to(output_root)),
            }

    # Split index into multiple smaller files
    print("Splitting index into smaller files...")
    split_icon_index(output_root, index_data, num_files=10)
    print()


def split_icon_index(output_dir: Path, index_data: dict, num_files: int = 10):
    """
    Split icon index into multiple smaller files for better handling.

    Args:
        output_dir: Directory to save the split files
        index_data: Complete icon index data
        num_files: Number of files to split into
    """
    import math

    all_icons = list(index_data["icons"].items())
    total_icons = len(all_icons)

    if total_icons == 0:
        print("  ⚠ No icons to split")
        return

    icons_per_file = math.ceil(total_icons / num_files)

    print(f"  Splitting {total_icons} icons into {num_files} files")
    print(f"  ~{icons_per_file} icons per file")

    # Create manifest file with metadata
    manifest = {
        "total_icons": total_icons,
        "num_files": num_files,
        "icons_per_file": icons_per_file,
        "stats": index_data["stats"],
        "files": [],
    }

    # Split and save files
    for i in range(num_files):
        start_idx = i * icons_per_file
        end_idx = min(start_idx + icons_per_file, total_icons)

        if start_idx >= total_icons:
            break

        # Get slice of icons
        icon_slice = all_icons[start_idx:end_idx]

        # Create file data
        file_data = {
            "file_index": i,
            "start_index": start_idx,
            "end_index": end_idx - 1,
            "icon_count": len(icon_slice),
            "icons": dict(icon_slice),
        }

        # Save file
        file_path = output_dir / f"icon_index_part_{i:02d}.json"
        with open(file_path, "w") as f:
            json.dump(file_data, f, indent=2)

        # Add to manifest
        manifest["files"].append(
            {
                "file": f"icon_index_part_{i:02d}.json",
                "start_index": start_idx,
                "end_index": end_idx - 1,
                "icon_count": len(icon_slice),
            }
        )

        print(
            f"  ✓ Part {i + 1}/{num_files}: {len(icon_slice)} icons -> {file_path.name}"
        )

    # Save manifest
    manifest_path = output_dir / "icon_index_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"  ✓ Manifest saved: {manifest_path.name}")

    # Also save a small lookup file for quick icon finding
    lookup_data = {}
    for key, icon_data in index_data["icons"].items():
        # Calculate which file contains this icon
        icon_idx = list(index_data["icons"].keys()).index(key)
        file_idx = icon_idx // icons_per_file
        lookup_data[key] = {
            "file": f"icon_index_part_{file_idx:02d}.json",
            "category": icon_data["category"],
            "atlas_number": icon_data["atlas_number"],
            "icon_index": icon_data["icon_index"],
        }

    lookup_path = output_dir / "icon_lookup.json"
    with open(lookup_path, "w") as f:
        json.dump(lookup_data, f, indent=2)

    print(f"  ✓ Lookup saved: {lookup_path.name}")
    print(f"  ✓ Split complete! Total files created: {num_files + 2}")

    # Print summary
    print("=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)
    print(f"Atlases found:     {index_data['stats']['atlases_found']}")
    print(f"Atlases converted: {index_data['stats']['atlases_converted']}")
    print(f"Icons extracted:   {index_data['stats']['icons_extracted']}")
    print()
    print("Categories:")
    for cat, count in sorted(index_data["stats"]["categories"].items()):
        print(f"  - {cat}: {count} atlases")
    print()
    print(f"Output: {output_dir}")
    print("=" * 80)

    # Next steps message
    print()
    print("NEXT STEPS:")
    print("-----------")
    print("1. Build handle-to-icon mapping by analyzing GameData.json")
    print("2. Create lookup function: handle -> (atlas_num, icon_index)")
    print("3. Update CFF editor to use the mapping")
    print()


if __name__ == "__main__":
    main()
