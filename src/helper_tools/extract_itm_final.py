#!/usr/bin/env python3
"""
Final ITM icon extraction with correct path handling.

Extract ITM icons from UI atlases using 16x16 grid.
Handles the correct subdirectory structure (sfX/texture/).
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


def extract_icons_from_atlas(
    atlas_png: Path,
    output_dir: Path,
    grid_size: int = 16,
    icon_size: int = 16,
) -> list[Path]:
    """Extract 16x16 icons from ITM atlas."""
    try:
        atlas = Image.open(atlas_png)
        output_dir.mkdir(parents=True, exist_ok=True)
        extracted = []

        for row in range(grid_size):
            for col in range(grid_size):
                x = col * icon_size
                y = row * icon_size

                if x + icon_size > atlas.size[0] or y + icon_size > atlas.size[1]:
                    continue

                icon = atlas.crop((x, y, x + icon_size, y + icon_size))
                index = row * grid_size + col + 1
                icon_path = output_dir / f"icon_{index:03d}.png"
                icon.save(icon_path)
                extracted.append(icon_path)

        return extracted
    except Exception as e:
        print(f"  ⚠ Error extracting from {atlas_png}: {e}")
        return []


def main():
    """Main ITM extraction process."""

    project_root = Path(__file__).parent.parent.parent
    extracted_ui = project_root / "ExtractedAssets" / "UI" / "extracted"
    output_root = project_root / "ExtractedAssets" / "UI" / "icons_extracted"

    print("=" * 80)
    print("ITM ICON EXTRACTION - FINAL VERSION")
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
        "icons_extracted": 0,
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

            # Extract icons
            print(f"[ITM_{atlas_num}] Extracting 16x16 icons...", end=" ", flush=True)
            extracted = extract_icons_from_atlas(temp_png, atlas_output)

            if extracted:
                print(f"✓ ({len(extracted)} icons)")
                stats["icons_extracted"] += len(extracted)
            else:
                print("✗")
        else:
            print("✗")

    # Create icon index for ITM
    print("\nCreating ITM icon index...")
    index_data = {
        "stats": stats,
        "icons": {},
        "extraction_info": {
            "grid_size": 16,
            "icon_size": 16,
            "category": "itm",
            "description": "ITM icons with 16x16 grid layout",
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

    # Save ITM index
    output_root.mkdir(parents=True, exist_ok=True)
    index_path = output_root / "icon_index.json"
    with open(index_path, "w") as f:
        json.dump(index_data, f, indent=2)
    print(f"✓ ITM icon index saved: {index_path.name}")

    # Print summary
    print()
    print("=" * 80)
    print("ITM EXTRACTION SUMMARY")
    print("=" * 80)
    print(f"Atlases converted: {stats['atlases_converted']}")
    print(f"Icons extracted:   {stats['icons_extracted']}")
    print()
    print(f"Output: {output_root}")
    print("=" * 80)
    print()
    print("✅ ITM ICON EXTRACTION COMPLETE!")
    print()
    print("All ITM icons extracted with:")
    print("- 16x16 pixel icons")
    print("- 16x16 grid layout (256 icons per atlas)")
    print("- Proper indexing for CFF editor")
    print()
    print(f"Total icons extracted: {stats['icons_extracted']:,}")
    print()


if __name__ == "__main__":
    main()
