"""
Script to extract UI assets from SpellForce PAK files with original filenames.
This script will be run on Windows where the game is installed.

Usage:
    python extract_ui_with_names.py

Requirements:
- QuickBMS installed (will be downloaded automatically)
- SpellForce game installed
- Run from Windows environment

Author: SpellSmut Modding Project
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
from pathlib import Path
import shutil

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
TOOLS_DIR = PROJECT_ROOT / "ModdingTools"
QUICKBMS_DIR = TOOLS_DIR / "quickbms"
QUICKBMS_EXE = QUICKBMS_DIR / "quickbms.exe"
BMS_SCRIPT = SCRIPT_DIR / "SpellForce_PAK_script.bms"

# Game installation (from gamepath.txt)
GAME_DIR = None
PAK_DIR = None

# Output directories
RAW_OUTPUT = PROJECT_ROOT / "ExtractedAssets" / "UI" / "raw_reextraction"
FINAL_OUTPUT = PROJECT_ROOT / "ExtractedAssets" / "UI" / "extracted"

# QuickBMS download URL
QUICKBMS_URL = "https://aluigi.altervista.org/papers/quickbms.zip"


def print_banner():
    """Print script banner."""
    print("=" * 70)
    print(" " * 10 + "SpellForce UI Asset Re-extraction")
    print(" " * 15 + "With Original Filenames")
    print("=" * 70)
    print()


def read_game_path():
    """Read the game installation path from gamepath.txt."""
    global GAME_DIR, PAK_DIR

    gamepath_file = PROJECT_ROOT / "OriginalGameFiles" / "gamepath.txt"
    if not gamepath_file.exists():
        print(f"[ERROR] gamepath.txt not found: {gamepath_file}")
        print("Please ensure the game path is configured.")
        return False

    with open(gamepath_file, 'r') as f:
        line = f.read().strip()
        # Format: "39540 D:\SteamLibrary\steamapps\common\Spellforce Platinum Edition"
        parts = line.split(' ', 1)
        if len(parts) >= 2:
            GAME_DIR = Path(parts[1])
            PAK_DIR = GAME_DIR / "pak"
        else:
            print(f"[ERROR] Invalid gamepath.txt format: {line}")
            return False

    print(f"[OK] Game directory: {GAME_DIR}")
    print(f"[OK] PAK directory: {PAK_DIR}")

    if not PAK_DIR.exists():
        print(f"[ERROR] PAK directory not found: {PAK_DIR}")
        return False

    return True


def download_quickbms():
    """Download and extract QuickBMS if not present."""
    if QUICKBMS_EXE.exists():
        print(f"[OK] QuickBMS already installed at: {QUICKBMS_EXE}")
        return True

    print("QuickBMS not found. Downloading...")
    print(f"Download URL: {QUICKBMS_URL}")

    # Create tools directory
    QUICKBMS_DIR.mkdir(parents=True, exist_ok=True)

    # Download QuickBMS
    zip_path = QUICKBMS_DIR / "quickbms.zip"

    try:
        print("Downloading QuickBMS... ", end="", flush=True)
        urllib.request.urlretrieve(QUICKBMS_URL, zip_path)
        print("[OK] Done")

        # Extract ZIP
        print("Extracting QuickBMS... ", end="", flush=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(QUICKBMS_DIR)
        print("[OK] Done")

        # Clean up ZIP
        zip_path.unlink()

        # Verify executable exists
        if not QUICKBMS_EXE.exists():
            print(f"[ERROR] quickbms.exe not found after extraction!")
            return False

        print(f"[OK] QuickBMS installed successfully at: {QUICKBMS_EXE}")
        return True

    except Exception as e:
        print(f"[ERROR] Failed")
        print(f"ERROR: {e}")
        return False


def verify_bms_script():
    """Verify the BMS script exists."""
    if not BMS_SCRIPT.exists():
        print(f"[ERROR] BMS script not found at: {BMS_SCRIPT}")
        print("Please ensure SpellForce_PAK_script.bms is in src/helper_tools/")
        return False

    print(f"[OK] BMS script found: {BMS_SCRIPT}")
    return True


def get_pak_files():
    """Get list of all PAK files to extract."""
    if PAK_DIR is None or not PAK_DIR.exists():
        print(f"[ERROR] PAK directory not found: {PAK_DIR}")
        return []

    pak_files = sorted(PAK_DIR.glob("*.pak"))

    if not pak_files:
        print(f"[ERROR] No PAK files found in {PAK_DIR}")
        return []

    print(f"\n[OK] Found {len(pak_files)} PAK files:")
    total_size = 0
    for pak in pak_files:
        size_mb = pak.stat().st_size / (1024 * 1024)
        total_size += size_mb
        print(f"  - {pak.name:15s} ({size_mb:7.1f} MB)")

    print(f"\nTotal size: {total_size:7.1f} MB ({total_size/1024:.2f} GB)")

    return pak_files


def extract_pak(pak_file, output_dir):
    """
    Extract a single PAK file using QuickBMS.

    Args:
        pak_file: Path to PAK file
        output_dir: Output directory

    Returns:
        True if successful, False otherwise
    """
    print(f"\nExtracting: {pak_file.name}")
    print(f"Output: {output_dir}")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build command
    # QuickBMS usage: quickbms.exe [script] [input_file] [output_folder]
    cmd = [
        str(QUICKBMS_EXE),
        "-o",  # Overwrite files without asking
        str(BMS_SCRIPT),
        str(pak_file),
        str(output_dir)
    ]

    try:
        # Run QuickBMS
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=600  # 10 minute timeout per file
        )

        if result.returncode == 0:
            print(f"[OK] Successfully extracted {pak_file.name}")

            # Parse output for file count
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'files found' in line.lower() or 'extracted' in line.lower():
                    print(f"  {line.strip()}")

            return True
        else:
            print(f"[ERROR] Failed to extract {pak_file.name}")
            print(f"Return code: {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"[ERROR] Timeout while extracting {pak_file.name}")
        return False
    except Exception as e:
        print(f"[ERROR] Error extracting {pak_file.name}: {e}")
        return False


def filter_ui_assets(raw_dir, ui_output_dir):
    """
    Filter and copy only UI assets from the raw extraction.

    Args:
        raw_dir: Directory containing all extracted PAK contents
        ui_output_dir: Directory to copy UI assets to
    """
    print("\n" + "=" * 70)
    print("Filtering UI assets from extraction...")
    print("=" * 70)

    ui_count = 0

    # Walk through all extracted files
    for root, dirs, files in os.walk(raw_dir):
        for file in files:
            file_lower = file.lower()

            # Check if it's a UI-related file
            is_ui_asset = (
                file_lower.startswith('ui_') or
                file_lower.startswith('font_')
            ) and (
                file_lower.endswith('.dds') or
                file_lower.endswith('.tga')
            )

            if is_ui_asset:
                source_path = Path(root) / file
                rel_path = source_path.relative_to(raw_dir)

                # Copy to UI output directory
                dest_path = ui_output_dir / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                try:
                    shutil.copy2(source_path, dest_path)
                    ui_count += 1
                    if ui_count % 50 == 0:
                        print(f"  Copied {ui_count} UI assets...")
                except Exception as e:
                    print(f"Warning: Could not copy {file}: {e}")

    print(f"[OK] Filtered {ui_count} UI assets to {ui_output_dir}")


def main():
    """Main execution function."""
    print_banner()

    # Step 1: Read game path
    print("Step 1: Reading game installation path")
    print("-" * 70)
    if not read_game_path():
        print("\n[ERROR] Failed to read game path. Exiting.")
        return 1

    # Step 2: Download/verify QuickBMS
    print("\nStep 2: Checking QuickBMS installation")
    print("-" * 70)
    if not download_quickbms():
        print("\n[ERROR] Failed to install QuickBMS. Exiting.")
        return 1

    # Step 3: Verify BMS script
    print("\nStep 3: Verifying BMS script")
    print("-" * 70)
    if not verify_bms_script():
        print("\n[ERROR] BMS script verification failed. Exiting.")
        return 1

    # Step 4: Find PAK files
    print("\nStep 4: Locating PAK files")
    print("-" * 70)
    pak_files = get_pak_files()
    if not pak_files:
        print("\n[ERROR] No PAK files found. Exiting.")
        return 1

    # Step 5: Confirm extraction
    print("\n" + "=" * 70)
    print("READY TO EXTRACT UI ASSETS")
    print("=" * 70)
    print(f"PAK files: {len(pak_files)}")
    print(f"Raw output: {RAW_OUTPUT}")
    print(f"UI output: {FINAL_OUTPUT}")
    print()

    response = input("Proceed with UI asset extraction? [y/N]: ").strip().lower()
    if response not in ['y', 'yes']:
        print("Extraction cancelled.")
        return 0

    # Step 6: Extract all PAK files
    print("\n" + "=" * 70)
    print("Step 5: Extracting PAK files")
    print("=" * 70)

    # Extract to raw directory
    success_count = 0
    failed_paks = []

    for i, pak_file in enumerate(pak_files, 1):
        print(f"\n[{i}/{len(pak_files)}] ", end="")

        # Extract to subdirectory named after PAK
        pak_output = RAW_OUTPUT / pak_file.stem

        if extract_pak(pak_file, pak_output):
            success_count += 1
        else:
            failed_paks.append(pak_file.name)

    # Step 7: Filter UI assets
    if success_count > 0:
        ui_temp_dir = RAW_OUTPUT / "_ui_assets"
        filter_ui_assets(RAW_OUTPUT, ui_temp_dir)

        # Move UI assets to final location
        if ui_temp_dir.exists():
            print(f"\nMoving UI assets to final location: {FINAL_OUTPUT}")
            if FINAL_OUTPUT.exists():
                shutil.rmtree(FINAL_OUTPUT)
            shutil.move(str(ui_temp_dir), str(FINAL_OUTPUT))

    # Step 8: Summary
    print("\n" + "=" * 70)
    print("EXTRACTION COMPLETE")
    print("=" * 70)
    print(f"Successfully extracted: {success_count}/{len(pak_files)} PAK files")

    if failed_paks:
        print(f"\nFailed PAK files:")
        for pak in failed_paks:
            print(f"  - {pak}")

    print(f"\nUI assets extracted to: {FINAL_OUTPUT}")
    print("\nNext steps:")
    print("1. Run convert_ui_textures.py to convert DDS to PNG")
    print("2. Run rotate_ui_pngs.py to rotate PNGs by 180°")
    print("3. Run organize_ui_assets.py to organize by category")

    print("\n[OK] UI asset extraction complete!")

    return 0 if success_count == len(pak_files) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nExtraction interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)