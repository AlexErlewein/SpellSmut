#!/usr/bin/env python3
"""
Direct test of enhanced map loader with texture assignment parsing
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.TirganachReloaded.map_viewer.simple_map_loader import SimpleMapLoader


def main():
    """Test the enhanced map loader"""
    print("🚀 Testing Enhanced Map Loader")
    print("=" * 40)

    # Test with a real map file
    test_map_path = (
        project_root / "OriginalGameFiles" / "map" / "campaign2" / "P108_Fastholme.map"
    )

    if not test_map_path.exists():
        print(f"❌ Test map not found: {test_map_path}")
        # Try alternative maps
        alternative_maps = [
            project_root
            / "OriginalGameFiles"
            / "map"
            / "campaign2"
            / "P111_Firefangs.map",
            project_root
            / "OriginalGameFiles"
            / "map"
            / "campaign2"
            / "P110_Shaldun.map",
        ]

        for alt_map in alternative_maps:
            if alt_map.exists():
                test_map_path = alt_map
                print(f"✅ Using alternative map: {test_map_path}")
                break
        else:
            print("❌ No test maps found!")
            return False

    print(f"📂 Loading test map: {test_map_path}")

    # Create map loader
    loader = SimpleMapLoader()

    # Load the map
    success = loader.load(test_map_path)

    if not success:
        print("❌ Failed to load map!")
        return False

    print("✅ Map loaded successfully!")

    # Check if we have heightmap data
    if loader.heightmap:
        print(f"🏔️  Heightmap: {loader.heightmap.width}x{loader.heightmap.height}")

        # Show some heightmap stats
        all_heights = [h for row in loader.heightmap.heights for h in row]
        if all_heights:
            min_h = min(all_heights)
            max_h = max(all_heights)
            avg_h = sum(all_heights) / len(all_heights)
            print(
                f"📊 Heightmap stats: min={min_h:.2f}, max={max_h:.2f}, avg={avg_h:.2f}"
            )
    else:
        print("❌ No heightmap data loaded!")
        return False

    # Check if we have terrain texture assignments
    if hasattr(loader, "terrain_textures") and loader.terrain_textures:
        print(f"🎨 Terrain textures: {len(loader.terrain_textures)} assignments")

        # Show some texture assignment stats
        if len(loader.terrain_textures) > 0:
            print("📋 Sample texture assignments:")
            for i, assignment in enumerate(loader.terrain_textures[:5]):
                print(
                    f"   {i + 1}. Position ({assignment.x}, {assignment.y}): Texture {assignment.texture_id}"
                )
                if hasattr(assignment, "blend_weights") and assignment.blend_weights:
                    print(f"      Blend weights: {assignment.blend_weights}")
    else:
        print("⚠️  No terrain texture assignments found (this is normal for some maps)")

    print("\n🎯 Enhanced Map Loader test completed successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
