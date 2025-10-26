#!/usr/bin/env python3
"""
Extract SpellForce spell icons from DDS files.

This script extracts spell icons from the raw spell DDS files with correct
parameters: 4x4 grid of 64x64 icons with 2-pixel offsets, following the
same approach as fix_spell_icon_extraction.py but applied to raw DDS files.
"""

from PIL import Image
import numpy as np
from pathlib import Path
import subprocess
import shutil
import os


def convert_dds_to_png(dds_path: Path, png_path: Path) -> bool:
    """
    Convert DDS file to PNG using ImageMagick.
    """
    try:
        result = subprocess.run([
            'magick', 'convert', str(dds_path), str(png_path)
        ], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        print("ImageMagick not found. Please install ImageMagick.")
        return False
    except Exception as e:
        print(f"Error converting {dds_path} to PNG: {e}")
        return False


def extract_spell_icons_from_png(
    png_path: Path,
    output_dir: Path,
    icon_size: int = 64,
    offset_x: int = 2,
    offset_y: int = 2
) -> list[Path]:
    """
    Extract spell icons from a PNG atlas with correct size and offset.
    
    Args:
        png_path: Path to PNG atlas file
        output_dir: Directory to save extracted icons
        icon_size: Size of each icon (64 for spells)
        offset_x: X offset in pixels
        offset_y: Y offset in pixels
        
    Returns:
        List of paths to extracted icon files
    """
    try:
        atlas = Image.open(png_path).convert('RGBA')
        
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
                
                # Apply 180-degree rotation to correct for SpellForce's inverted Y-axis
                icon = icon.rotate(180, expand=False)
                
                # Calculate index (1-based)
                index = row * grid_size + col + 1
                
                # Save icon
                icon_path = output_dir / f"icon_{index:03d}.png"
                icon.save(icon_path)
                extracted.append(icon_path)
        
        return extracted
        
    except Exception as e:
        print(f"  ⚠ Error extracting from {png_path}: {e}")
        return []


def main():
    """
    Main function to extract spell icons from raw re-extraction files.
    """
    project_root = Path(__file__).parent.parent.parent
    raw_spell_dir = project_root / "ExtractedAssets" / "UI" / "raw_reextraction"
    output_root = project_root / "ExtractedAssets" / "UI" / "icons_extracted"
    
    print("SpellForce Spell Icon Extraction")
    print("=" * 50)
    print(f"Source: {raw_spell_dir}")
    print(f"Output: {output_root}")
    print()
    print("Settings:")
    print("  Icon size: 64×64 pixels")
    print("  Offset: (2, 2)")
    print("  Grid: 4×4 = 16 slots")
    print()
    
    # Find all spell DDS files
    spell_dds_files = []
    for sf_dir in raw_spell_dir.glob("sf*"):
        if sf_dir.is_dir():
            spell_dds_files.extend(sf_dir.glob("texture/ui_spell*.dds"))
    
    if not spell_dds_files:
        print("No spell DDS files found!")
        print(f"Looked in: {raw_spell_dir}/sf*/texture/ui_spell*.dds")
        return
    
    print(f"Found {len(spell_dds_files)} spell DDS files to process")
    print()
    
    # Process each DDS file
    stats = {
        'files_processed': 0,
        'icons_extracted': 0,
        'conversion_errors': 0
    }
    
    # Create temp directory for intermediate PNG files
    temp_dir = project_root / "temp_spell_processing"
    temp_dir.mkdir(exist_ok=True)
    
    for dds_file in sorted(spell_dds_files):
        print(f"Processing {dds_file.name}...", end=" ", flush=True)
        
        # Extract just the number from filename to create atlas directory
        import re
        match = re.search(r'ui_spell(\d+)\.dds', dds_file.name)
        atlas_num = 0
        if match:
            atlas_num = int(match.group(1))
        
        # Convert DDS to PNG
        temp_png = temp_dir / f"{dds_file.name.replace('.dds', '.png')}"
        conversion_success = convert_dds_to_png(dds_file, temp_png)
        
        if not conversion_success:
            print("✗ (conversion failed)")
            stats['conversion_errors'] += 1
            continue
        
        # Extract icons from PNG
        output_dir = output_root / "spell" / f"atlas_{atlas_num}"
        extracted_icons = extract_spell_icons_from_png(
            temp_png,
            output_dir,
            icon_size=64,
            offset_x=2,
            offset_y=2
        )
        
        if extracted_icons:
            print(f"✓ ({len(extracted_icons)} icons)")
            stats['files_processed'] += 1
            stats['icons_extracted'] += len(extracted_icons)
            
            # Save the original atlas too, with 180-degree rotation for consistency
            atlas_output = output_dir / f"_atlas_{atlas_num}.png"
            # Rotate the atlas image by 180 degrees to match SpellForce's inverted Y-axis
            atlas_img = Image.open(temp_png).convert('RGBA')
            rotated_atlas = atlas_img.rotate(180, expand=False)
            rotated_atlas.save(atlas_output)
        else:
            print("✗ (no icons extracted)")
    
    # Clean up temp directory
    shutil.rmtree(temp_dir)
    
    print()
    print("=" * 50)
    print("EXTRACTION COMPLETE")
    print("=" * 50)
    print(f"Files processed: {stats['files_processed']}")
    print(f"Icons extracted: {stats['icons_extracted']}")
    print(f"Conversion errors: {stats['conversion_errors']}")
    print()
    
    # Analyze content
    print("Analyzing extracted icons...")
    spell_dir = output_root / "spell"
    if spell_dir.exists():
        for atlas_dir in sorted(spell_dir.glob("atlas_*")):
            atlas_num = atlas_dir.name.replace('atlas_', '')
            non_empty = []
            for i in range(1, 17):  # 16 slots
                icon_path = atlas_dir / f"icon_{i:03d}.png"
                if icon_path.exists():
                    try:
                        icon = Image.open(icon_path)
                        pixels = np.array(icon)
                        if icon.mode == 'RGBA':
                            alpha = pixels[:,:,3]
                            if np.mean(alpha) > 10:  # Has significant content
                                non_empty.append(i)
                    except:
                        continue  # Skip if image is corrupted
            
            if non_empty:
                print(f"  Atlas {atlas_num}: {len(non_empty)} filled - slots {non_empty}")
    
    print()
    print("Spell icon extraction finished!")
    print(f"Icons saved to: {output_root / 'spell'}")


if __name__ == '__main__':
    main()