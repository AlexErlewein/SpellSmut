#!/usr/bin/env python3
"""
Extract wide weapons from ITM atlases where each weapon spans the whole Y-axis
but is equally divided on the X-axis.

This handles cases where an atlas contains N wide weapons, each spanning the 
full height but occupying 256/N pixels in width.
"""

import sys
from pathlib import Path
from PIL import Image

def extract_wide_weapons_from_atlas(atlas_path, output_dir, num_weapons=4):
    """
    Extract wide weapons from an atlas where each weapon spans the full Y-axis
    but is equally divided on the X-axis.
    
    Args:
        atlas_path: Path to the 256x256 atlas PNG
        output_dir: Directory to save extracted weapon images
        num_weapons: Number of weapons in the atlas (default 4)
    """
    # Validate atlas size
    atlas = Image.open(atlas_path)
    width, height = atlas.size
    
    if width != 256 or height != 256:
        print(f"Expected 256x256 atlas, got {width}x{height}")
        return []
    
    # Calculate width of each weapon
    weapon_width = width // num_weapons
    
    output_dir.mkdir(parents=True, exist_ok=True)
    extracted = []
    
    print(f"Extracting {num_weapons} wide weapons of size {weapon_width}x{height}px each")
    
    for i in range(num_weapons):
        # Calculate crop boundaries
        left = i * weapon_width
        top = 0
        right = (i + 1) * weapon_width
        bottom = height
        
        # Extract weapon
        weapon = atlas.crop((left, top, right, bottom))
        
        # Save weapon
        weapon_path = output_dir / f"weapon_{i+1:02d}.png"
        weapon.save(weapon_path)
        extracted.append(weapon_path)
        
        print(f"  Extracted weapon {i+1}: {weapon_path.name} ({weapon_width}x{height}px)")
    
    return extracted

def process_all_atlases(base_dir, num_weapons=4):
    """
    Process all atlas files to extract wide weapons.
    
    Args:
        base_dir: Base directory containing atlas subdirectories
        num_weapons: Number of weapons per atlas
    """
    base_path = Path(base_dir)
    atlas_dirs = list(base_path.glob("atlas_*"))
    
    print(f"Found {len(atlas_dirs)} atlas directories")
    
    for atlas_dir in atlas_dirs:
        atlas_num = atlas_dir.name.replace("atlas_", "")
        print(f"\nProcessing atlas {atlas_num}...")
        
        # Find the original atlas file
        atlas_files = list(atlas_dir.glob("_atlas_*.png"))
        if not atlas_files:
            print(f"  No original atlas files found in {atlas_dir}")
            continue
            
        original_atlas = atlas_files[0]
        print(f"  Found original atlas: {original_atlas.name}")
        
        # Create output directory for wide weapons
        output_dir = atlas_dir / "wide_weapons"
        
        # Extract wide weapons
        extracted = extract_wide_weapons_from_atlas(original_atlas, output_dir, num_weapons)
        
        print(f"  Extracted {len(extracted)} wide weapons to {output_dir}")
    
    print(f"\nCompleted processing all atlases")

def main():
    """Main function to process ITM atlas files."""
    project_root = Path(__file__).parent
    base_dir = project_root / "ExtractedAssets" / "UI" / "itm_icons_extracted"
    
    print("=" * 70)
    print("WIDE WEAPON EXTRACTION TOOL")
    print("=" * 70)
    print(f"Processing atlases from: {base_dir}")
    print("This tool extracts weapons that span the full Y-axis")
    print("but are equally divided along the X-axis")
    print()
    
    # Process all atlases with 4 weapons per atlas
    process_all_atlases(base_dir, num_weapons=4)

if __name__ == "__main__":
    main()