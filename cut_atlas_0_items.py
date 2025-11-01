#!/usr/bin/env python3
"""
Script to cut the atlas_0 image into 4 specific items based on manual analysis.
This creates clean individual icon files for each item.
"""

import sys
from pathlib import Path
from PIL import Image

def cut_atlas_0_items(atlas_path, output_dir):
    """
    Cut the atlas_0 image into 4 specific items based on manual analysis.
    """
    # Load the atlas
    atlas = Image.open(atlas_path)
    width, height = atlas.size
    print(f"Processing atlas: {atlas_path.name} ({width}x{height})")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define the 4 items with their exact coordinates
    items = [
        {
            'name': 'lila_robe',
            'x': 0,
            'y': 0,
            'width': 64,
            'height': 177,
            'description': 'Purple lila robe (top portion of first column)'
        },
        {
            'name': 'body_armor',
            'x': 0,
            'y': 177,
            'width': 64,
            'height': 53,
            'description': 'Golden body armor piece (bottom portion of first column)'
        },
        {
            'name': 'sword',
            'x': 64,
            'y': 0,
            'width': 64,
            'height': 239,
            'description': 'Light blue sword (middle column)'
        },
        {
            'name': 'scythe_hook',
            'x': 128,
            'y': 0,
            'width': 64,
            'height': 256,
            'description': 'Brown-handled scythe/hook weapon (right column)'
        }
    ]
    
    extracted_items = []
    
    for i, item in enumerate(items):
        # Calculate crop boundaries
        left = item['x']
        top = item['y']
        right = left + item['width']
        bottom = top + item['height']
        
        # Extract the item
        item_img = atlas.crop((left, top, right, bottom))
        
        # Save the item
        item_path = output_dir / f"{item['name']}_{item['width']}x{item['height']}.png"
        item_img.save(item_path)
        extracted_items.append(item_path)
        
        print(f"Extracted {item['name']}: {item_path.name} ({item['width']}x{item['height']}px) - {item['description']}")
    
    return extracted_items

def main():
    """
    Main function to cut atlas_0 into 4 specific items.
    """
    project_root = Path(__file__).parent
    atlas_path = project_root / "ExtractedAssets" / "UI" / "itm_icons_extracted" / "atlas_0" / "_atlas_0.png"
    output_dir = project_root / "ExtractedAssets" / "UI" / "cut_items"
    
    print("=" * 70)
    print("ATLAS_0 ITEM CUTTING SCRIPT")
    print("=" * 70)
    print(f"Cutting atlas_0 into 4 specific items:")
    print(f"Atlas source: {atlas_path}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Cut the items
    extracted = cut_atlas_0_items(atlas_path, output_dir)
    
    print(f"\nSuccessfully extracted {len(extracted)} items!")
    print(f"Check the following directory for results:")
    print(f"  - {output_dir}")

if __name__ == "__main__":
    main()