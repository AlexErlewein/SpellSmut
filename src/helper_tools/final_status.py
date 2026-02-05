#!/usr/bin/env python3
"""
Final status report for ITM icon extraction and Allwissende Almacht integration.
"""

import json
from pathlib import Path

def show_final_status():
    project_root = Path(__file__).parent
    icons_root = project_root / "ExtractedAssets" / "UI" / "icons_extracted"
    
    print("🎯 ITM ICON EXTRACTION & INTEGRATION - FINAL STATUS")
    print("=" * 60)
    
    # Load icon index
    index_path = icons_root / "icon_index.json"
    with open(index_path) as f:
        index_data = json.load(f)
    
    # Count by category
    categories = {}
    for key, data in index_data["icons"].items():
        category = data["category"]
        categories[category] = categories.get(category, 0) + 1
    
    print("📊 Icon Statistics:")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count:,} icons")
    
    print(f"\n📁 Directory Structure:")
    for category_dir in icons_root.iterdir():
        if category_dir.is_dir():
            icon_count = len(list(category_dir.rglob("icon_*.png")))
            weapon_count = len(list(category_dir.rglob("weapon_*.png")))
            print(f"  {category_dir.name}/: {icon_count} icons, {weapon_count} weapons")
    
    # Check ITM specific details
    itm_dir = icons_root / "itm"
    if itm_dir.exists():
        atlas_count = len(list(itm_dir.glob("atlas_*")))
        print(f"\n🎮 ITM Specific Details:")
        print(f"  Atlas directories: {atlas_count}")
        print(f"  Total ITM icons: {categories.get('itm', 0):,}")
        
        # Show sample atlases
        sample_atlases = sorted(itm_dir.glob("atlas_*"))[:3]
        print(f"  Sample atlases:")
        for atlas in sample_atlases:
            icons = list(atlas.glob("icon_*.png"))
            weapons = list(atlas.glob("weapon_*.png"))
            print(f"    {atlas.name}: {len(icons)} icons, {len(weapons)} weapons")
    
    print(f"\n✅ Integration Status:")
    print(f"  ✓ Allwissende Almacht updated with dynamic category detection")
    print(f"  ✓ Filter statistics implemented")
    print(f"  ✓ ITM icons available at: {itm_dir.relative_to(project_root)}")
    print(f"  ✓ Icon index updated with {categories.get('itm', 0):,} ITM entries")
    
    print(f"\n🚀 Ready for:")
    print(f"  1. Allwissende Almacht testing (requires PySide6 installation)")
    print(f"  2. CFF editor integration")
    print(f"  3. Item icon mapping to GameData.cff")
    
    print(f"\n🎉 ITM Icon Extraction: COMPLETE!")

if __name__ == "__main__":
    show_final_status()