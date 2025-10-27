#!/usr/bin/env python3
"""
Convert ITM DDS atlas files to PNG format (atlas-only, no individual icon extraction).

This script converts DDS atlas files to PNG format for ITM (item) textures,
keeping them as atlases without extracting individual icons.

Requirements:
- UV package manager (project standard)
- ImageMagick (magick command)

Usage:
    uv run convert_itm_atlases_only.py

Author: SpellSmut Modding Project
"""

import os
import sys
import subprocess
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
EXTRACTED_UI = PROJECT_ROOT / "ExtractedAssets" / "UI" / "extracted"
OUTPUT_ROOT = PROJECT_ROOT / "ExtractedAssets" / "UI" / "icons_extracted"


def print_banner():
    """Print script banner."""
    print("=" * 70)
    print(" " * 10 + "ITM Atlas Conversion: DDS → PNG (Atlas Only)")
    print("=" * 70)
    print()


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


def main():
    """Main conversion process for ITM atlases only."""

    print_banner()

    print(f"Input:  {EXTRACTED_UI}")
    print(f"Output: {OUTPUT_ROOT / 'itm'}")
    print()

    # Find all ITM DDS files
    itm_dds_files = list(EXTRACTED_UI.rglob("ui_itm*.dds"))
    print(f"Found {len(itm_dds_files)} ITM DDS atlas files")
    print()

    if not itm_dds_files:
        print("No ITM DDS files found!")
        print(f"Looked in: {EXTRACTED_UI}/**/ui_itm*.dds")
        return

    # Statistics
    stats = {
        "files_processed": 0,
        "conversions_successful": 0,
    }

    # Process each ITM DDS file
    for dds_file in sorted(itm_dds_files):
        print(f"Converting {dds_file.name}...", end=" ", flush=True)

        # Extract atlas number from filename (ui_itm14.dds -> 14)
        import re
        match = re.search(r'ui_itm(\d+)\.dds', dds_file.name)
        atlas_num = 0
        if match:
            atlas_num = int(match.group(1))

        # Create output directory for this atlas
        atlas_output = OUTPUT_ROOT / "itm" / f"atlas_{atlas_num}"

        # Convert DDS to PNG atlas
        png_atlas = atlas_output / f"_atlas_{atlas_num}.png"

        if convert_dds_to_png(dds_file, png_atlas):
            print("✓")
            stats["files_processed"] += 1
            stats["conversions_successful"] += 1
        else:
            print("✗")

    print()
    print("=" * 70)
    print("CONVERSION COMPLETE")
    print("=" * 70)
    print(f"Files processed: {stats['files_processed']}")
    print(f"Successful conversions: {stats['conversions_successful']}")
    print()
    print(f"Atlas PNG files saved to: {OUTPUT_ROOT / 'itm'}")
    print()
    print("Note: Individual icons were NOT extracted (as requested)")
    print("Each atlas contains 256 icons in a 16x16 grid")


if __name__ == "__main__":
    main()