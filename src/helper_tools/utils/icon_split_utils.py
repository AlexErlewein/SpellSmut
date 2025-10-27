#!/usr/bin/env python3
"""
Utility functions for working with split icon index and analysis files.

This module provides helper functions to:
1. Load split icon index files
2. Load split icon analysis files
3. Search for specific icons across split files
4. Merge split files back into a single file
5. Get statistics about split files
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def load_split_icon_index(icons_root: Path) -> Dict[str, Any]:
    """
    Load icon index from split files.

    Args:
        icons_root: Directory containing split index files

    Returns:
        Combined icon index data with stats and icons
    """
    manifest_path = icons_root / "icon_index_manifest.json"

    if not manifest_path.exists():
        # Try to load single file
        single_path = icons_root / "icon_index.json"
        if single_path.exists():
            with open(single_path, "r") as f:
                return json.load(f)
        raise FileNotFoundError(f"No icon index manifest found at {manifest_path}")

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    # Combine all icons from split files
    all_icons = {}

    for file_info in manifest["files"]:
        file_path = icons_root / file_info["file"]
        with open(file_path, "r") as f:
            part_data = json.load(f)
            all_icons.update(part_data["icons"])

    return {"stats": manifest["stats"], "icons": all_icons}


def load_split_icon_analysis(icons_root: Path) -> Dict[str, Any]:
    """
    Load icon analysis from split files.

    Args:
        icons_root: Directory containing split analysis files

    Returns:
        Combined analysis data
    """
    manifest_path = icons_root / "icon_analysis_manifest.json"

    if not manifest_path.exists():
        # Try to load single file
        single_path = icons_root / "icon_analysis.json"
        if single_path.exists():
            with open(single_path, "r") as f:
                return json.load(f)
        raise FileNotFoundError(f"No icon analysis manifest found at {manifest_path}")

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    # Combine all analyses from split files
    all_analyses = []

    for file_info in manifest["files"]:
        file_path = icons_root / file_info["file"]
        with open(file_path, "r") as f:
            part_data = json.load(f)
            all_analyses.extend(part_data["analyses"])

    return {"summary": manifest["summary"], "analyses": all_analyses}


def find_icon(
    icons_root: Path, category: str, atlas_number: str, icon_index: int
) -> Optional[Dict]:
    """
    Find a specific icon in the split index files.

    Args:
        icons_root: Directory containing split index files
        category: Icon category (e.g., 'item', 'spell')
        atlas_number: Atlas number as string
        icon_index: Icon index within atlas

    Returns:
        Icon data dict if found, None otherwise
    """
    # First try the quick lookup file
    lookup_path = icons_root / "icon_lookup.json"
    if lookup_path.exists():
        with open(lookup_path, "r") as f:
            lookup = json.load(f)

        key = f"{category}_{atlas_number}_{icon_index:03d}"
        if key in lookup:
            file_name = lookup[key]["file"]
            file_path = icons_root / file_name

            with open(file_path, "r") as f:
                part_data = json.load(f)

            return part_data["icons"].get(key)

    # Fallback to loading all files
    icon_index_data = load_split_icon_index(icons_root)
    key = f"{category}_{atlas_number}_{icon_index:03d}"
    return icon_index_data["icons"].get(key)


def get_split_file_stats(icons_root: Path) -> Dict[str, Any]:
    """
    Get statistics about split files.

    Args:
        icons_root: Directory containing split files

    Returns:
        Dictionary with file statistics
    """
    stats = {
        "icon_index": {"exists": False, "files": [], "total_size_mb": 0},
        "icon_analysis": {"exists": False, "files": [], "total_size_mb": 0},
        "lookup": {"exists": False, "size_mb": 0},
    }

    # Icon index stats
    manifest_path = icons_root / "icon_index_manifest.json"
    if manifest_path.exists():
        stats["icon_index"]["exists"] = True
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        for file_info in manifest["files"]:
            file_path = icons_root / file_info["file"]
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                stats["icon_index"]["files"].append(
                    {
                        "name": file_info["file"],
                        "size_mb": round(size_mb, 2),
                        "icon_count": file_info["icon_count"],
                    }
                )
                stats["icon_index"]["total_size_mb"] += size_mb

        stats["icon_index"]["total_size_mb"] = round(
            stats["icon_index"]["total_size_mb"], 2
        )

    # Icon analysis stats
    analysis_manifest_path = icons_root / "icon_analysis_manifest.json"
    if analysis_manifest_path.exists():
        stats["icon_analysis"]["exists"] = True
        with open(analysis_manifest_path, "r") as f:
            manifest = json.load(f)

        for file_info in manifest["files"]:
            file_path = icons_root / file_info["file"]
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                stats["icon_analysis"]["files"].append(
                    {
                        "name": file_info["file"],
                        "size_mb": round(size_mb, 2),
                        "analysis_count": file_info["analysis_count"],
                    }
                )
                stats["icon_analysis"]["total_size_mb"] += size_mb

        stats["icon_analysis"]["total_size_mb"] = round(
            stats["icon_analysis"]["total_size_mb"], 2
        )

    # Lookup file stats
    lookup_path = icons_root / "icon_lookup.json"
    if lookup_path.exists():
        stats["lookup"]["exists"] = True
        size_mb = lookup_path.stat().st_size / (1024 * 1024)
        stats["lookup"]["size_mb"] = round(size_mb, 2)

    return stats


def merge_split_files(
    icons_root: Path, output_dir: Optional[Path] = None
) -> Tuple[Path, Path]:
    """
    Merge split files back into single files.

    Args:
        icons_root: Directory containing split files
        output_dir: Directory to save merged files (default: icons_root)

    Returns:
        Tuple of (merged_index_path, merged_analysis_path)
    """
    if output_dir is None:
        output_dir = icons_root

    # Merge icon index
    print("Merging icon index files...")
    icon_data = load_split_icon_index(icons_root)
    merged_index_path = output_dir / "icon_index_merged.json"

    with open(merged_index_path, "w") as f:
        json.dump(icon_data, f, indent=2)

    print(f"  ✓ Icon index merged: {merged_index_path}")

    # Merge icon analysis
    print("Merging icon analysis files...")
    analysis_data = load_split_icon_analysis(icons_root)
    merged_analysis_path = output_dir / "icon_analysis_merged.json"

    with open(merged_analysis_path, "w") as f:
        json.dump(analysis_data, f, indent=2)

    print(f"  ✓ Icon analysis merged: {merged_analysis_path}")

    return merged_index_path, merged_analysis_path


def search_icons(
    icons_root: Path,
    category: Optional[str] = None,
    atlas_range: Optional[Tuple[int, int]] = None,
    is_empty: Optional[bool] = None,
    limit: int = 100,
) -> List[Dict]:
    """
    Search for icons matching criteria.

    Args:
        icons_root: Directory containing split files
        category: Filter by category (e.g., 'item', 'spell')
        atlas_range: Filter by atlas number range (min, max)
        is_empty: Filter by empty status
        limit: Maximum number of results to return

    Returns:
        List of matching icon data
    """
    # Load lookup for quick filtering
    lookup_path = icons_root / "icon_lookup.json"
    lookup = {}

    if lookup_path.exists():
        with open(lookup_path, "r") as f:
            lookup = json.load(f)

    results = []

    for key, info in lookup.items():
        # Apply filters
        if category and info["category"] != category:
            continue

        if atlas_range:
            atlas_num = int(info["atlas_number"])
            if atlas_num < atlas_range[0] or atlas_num > atlas_range[1]:
                continue

        # Load full icon data if we need to check is_empty
        if is_empty is not None:
            icon_data = find_icon(
                icons_root, info["category"], info["atlas_number"], info["icon_index"]
            )
            if icon_data and icon_data.get("is_empty") != is_empty:
                continue

        results.append({"key": key, **info})

        if len(results) >= limit:
            break

    return results


def main():
    """Demo utility functions."""
    import sys

    project_root = Path(__file__).parent.parent.parent
    icons_root = project_root / "ExtractedAssets" / "UI" / "icons_extracted"

    if not icons_root.exists():
        print(f"❌ Icons directory not found: {icons_root}")
        sys.exit(1)

    print("=" * 80)
    print("ICON SPLIT FILES UTILITIES")
    print("=" * 80)
    print(f"Icons directory: {icons_root}")
    print()

    # Show file statistics
    print("FILE STATISTICS")
    print("-" * 40)
    stats = get_split_file_stats(icons_root)

    if stats["icon_index"]["exists"]:
        print("Icon Index:")
        print(f"  Files: {len(stats['icon_index']['files'])}")
        print(f"  Total size: {stats['icon_index']['total_size_mb']} MB")
        for file in stats["icon_index"]["files"][:3]:  # Show first 3
            print(
                f"    - {file['name']}: {file['size_mb']} MB ({file['icon_count']} icons)"
            )

    if stats["icon_analysis"]["exists"]:
        print("\nIcon Analysis:")
        print(f"  Files: {len(stats['icon_analysis']['files'])}")
        print(f"  Total size: {stats['icon_analysis']['total_size_mb']} MB")
        for file in stats["icon_analysis"]["files"][:3]:  # Show first 3
            print(
                f"    - {file['name']}: {file['size_mb']} MB ({file['analysis_count']} analyses)"
            )

    if stats["lookup"]["exists"]:
        print("\nLookup File:")
        print(f"  Size: {stats['lookup']['size_mb']} MB")

    print()

    # Demo search
    print("DEMO SEARCH")
    print("-" * 40)

    try:
        # Search for item icons
        results = search_icons(icons_root, category="itm", limit=5)
        print(f"Found {len(results)} item icons (showing first 5):")
        for result in results:
            print(
                f"  - {result['key']}: {result['category']}/atlas_{result['atlas_number']}/icon_{result['icon_index']:03d}"
            )
    except Exception as e:
        print(f"Search failed: {e}")

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
