#!/usr/bin/env python3
"""
Visual inspection helper - convert sample atlases to PNG for manual review.
"""

from pathlib import Path
import subprocess
import re

def main():
    project_root = Path(__file__).parent.parent.parent
    extracted_ui = project_root / "ExtractedAssets" / "UI" / "extracted"
    output_dir = project_root / "ExtractedAssets" / "UI" / "category_samples"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Converting sample atlases for visual inspection...")
    print()
    
    # Categories to sample
    categories = ['bgr', 'btn', 'oth', 'cnt', 'itm', 'logo']
    
    for cat in categories:
        # Find first file for this category
        files = list(extracted_ui.rglob(f"ui_{cat}*.dds"))
        if not files:
            print(f"  ⚠ No files found for category: {cat}")
            continue
        
        # Take first file
        sample_file = sorted(files)[0]
        
        # Extract number from filename
        match = re.search(r'ui_([a-z]+)(\d+)', sample_file.stem)
        if match:
            cat_name = match.group(1)
            cat_num = match.group(2)
        else:
            cat_name = cat
            cat_num = "0"
        
        # Convert to PNG
        output_png = output_dir / f"{cat_name}_{cat_num}_sample.png"
        
        print(f"  [{cat}] {sample_file.name} -> {output_png.name}...", end=" ", flush=True)
        
        result = subprocess.run(
            ['magick', 'convert', str(sample_file), str(output_png)],
            capture_output=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✓")
        else:
            print(f"✗ {result.stderr}")
    
    print()
    print(f"Samples saved to: {output_dir}")
    print(f"Opening folder for visual inspection...")
    
    # Open folder
    subprocess.run(['open', str(output_dir)])

if __name__ == '__main__':
    main()
