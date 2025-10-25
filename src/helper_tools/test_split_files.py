#!/usr/bin/env python3
"""
Test script for the split icon file system.

This script tests:
1. Creating mock split files
2. Loading split files
3. Finding icons
4. Searching functionality
5. Merging files
"""

import json

# Add the helper_tools directory to the path
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from icon_split_utils import (
    find_icon,
    get_split_file_stats,
    load_split_icon_analysis,
    load_split_icon_index,
    merge_split_files,
    search_icons,
)


def create_mock_split_files(test_dir: Path):
    """Create mock split files for testing."""
    print("Creating mock split files...")

    icons_dir = test_dir / "icons_extracted"
    icons_dir.mkdir(parents=True, exist_ok=True)

    # Create mock icon index manifest
    manifest = {
        "total_icons": 100,
        "num_files": 5,
        "icons_per_file": 20,
        "stats": {
            "atlases_found": 5,
            "atlases_converted": 5,
            "icons_extracted": 100,
            "categories": {"itm": 5},
        },
        "files": [],
    }

    # Create mock part files
    all_icons = {}
    for i in range(5):
        start_idx = i * 20
        end_idx = start_idx + 19

        part_icons = {}
        for j in range(20):
            icon_idx = start_idx + j
            key = f"itm_{i}_{icon_idx:03d}"
            part_icons[key] = {
                "category": "itm",
                "atlas_number": str(i),
                "icon_index": icon_idx,
                "path": f"itm/atlas_{i}/icon_{icon_idx:03d}.png",
                "is_empty": icon_idx % 10 == 0,  # Every 10th icon is empty
            }
            all_icons[key] = part_icons[key]

        part_data = {
            "file_index": i,
            "start_index": start_idx,
            "end_index": end_idx,
            "icon_count": 20,
            "icons": part_icons,
        }

        part_file = icons_dir / f"icon_index_part_{i:02d}.json"
        with open(part_file, "w") as f:
            json.dump(part_data, f, indent=2)

        manifest["files"].append(
            {
                "file": f"icon_index_part_{i:02d}.json",
                "start_index": start_idx,
                "end_index": end_idx,
                "icon_count": 20,
            }
        )

    # Save manifest
    with open(icons_dir / "icon_index_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    # Create lookup file
    lookup = {}
    for key, icon_data in all_icons.items():
        lookup[key] = {
            "file": f"icon_index_part_{int(icon_data['atlas_number']):02d}.json",
            "category": icon_data["category"],
            "atlas_number": icon_data["atlas_number"],
            "icon_index": icon_data["icon_index"],
        }

    with open(icons_dir / "icon_lookup.json", "w") as f:
        json.dump(lookup, f, indent=2)

    # Create mock analysis manifest
    analysis_manifest = {
        "total_analyses": 100,
        "num_files": 5,
        "analyses_per_file": 20,
        "summary": {
            "total_icons": 100,
            "empty_count": 10,
            "duplicate_groups": 0,
            "total_duplicates": 0,
            "empty_by_reason": {"fully_transparent": 10},
        },
        "files": [],
    }

    # Create mock analysis part files
    for i in range(5):
        start_idx = i * 20
        end_idx = start_idx + 19

        part_analyses = []
        for j in range(20):
            icon_idx = start_idx + j
            key = f"itm_{i}_{icon_idx:03d}"
            analysis = {
                "key": key,
                "category": "itm",
                "atlas_number": str(i),
                "icon_index": icon_idx,
                "path": f"itm/atlas_{i}/icon_{icon_idx:03d}.png",
                "is_empty": icon_idx % 10 == 0,
                "reasons": ["fully_transparent"] if icon_idx % 10 == 0 else [],
                "metrics": {"alpha_mean": 0.0 if icon_idx % 10 == 0 else 128.0},
            }
            part_analyses.append(analysis)

        part_data = {
            "file_index": i,
            "start_index": start_idx,
            "end_index": end_idx,
            "analysis_count": 20,
            "analyses": part_analyses,
        }

        part_file = icons_dir / f"icon_analysis_part_{i:02d}.json"
        with open(part_file, "w") as f:
            json.dump(part_data, f, indent=2)

        analysis_manifest["files"].append(
            {
                "file": f"icon_analysis_part_{i:02d}.json",
                "start_index": start_idx,
                "end_index": end_idx,
                "analysis_count": 20,
            }
        )

    # Save analysis manifest
    with open(icons_dir / "icon_analysis_manifest.json", "w") as f:
        json.dump(analysis_manifest, f, indent=2)

    print(f"✓ Created mock split files in {icons_dir}")
    return icons_dir


def test_load_split_files(icons_dir: Path):
    """Test loading split files."""
    print("\n" + "=" * 60)
    print("TEST: Loading Split Files")
    print("=" * 60)

    try:
        # Test loading icon index
        print("Loading icon index...")
        icon_data = load_split_icon_index(icons_dir)
        assert len(icon_data["icons"]) == 100, (
            f"Expected 100 icons, got {len(icon_data['icons'])}"
        )
        print(f"✓ Loaded {len(icon_data['icons'])} icons")

        # Test loading analysis
        print("\nLoading icon analysis...")
        analysis_data = load_split_icon_analysis(icons_dir)
        assert len(analysis_data["analyses"]) == 100, (
            f"Expected 100 analyses, got {len(analysis_data['analyses'])}"
        )
        print(f"✓ Loaded {len(analysis_data['analyses'])} analyses")

        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_find_icon(icons_dir: Path):
    """Test finding specific icons."""
    print("\n" + "=" * 60)
    print("TEST: Finding Icons")
    print("=" * 60)

    test_cases = [
        ("itm", "0", 1, True),
        ("itm", "0", 10, True),  # Empty icon
        ("itm", "2", 50, True),
        ("itm", "4", 99, True),
        ("itm", "10", 1, False),  # Doesn't exist
    ]

    all_passed = True
    for category, atlas_num, icon_idx, should_exist in test_cases:
        print(f"Finding {category}_atlas_{atlas_num}_icon_{icon_idx:03d}...", end=" ")

        icon = find_icon(icons_dir, category, atlas_num, icon_idx)

        if should_exist:
            if icon:
                print("✓ Found")
                assert icon["category"] == category
                assert icon["atlas_number"] == atlas_num
                assert icon["icon_index"] == icon_idx
            else:
                print("❌ Not found (should exist)")
                all_passed = False
        else:
            if icon is None:
                print("✓ Not found (correct)")
            else:
                print("❌ Found (should not exist)")
                all_passed = False

    return all_passed


def test_search_icons(icons_dir: Path):
    """Test searching for icons."""
    print("\n" + "=" * 60)
    print("TEST: Searching Icons")
    print("=" * 60)

    try:
        # Test category search
        print("Searching for 'itm' category (limit 5)...")
        results = search_icons(icons_dir, category="itm", limit=5)
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"
        print(f"✓ Found {len(results)} results")

        # Test empty icon search
        print("\nSearching for empty icons...")
        results = search_icons(icons_dir, is_empty=True, limit=20)
        assert len(results) == 10, f"Expected 10 empty icons, got {len(results)}"
        print(f"✓ Found {len(results)} empty icons")

        # Test non-empty icon search
        print("\nSearching for non-empty icons...")
        results = search_icons(icons_dir, is_empty=False, limit=20)
        assert len(results) == 20, f"Expected 20 non-empty icons, got {len(results)}"
        print(f"✓ Found {len(results)} non-empty icons")

        # Test atlas range search
        print("\nSearching icons in atlas range 1-2...")
        results = search_icons(icons_dir, atlas_range=(1, 2), limit=50)
        assert len(results) == 40, (
            f"Expected 40 icons in atlases 1-2, got {len(results)}"
        )
        print(f"✓ Found {len(results)} icons in range")

        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_file_stats(icons_dir: Path):
    """Test getting file statistics."""
    print("\n" + "=" * 60)
    print("TEST: File Statistics")
    print("=" * 60)

    try:
        stats = get_split_file_stats(icons_dir)

        # Check icon index stats
        assert stats["icon_index"]["exists"], "Icon index should exist"
        assert len(stats["icon_index"]["files"]) == 5, "Should have 5 index files"
        assert stats["icon_index"]["total_size_mb"] > 0, "Should have non-zero size"
        print(
            f"✓ Icon index: {len(stats['icon_index']['files'])} files, {stats['icon_index']['total_size_mb']:.2f} MB"
        )

        # Check analysis stats
        assert stats["icon_analysis"]["exists"], "Icon analysis should exist"
        assert len(stats["icon_analysis"]["files"]) == 5, "Should have 5 analysis files"
        assert stats["icon_analysis"]["total_size_mb"] > 0, "Should have non-zero size"
        print(
            f"✓ Icon analysis: {len(stats['icon_analysis']['files'])} files, {stats['icon_analysis']['total_size_mb']:.2f} MB"
        )

        # Check lookup stats
        assert stats["lookup"]["exists"], "Lookup file should exist"
        assert stats["lookup"]["size_mb"] > 0, "Should have non-zero size"
        print(f"✓ Lookup file: {stats['lookup']['size_mb']:.2f} MB")

        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_merge_files(icons_dir: Path):
    """Test merging split files."""
    print("\n" + "=" * 60)
    print("TEST: Merging Split Files")
    print("=" * 60)

    try:
        merged_index, merged_analysis = merge_split_files(icons_dir)

        # Check merged files exist
        assert merged_index.exists(), "Merged index should exist"
        assert merged_analysis.exists(), "Merged analysis should exist"
        print("✓ Created merged files")

        # Load and verify merged index
        with open(merged_index, "r") as f:
            merged_data = json.load(f)
        assert len(merged_data["icons"]) == 100, "Expected 100 icons in merged file"
        print(f"✓ Merged index contains {len(merged_data['icons'])} icons")

        # Load and verify merged analysis
        with open(merged_analysis, "r") as f:
            merged_analysis_data = json.load(f)
        assert len(merged_analysis_data["analyses"]) == 100, (
            "Expected 100 analyses in merged file"
        )
        print(
            f"✓ Merged analysis contains {len(merged_analysis_data['analyses'])} analyses"
        )

        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("SPLIT FILE SYSTEM TESTS")
    print("=" * 80)

    # Create temporary test directory
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        print(f"Using test directory: {test_dir}")

        # Create mock files
        icons_dir = create_mock_split_files(test_dir)

        # Run tests
        tests = [
            ("Load Split Files", test_load_split_files),
            ("Find Icons", test_find_icon),
            ("Search Icons", test_search_icons),
            ("File Statistics", test_file_stats),
            ("Merge Files", test_merge_files),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                result = test_func(icons_dir)
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))

        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✓ PASS" if result else "❌ FAIL"
            print(f"{status:8s} {test_name}")

        print(f"\nOverall: {passed}/{total} tests passed")

        if passed == total:
            print("\n🎉 All tests passed!")
            return 0
        else:
            print(f"\n⚠ {total - passed} test(s) failed")
            return 1


if __name__ == "__main__":
    sys.exit(main())
