"""
Organize extracted files using the extraction lists as a guide.

This script reads the extraction list files and organizes the extracted
files into the same categories defined in those lists.
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
EXTRACTED_DIR = PROJECT_ROOT / "ExtractedAssets"


def read_extraction_list(list_file):
    """Read an extraction list file and return list of filenames."""
    filenames = []

    try:
        with open(list_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                filenames.append(line)
    except Exception as e:
        print(f"Error reading {list_file}: {e}")

    return filenames


def organize_audio_by_lists():
    """Organize audio files using extraction lists."""
    print("\n" + "=" * 70)
    print("Organizing Audio Files by Extraction Lists...")
    print("=" * 70)

    audio_dir = EXTRACTED_DIR / "Audio" / "extracted"
    lists_dir = EXTRACTED_DIR / "Audio" / "extraction_lists"

    if not audio_dir.exists():
        print(f"Audio directory not found: {audio_dir}")
        return

    if not lists_dir.exists():
        print(f"Extraction lists not found: {lists_dir}")
        return

    # Get all extraction list files
    list_files = sorted(lists_dir.glob("*.txt"))

    if not list_files:
        print("No extraction list files found!")
        return

    file_counts = defaultdict(int)
    moved_files = set()

    # Process each extraction list
    for list_file in list_files:
        category = list_file.stem  # Filename without .txt

        print(f"\nProcessing category: {category}")

        # Read the list of files for this category
        expected_files = read_extraction_list(list_file)

        if not expected_files:
            continue

        # Create category subdirectory
        dest_dir = audio_dir / category
        dest_dir.mkdir(exist_ok=True)

        # Move matching files
        for filename in expected_files:
            source = audio_dir / filename

            if source.exists() and source.is_file():
                dest = dest_dir / filename
                try:
                    shutil.move(str(source), str(dest))
                    file_counts[category] += 1
                    moved_files.add(filename)
                except Exception as e:
                    print(f"  Error moving {filename}: {e}")
            # Note: File might not exist if naming doesn't match exactly

    # Count remaining files
    remaining = []
    for file in os.listdir(audio_dir):
        if (audio_dir / file).is_file() and file not in moved_files:
            remaining.append(file)

    if remaining:
        # Move remaining files to "uncategorized"
        uncategorized_dir = audio_dir / "uncategorized"
        uncategorized_dir.mkdir(exist_ok=True)

        for file in remaining:
            source = audio_dir / file
            dest = uncategorized_dir / file
            try:
                shutil.move(str(source), str(dest))
                file_counts['uncategorized'] += 1
            except Exception as e:
                print(f"Error moving {file}: {e}")

    # Print summary
    print("\n" + "=" * 70)
    print("Audio Organization Summary:")
    print("-" * 70)
    for cat in sorted(file_counts.keys()):
        count = file_counts[cat]
        print(f"  {cat:25s}: {count:5d} files")
    print("-" * 70)
    print(f"  {'TOTAL':25s}: {sum(file_counts.values()):5d} files")


def organize_ui_by_lists():
    """Organize UI files using extraction lists."""
    print("\n" + "=" * 70)
    print("Organizing UI Files by Extraction Lists...")
    print("=" * 70)

    ui_dir = EXTRACTED_DIR / "UI" / "extracted"
    lists_dir = EXTRACTED_DIR / "UI" / "extraction_lists"

    if not ui_dir.exists():
        print(f"UI directory not found: {ui_dir}")
        return

    if not lists_dir.exists():
        print(f"Extraction lists not found: {lists_dir}")
        return

    list_files = sorted(lists_dir.glob("*.txt"))

    if not list_files:
        print("No extraction list files found!")
        return

    file_counts = defaultdict(int)
    moved_files = set()

    for list_file in list_files:
        category = list_file.stem

        print(f"\nProcessing category: {category}")

        expected_files = read_extraction_list(list_file)

        if not expected_files:
            continue

        dest_dir = ui_dir / category
        dest_dir.mkdir(exist_ok=True)

        for filename in expected_files:
            source = ui_dir / filename

            if source.exists() and source.is_file():
                dest = dest_dir / filename
                try:
                    shutil.move(str(source), str(dest))
                    file_counts[category] += 1
                    moved_files.add(filename)
                except Exception as e:
                    print(f"  Error moving {filename}: {e}")

    # Count remaining files
    remaining = []
    for file in os.listdir(ui_dir):
        if (ui_dir / file).is_file() and file not in moved_files:
            remaining.append(file)

    if remaining:
        uncategorized_dir = ui_dir / "uncategorized"
        uncategorized_dir.mkdir(exist_ok=True)

        for file in remaining:
            source = ui_dir / file
            dest = uncategorized_dir / file
            try:
                shutil.move(str(source), str(dest))
                file_counts['uncategorized'] += 1
            except Exception as e:
                print(f"Error moving {file}: {e}")

    # Print summary
    print("\n" + "=" * 70)
    print("UI Organization Summary:")
    print("-" * 70)
    for cat in sorted(file_counts.keys()):
        count = file_counts[cat]
        print(f"  {cat:25s}: {count:5d} files")
    print("-" * 70)
    print(f"  {'TOTAL':25s}: {sum(file_counts.values()):5d} files")


def main():
    """Main execution."""
    print("=" * 70)
    print(" " * 15 + "File Organization by Extraction Lists")
    print("=" * 70)
    print("\nThis script organizes files using the extraction lists")
    print("generated by the asset scanners.\n")

    # Organize audio files
    organize_audio_by_lists()

    # Organize UI files
    organize_ui_by_lists()

    print("\n" + "=" * 70)
    print("Organization Complete!")
    print("=" * 70)
    print(f"\nFiles organized in: {EXTRACTED_DIR}")
    print("\nAudio categories:")
    print(f"  {EXTRACTED_DIR / 'Audio' / 'extracted'}")
    print("\nUI categories:")
    print(f"  {EXTRACTED_DIR / 'UI' / 'extracted'}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
