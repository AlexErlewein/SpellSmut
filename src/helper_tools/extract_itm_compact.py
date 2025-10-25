#!/usr/bin/env python3
"""
Compact ITM icon extraction - only keeps non-empty icons.

ITM atlases have 16x16 grid but most slots are empty.
This script extracts only the actual icons (typically ~16 per atlas).
"""

import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image


def convert_dds_to_png(dds_path: Path, png_path: Path) -> bool:
    """Convert DDS file to PNG using ImageMagick."""
    try:
        png_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["magick", "convert", str(dds_path), str(png_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0 and png_path.exists()
    except Exception as e:
        print(f"  ⚠ Conversion failed for {dds_path.name}: {e}")
        return False


def extract_non_empty_icons(
    atlas_png: Path,
    output_dir: Path,
    grid_size: int = 16,
    icon_size: int = 16,
) -> tuple[list[Path], dict]:
    """Extract only non-empty icons from ITM atlas."""
    try:
        atlas = Image.open(atlas_png)
        output_dir.mkdir(parents=True, exist_ok=True)
        extracted = []
        empty_count = 0
        icon_positions = {}

        for row in range(grid_size):
            for col in range(grid_size):
                x = col * icon_size
                y = row * icon_size

                if x + icon_size > atlas.size[0] or y + icon_size > atlas.size[1]:
                    continue

                icon = atlas.crop((x, y, x + icon_size, y + icon_size))

                # Check if icon is empty (transparent or single color)
                rgb_icon = icon.convert("RGB")
                pixels = list(rgb_icon.getdata())

                # Icon is empty if all pixels are the same
                is_empty = len(set(pixels)) == 1

                if not is_empty:
                    index = row * grid_size + col + 1
                    icon_path = output_dir / f"icon_{index:03d}.png"
                    icon.save(icon_path)
                    extracted.append(icon_path)
                    icon_positions[index] = (col, row)
                else:
                    empty_count += 1

        return extracted, {
            "total_positions": grid_size * grid_size,
            "empty_count": empty_count,
            "actual_icons": len(extracted),
            "icon_positions": icon_positions,
        }
    except Exception as e:
        print(f"  ⚠ Error extracting from {atlas_png}: {e}")
        return [], {}


def main():
    """Main compact ITM extraction process."""

    project_root = Path(__file__).parent.parent.parent
    extracted_ui = project_root / "ExtractedAssets" / "UI" / "extracted"
    output_root = project_root / "ExtractedAssets" / "UI" / "icons_extracted"

    print("=" * 80)
    print("COMPACT ITM ICON EXTRACTION")
    print("=" * 80)
    print(f"Input:  {extracted_ui}")
    print(f"Output: {output_root}")
    print()

    # Clean up existing ITM icons
    itm_output = output_root / "itm"
    if itm_output.exists():
        print("Cleaning up existing ITM icons...")
        shutil.rmtree(itm_output)
        print("  ✓ Cleanup complete")
        print()

    # Find all ITM DDS files in subdirectories
    itm_files = list(extracted_ui.rglob("ui_itm*.dds"))
    print(f"Found {len(itm_files)} ITM texture files")
    print()

    if not itm_files:
        print("⚠ No ITM files found!")
        return

    # Sort by atlas number
    itm_files.sort(key=lambda x: int(x.stem.split("m")[1]) if "m" in x.stem else 0)

    # Statistics
    stats = {
        "atlases_converted": 0,
        "total_positions": 0,
        "empty_slots": 0,
        "actual_icons": 0,
        "atlases": {},
    }

    # Process each ITM atlas
    for dds_path in itm_files:
        # Extract atlas number from filename (ui_itm0.dds -> 0)
        parts = dds_path.stem.split("m")
        if len(parts) < 2:
            continue
        atlas_num = parts[1]

        # Create output directory
        atlas_output = output_root / "itm" / f"atlas_{atlas_num}"

        # Convert DDS to PNG
        temp_png = atlas_output / f"_atlas_{atlas_num}.png"
        print(f"[ITM_{atlas_num}] Converting to PNG...", end=" ", flush=True)

        if convert_dds_to_png(dds_path, temp_png):
            print("✓")
            stats["atlases_converted"] += 1

            # Extract only non-empty icons
            print(
                f"[ITM_{atlas_num}] Extracting non-empty icons...", end=" ", flush=True
            )
            extracted, analysis = extract_non_empty_icons(temp_png, atlas_output)

            if extracted:
                print(
                    f"✓ ({len(extracted)} actual icons, {analysis['empty_count']} empty)"
                )
                stats["actual_icons"] += len(extracted)
                stats["total_positions"] += analysis["total_positions"]
                stats["empty_slots"] += analysis["empty_count"]

                # Store atlas statistics
                stats["atlases"][f"atlas_{atlas_num}"] = {
                    "actual_icons": len(extracted),
                    "empty_slots": analysis["empty_count"],
                    "icon_positions": analysis["icon_positions"],
                }
            else:
                print("✗")
        else:
            print("✗")

    # Create compact icon index for ITM
    print("\nCreating compact ITM icon index...")
    index_data = {
        "stats": stats,
        "icons": {},
        "extraction_info": {
            "grid_size": 16,
            "icon_size": 16,
            "category": "itm",
            "description": "ITM icons - non-empty only from 16x16 grid",
            "extraction_method": "compact_non_empty",
        },
    }

    # Build index from extracted ITM icons
    for icon_file in output_root.rglob("itm/*/icon_*.png"):
        parts = icon_file.relative_to(output_root).parts
        if len(parts) == 3 and parts[0] == "itm":
            category = parts[0]
            atlas = parts[1].replace("atlas_", "")
            icon_num = icon_file.stem.replace("icon_", "")

            key = f"{category}_{atlas}_{icon_num}"
            index_data["icons"][key] = {
                "category": category,
                "atlas_number": atlas,
                "icon_index": int(icon_num),
                "path": str(icon_file.relative_to(output_root)),
                "grid_size": 16,
                "icon_size": 16,
            }

    # Save compact index
    output_root.mkdir(parents=True, exist_ok=True)
    index_path = output_root / "icon_index.json"
    with open(index_path, "w") as f:
        json.dump(index_data, f, indent=2)
    print(f"✓ Compact ITM icon index saved: {index_path.name}")

    # Print summary
    print()
    print("=" * 80)
    print("COMPACT ITM EXTRACTION SUMMARY")
    print("=" * 80)
    print(f"Atlases processed: {stats['atlases_converted']}")
    print(f"Total grid positions: {stats['total_positions']}")
    print(f"Empty slots: {stats['empty_slots']}")
    print(f"Actual icons extracted: {stats['actual_icons']}")
    print(
        f"Average icons per atlas: {stats['actual_icons'] / stats['atlases_converted']:.1f}"
    )
    print()

    for atlas_name, atlas_stats in stats["atlases"].items():
        print(f"{atlas_name}:")
        print(f"  Actual icons: {atlas_stats['actual_icons']}")
        print(f"  Empty slots: {atlas_stats['empty_slots']}")
    print()

    print(f"Output: {output_root}")
    print("=" * 80)
    print()
    print("✅ COMPACT ITM ICON EXTRACTION COMPLETE!")
    print()
    print("Extracted only non-empty ITM icons:")
    print("- 16x16 pixel icons")
    print("- From 16x16 grid (256 positions per atlas)")
    print(
        f"- {stats['actual_icons']} actual icons from {stats['total_positions']} total positions"
    )
    print("- Compact, non-redundant icon library")
    print()


if __name__ == "__main__":
    main()
