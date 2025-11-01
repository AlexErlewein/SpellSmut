#!/usr/bin/env python3
"""
Advanced extraction tool for atlas_0 to detect vertically-stacked items
within horizontal segments. This handles cases where items like robes
and armor are stacked vertically within a single horizontal segment.
"""

import sys
from pathlib import Path
from PIL import Image

def detect_content_regions_v2(image, threshold=20):
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

def extract_vertical_segments_v2(atlas_path, output_dir):
    """
    Extract both horizontal strips AND detect vertical subdivisions within each strip.
    """
    atlas = Image.open(atlas_path)
    atlas_width, atlas_height = atlas.size
    print(f"Processing atlas: {atlas_path.name} ({atlas_width}x{atlas_height})")
    
    # Divide horizontally into 4 segments
    num_segments = 4
    segment_width = atlas_width // num_segments
    
    output_dir.mkdir(parents=True, exist_ok=True)
    extracted = []
    
    for i in range(num_segments):
        left = i * segment_width
        right = (i + 1) * segment_width
        
        # Extract horizontal segment
        segment = atlas.crop((left, 0, right, atlas_height))
        
        # Detect content regions within this segment
        content_regions = detect_content_regions_v2(segment)
        
        print(f"\nSegment {i+1} ({left}-{right-1}):")
        print(f"  Horizontal segment: {segment_width}x{atlas_height}")
        print(f"  Content regions detected: {len(content_regions)}")
        
        if content_regions:
            for j, (start_y, end_y) in enumerate(content_regions):
                actual_height = end_y - start_y
                if actual_height > 10:  # Only extract if region is significant
                    # Crop to content region
                    content_img = segment.crop((0, start_y, segment_width, end_y))
                    
                    # Save as individual extracted item
                    item_path = output_dir / f"segment_{i+1:02d}_item_{j+1:02d}_{actual_height}px.png"
                    content_img.save(item_path)
                    extracted.append(item_path)
                    
                    print(f"    Extracted item {j+1}: {item_path.name} ({segment_width}x{actual_height}px)")
        else:
            # If no content regions detected, save the whole segment
            segment_path = output_dir / f"segment_{i+1:02d}_full.png"
            segment.save(segment_path)
            extracted.append(segment_path)
            print(f"    Saved full segment: {segment_path.name}")
    
    return extracted

def advanced_analysis_atlas_0():
    """
    Perform advanced analysis specifically on atlas_0 to extract
    vertically-stacked items like robes and armor.
    """
    project_root = Path(__file__).parent
    atlas_path = project_root / "ExtractedAssets" / "UI" / "itm_icons_extracted" / "atlas_0" / "_atlas_0.png"
    
    print("Advanced analysis of atlas_0 for vertically-stacked items:")
    print(f"Atlas: {atlas_path.name}")
    
    if not atlas_path.exists():
        print("Atlas file not found!")
        return
    
    # Create output directory
    output_dir = project_root / "ExtractedAssets" / "UI" / "advanced_extraction"
    
    # Extract with advanced segmentation
    extracted = extract_vertical_segments_v2(atlas_path, output_dir)
    
    print(f"\nAdvanced extraction completed!")
    print(f"Extraction saved to: {output_dir}")
    print(f"Total items extracted: {len(extracted)}")
    
    # Also run the simple 4 vertical strips for comparison
    print(f"\nFor comparison, running simple 4 vertical strips:")
    simple_output = project_root / "ExtractedAssets" / "UI" / "simple_vertical_strips"
    simple_output.mkdir(parents=True, exist_ok=True)  # Create directory first
    
    atlas = Image.open(atlas_path)
    width, height = atlas.size
    num_strips = 4
    strip_width = width // num_strips
    
    for i in range(num_strips):
        left = i * strip_width
        right = (i + 1) * strip_width
        
        # Extract the strip
        strip = atlas.crop((left, 0, right, height))
        
        # Save the strip
        strip_path = simple_output / f"atlas_0_strip_{i+1:02d}_{strip_width}x{height}.png"
        strip.save(strip_path)
    
    print(f"Simple vertical strips saved to: {simple_output}")
    print(f"Created {num_strips} vertical strips of {strip_width}x{height} pixels each")

def detect_2by3_1by3_layout(atlas_path, output_dir):
    """
    Specialized function to detect if there are items that take 2/3 and 1/3 of vertical space.
    """
    atlas = Image.open(atlas_path)
    atlas_width, atlas_height = atlas.size
    
    # 2/3 height = ~171 pixels, 1/3 height = ~85 pixels (for 256px height)
    two_thirds_height = int(atlas_height * 2 / 3)
    one_third_height = atlas_height - two_thirds_height
    
    print(f"\nAnalyzing for 2/3 (~{two_thirds_height}px) and 1/3 (~{one_third_height}px) layout...")
    
    # Divide horizontally into 4 segments as before
    num_segments = 4
    segment_width = atlas_width // num_segments
    segment_output = output_dir / "2by3_1by3_analysis"
    segment_output.mkdir(parents=True, exist_ok=True)
    
    for i in range(num_segments):
        left = i * segment_width
        right = (i + 1) * segment_width
        
        # Extract horizontal segment
        segment = atlas.crop((left, 0, right, atlas_height))
        
        # Try to detect upper (robe) and lower (armor) parts at 2/3 and 1/3 heights
        upper_part = segment.crop((0, 0, segment_width, two_thirds_height))
        lower_part = segment.crop((0, two_thirds_height, segment_width, atlas_height))
        
        # Check if each part has significant content
        upper_content = detect_content_regions_v2(upper_part)
        lower_content = detect_content_regions_v2(lower_part)
        
        print(f"Segment {i+1}:")
        print(f"  Upper (robe area {two_thirds_height}px): {len(upper_content)} content regions")
        print(f"  Lower (armor area {one_third_height}px): {len(lower_content)} content regions")
        
        # Save parts if they have content
        if upper_content:
            upper_path = segment_output / f"seg_{i+1:02d}_upper_2by3.png"
            upper_part.save(upper_path)
        
        if lower_content:
            # Offset the Y position for the lower part
            lower_path = segment_output / f"seg_{i+1:02d}_lower_1by3.png"
            lower_part.save(lower_path)

if __name__ == "__main__":
    advanced_analysis_atlas_0()
    
    # Now run the specialized 2/3 and 1/3 analysis
    project_root = Path(__file__).parent
    atlas_path = project_root / "ExtractedAssets" / "UI" / "itm_icons_extracted" / "atlas_0" / "_atlas_0.png"
    output_dir = project_root / "ExtractedAssets" / "UI" / "advanced_extraction"
    
    detect_2by3_1by3_layout(atlas_path, output_dir)
    
    print(f"\nAdvanced extraction and analysis complete!")
    print(f"Check the following directories:")
    print(f"  - {output_dir / 'advanced_extraction'} - For detailed segmentation")
    print(f"  - {output_dir / '2by3_1by3_analysis'} - For 2/3 and 1/3 layout analysis")
    print(f"  - {project_root / 'ExtractedAssets' / 'UI' / 'simple_vertical_strips'} - For simple vertical strips")