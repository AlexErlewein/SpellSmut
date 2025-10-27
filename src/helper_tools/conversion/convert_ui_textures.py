"""
Convert DDS UI textures to PNG format.
This script converts all DDS files in the UI extracted directory to PNG.

Requirements:
- UV package manager (project standard)
- ImageMagick (magick command) or Pillow with DDS support
- Run after extract_ui_with_names.py

Usage:
    uv run convert_ui_textures.py [--yes] [--workers N]

Arguments:
    --yes, -y        Skip confirmation prompts
    --workers N      Number of parallel workers (default: CPU count)

Author: SpellSmut Modding Project
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

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
    """Check if ImageMagick is available (cross-platform)."""
    # On macOS/Linux, the command might be 'convert' instead of 'magick'
    commands_to_try = ["magick", "convert"]

    for cmd in commands_to_try:
        try:
            result = subprocess.run(
                [cmd, "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode == 0:
                print(f"[OK] ImageMagick found (using '{cmd}' command)")
                return cmd
        except FileNotFoundError:
            continue

    print("[WARNING] ImageMagick not found")
    return None


def convert_with_imagemagick(dds_file, png_file, magick_cmd):
    """Convert DDS to PNG using ImageMagick."""
    try:
        # Build command based on which ImageMagick command is available
        if magick_cmd == "magick":
            cmd = ["magick", "convert", str(dds_file), str(png_file)]
        else:  # convert command (macOS/Linux)
            cmd = ["convert", str(dds_file), str(png_file)]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,  # Add timeout to prevent hanging
        )

        if result.returncode == 0:
            return True
        else:
            return False

    except Exception as e:
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


def convert_single_file(args):
    """Convert a single DDS file to PNG (for parallel processing)."""
    dds_file, magick_cmd = args
    png_file = dds_file.with_suffix(".png")

    # Skip if PNG already exists
    if png_file.exists():
        return (True, dds_file.name, "skipped")

    success = False

    if magick_cmd:
        success = convert_with_imagemagick(dds_file, png_file, magick_cmd)

    if success:
        return (True, dds_file.name, "converted")
    else:
        return (False, dds_file.name, "failed")


def convert_dds_files(num_workers=None):
    """Convert all DDS files to PNG using parallel processing."""
    if not UI_DIR.exists():
        print(f"[ERROR] UI directory not found: {UI_DIR}")
        print("Please run extract_ui_with_names.py first.")
        return False

    print(f"Scanning for DDS files in: {UI_DIR}")

    # Find all DDS files
    dds_files = list(UI_DIR.rglob("*.dds"))
    dds_files.extend(UI_DIR.rglob("*.DDS"))  # Case insensitive

    # Remove duplicates
    dds_files = list(set(dds_files))

    if not dds_files:
        print("[WARNING] No DDS files found")
        return True

    print(f"Found {len(dds_files)} DDS files to convert")

    # Check for ImageMagick
    magick_cmd = check_imagemagick()

    if not magick_cmd:
        print("[ERROR] ImageMagick is required for conversion")
        return False

    # Determine number of workers
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()

    print(f"Using {num_workers} parallel workers")
    print()

    success_count = 0
    error_count = 0
    skipped_count = 0

    # Prepare arguments for parallel processing
    tasks = [(dds_file, magick_cmd) for dds_file in dds_files]

    # Process files in parallel
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(convert_single_file, task): task for task in tasks}

        completed = 0
        for future in as_completed(futures):
            completed += 1
            success, filename, status = future.result()

            if success:
                if status == "skipped":
                    skipped_count += 1
                else:
                    success_count += 1
            else:
                error_count += 1

            # Print progress every 100 files
            if completed % 100 == 0 or completed == len(dds_files):
                print(
                    f"Progress: {completed}/{len(dds_files)} files processed "
                    f"(✓ {success_count} | ⊘ {skipped_count} | ✗ {error_count})"
                )

    print("\n" + "=" * 70)
    print("Conversion Summary:")
    print(f"  Total files: {len(dds_files)}")
    print(f"  Converted: {success_count}")
    print(f"  Skipped (already exist): {skipped_count}")
    print(f"  Failed: {error_count}")

    if error_count > 0:
        print(f"\n[WARNING] {error_count} files failed to convert")

    return error_count == 0


def main():
    """Main execution function."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Convert DDS UI textures to PNG format with parallel processing"
    )
    parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompts"
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=None,
        help="Number of parallel workers (default: CPU count)",
    )
    args = parser.parse_args()

    print_banner()

    print("Step 1: Checking conversion tools")
    print("-" * 70)

    magick_cmd = check_imagemagick()

    if not magick_cmd:
        print("\n[ERROR] ImageMagick not available.")
        print("Installing ImageMagick is required for DDS conversion.")
        print()
        print("Installation instructions:")
        print("  Windows: winget install ImageMagick.ImageMagick")
        print("           or: choco install imagemagick")
        print("  macOS:   brew install imagemagick")
        print("  Ubuntu:  sudo apt install imagemagick")
        return 1

    print("\nStep 2: Converting DDS files to PNG")
    print("-" * 70)

    if convert_dds_files(num_workers=args.workers):
        print("\n" + "=" * 70)
        print("CONVERSION COMPLETE")
        print("=" * 70)
        print("Next step: Run rotate_ui_pngs.py to rotate PNGs by 180°")
        print("Command: uv run rotate_ui_pngs.py")
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
