"""
Rotate UI PNG files by 180 degrees.
SpellForce uses an inverted Y-axis, so UI elements need to be rotated.

Requirements:
- UV package manager (project standard)
- Pillow (PIL) library
- Run after convert_ui_textures.py

Usage:
    uv run rotate_ui_pngs.py

Author: SpellSmut Modding Project
"""

import sys
from pathlib import Path
from PIL import Image

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
UI_DIR = PROJECT_ROOT / "ExtractedAssets" / "UI" / "extracted"


def print_banner():
    """Print script banner."""
    print("=" * 70)
    print(" " * 15 + "UI PNG Rotation (180°)")
    print("=" * 70)
    print()


def check_pillow():
    """Check if Pillow is available."""
    try:
        print(f"[OK] Pillow version: {Image.__version__}")
        return True
    except AttributeError:
        print("[OK] Pillow available")
        return True
    except ImportError:
        print("[ERROR] Pillow not found. Please install with: pip install Pillow")
        return False


def rotate_png_files():
    """Rotate all UI PNG files by 180 degrees."""
    if not UI_DIR.exists():
        print(f"[ERROR] UI directory not found: {UI_DIR}")
        print("Please run convert_ui_textures.py first.")
        return False

    print(f"Scanning for PNG files in: {UI_DIR}")

    # Find all PNG files
    png_files = list(UI_DIR.rglob("*.png"))
    png_files.extend(UI_DIR.rglob("*.PNG"))  # Case insensitive

    if not png_files:
        print("[WARNING] No PNG files found")
        return True

    print(f"Found {len(png_files)} PNG files to rotate")

    success_count = 0
    error_count = 0

    for i, png_file in enumerate(png_files, 1):
        print(f"[{i}/{len(png_files)}] Rotating: {png_file.name}")

        try:
            # Open image
            with Image.open(png_file) as img:
                # Rotate by 180 degrees
                rotated = img.rotate(180)

                # Save back to the same file
                rotated.save(png_file, "PNG")

            success_count += 1

        except Exception as e:
            print(f"  [ERROR] Failed to rotate {png_file.name}: {e}")
            error_count += 1

    print("\nRotation Summary:")
    print(f"  Total files: {len(png_files)}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {error_count}")

    if error_count > 0:
        print(f"\n[WARNING] {error_count} files failed to rotate")

    return error_count == 0


def main():
    """Main execution function."""
    print_banner()

    print("Step 1: Checking Pillow installation")
    print("-" * 70)

    if not check_pillow():
        return 1

    print("\nStep 2: Rotating PNG files")
    print("-" * 70)

    if rotate_png_files():
        print("\n" + "=" * 70)
        print("ROTATION COMPLETE")
        print("=" * 70)
        print("Next step: Run organize_ui_assets.py to organize by category")
        print("Command: uv run organize_ui_assets.py")
        return 0
    else:
        print("\n[ERROR] Rotation failed")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nRotation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
