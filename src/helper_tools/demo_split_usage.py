#!/usr/bin/env python3
"""
Demo script showing how to use the split icon index and analysis files.

This script demonstrates:
1. Loading split icon data
2. Finding specific icons
3. Searching for icons by criteria
4. Working with analysis data
"""

import sys
from pathlib import Path

# Add the helper_tools directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from icon_split_utils import (
    find_icon,
    get_split_file_stats,
    load_split_icon_analysis,
    load_split_icon_index,
    merge_split_files,
    search_icons,
)


def demo_load_data(icons_root: Path):
    """Demonstrate loading split icon data."""
    print("\n" + "=" * 60)
    print("DEMO: Loading Split Icon Data")
    print("=" * 60)

    try:
        # Load icon index
        print("Loading icon index from split files...")
        icon_data = load_split_icon_index(icons_root)
        print(f"✓ Loaded {len(icon_data['icons'])} icons")
        print(f"  Stats: {icon_data['stats']['icons_extracted']} icons extracted")

        # Load icon analysis
        print("\nLoading icon analysis from split files...")
        analysis_data = load_split_icon_analysis(icons_root)
        print(f"✓ Loaded {len(analysis_data['analyses'])} analyses")
        print(f"  Empty icons: {analysis_data['summary']['empty_count']}")

        return icon_data, analysis_data

    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        return None, None


def demo_find_icon(icons_root: Path):
    """Demonstrate finding a specific icon."""
    print("\n" + "=" * 60)
    print("DEMO: Finding Specific Icons")
    print("=" * 60)

    # Try to find some specific icons
    test_cases = [
        ("itm", "0", 1),  # First item icon
        ("itm", "0", 64),  # Last icon in first atlas
        ("itm", "1", 1),  # First icon in second atlas
    ]

    for category, atlas_num, icon_idx in test_cases:
        print(f"\nLooking for: {category}_atlas_{atlas_num}_icon_{icon_idx:03d}")

        icon_data = find_icon(icons_root, category, atlas_num, icon_idx)

        if icon_data:
            print("✓ Found icon:")
            print(f"  Path: {icon_data['path']}")
            print(f"  Empty: {icon_data.get('is_empty', 'Unknown')}")
            if "empty_reasons" in icon_data and icon_data["empty_reasons"]:
                print(f"  Reasons: {', '.join(icon_data['empty_reasons'])}")
        else:
            print("❌ Icon not found")


def demo_search(icons_root: Path):
    """Demonstrate searching for icons."""
    print("\n" + "=" * 60)
    print("DEMO: Searching Icons")
    print("=" * 60)

    # Search for different types of icons
    searches = [
        {"category": "itm", "limit": 5, "desc": "First 5 item icons"},
        {
            "category": "itm",
            "atlas_range": (0, 2),
            "limit": 10,
            "desc": "First 10 icons from atlases 0-2",
        },
        {"is_empty": True, "limit": 5, "desc": "First 5 empty icons"},
        {"is_empty": False, "limit": 5, "desc": "First 5 non-empty icons"},
    ]

    for search_params in searches:
        desc = search_params.pop("desc")
        print(f"\n{desc}:")

        try:
            results = search_icons(icons_root, **search_params)

            if results:
                for result in results[:3]:  # Show first 3
                    print(f"  - {result['key']}")
            else:
                print("  No results found")

        except Exception as e:
            print(f"  Search failed: {e}")


def demo_stats(icons_root: Path):
    """Demonstrate getting file statistics."""
    print("\n" + "=" * 60)
    print("DEMO: File Statistics")
    print("=" * 60)

    stats = get_split_file_stats(icons_root)

    print("Icon Index Files:")
    if stats["icon_index"]["exists"]:
        print(f"  Total files: {len(stats['icon_index']['files'])}")
        print(f"  Total size: {stats['icon_index']['total_size_mb']} MB")
        print("  File details:")
        for file in stats["icon_index"]["files"]:
            print(f"    - {file['name']}: {file['size_mb']} MB")
    else:
        print("  ❌ No split index files found")

    print("\nIcon Analysis Files:")
    if stats["icon_analysis"]["exists"]:
        print(f"  Total files: {len(stats['icon_analysis']['files'])}")
        print(f"  Total size: {stats['icon_analysis']['total_size_mb']} MB")
        print("  File details:")
        for file in stats["icon_analysis"]["files"]:
            print(f"    - {file['name']}: {file['size_mb']} MB")
    else:
        print("  ❌ No split analysis files found")

    print("\nLookup File:")
    if stats["lookup"]["exists"]:
        print(f"  Size: {stats['lookup']['size_mb']} MB")
    else:
        print("  ❌ No lookup file found")


def demo_merge(icons_root: Path):
    """Demonstrate merging split files."""
    print("\n" + "=" * 60)
    print("DEMO: Merging Split Files")
    print("=" * 60)

    try:
        merged_index, merged_analysis = merge_split_files(icons_root)

        print(f"✓ Merged index: {merged_index}")
        print(f"✓ Merged analysis: {merged_analysis}")

        # Show file sizes
        index_size = merged_index.stat().st_size / (1024 * 1024)
        analysis_size = merged_analysis.stat().st_size / (1024 * 1024)

        print("\nMerged file sizes:")
        print(f"  Icon index: {index_size:.2f} MB")
        print(f"  Icon analysis: {analysis_size:.2f} MB")

    except Exception as e:
        print(f"❌ Merge failed: {e}")


def main():
    """Run all demos."""
    project_root = Path(__file__).parent.parent.parent
    icons_root = project_root / "ExtractedAssets" / "UI" / "icons_extracted"

    if not icons_root.exists():
        print(f"❌ Icons directory not found: {icons_root}")
        print("Please run the icon extraction and analysis first.")
        sys.exit(1)

    print("ICON SPLIT FILES DEMO")
    print("=" * 80)
    print(f"Working with: {icons_root}")

    # Check if split files exist
    manifest_path = icons_root / "icon_index_manifest.json"
    if not manifest_path.exists():
        print("\n⚠ No split files found!")
        print("Please run extract_icons_from_atlases.py with the updated code first.")
        sys.exit(1)

    # Run demos
    demo_stats(icons_root)
    demo_load_data(icons_root)
    demo_find_icon(icons_root)
    demo_search(icons_root)

    # Ask if user wants to merge
    print("\n" + "=" * 60)
    response = input("Do you want to merge split files into single files? (y/N): ")
    if response.lower() == "y":
        demo_merge(icons_root)

    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
