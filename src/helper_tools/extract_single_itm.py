#!/usr/bin/env python3
"""
Extract a single ITM atlas for examination.
This will help us understand the actual layout and content.
"""

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


def extract_grid_preview(atlas_png: Path, output_dir: Path):
    """Extract a visual grid preview of the atlas."""
    try:
        atlas = Image.open(atlas_png)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create a grid preview showing all positions
        grid_size = 16
        icon_size = 16

        print(f"\nAtlas size: {atlas.size}")
        print(f"Grid layout: {grid_size}x{grid_size}")
        print(f"Icon size: {icon_size}x{icon_size}")

        # Extract first few icons to examine
        print("\nExtracting sample icons for examination:")

        sample_positions = [
            (0, 0),  # Top-left
            (0, 1),  # Next to it
            (1, 0),  # Below first
            (15, 15),  # Bottom-right
        ]

        for row, col in sample_positions:
            x = col * icon_size
            y = row * icon_size

            if x + icon_size <= atlas.size[0] and y + icon_size <= atlas.size[1]:
                icon = atlas.crop((x, y, x + icon_size, y + icon_size))

                # Check if icon is empty
                rgb_icon = icon.convert("RGB")
                pixels = list(rgb_icon.getdata())
                is_empty = len(set(pixels)) == 1

                index = row * grid_size + col + 1
                icon_path = output_dir / f"sample_{index:03d}_r{row}c{col}.png"
                icon.save(icon_path)

                print(
                    f"  Position ({row},{col}) -> icon_{index:03d}: {'EMPTY' if is_empty else 'HAS CONTENT'}"
                )

        # Count non-empty icons
        non_empty = 0
        empty = 0

        for row in range(grid_size):
            for col in range(grid_size):
                x = col * icon_size
                y = row * icon_size

                icon = atlas.crop((x, y, x + icon_size, y + icon_size))
                rgb_icon = icon.convert("RGB")
                pixels = list(rgb_icon.getdata())

                if len(set(pixels)) == 1:
                    empty += 1
                else:
                    non_empty += 1

        print("\nGrid Analysis:")
        print(f"  Total positions: {grid_size * grid_size}")
        print(f"  Non-empty icons: {non_empty}")
        print(f"  Empty icons: {empty}")
        print(f"  Fill ratio: {non_empty / (grid_size * grid_size) * 100:.1f}%")

        return non_empty, empty

    except Exception as e:
        print(f"  ⚠ Error analyzing atlas: {e}")
        return 0, 0


def main():
    """Extract single ITM atlas for examination."""

    project_root = Path(__file__).parent.parent.parent
    extracted_ui = project_root / "ExtractedAssets" / "UI" / "extracted"
    output_dir = project_root / "ExtractedAssets" / "UI" / "itm_examination"

    print("=" * 80)
    print("SINGLE ITM ATLAS EXAMINATION")
    print("=" * 80)
    print(f"Input:  {extracted_ui}")
    print(f"Output: {output_dir}")
    print()

    # Find ITM files
    itm_files = list(extracted_ui.rglob("ui_itm*.dds"))

    if not itm_files:
        print("⚠ No ITM files found!")
        return

    # Use the first ITM file for examination
    dds_path = itm_files[0]
    atlas_num = dds_path.stem.split("m")[1]

    print(f"Examining: {dds_path.name} (atlas {atlas_num})")

    # Convert DDS to PNG
    temp_png = output_dir / f"atlas_{atlas_num}.png"
    print("Converting to PNG...", end=" ", flush=True)

    if convert_dds_to_png(dds_path, temp_png):
        print("✓")

        # Analyze the grid
        non_empty, empty = extract_grid_preview(temp_png, output_dir)

        print(f"\n✅ Atlas {atlas_num} examination complete!")
        print("Check the output directory for sample icons:")
        print(f"  {output_dir}")

    else:
        print("✗")


if __name__ == "__main__":
    main()
