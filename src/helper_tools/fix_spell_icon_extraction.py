#!/usr/bin/env python3
"""
Fix spell icon extraction with correct size and offset.

Findings:
- Spell atlases use 64x64 icons (not 32x32)
- Icons have a 2-pixel offset
- 4x4 grid = 16 slots total
- Only 9 slots are actually filled (positions 1,2,3,5,6,7,9,10,11)
"""

from PIL import Image
import numpy as np
from pathlib import Path
import json
import shutil

def extract_spell_icons_corrected(
    atlas_png: Path,
    output_dir: Path,
    icon_size: int = 64,
    offset_x: int = 2,
    offset_y: int = 2
) -> list[Path]:
    """
    Extract spell icons with correct size and offset.
    
    Args:
        atlas_png: Path to atlas PNG file
        output_dir: Directory to save extracted icons
        icon_size: Size of each icon (64 for spells)
        offset_x: X offset in pixels
        offset_y: Y offset in pixels
        
    Returns:
        List of paths to extracted icon files
    """
    try:
        atlas = Image.open(atlas_png).convert('RGBA')
        
        if atlas.size[0] != 256 or atlas.size[1] != 256:
            print(f"  ⚠ Unexpected atlas size: {atlas.size}")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        extracted = []
        
        grid_size = 4  # 4x4 grid for 64x64 icons
        
        for row in range(grid_size):
            for col in range(grid_size):
                # Calculate position with offset
                x = offset_x + (col * icon_size)
                y = offset_y + (row * icon_size)
                
                # Check bounds
                if x + icon_size > atlas.size[0] or y + icon_size > atlas.size[1]:
                    print(f"  ⚠ Icon at ({row},{col}) exceeds bounds, skipping")
                    continue
                
                # Extract icon
                icon = atlas.crop((x, y, x + icon_size, y + icon_size))
                
                # Calculate index (1-based)
                index = row * grid_size + col + 1
                
                # Save icon
                icon_path = output_dir / f"icon_{index:03d}.png"
                icon.save(icon_path)
                extracted.append(icon_path)
        
        return extracted
        
    except Exception as e:
        print(f"  ⚠ Error extracting from {atlas_png}: {e}")
        return []

def main():
    """Re-extract all spell icons with correct settings."""
    
    project_root = Path(__file__).parent.parent.parent
    icons_root = project_root / "ExtractedAssets" / "UI" / "icons_extracted"
    output_root = project_root / "ExtractedAssets" / "UI" / "icons_extracted_fixed"
    
    print("=" * 80)
    print("FIXING SPELL ICON EXTRACTION")
    print("=" * 80)
    print(f"Source: {icons_root / 'spell'}")
    print(f"Output: {output_root / 'spell'}")
    print()
    print("Settings:")
    print("  Icon size: 64×64 pixels")
    print("  Offset: (2, 2)")
    print("  Grid: 4×4 = 16 slots")
    print()
    
    # Find all spell atlases
    spell_atlases = sorted((icons_root / "spell").glob("atlas_*/_atlas_*.png"))
    
    if not spell_atlases:
        print("No spell atlases found!")
        return
    
    print(f"Found {len(spell_atlases)} spell atlases to process")
    print()
    
    stats = {
        'atlases_processed': 0,
        'icons_extracted': 0,
        'spell': {}
    }
    
    for atlas_path in spell_atlases:
        atlas_num = atlas_path.parent.name.replace('atlas_', '')
        
        print(f"Processing spell atlas {atlas_num}...", end=" ", flush=True)
        
        output_dir = output_root / "spell" / f"atlas_{atlas_num}"
        
        # Extract with correct settings
        extracted = extract_spell_icons_corrected(
            atlas_path,
            output_dir,
            icon_size=64,
            offset_x=2,
            offset_y=2
        )
        
        if extracted:
            print(f"✓ ({len(extracted)} icons)")
            stats['atlases_processed'] += 1
            stats['icons_extracted'] += len(extracted)
            
            # Copy the original atlas too
            shutil.copy(atlas_path, output_dir / atlas_path.name)
        else:
            print("✗")
    
    print()
    print("=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"Atlases processed: {stats['atlases_processed']}")
    print(f"Icons extracted:   {stats['icons_extracted']}")
    print()
    
    # Analyze content
    print("Analyzing extracted icons...")
    
    for atlas_num in range(18):  # 18 spell atlases
        atlas_dir = output_root / "spell" / f"atlas_{atlas_num}"
        if not atlas_dir.exists():
            continue
        
        non_empty = []
        for i in range(1, 17):  # 16 slots
            icon_path = atlas_dir / f"icon_{i:03d}.png"
            if icon_path.exists():
                icon = Image.open(icon_path)
                pixels = np.array(icon)
                if icon.mode == 'RGBA':
                    alpha = pixels[:,:,3]
                    if np.mean(alpha) > 10:  # Has significant content
                        non_empty.append(i)
        
        if non_empty:
            print(f"  Atlas {atlas_num}: {len(non_empty)} filled - slots {non_empty}")
    
    print()
    print("Next steps:")
    print("  1. Verify output looks correct:")
    print(f"     open {output_root / 'spell' / 'atlas_0'}")
    print("  2. If correct, replace old extraction:")
    print(f"     rm -rf {icons_root / 'spell'}")
    print(f"     mv {output_root / 'spell'} {icons_root / 'spell'}")
    print("  3. Re-run icon analysis:")
    print("     uv run src/helper_tools/filter_empty_icons.py")
    print("=" * 80)

if __name__ == '__main__':
    main()
