#!/usr/bin/env python3
"""
Sprite Atlas Item Extractor

Automatically detects and extracts individual items from sprite atlas PNG files.
Handles transparency and can optionally rotate items by 180 degrees.

Usage:
    python extract_atlas_items.py input_atlas.png
    python extract_atlas_items.py input_atlas.png --output my_items --padding 10
    python extract_atlas_items.py input_atlas.png --no-rotate
"""

import cv2
import numpy as np
from pathlib import Path
import argparse


def extract_items_from_atlas(input_path, output_dir='extracted_items', padding=5, min_area=100, rotate_180=True):
    """
    Extract individual items from a sprite atlas with transparency.
    
    Args:
        input_path: Path to the atlas PNG file
        output_dir: Directory to save extracted items
        padding: Extra pixels around each item (default: 5)
        min_area: Minimum pixel area to consider (filters noise, default: 100)
        rotate_180: Rotate each extracted item by 180 degrees (default: True)
    
    Returns:
        Number of items extracted
    """
    # Read image with alpha channel
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    
    if img is None:
        print(f"Error: Could not read image '{input_path}'")
        return 0
    
    print(f"Processing: {input_path}")
    print(f"Image shape: {img.shape}")
    print(f"Channels: {img.shape[2] if len(img.shape) > 2 else 1}")
    
    # Extract alpha channel
    if len(img.shape) > 2 and img.shape[2] == 4:
        alpha = img[:, :, 3]
    else:
        # If no alpha, use brightness threshold
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, alpha = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    
    # Find contours on alpha channel
    contours, _ = cv2.findContours(alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    print(f"Found {len(contours)} potential items")
    
    item_count = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Skip tiny artifacts
        if area < min_area:
            continue
            
        # Get bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        # Add padding
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(img.shape[1], x + w + padding)
        y2 = min(img.shape[0], y + h + padding)
        
        # Extract item
        item = img[y1:y2, x1:x2]
        
        # Rotate 180 degrees if requested
        if rotate_180:
            item = cv2.rotate(item, cv2.ROTATE_180)
        
        # Save with transparency preserved
        output_path = f"{output_dir}/item_{item_count:03d}.png"
        cv2.imwrite(output_path, item)
        
        print(f"  Extracted item {item_count}: {w}x{h} pixels -> {output_path}")
        item_count += 1
    
    print(f"\nSuccessfully extracted {item_count} items to '{output_dir}/'")
    return item_count


def main():
    parser = argparse.ArgumentParser(
        description='Extract individual items from sprite atlas PNG files'
    )
    parser.add_argument(
        'input',
        help='Path to the input atlas PNG file'
    )
    parser.add_argument(
        '--output', '-o',
        default='extracted_items',
        help='Output directory for extracted items (default: extracted_items)'
    )
    parser.add_argument(
        '--padding', '-p',
        type=int,
        default=5,
        help='Padding in pixels around each item (default: 5)'
    )
    parser.add_argument(
        '--min-area', '-m',
        type=int,
        default=100,
        help='Minimum area in pixels to consider an item (default: 100)'
    )
    parser.add_argument(
        '--no-rotate',
        action='store_true',
        help='Do not rotate items by 180 degrees'
    )
    
    args = parser.parse_args()
    
    # Extract items
    count = extract_items_from_atlas(
        input_path=args.input,
        output_dir=args.output,
        padding=args.padding,
        min_area=args.min_area,
        rotate_180=not args.no_rotate
    )
    
    if count == 0:
        print("\nWarning: No items were extracted. Try adjusting --min-area or check the input file.")
    

if __name__ == '__main__':
    main()
