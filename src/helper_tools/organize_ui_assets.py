"""
Organize UI assets into categories while preserving existing folder structure.
This script organizes the re-extracted UI assets with original names into the existing category structure.

Requirements:
- UV package manager (project standard)
- Run after rotate_ui_pngs.py
- Preserves existing ExtractedAssets/UI/extracted/ structure

Usage:
    uv run organize_ui_assets.py

Author: SpellSmut Modding Project
"""

import os
import sys
import shutil
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
SOURCE_DIR = PROJECT_ROOT / "ExtractedAssets" / "UI" / "raw_reextraction" / "_ui_assets"
TARGET_DIR = PROJECT_ROOT / "ExtractedAssets" / "UI" / "extracted"


def print_banner():
    """Print script banner."""
    print("=" * 70)
    print(" " * 10 + "UI Asset Organization by Category")
    print("=" * 70)
    print()


def get_category_mapping():
    """Get the mapping of filename prefixes to categories."""
    return {
        "items": ["ui_item_", "ui_itm_"],
        "spells": ["ui_spell_"],
        "cursors": ["ui_cursor_"],
        "backgrounds": ["ui_bgr_"],
        "buttons": ["ui_btn_"],
        "mainmenu": ["ui_mainmenu_"],
        "containers": ["ui_cnt_"],
        "logos": ["ui_logo_"],
        "fonts": ["font_"],
        "other": ["ui_"],  # Catch-all for ui_ files not in other categories
    }


def organize_assets():
    """Organize UI assets into categories."""
    if not SOURCE_DIR.exists():
        print(f"[ERROR] Source directory not found: {SOURCE_DIR}")
        print("Please run extract_ui_with_names.py first.")
        return False

    if not TARGET_DIR.exists():
        print(f"[WARNING] Target directory doesn't exist: {TARGET_DIR}")
        print("Creating it...")
        TARGET_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Source directory: {SOURCE_DIR}")
    print(f"Target directory: {TARGET_DIR}")

    categories = get_category_mapping()
    file_counts = {cat: 0 for cat in categories}

    # Walk through all source files
    for root, dirs, files in os.walk(SOURCE_DIR):
        for file in files:
            source_path = Path(root) / file

            # Determine category based on filename prefix
            categorized = False
            for category, prefixes in categories.items():
                if any(file.startswith(p) for p in prefixes):
                    # Create target path
                    target_path = TARGET_DIR / category / file
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    # Copy file
                    try:
                        shutil.copy2(source_path, target_path)
                        file_counts[category] += 1
                        categorized = True
                        break
                    except Exception as e:
                        print(f"Warning: Could not copy {file}: {e}")

            # If not categorized, put in "other"
            if not categorized:
                target_path = TARGET_DIR / "other" / file
                target_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(source_path, target_path)
                    file_counts["other"] += 1
                except Exception as e:
                    print(f"Warning: Could not copy {file}: {e}")

    # Print summary
    print("\nOrganization Summary:")
    print("-" * 70)
    total_files = 0
    for category, count in file_counts.items():
        if count > 0:
            print(f"  {category:12s}: {count:5d} files")
            total_files += count
    print("-" * 70)
    print(f"  {'TOTAL':12s}: {total_files:5d} files")

    return True


def verify_organization():
    """Verify that the organization was successful."""
    print("\nVerifying organization...")

    categories = get_category_mapping()
    issues = []

    # Check that each category directory exists and has files
    for category in categories:
        category_dir = TARGET_DIR / category
        if category_dir.exists():
            files = list(category_dir.glob("*"))
            if not files:
                issues.append(f"Category '{category}' is empty")
        else:
            issues.append(f"Category '{category}' directory not created")

    if issues:
        print("[WARNING] Organization issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("[OK] All categories organized successfully")
        return True


def main():
    """Main execution function."""
    print_banner()

    print("Step 1: Organizing UI assets by category")
    print("-" * 70)

    if not organize_assets():
        print("\n[ERROR] Organization failed")
        return 1

    print("\nStep 2: Verifying organization")
    print("-" * 70)

    if verify_organization():
        print("\n" + "=" * 70)
        print("ORGANIZATION COMPLETE")
        print("=" * 70)
        print(f"UI assets are now organized in: {TARGET_DIR}")
        print("\nNext steps:")
        print("1. Test in GUI editor:")
        print("   cd ../../TirganachReloaded")
        print("   uv run tirganach")
        print("2. Verify icons display correctly")
        return 0
    else:
        print("\n[WARNING] Organization completed with issues")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nOrganization interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
