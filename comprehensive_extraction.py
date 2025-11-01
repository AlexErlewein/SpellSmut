#!/usr/bin/env python3
"""
Comprehensive weapon extraction tool for ITM atlases.

This handles both:
1. The existing approach: individual 16x16 icons + horizontal weapon combinations (1x2, 1x4, etc.)
2. The vertical approach: 4 vertical strips spanning full Y-axis (256x64 each)
"""

import sys
from pathlib import Path
from PIL import Image

def extract_individual_and_horizontal_weapons(atlas_path, output_dir):
    """
    Extract individual 16x16 icons and detect horizontal weapon combinations.
    This replicates the original extraction logic.
    """
    # This follows the same pattern as the existing extract_itm_icons.py
    atlas = Image.open(atlas_path)
    width, height = atlas.size
    
    if width != 256 or height != 256:
        print(f"Expected 256x256 atlas, got {width}x{height}")
        return []
    
    grid_size = 16
    icon_size = 16
    extracted = []
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for row in range(grid_size):
        for col in range(grid_size):
            # Calculate position in atlas
            x = col * icon_size
            y = row * icon_size
            
            # Extract icon
            icon = atlas.crop((x, y, x + icon_size, y + icon_size))
            
            # Calculate index (1-based to match game's item_ui_index)
            index = row * grid_size + col + 1
            
            # Save icon
            icon_path = output_dir / f"icon_{index:03d}.png"
            icon.save(icon_path)
            extracted.append(icon_path)
    
    return extracted

def extract_vertical_weapons(atlas_path, output_dir, num_weapons=4):
    """
    Extract wide weapons from an atlas where each weapon spans the full Y-axis
    but is equally divided on the X-axis.
    """
    atlas = Image.open(atlas_path)
    width, height = atlas.size
    
    if width != 256 or height != 256:
        print(f"Expected 256x256 atlas, got {width}x{height}")
        return []
    
    # Calculate width of each weapon
    weapon_width = width // num_weapons
    
    output_dir.mkdir(parents=True, exist_ok=True)
    extracted = []
    
    print(f"Extracting {num_weapons} vertical weapons of size {weapon_width}x{height}px each")
    
    for i in range(num_weapons):
        # Calculate crop boundaries
        left = i * weapon_width
        top = 0
        right = (i + 1) * weapon_width
        bottom = height
        
        # Extract weapon
        weapon = atlas.crop((left, top, right, bottom))
        
        # Save weapon
        weapon_path = output_dir / f"vertical_weapon_{i+1:02d}_{weapon_width}x{height}.png"
        weapon.save(weapon_path)
        extracted.append(weapon_path)
        
        print(f"  Extracted vertical weapon {i+1}: {weapon_path.name} ({weapon_width}x{height}px)")
    
    return extracted

def process_atlas_comprehensive(original_atlas_path, base_output_dir, atlas_num, num_weapons=4):
    """
    Process a single atlas comprehensively: both existing and vertical extraction.
    """
    print(f"\nProcessing atlas {atlas_num} comprehensively...")
    
    # Create individual icons and horizontal combinations (existing approach)
    individual_output = base_output_dir / f"atlas_{atlas_num}" / "individual_and_horizontal"
    print(f"  Extracting individual icons and horizontal weapons to {individual_output}")
    extracted_individual = extract_individual_and_horizontal_weapons(original_atlas_path, individual_output)
    
    # Create vertical weapons (your requested approach)
    vertical_output = base_output_dir / f"atlas_{atlas_num}" / "vertical_weapons"
    print(f"  Extracting vertical weapons to {vertical_output}")
    extracted_vertical = extract_vertical_weapons(original_atlas_path, vertical_output, num_weapons)
    
    print(f"  Total extracted - Individual/Horizontal: {len(extracted_individual)}, Vertical: {len(extracted_vertical)}")

def main():
    """Main function to process ITM atlas files comprehensively."""
    project_root = Path(__file__).parent
    original_base_dir = project_root / "ExtractedAssets" / "UI" / "itm_icons_extracted"
    new_output_base = project_root / "ExtractedAssets" / "UI" / "comprehensive_extraction"
    
    print("=" * 70)
    print("COMPREHENSIVE WEAPON EXTRACTION TOOL")
    print("=" * 70)
    print(f"Processing original atlases from: {original_base_dir}")
    print(f"Output comprehensive extraction to: {new_output_base}")
    print("This tool extracts:")
    print("1. Individual 16x16 icons + horizontal weapon combinations (1x2, 1x4, etc.)")
    print("2. 4 vertical strips spanning full Y-axis (256x64 each)")
    print()
    
    # Process only a specific atlas for testing (atlas_1 as mentioned in your example)
    specific_atlas_num = 1
    atlas_dir = original_base_dir / f"atlas_{specific_atlas_num}"
    atlas_file = atlas_dir / f"_atlas_{specific_atlas_num}.png"
    
    if not atlas_file.exists():
        print(f"Atlas file not found: {atlas_file}")
        return
    
    print(f"Processing specific atlas {specific_atlas_num}...")
    process_atlas_comprehensive(atlas_file, new_output_base, specific_atlas_num, num_weapons=4)
    
    # Show summary for this specific atlas
    print(f"\nSUMMARY for atlas_{specific_atlas_num}:")
    individual_dir = new_output_base / f"atlas_{specific_atlas_num}" / "individual_and_horizontal"
    vertical_dir = new_output_base / f"atlas_{specific_atlas_num}" / "vertical_weapons"
    
    if individual_dir.exists():
        individual_count = len(list(individual_dir.glob("*.png")))
        print(f"  Individual/Horizontal: {individual_count} files in {individual_dir}")
    
    if vertical_dir.exists():
        vertical_count = len(list(vertical_dir.glob("*.png")))
        print(f"  Vertical: {vertical_count} files in {vertical_dir}")
    
    print(f"\nAll comprehensive extractions saved to: {new_output_base}")

if __name__ == "__main__":
    main()