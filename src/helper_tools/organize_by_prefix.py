"""
Organize files by common name prefixes.

This script analyzes files in each category and groups them into subfolders
based on shared filename prefixes (e.g., all files starting with "char_avatar_"
go into a "char_avatar" subfolder).
"""

import os
import re
import shutil
from pathlib import Path
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
EXTRACTED_DIR = PROJECT_ROOT / "ExtractedAssets"

# Minimum files to create a group (avoid creating folders for single files)
MIN_GROUP_SIZE = 3


def extract_prefix(filename, min_length=3):
    """
    Extract meaningful prefix from filename.

    Strategy:
    1. Remove file extension
    2. Find common prefix pattern (words separated by _ or -)
    3. Return prefix up to first number or last separator before numbers
    """
    # Remove extension
    name = Path(filename).stem

    # Pattern: Extract prefix before numbers or version indicators
    # Examples:
    # "building_darkelf_arcanum_id1" -> "building_darkelf_arcanum"
    # "a_0100_01_0_3_01" -> "a"
    # "char_avatar_male_body_01" -> "char_avatar_male_body"
    # "ui_item_sword_long" -> "ui_item_sword"

    # Split by common separators
    parts = re.split(r'[_\-\.]', name)

    # Build prefix by taking parts until we hit a number-heavy part
    prefix_parts = []
    for part in parts:
        # If part is all digits, stop here
        if part.isdigit():
            break
        # If part starts with a digit (like "01abc"), stop here
        if part and part[0].isdigit():
            break
        # If part is very short and next parts exist, might be separator
        if len(part) < 2 and len(prefix_parts) > 0:
            break
        prefix_parts.append(part)

        # Stop at reasonable prefix length
        if len(prefix_parts) >= 5:
            break

    # Join back
    if prefix_parts:
        prefix = '_'.join(prefix_parts)
        # Minimum length check
        if len(prefix) >= min_length:
            return prefix

    # Fallback: first word only
    if parts and len(parts[0]) >= min_length:
        return parts[0]

    return None


def group_files_by_prefix(directory, min_group_size=MIN_GROUP_SIZE):
    """
    Group files in directory by common prefix.
    Returns dict of {prefix: [files]}
    """
    if not directory.exists() or not directory.is_dir():
        return {}

    # Collect all files (not directories)
    files = [f for f in os.listdir(directory) if (directory / f).is_file()]

    if not files:
        return {}

    # Group by prefix
    prefix_groups = defaultdict(list)

    for file in files:
        prefix = extract_prefix(file)
        if prefix:
            prefix_groups[prefix].append(file)

    # Filter out groups that are too small
    filtered_groups = {
        prefix: file_list
        for prefix, file_list in prefix_groups.items()
        if len(file_list) >= min_group_size
    }

    return filtered_groups


def organize_directory(directory, category_name, dry_run=False):
    """Organize files in a directory by prefix."""
    print(f"\nProcessing: {category_name}")
    print(f"  Path: {directory}")

    if not directory.exists():
        print(f"  [SKIP] Directory not found")
        return

    groups = group_files_by_prefix(directory)

    if not groups:
        print(f"  [SKIP] No groups found (all files unique or groups too small)")
        return

    # Sort groups by size (largest first)
    sorted_groups = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)

    print(f"  Found {len(sorted_groups)} groups:")

    moved_count = 0
    for prefix, files in sorted_groups:
        print(f"    {prefix:40s}: {len(files):4d} files")

        if not dry_run:
            # Create subfolder
            dest_dir = directory / prefix
            dest_dir.mkdir(exist_ok=True)

            # Move files
            for file in files:
                source = directory / file
                dest = dest_dir / file
                try:
                    shutil.move(str(source), str(dest))
                    moved_count += 1
                except Exception as e:
                    print(f"      [ERROR] Failed to move {file}: {e}")

    if not dry_run:
        print(f"  [OK] Moved {moved_count} files into {len(sorted_groups)} groups")

    return len(sorted_groups), moved_count


def organize_audio_uncategorized(dry_run=False):
    """Organize uncategorized audio files."""
    print("\n" + "=" * 70)
    print("Audio - Uncategorized Files")
    print("=" * 70)

    audio_dir = EXTRACTED_DIR / "Audio" / "extracted" / "uncategorized"
    organize_directory(audio_dir, "Audio/uncategorized", dry_run)


def organize_textures(dry_run=False):
    """Organize texture files in root directory."""
    print("\n" + "=" * 70)
    print("Textures - Root Directory")
    print("=" * 70)

    textures_dir = EXTRACTED_DIR / "Textures"
    organize_directory(textures_dir, "Textures", dry_run)


def organize_models(dry_run=False):
    """Organize model files in root directory."""
    print("\n" + "=" * 70)
    print("Models - Root Directory")
    print("=" * 70)

    models_dir = EXTRACTED_DIR / "Models"
    organize_directory(models_dir, "Models", dry_run)


def organize_animations(dry_run=False):
    """Organize animation files in root directory."""
    print("\n" + "=" * 70)
    print("Animations - Root Directory")
    print("=" * 70)

    anims_dir = EXTRACTED_DIR / "Animations"
    organize_directory(anims_dir, "Animations", dry_run)


def organize_skeletons(dry_run=False):
    """Organize skeleton files."""
    print("\n" + "=" * 70)
    print("Skeletons - All Files")
    print("=" * 70)

    skeletons_dir = EXTRACTED_DIR / "Skeletons"
    organize_directory(skeletons_dir, "Skeletons", dry_run)


def organize_scripts(dry_run=False):
    """Organize script files in root directory."""
    print("\n" + "=" * 70)
    print("Scripts - Root Directory")
    print("=" * 70)

    scripts_dir = EXTRACTED_DIR / "Scripts"
    organize_directory(scripts_dir, "Scripts", dry_run)


def organize_all_categories(dry_run=False):
    """
    Recursively organize all directories.
    This will organize both root files and files in existing subdirectories.
    """
    categories_to_process = [
        EXTRACTED_DIR / "Audio" / "extracted" / "uncategorized",
        EXTRACTED_DIR / "Textures",
        EXTRACTED_DIR / "Models",
        EXTRACTED_DIR / "Animations",
        EXTRACTED_DIR / "Skeletons",
        EXTRACTED_DIR / "Scripts",
    ]

    total_groups = 0
    total_moved = 0

    for category_dir in categories_to_process:
        if category_dir.exists():
            result = organize_directory(category_dir, str(category_dir.relative_to(EXTRACTED_DIR)), dry_run)
            if result:
                groups, moved = result
                total_groups += groups
                total_moved += moved

    return total_groups, total_moved


def main():
    """Main execution."""
    print("=" * 70)
    print(" " * 15 + "Organization by Filename Prefix")
    print(" " * 10 + "Grouping files with common name patterns")
    print("=" * 70)

    # First, show what would be done (dry run)
    print("\n[DRY RUN] Analyzing file groupings...\n")
    organize_all_categories(dry_run=True)

    # Ask for confirmation
    print("\n" + "=" * 70)
    response = input("\nProceed with organization? [y/N]: ").strip().lower()

    if response != 'y':
        print("Organization cancelled.")
        return

    # Perform actual organization
    print("\n" + "=" * 70)
    print("Organizing files...")
    print("=" * 70)

    groups, moved = organize_all_categories(dry_run=False)

    print("\n" + "=" * 70)
    print("Organization Complete!")
    print("=" * 70)
    print(f"\nCreated {groups} new groups")
    print(f"Moved {moved} files")
    print(f"\nLocation: {EXTRACTED_DIR}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
