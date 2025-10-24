#!/usr/bin/env python3
"""
Re-extract spell icons with correct size.

Analysis shows spell atlases might use 64x64 icons instead of 32x32.
This script re-extracts spell icons with the correct dimensions.
"""

from PIL import Image
from pathlib import Path
import json

def extract_icons_correct_size(atlas_path: Path, output_dir: Path, icon_size: int):
    """Extract icons from atlas with specified icon size."""
    
    atlas = Image.open(atlas_path).convert('RGBA')
    
    if atlas.size[0] != 256 or atlas.size[1] != 256:
        print(f"  Warning: Unexpected atlas size {atlas.size}")
        return 0
    
    grid_size = 256 // icon_size
    total_icons = grid_size * grid_size
    
    output_dir.mkdir(parents=True, exist_ok=True)
    extracted = 0
    
    for row in range(grid_size):
        for col in range(grid_size):
            x = col * icon_size
            y = row * icon_size
            
            icon = atlas.crop((x, y, x + icon_size, y + icon_size))
            index = row * grid_size + col + 1
            
            icon_path = output_dir / f"icon_{index:03d}.png"
            icon.save(icon_path)
            extracted += 1
    
    return extracted

def main():
    project_root = Path(__file__).parent.parent.parent
    icons_root = project_root / "ExtractedAssets" / "UI" / "icons_extracted"
    
    print("=" * 80)
    print("RE-EXTRACTING SPELL ICONS WITH CORRECT SIZE")
    print("=" * 80)
    print()
    
    # Test different icon sizes on spell atlas_0
    test_atlas = icons_root / "spell" / "atlas_0" / "_atlas_0.png"
    
    if not test_atlas.exists():
        print(f"Error: Atlas not found: {test_atlas}")
        return
    
    print(f"Testing icon sizes on: {test_atlas.name}")
    print()
    
    for icon_size in [32, 64]:
        print(f"Testing {icon_size}x{icon_size} icons...")
        
        test_output = icons_root / "spell" / f"test_size_{icon_size}"
        count = extract_icons_correct_size(test_atlas, test_output, icon_size)
        
        # Count non-empty icons
        import numpy as np
        non_empty = 0
        for i in range(1, count + 1):
            icon_path = test_output / f"icon_{i:03d}.png"
            if icon_path.exists():
                icon = Image.open(icon_path)
                pixels = np.array(icon)
                if icon.mode == 'RGBA':
                    alpha = pixels[:,:,3]
                    if np.max(alpha) > 10:
                        non_empty += 1
        
        print(f"  Grid: {256//icon_size}x{256//icon_size}")
        print(f"  Total icons: {count}")
        print(f"  Non-empty: {non_empty}")
        print()
    
    # Now let's check if all spell atlases should use 64x64
    print("Checking all spell atlases...")
    print()
    
    spell_atlases = sorted((icons_root / "spell").glob("atlas_*/_atlas_*.png"))
    
    for atlas_path in spell_atlases:
        atlas = Image.open(atlas_path)
        print(f"{atlas_path.parent.name}: {atlas.size}")
    
    print()
    print("Based on your observation (9 different pictures), please:")
    print("1. Check ExtractedAssets/UI/icons_extracted/spell/test_size_32/")
    print("2. Check ExtractedAssets/UI/icons_extracted/spell/test_size_64/")
    print("3. Let me know which size shows the correct number of distinct icons")
    print()
    print("Hypothesis:")
    print("  - 32x32 grid = 8x8 = 64 icons (too many, many empty/similar)")
    print("  - 64x64 grid = 4x4 = 16 icons (likely correct)")
    print("=" * 80)

if __name__ == '__main__':
    main()
