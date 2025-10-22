"""
Convert DDS UI textures to PNG format.
This script converts all DDS files in the UI extracted directory to PNG.

Requirements:
- ImageMagick (magick command) or Pillow with DDS support
- Run after extract_ui_with_names.py

Usage:
    python convert_ui_textures.py

Author: SpellSmut Modding Project
"""

import os
import sys
import subprocess
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
UI_DIR = PROJECT_ROOT / "ExtractedAssets" / "UI" / "extracted"


def print_banner():
    """Print script banner."""
    print("=" * 70)
    print(" " * 10 + "UI Texture Conversion: DDS → PNG")
    print("=" * 70)
    print()


def check_imagemagick():
    """Check if ImageMagick is available."""
    try:
        result = subprocess.run(
            ["magick", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            print("[OK] ImageMagick found")
            return True
        else:
            print("[WARNING] ImageMagick not found or not working")
            return False
    except FileNotFoundError:
        print("[WARNING] ImageMagick (magick command) not found")
        return False


def convert_with_imagemagick(dds_file, png_file):
    """Convert DDS to PNG using ImageMagick."""
    try:
        cmd = ["magick", "convert", str(dds_file), str(png_file)]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            return True
        else:
            print(f"  [ERROR] ImageMagick conversion failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"  [ERROR] ImageMagick conversion error: {e}")
        return False


def convert_with_pillow(dds_file, png_file):
    """Convert DDS to PNG using Pillow (fallback)."""
    try:
        from PIL import Image

        # Note: Pillow doesn't have built-in DDS support
        # This would require additional plugins
        print("  [WARNING] Pillow DDS conversion not implemented")
        return False

    except ImportError:
        print("  [WARNING] Pillow not available")
        return False


def convert_dds_files():
    """Convert all DDS files to PNG."""
    if not UI_DIR.exists():
        print(f"[ERROR] UI directory not found: {UI_DIR}")
        print("Please run extract_ui_with_names.py first.")
        return False

    print(f"Scanning for DDS files in: {UI_DIR}")

    # Find all DDS files
    dds_files = list(UI_DIR.rglob("*.dds"))
    dds_files.extend(UI_DIR.rglob("*.DDS"))  # Case insensitive

    if not dds_files:
        print("[WARNING] No DDS files found")
        return True

    print(f"Found {len(dds_files)} DDS files to convert")

    # Check for ImageMagick
    has_imagemagick = check_imagemagick()

    success_count = 0
    error_count = 0

    for i, dds_file in enumerate(dds_files, 1):
        # Create PNG path (same directory, same name, .png extension)
        png_file = dds_file.with_suffix('.png')

        print(f"[{i}/{len(dds_files)}] Converting: {dds_file.name} → {png_file.name}")

        success = False

        # Try ImageMagick first
        if has_imagemagick:
            success = convert_with_imagemagick(dds_file, png_file)

        # Fallback to Pillow
        if not success:
            success = convert_with_pillow(dds_file, png_file)

        if success:
            success_count += 1
            # Optionally remove the original DDS file
            # dds_file.unlink()  # Uncomment to delete DDS after conversion
        else:
            error_count += 1

    print("\nConversion Summary:")
    print(f"  Total files: {len(dds_files)}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {error_count}")

    if error_count > 0:
        print(f"\n[WARNING] {error_count} files failed to convert")
        print("You may need to install ImageMagick or DDS plugins for Pillow")

    return error_count == 0


def main():
    """Main execution function."""
    print_banner()

    print("Step 1: Checking conversion tools")
    print("-" * 70)

    if not check_imagemagick():
        print("\n[WARNING] ImageMagick not available.")
        print("Installing ImageMagick is recommended for best results.")
        print("On Windows: choco install imagemagick")
        print("On macOS: brew install imagemagick")
        print("On Ubuntu: sudo apt install imagemagick")
        print()

        response = input("Continue anyway? [y/N]: ").strip().lower()
        if response not in ['y', 'yes']:
            print("Conversion cancelled.")
            return 1

    print("\nStep 2: Converting DDS files to PNG")
    print("-" * 70)

    if convert_dds_files():
        print("\n" + "=" * 70)
        print("CONVERSION COMPLETE")
        print("=" * 70)
        print("Next step: Run rotate_ui_pngs.py to rotate PNGs by 180°")
        return 0
    else:
        print("\n[ERROR] Conversion failed")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nConversion interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)