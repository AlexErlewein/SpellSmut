"""
SpellForce PAK Bulk Extractor using QuickBMS
Automatically downloads QuickBMS and extracts all PAK files using the BMS script.

This script:
1. Downloads QuickBMS if not present
2. Uses the SpellForce_PAK_script.bms to extract all PAK files
3. Organizes extracted files by type (audio, UI, textures, models, etc.)
4. Provides progress reporting

Author: SpellSmut Modding Project
Date: October 18, 2025
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
from pathlib import Path
import shutil

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
TOOLS_DIR = PROJECT_ROOT / "ModdingTools"
QUICKBMS_DIR = TOOLS_DIR / "quickbms"
QUICKBMS_EXE = QUICKBMS_DIR / "quickbms.exe"
BMS_SCRIPT = SCRIPT_DIR / "SpellForce_PAK_script.bms"

GAME_DIR = PROJECT_ROOT / "OriginalGameFiles"
PAK_DIR = GAME_DIR / "pak"
EXTRACTED_DIR = PROJECT_ROOT / "ExtractedAssets"

# QuickBMS download URL (official source)
QUICKBMS_URL = "https://aluigi.altervista.org/papers/quickbms.zip"


def print_banner():
    """Print script banner."""
    print("=" * 70)
    print(" " * 15 + "SpellForce PAK Bulk Extractor")
    print(" " * 20 + "Using QuickBMS")
    print("=" * 70)
    print()


def download_quickbms():
    """Download and extract QuickBMS if not present."""
    if QUICKBMS_EXE.exists():
        print(f"✓ QuickBMS already installed at: {QUICKBMS_EXE}")
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
        print("✓ Done")

        # Extract ZIP
        print("Extracting QuickBMS... ", end="", flush=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(QUICKBMS_DIR)
        print("✓ Done")

        # Clean up ZIP
        zip_path.unlink()

        # Verify executable exists
        if not QUICKBMS_EXE.exists():
            print(f"✗ ERROR: quickbms.exe not found after extraction!")
            return False

        print(f"✓ QuickBMS installed successfully at: {QUICKBMS_EXE}")
        return True

    except Exception as e:
        print(f"✗ Failed")
        print(f"ERROR: {e}")
        return False


def verify_bms_script():
    """Verify the BMS script exists."""
    if not BMS_SCRIPT.exists():
        print(f"✗ ERROR: BMS script not found at: {BMS_SCRIPT}")
        print("Please ensure SpellForce_PAK_script.bms is in src/helper_tools/")
        return False

    print(f"✓ BMS script found: {BMS_SCRIPT}")
    return True


def get_pak_files():
    """Get list of all PAK files to extract."""
    if not PAK_DIR.exists():
        print(f"✗ ERROR: PAK directory not found: {PAK_DIR}")
        return []

    pak_files = sorted(PAK_DIR.glob("*.pak"))

    if not pak_files:
        print(f"✗ ERROR: No PAK files found in {PAK_DIR}")
        return []

    print(f"\n✓ Found {len(pak_files)} PAK files:")
    total_size = 0
    for pak in pak_files:
        size_mb = pak.stat().st_size / (1024 * 1024)
        total_size += size_mb
        print(f"  - {pak.name:15s} ({size_mb:7.1f} MB)")

    print(f"\nTotal size: {total_size:7.1f} MB ({total_size/1024:.2f} GB)")

    return pak_files


def extract_pak(pak_file, output_dir, quickbms_exe, bms_script):
    """
    Extract a single PAK file using QuickBMS.

    Args:
        pak_file: Path to PAK file
        output_dir: Output directory
        quickbms_exe: Path to quickbms.exe
        bms_script: Path to BMS script

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
        str(quickbms_exe),
        "-o",  # Overwrite files without asking
        str(bms_script),
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
            print(f"✓ Successfully extracted {pak_file.name}")

            # Parse output for file count
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'files found' in line.lower() or 'extracted' in line.lower():
                    print(f"  {line.strip()}")

            return True
        else:
            print(f"✗ Failed to extract {pak_file.name}")
            print(f"Return code: {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"✗ Timeout while extracting {pak_file.name}")
        return False
    except Exception as e:
        print(f"✗ Error extracting {pak_file.name}: {e}")
        return False


def organize_extracted_files(raw_output_dir):
    """
    Organize extracted files into categories (audio, UI, textures, etc.).

    Args:
        raw_output_dir: Directory containing all extracted PAK contents
    """
    print("\n" + "=" * 70)
    print("Organizing extracted files by category...")
    print("=" * 70)

    # Category definitions (file extensions)
    categories = {
        'Audio': {
            'extensions': ['.wav', '.mp3'],
            'output_dir': EXTRACTED_DIR / 'Audio' / 'extracted'
        },
        'UI': {
            'extensions': ['.dds', '.tga'],
            'patterns': ['ui_', 'font_'],  # Must start with these
            'output_dir': EXTRACTED_DIR / 'UI' / 'extracted'
        },
        'Textures': {
            'extensions': ['.dds', '.tga'],
            'exclude_patterns': ['ui_', 'font_'],  # Exclude UI textures
            'output_dir': EXTRACTED_DIR / 'Textures'
        },
        'Models': {
            'extensions': ['.msb'],
            'output_dir': EXTRACTED_DIR / 'Models'
        },
        'Animations': {
            'extensions': ['.bob'],
            'output_dir': EXTRACTED_DIR / 'Animations'
        },
        'Skeletons': {
            'extensions': ['.bor'],
            'output_dir': EXTRACTED_DIR / 'Skeletons'
        },
        'Scripts': {
            'extensions': ['.lua'],
            'output_dir': EXTRACTED_DIR / 'Scripts'
        },
        'Other': {
            'extensions': [],  # Catch-all
            'output_dir': EXTRACTED_DIR / 'Other'
        }
    }

    # Count files by category
    file_counts = {cat: 0 for cat in categories}

    # Walk through all extracted files
    for root, dirs, files in os.walk(raw_output_dir):
        for file in files:
            source_path = Path(root) / file
            file_lower = file.lower()
            categorized = False

            # Try to categorize file
            for category, rules in categories.items():
                # Check extension
                if 'extensions' in rules and rules['extensions']:
                    if not any(file_lower.endswith(ext) for ext in rules['extensions']):
                        continue

                # Check patterns (must match)
                if 'patterns' in rules:
                    if not any(file_lower.startswith(pat) for pat in rules['patterns']):
                        continue

                # Check exclude patterns
                if 'exclude_patterns' in rules:
                    if any(file_lower.startswith(pat) for pat in rules['exclude_patterns']):
                        continue

                # Move file to category folder
                dest_dir = rules['output_dir']
                dest_dir.mkdir(parents=True, exist_ok=True)

                # Preserve subdirectory structure relative to PAK
                rel_path = source_path.relative_to(raw_output_dir)
                dest_path = dest_dir / rel_path.name  # Flatten structure

                # Copy file
                try:
                    shutil.copy2(source_path, dest_path)
                    file_counts[category] += 1
                    categorized = True
                    break
                except Exception as e:
                    print(f"Warning: Could not copy {file}: {e}")

            # If not categorized, put in "Other"
            if not categorized:
                dest_dir = categories['Other']['output_dir']
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_path = dest_dir / file
                try:
                    shutil.copy2(source_path, dest_path)
                    file_counts['Other'] += 1
                except Exception as e:
                    print(f"Warning: Could not copy {file}: {e}")

    # Print summary
    print("\nOrganization Summary:")
    print("-" * 70)
    for category, count in file_counts.items():
        if count > 0:
            print(f"  {category:15s}: {count:5d} files → {categories[category]['output_dir']}")
    print("-" * 70)
    print(f"  {'TOTAL':15s}: {sum(file_counts.values()):5d} files")


def main():
    """Main execution function."""
    print_banner()

    # Step 1: Download/verify QuickBMS
    print("Step 1: Checking QuickBMS installation")
    print("-" * 70)
    if not download_quickbms():
        print("\n✗ Failed to install QuickBMS. Exiting.")
        return 1

    # Step 2: Verify BMS script
    print("\nStep 2: Verifying BMS script")
    print("-" * 70)
    if not verify_bms_script():
        print("\n✗ BMS script verification failed. Exiting.")
        return 1

    # Step 3: Find PAK files
    print("\nStep 3: Locating PAK files")
    print("-" * 70)
    pak_files = get_pak_files()
    if not pak_files:
        print("\n✗ No PAK files found. Exiting.")
        return 1

    # Step 4: Confirm extraction
    print("\n" + "=" * 70)
    print("READY TO EXTRACT")
    print("=" * 70)
    print(f"PAK files: {len(pak_files)}")
    print(f"Output directory: {EXTRACTED_DIR}")
    print()

    response = input("Proceed with extraction? [y/N]: ").strip().lower()
    if response not in ['y', 'yes']:
        print("Extraction cancelled.")
        return 0

    # Step 5: Extract all PAK files
    print("\n" + "=" * 70)
    print("Step 4: Extracting PAK files")
    print("=" * 70)

    # Create temporary output directory
    raw_output = EXTRACTED_DIR / "_raw_extraction"
    raw_output.mkdir(parents=True, exist_ok=True)

    success_count = 0
    failed_paks = []

    for i, pak_file in enumerate(pak_files, 1):
        print(f"\n[{i}/{len(pak_files)}] ", end="")

        # Extract to subdirectory named after PAK
        pak_output = raw_output / pak_file.stem

        if extract_pak(pak_file, pak_output, QUICKBMS_EXE, BMS_SCRIPT):
            success_count += 1
        else:
            failed_paks.append(pak_file.name)

    # Step 6: Organize files
    if success_count > 0:
        organize_extracted_files(raw_output)

    # Step 7: Summary
    print("\n" + "=" * 70)
    print("EXTRACTION COMPLETE")
    print("=" * 70)
    print(f"Successfully extracted: {success_count}/{len(pak_files)} PAK files")

    if failed_paks:
        print(f"\nFailed PAK files:")
        for pak in failed_paks:
            print(f"  - {pak}")

    print(f"\nExtracted files location: {EXTRACTED_DIR}")
    print("\nCategories:")
    print(f"  - Audio: {EXTRACTED_DIR / 'Audio' / 'extracted'}")
    print(f"  - UI: {EXTRACTED_DIR / 'UI' / 'extracted'}")
    print(f"  - Textures: {EXTRACTED_DIR / 'Textures'}")
    print(f"  - Models: {EXTRACTED_DIR / 'Models'}")
    print(f"  - Other categories in: {EXTRACTED_DIR}")

    print("\n✓ Bulk extraction complete!")

    return 0 if success_count == len(pak_files) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nExtraction interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
