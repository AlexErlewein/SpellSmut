#!/usr/bin/env python3
"""
Final extraction tool that creates clean individual icon files for each item.
This handles both the 4 vertical strip approach and advanced content detection.
"""

import sys
from pathlib import Path
from PIL import Image

def detect_content_regions(image, threshold=20):
    """
    Detect regions with content vs. empty regions in an image.
    This helps identify where actual items are vs. empty space.
    """
    img = image.convert('RGBA')  # Ensure alpha channel for transparency
    width, height = img.size
    
    content_regions = []
    
    # Sample every 4th row to make detection faster while still being accurate
    for y in range(0, height, 4):
        has_content = False
        start_y = y
        end_y = y
        
        # Check if this row has non-transparent pixels
        row_content = 0
        for x in range(width):
            pixel = img.getpixel((x, y))
            # Check if pixel is not transparent (alpha > threshold) and not blank
            if len(pixel) >= 4:  # RGBA
                if pixel[3] > threshold:  # Alpha channel
                    row_content += 1
            else:  # RGB (assume opaque)
                # Check if it's not a background color (like pure black or pure white)
                if pixel != (0, 0, 0) and pixel != (255, 255, 255):
                    row_content += 1
        
        if row_content > width * 0.1:  # If more than 10% of row has content
            has_content = True
            # Expand to find full content block
            while end_y < height:
                temp_row_content = 0
                for x in range(width):
                    pixel = img.getpixel((x, end_y))
                    if len(pixel) >= 4:
                        if pixel[3] > threshold:
                            temp_row_content += 1
                    else:
                        if pixel != (0, 0, 0) and pixel != (255, 255, 255):
                            temp_row_content += 1
                
                if temp_row_content <= width * 0.1:  # Less than 10% content
                    break
                end_y += 1
        
        if has_content:
            # Add content region
            content_regions.append((start_y, end_y))
    
    # Merge overlapping regions
    if not content_regions:
        return []
    
    merged_regions = [content_regions[0]]
    for start, end in content_regions[1:]:
        prev_start, prev_end = merged_regions[-1]
        if start <= prev_end:  # Overlapping or adjacent
            merged_regions[-1] = (prev_start, max(prev_end, end))
        else:
            merged_regions.append((start, end))
    
    return merged_regions

def extract_clean_items(atlas_path, output_dir):
    """
    Extract clean individual icon files for each item.
    This handles both horizontal segments and vertical stacking within them.
    """
    atlas = Image.open(atlas_path)
    atlas_width, atlas_height = atlas.size
    print(f"Processing atlas: {atlas_path.name} ({atlas_width}x{atlas_height})")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Divide horizontally into 4 segments
    num_segments = 4
    segment_width = atlas_width // num_segments
    
    extracted_items = []
    
    for i in range(num_segments):
        left = i * segment_width
        right = (i + 1) * segment_width
        
        # Extract horizontal segment
        segment = atlas.crop((left, 0, right, atlas_height))
        
        # Detect content regions within this segment
        content_regions = detect_content_regions(segment)
        
        print(f"\nSegment {i+1} ({left}-{right-1}):")
        print(f"  Horizontal segment: {segment_width}x{atlas_height}")
        print(f"  Content regions detected: {len(content_regions)}")
        
        if content_regions:
            for j, (start_y, end_y) in enumerate(content_regions):
                actual_height = end_y - start_y
                if actual_height > 10:  # Only extract if region is significant
                    # Crop to content region
                    content_img = segment.crop((0, start_y, segment_width, end_y))
                    
                    # Save as individual extracted item with clean naming
                    item_path = output_dir / f"item_segment_{i+1:02d}_region_{j+1:02d}_{actual_height}px.png"
                    content_img.save(item_path)
                    extracted_items.append(item_path)
                    
                    print(f"    Extracted item {j+1}: {item_path.name} ({segment_width}x{actual_height}px)")
        else:
            # If no content regions detected, save the whole segment
            segment_path = output_dir / f"item_segment_{i+1:02d}_full.png"
            segment.save(segment_path)
            extracted_items.append(segment_path)
            print(f"    Saved full segment: {segment_path.name}")
    
    return extracted_items

def process_multiple_atlases():
    """
    Process multiple atlases to get more diversity in extraction.
    """
    project_root = Path(__file__).parent
    base_dir = project_root / "ExtractedAssets" / "UI" / "itm_icons_extracted"
    
    # List all atlas directories
    atlas_dirs = list(base_dir.glob("atlas_*"))
    
    print(f"Found {len(atlas_dirs)} atlas directories")
    
    # Process first 5 atlases for diversity
    for atlas_dir in atlas_dirs[:5]:  # Just process first 5 for now
        atlas_num = atlas_dir.name.replace("atlas_", "")
        print(f"\nProcessing atlas {atlas_num}...")
        
        # Find the original atlas file
        atlas_files = list(atlas_dir.glob("_atlas_*.png"))
        if not atlas_files:
            print(f"  No original atlas files found in {atlas_dir}")
            continue
            
        original_atlas = atlas_files[0]
        print(f"  Found original atlas: {original_atlas.name}")
        
        # Create output directory for this atlas
        output_dir = project_root / "ExtractedAssets" / "UI" / "clean_extraction" / f"atlas_{atlas_num}"
        
        # Extract clean items
        extracted = extract_clean_items(original_atlas, output_dir)
        
        print(f"  Extracted {len(extracted)} clean items to {output_dir}")
    
    print(f"\nCompleted processing all selected atlases")

def main():
    """
    Main function to extract clean individual icon files.
    """
    print("=" * 70)
    print("CLEAN ITEM EXTRACTION TOOL")
    print("=" * 70)
    print("This tool extracts clean individual icon files for each item,")
    print("handling both horizontal segments and vertical stacking within them.")
    print()
    
    # Process atlas_0 specifically first
    project_root = Path(__file__).parent
    atlas_path = project_root / "ExtractedAssets" / "UI" / "itm_icons_extracted" / "atlas_0" / "_atlas_0.png"
    output_dir = project_root / "ExtractedAssets" / "UI" / "clean_extraction" / "atlas_0"
    
    print(f"Processing atlas_0...")
    extracted = extract_clean_items(atlas_path, output_dir)
    
    print(f"\nTotal extracted from atlas_0: {len(extracted)} items")
    
    # Also process other atlases for more diversity
    print(f"\nNow processing additional atlases for more diversity...")
    process_multiple_atlases()
    
    print(f"\nAll clean extractions completed!")
    print(f"Check the following directory for results:")
    print(f"  - {project_root / 'ExtractedAssets' / 'UI' / 'clean_extraction'}")

if __name__ == "__main__":
    main()