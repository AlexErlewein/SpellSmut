#!/usr/bin/env python3
"""
Extract individual icons from UI texture atlases.

SpellForce stores UI icons in 256x256 texture atlases (DDS files).
This script extracts individual icons from these atlases into named PNG files.

The challenge:
- Texture files are numbered (ui_item14.dds, ui_spell5.dds)
- Database has handles (ui_item_equip_weapon_dagger_flame) and indices (1, 2, 3...)
- No direct mapping exists between file numbers and handles

Solution:
- Extract ALL icons from ALL atlases
- Create organized structure: item/atlas_N/icon_M.png
- Build mapping database linking handles to actual files
- Users can then look up icons by handle through the mapping
"""

from PIL import Image
from pathlib import Path
import json
import subprocess
import sys

def convert_dds_to_png(dds_path: Path, png_path: Path) -> bool:
    """
    Convert DDS file to PNG using ImageMagick.
    
    Args:
        dds_path: Path to input DDS file
        png_path: Path to output PNG file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        png_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use ImageMagick to convert
        result = subprocess.run(
            ['magick', 'convert', str(dds_path), str(png_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and png_path.exists():
            return True
        else:
            print(f"  ⚠ Conversion failed for {dds_path.name}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  ⚠ Timeout converting {dds_path.name}")
        return False
    except Exception as e:
        print(f"  ⚠ Error converting {dds_path.name}: {e}")
        return False

def extract_icons_from_atlas(
    atlas_png: Path,
    output_dir: Path,
    grid_size: int = 8,
    icon_size: int = 32
) -> list[Path]:
    """
    Extract individual icons from a texture atlas.
    
    Args:
        atlas_png: Path to atlas PNG file
        output_dir: Directory to save extracted icons
        grid_size: Number of icons per row/column (default 8 for 256x256 atlas with 32x32 icons)
        icon_size: Size of each icon in pixels
        
    Returns:
        List of paths to extracted icon files
    """
    try:
        atlas = Image.open(atlas_png)
        
        if atlas.size[0] != 256 or atlas.size[1] != 256:
            print(f"  ⚠ Unexpected atlas size: {atlas.size} (expected 256x256)")
            # Recalculate grid size
            grid_size = atlas.size[0] // icon_size
        
        output_dir.mkdir(parents=True, exist_ok=True)
        extracted = []
        
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
        
    except Exception as e:
        print(f"  ⚠ Error extracting from {atlas_png}: {e}")
        return []

def main():
    """Main extraction process."""
    
    project_root = Path(__file__).parent.parent.parent
    extracted_ui = project_root / "ExtractedAssets" / "UI" / "extracted"
    output_root = project_root / "ExtractedAssets" / "UI" / "icons_extracted"
    
    print("=" * 80)
    print("UI ICON ATLAS EXTRACTION")
    print("=" * 80)
    print(f"Input:  {extracted_ui}")
    print(f"Output: {output_root}")
    print()
    
    # Statistics
    stats = {
        'atlases_found': 0,
        'atlases_converted': 0,
        'icons_extracted': 0,
        'categories': {}
    }
    
    # Find all UI DDS files
    dds_files = list(extracted_ui.rglob("ui_*.dds"))
    print(f"Found {len(dds_files)} UI texture files")
    print()
    
    # Group by category (item, spell, bgr, etc.)
    by_category = {}
    for dds in dds_files:
        # Extract category from filename (ui_item14.dds -> item)
        parts = dds.stem.split('_')
        if len(parts) >= 2:
            category = parts[1]
            # Extract number from category (item14 -> item, 14)
            import re
            match = re.match(r'([a-z]+)(\d+)', category)
            if match:
                cat_name = match.group(1)
                cat_num = match.group(2)
                by_category.setdefault(cat_name, []).append((cat_num, dds))
    
    print(f"Found {len(by_category)} categories:")
    for cat, files in sorted(by_category.items()):
        print(f"  - {cat}: {len(files)} atlases")
        stats['categories'][cat] = len(files)
    print()
    
    # Process each category
    for cat_name in ['item', 'spell']:  # Focus on game content first
        if cat_name not in by_category:
            print(f"⚠ Category '{cat_name}' not found, skipping")
            continue
        
        print(f"Processing category: {cat_name.upper()}")
        print("-" * 80)
        
        cat_files = sorted(by_category[cat_name], key=lambda x: int(x[0]))
        
        for atlas_num, dds_path in cat_files:
            stats['atlases_found'] += 1
            
            # Create output directory for this atlas
            atlas_output = output_root / cat_name / f"atlas_{atlas_num}"
            
            # Convert DDS to PNG first
            temp_png = atlas_output / f"_atlas_{atlas_num}.png"
            
            print(f"  [{cat_name}_{atlas_num}] Converting to PNG...", end=" ", flush=True)
            if convert_dds_to_png(dds_path, temp_png):
                print("✓")
                stats['atlases_converted'] += 1
                
                # Extract icons from atlas
                print(f"  [{cat_name}_{atlas_num}] Extracting icons...", end=" ", flush=True)
                extracted = extract_icons_from_atlas(
                    temp_png,
                    atlas_output,
                    grid_size=8,
                    icon_size=32
                )
                
                if extracted:
                    print(f"✓ ({len(extracted)} icons)")
                    stats['icons_extracted'] += len(extracted)
                else:
                    print("✗")
            else:
                print("✗")
        
        print()
    
    # Create index of all extracted icons
    print("Creating icon index...")
    index_data = {
        'stats': stats,
        'icons': {}
    }
    
    for icon_file in output_root.rglob("icon_*.png"):
        # Parse path: icons_extracted/item/atlas_14/icon_003.png
        parts = icon_file.relative_to(output_root).parts
        if len(parts) == 3:
            category = parts[0]  # item
            atlas = parts[1].replace('atlas_', '')  # 14
            icon_num = icon_file.stem.replace('icon_', '')  # 003
            
            key = f"{category}_{atlas}_{icon_num}"
            index_data['icons'][key] = {
                'category': category,
                'atlas_number': atlas,
                'icon_index': int(icon_num),
                'path': str(icon_file.relative_to(output_root))
            }
    
    index_file = output_root / "icon_index.json"
    with open(index_file, 'w') as f:
        json.dump(index_data, f, indent=2)
    
    print(f"✓ Icon index saved: {index_file}")
    print()
    
    # Print summary
    print("=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)
    print(f"Atlases found:     {stats['atlases_found']}")
    print(f"Atlases converted: {stats['atlases_converted']}")
    print(f"Icons extracted:   {stats['icons_extracted']}")
    print()
    print("Categories:")
    for cat, count in sorted(stats['categories'].items()):
        print(f"  - {cat}: {count} atlases")
    print()
    print(f"Output: {output_root}")
    print("=" * 80)
    
    # Next steps message
    print()
    print("NEXT STEPS:")
    print("-----------")
    print("1. Build handle-to-icon mapping by analyzing GameData.json")
    print("2. Create lookup function: handle -> (atlas_num, icon_index)")
    print("3. Update CFF editor to use the mapping")
    print()

if __name__ == '__main__':
    main()
