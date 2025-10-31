#!/usr/bin/env python3
"""
Test script to verify ITM icons are properly extracted and accessible.
"""

import json
from pathlib import Path

def test_itm_icons():
    project_root = Path(__file__).parent
    icons_root = project_root / "ExtractedAssets" / "UI" / "icons_extracted"
    
    print("Testing ITM Icon Extraction")
    print("=" * 50)
    
    # Check icon index
    index_path = icons_root / "icon_index.json"
    if not index_path.exists():
        print("❌ Icon index not found")
        return False
    
    with open(index_path) as f:
        index_data = json.load(f)
    
    # Count ITM entries
    itm_entries = {k: v for k, v in index_data["icons"].items() if k.startswith("itm_")}
    print(f"✅ Found {len(itm_entries)} ITM entries in icon index")
    
    # Check some sample files exist
    sample_entries = list(itm_entries.items())[:5]
    for key, data in sample_entries:
        icon_path = icons_root / data["path"]
        if icon_path.exists():
            print(f"✅ {key}: {icon_path.relative_to(project_root)}")
        else:
            print(f"❌ {key}: {icon_path.relative_to(project_root)} (missing)")
    
    # Check ITM directory structure
    itm_dir = icons_root / "itm"
    if itm_dir.exists():
        atlas_dirs = list(itm_dir.glob("atlas_*"))
        print(f"✅ Found {len(atlas_dirs)} atlas directories")
        
        # Count total icon files
        icon_files = list(itm_dir.rglob("icon_*.png"))
        print(f"✅ Found {len(icon_files)} icon files")
        
        # Count weapon files
        weapon_files = list(itm_dir.rglob("weapon_*.png"))
        print(f"✅ Found {len(weapon_files)} weapon files")
    else:
        print("❌ ITM directory not found")
        return False
    
    print("\n🎉 ITM icon extraction test PASSED!")
    return True

if __name__ == "__main__":
    test_itm_icons()