#!/usr/bin/env python3
"""
Sprite Atlas Item Extractor

Automatically detects and extracts individual items from sprite atlas PNG files.
Handles transparency and can optionally rotate items by 180 degrees.
"""

import cv2
import numpy as np
from pathlib import Path
import argparse


def _split_touching_components(
    mask_roi: np.ndarray,
    *,
    min_area: int,
    kernel_size: int,
    max_erosion: int,
) -> list[tuple[np.ndarray, tuple[int, int, int, int]]]:
    if max_erosion <= 0:
        return []

    k = max(1, int(kernel_size))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))

    for erosion_iter in range(1, int(max_erosion) + 1):
        eroded = cv2.erode(mask_roi, kernel, iterations=erosion_iter)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(eroded, connectivity=8)
        component_ids = [
            cid
            for cid in range(1, num_labels)
            if int(stats[cid, cv2.CC_STAT_AREA]) >= int(min_area)
        ]

        if len(component_ids) < 2:
            continue

        components: list[tuple[np.ndarray, tuple[int, int, int, int]]] = []
        for cid in component_ids:
            comp_mask = (labels == cid).astype(np.uint8) * 255
            comp_mask = cv2.dilate(comp_mask, kernel, iterations=erosion_iter)

            ys, xs = np.where(comp_mask > 0)
            if len(xs) == 0 or len(ys) == 0:
                continue

            x1 = int(xs.min())
            y1 = int(ys.min())
            x2 = int(xs.max()) + 1
            y2 = int(ys.max()) + 1
            components.append((comp_mask, (x1, y1, x2 - x1, y2 - y1)))

        components.sort(key=lambda c: (c[1][1], c[1][0]))
        return components

    return []


def extract_items_from_atlas(
    input_path,
    output_dir='extracted_items',
    padding=5,
    min_area=100,
    rotate_180=True,
    alpha_threshold=10,
    open_kernel=0,
    open_iterations=1,
    close_kernel=0,
    close_iterations=1,
    split_touching=False,
    split_kernel=3,
    split_max_erosion=5,
    split_min_area=0,
):
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
        _, mask = cv2.threshold(alpha, int(alpha_threshold), 255, cv2.THRESH_BINARY)
    else:
        # If no alpha, use brightness threshold
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)

    if open_kernel and int(open_kernel) > 0:
        k = int(open_kernel)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=int(open_iterations))

    if close_kernel and int(close_kernel) > 0:
        k = int(close_kernel)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=int(close_iterations))

    # Find contours on binary mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
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

        components: list[tuple[np.ndarray, tuple[int, int, int, int]]] = []
        if split_touching:
            roi_mask = mask[y : y + h, x : x + w]
            components = _split_touching_components(
                roi_mask,
                min_area=int(split_min_area) if int(split_min_area) > 0 else int(min_area),
                kernel_size=int(split_kernel),
                max_erosion=int(split_max_erosion),
            )

        if not components:
            components = [(mask[y : y + h, x : x + w], (0, 0, w, h))]

        for comp_mask, (cx, cy, cw, ch) in components:
            ax = x + int(cx)
            ay = y + int(cy)
            aw = int(cw)
            ah = int(ch)

            # Add padding
            x1 = max(0, ax - padding)
            y1 = max(0, ay - padding)
            x2 = min(img.shape[1], ax + aw + padding)
            y2 = min(img.shape[0], ay + ah + padding)

            item = img[y1:y2, x1:x2].copy()

            if len(img.shape) > 2 and img.shape[2] == 4:
                alpha_ch = item[:, :, 3]
                padded_mask = np.zeros((y2 - y1, x2 - x1), dtype=np.uint8)
                mx1 = ax - x1
                my1 = ay - y1
                padded_mask[my1 : my1 + ah, mx1 : mx1 + aw] = comp_mask[
                    int(cy) : int(cy) + ah, int(cx) : int(cx) + aw
                ]
                alpha_ch[padded_mask == 0] = 0
                item[:, :, 3] = alpha_ch
            else:
                padded_mask = np.zeros((y2 - y1, x2 - x1), dtype=np.uint8)
                mx1 = ax - x1
                my1 = ay - y1
                padded_mask[my1 : my1 + ah, mx1 : mx1 + aw] = comp_mask[
                    int(cy) : int(cy) + ah, int(cx) : int(cx) + aw
                ]
                item[padded_mask == 0] = 0

            # Rotate 180 degrees if requested
            if rotate_180:
                item = cv2.rotate(item, cv2.ROTATE_180)

            # Save with transparency preserved
            output_path = f"{output_dir}/item_{item_count:03d}.png"
            cv2.imwrite(output_path, item)

            print(f"  Extracted item {item_count}: {aw}x{ah} pixels -> {output_path}")
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
        '--alpha-threshold',
        type=int,
        default=10,
        help='Alpha threshold (0-255). Pixels <= threshold are treated as transparent (default: 10)'
    )
    parser.add_argument(
        '--open-kernel',
        type=int,
        default=0,
        help='Optional morphology opening kernel size (odd int like 3/5). 0 disables (default: 0)'
    )
    parser.add_argument(
        '--open-iterations',
        type=int,
        default=1,
        help='Morphology opening iterations (default: 1)'
    )
    parser.add_argument(
        '--close-kernel',
        type=int,
        default=0,
        help='Optional morphology closing kernel size. 0 disables (default: 0)'
    )
    parser.add_argument(
        '--close-iterations',
        type=int,
        default=1,
        help='Morphology closing iterations (default: 1)'
    )
    parser.add_argument(
        '--split-touching',
        action='store_true',
        help='Try to split merged items by eroding the mask until components separate (default: off)'
    )
    parser.add_argument(
        '--split-kernel',
        type=int,
        default=3,
        help='Kernel size used when splitting touching items (default: 3)'
    )
    parser.add_argument(
        '--split-max-erosion',
        type=int,
        default=5,
        help='Maximum erosion iterations to attempt when splitting touching items (default: 5)'
    )
    parser.add_argument(
        '--split-min-area',
        type=int,
        default=0,
        help='Min area for split components; 0 uses --min-area (default: 0)'
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
        rotate_180=not args.no_rotate,
        alpha_threshold=args.alpha_threshold,
        open_kernel=args.open_kernel,
        open_iterations=args.open_iterations,
        close_kernel=args.close_kernel,
        close_iterations=args.close_iterations,
        split_touching=args.split_touching,
        split_kernel=args.split_kernel,
        split_max_erosion=args.split_max_erosion,
        split_min_area=args.split_min_area,
    )
    
    if count == 0:
        print("\nWarning: No items were extracted. Try adjusting --min-area or check the input file.")
    

if __name__ == '__main__':
    main()
