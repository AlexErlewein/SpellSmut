#!/usr/bin/env python3
"""
Analysis script for atlas_0 to understand how items are distributed in the vertical layout.
"""

import sys
from pathlib import Path
from PIL import Image

def analyze_atlas_0():
    """
    Analyze atlas_0 specifically to understand the vertical distribution
    of weapons, armor, and robes.
    """
    project_root = Path(__file__).parent
    atlas_path = project_root / "ExtractedAssets" / "UI" / "itm_icons_extracted" / "atlas_0" / "_atlas_0.png"
    
    print("Analyzing atlas_0:")
    print(f"Atlas path: {atlas_path}")
    
    if not atlas_path.exists():
        print("Atlas file does not exist!")
        return
    
    # Load the atlas
    atlas = Image.open(atlas_path)
    width, height = atlas.size
    print(f"Atlas dimensions: {width}x{height}")
    
    # Calculate the 4 vertical strips
    num_weapons = 4
    strip_width = width // num_weapons
    print(f"Number of vertical strips: {num_weapons}")
    print(f"Each strip: {strip_width}x{height} pixels")
    
    # Analyze each strip
    for i in range(num_weapons):
        left = i * strip_width
        right = (i + 1) * strip_width
        
        # Extract the strip
        strip = atlas.crop((left, 0, right, height))
        
        print(f"\nStrip {i+1} ({left}-{right}):")
        print(f"  Position: column {left} to {right-1}")
        print(f"  Size: {strip_width}x{height}")
        
        # Show some characteristics
        # Convert to avoid palette issues
        strip_rgb = strip.convert('RGB')
        
        # Check if the strip has content (not fully transparent or blank)
        pixels = list(strip_rgb.getdata())
        unique_colors = len(set(pixels))
        
        print(f"  Unique colors: {unique_colors}")
        
        # Check for non-transparent content by analyzing by row
        content_rows = []
        for y in range(height):
            row_pixels = []
            for x in range(strip_width):
                pixel = strip_rgb.getpixel((x, y))
                row_pixels.append(pixel)
            
            # Check if this row has significant content (not all the same color)
            if len(set(row_pixels)) > 1:  # More than one color in the row
                content_rows.append(y)
        
        if content_rows:
            content_start = min(content_rows)
            content_end = max(content_rows)
            print(f"  Content spans from row {content_start} to {content_end} ({content_end - content_start + 1} rows)")
        else:
            print(f"  No significant content detected")
    
    # Also check the original individual extraction
    print(f"\nChecking original individual extraction:")
    individual_dir = project_root / "ExtractedAssets" / "UI" / "itm_icons_extracted" / "atlas_0"
    individual_icons = list(individual_dir.glob("icon_*.png"))
    weapon_files = list(individual_dir.glob("weapon_*.png"))
    
    print(f"  Individual icons: {len(individual_icons)}")
    print(f"  Weapon combinations: {len(weapon_files)}")
    
    if weapon_files:
        print(f"  Weapon files:")
        for wf in weapon_files[:5]:  # Show first 5
            weapon_img = Image.open(wf)
            w, h = weapon_img.size
            print(f"    {wf.name}: {w}x{h} pixels")

def extract_detailed_vertical_analysis():
    """
    Extract detailed vertical analysis for atlas_0 with different partitioning
    if needed (e.g., for robes that might take 2/3 and armor 1/3).
    """
    project_root = Path(__file__).parent
    atlas_path = project_root / "ExtractedAssets" / "UI" / "itm_icons_extracted" / "atlas_0" / "_atlas_0.png"
    
    if not atlas_path.exists():
        return
    
    atlas = Image.open(atlas_path)
    width, height = atlas.size
    
    # Create detailed analysis directory
    output_dir = project_root / "ExtractedAssets" / "UI" / "detailed_analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Standard 4 vertical strips
    print(f"\nCreating detailed vertical analysis...")
    
    num_strips = 4
    strip_width = width // num_strips
    
    for i in range(num_strips):
        left = i * strip_width
        right = (i + 1) * strip_width
        
        # Extract the strip
        strip = atlas.crop((left, 0, right, height))
        
        # Save the strip
        strip_path = output_dir / f"atlas_0_vertical_strip_{i+1:02d}.png"
        strip.save(strip_path)
        
        print(f"  Saved vertical strip {i+1}: {strip_path} ({strip_width}x{height})")
    
    # Also try alternative layout: 2/3 and 1/3 vertical splits for robe/armor
    print(f"\nTrying 2/3 and 1/3 vertical splits...")
    # This would be if specific content takes vertical space differently
    # For example: if we know that robes take 2/3 of height (170 pixels) and armor 1/3 (86 pixels)
    
    # Create alternative partitioning just for demonstration
    # Actually, this doesn't make sense for the 4 vertical strips approach
    # since that approach divides horizontally, not vertically
    
    print(f"Note: The 4 vertical strips approach divides horizontally (256/4 = 64-wide strips)")
    print(f"   It doesn't address vertical distribution within each strip.")
    print(f"   For vertical distribution (like 2/3 robe + 1/3 armor),")
    print(f"   we'd need a different approach that looks for vertical content patterns.")

if __name__ == "__main__":
    analyze_atlas_0()
    extract_detailed_vertical_analysis()