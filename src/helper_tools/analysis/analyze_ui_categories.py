#!/usr/bin/env python3
"""
Analyze UI texture atlases to determine optimal extraction settings.
Check dimensions, grid patterns, and visual characteristics.
"""

from PIL import Image
from pathlib import Path
import json

def analyze_atlas(png_path: Path) -> dict:
    """Analyze an atlas image to determine its characteristics."""
    try:
        img = Image.open(png_path)
        width, height = img.size
        
        # Detect potential grid sizes based on common icon sizes
        potential_grids = []
        for icon_size in [16, 24, 32, 48, 64, 128]:
            if width % icon_size == 0 and height % icon_size == 0:
                grid_w = width // icon_size
                grid_h = height // icon_size
                if grid_w == grid_h:  # Square grids only
                    potential_grids.append({
                        'icon_size': icon_size,
                        'grid_size': grid_w,
                        'total_slots': grid_w * grid_h
                    })
        
        return {
            'dimensions': f"{width}x{height}",
            'width': width,
            'height': height,
            'mode': img.mode,
            'potential_grids': potential_grids
        }
    except Exception as e:
        return {'error': str(e)}

def main():
    project_root = Path(__file__).parent.parent.parent
    extracted_ui = project_root / "ExtractedAssets" / "UI" / "extracted"
    
    print("=" * 80)
    print("UI CATEGORY ANALYSIS")
    print("=" * 80)
    print()
    
    # Find all UI DDS files
    dds_files = list(extracted_ui.rglob("ui_*.dds"))
    
    # Group by category
    import re
    by_category = {}
    for dds in dds_files:
        parts = dds.stem.split('_')
        if len(parts) >= 2:
            category = parts[1]
            match = re.match(r'([a-z]+)(\d+)', category)
            if match:
                cat_name = match.group(1)
                cat_num = match.group(2)
                by_category.setdefault(cat_name, []).append((cat_num, dds))
    
    # Focus on categories we want to investigate
    categories_to_check = ['bgr', 'btn', 'oth', 'cnt', 'itm', 'logo']
    
    for cat_name in categories_to_check:
        if cat_name not in by_category:
            print(f"Category '{cat_name}' not found")
            continue
        
        print(f"Category: {cat_name.upper()}")
        print("-" * 80)
        
        cat_files = sorted(by_category[cat_name], key=lambda x: int(x[0]))
        print(f"Total atlases: {len(cat_files)}")
        
        # Sample first few atlases
        sample_size = min(3, len(cat_files))
        print(f"Sampling first {sample_size} atlases:")
        print()
        
        for i, (atlas_num, dds_path) in enumerate(cat_files[:sample_size]):
            # Convert to PNG temporarily
            temp_png = Path(f"/tmp/temp_atlas_{cat_name}_{atlas_num}.png")
            
            import subprocess
            result = subprocess.run(
                ['magick', 'convert', str(dds_path), str(temp_png)],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0 and temp_png.exists():
                analysis = analyze_atlas(temp_png)
                
                print(f"  [{cat_name}_{atlas_num}] {dds_path.name}")
                print(f"    Dimensions: {analysis['dimensions']}")
                print(f"    Mode: {analysis['mode']}")
                
                if analysis.get('potential_grids'):
                    print(f"    Possible grid configurations:")
                    for grid in analysis['potential_grids']:
                        print(f"      - {grid['grid_size']}x{grid['grid_size']} grid of {grid['icon_size']}x{grid['icon_size']}px icons ({grid['total_slots']} slots)")
                else:
                    print(f"    No standard grid pattern detected")
                print()
                
                # Clean up
                temp_png.unlink()
            else:
                print(f"  [{cat_name}_{atlas_num}] Failed to convert")
                print()
        
        print()
    
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print("Based on the analysis above, determine extraction settings for each category:")
    print("- Grid size (e.g., 4x4, 8x8)")
    print("- Icon size (e.g., 32x32, 64x64)")
    print("- Offset if needed")
    print("- Rotation if needed")

if __name__ == '__main__':
    main()
