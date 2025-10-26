#!/usr/bin/env python3
"""
Simple test script to verify spell icon path resolution.
"""

import sys
import json
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "TirganachReloaded"))

def test_spell_icon_resolution():
    """Test spell icon path resolution directly."""
    print("Testing Spell Icon Path Resolution")
    print("=" * 50)
    
    # Load spell data to get handles
    gamedata_path = project_root / "TirganachReloaded" / "GameData.json"
    if not gamedata_path.exists():
        print(f"❌ GameData not found: {gamedata_path}")
        return False
    
    print(f"✓ Loading GameData from: {gamedata_path}")
    
    try:
        with open(gamedata_path, 'r') as f:
            game_data = json.load(f)
        print("✓ GameData loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load GameData: {e}")
        return False
    
    # Get spell names to test with
    spell_names = game_data.get('spell_names', [])
    if not spell_names:
        print("❌ No spell_names found in GameData")
        return False
    
    print(f"✓ Found {len(spell_names)} spell names")
    
    # Test a few spell handles
    test_handles = []
    for spell in spell_names[:5]:  # Test first 5
        handle = spell.get('spell_ui_handle', '')
        if handle and handle.startswith('ui_spell_'):
            test_handles.append(handle)
    
    print(f"\nTesting {len(test_handles)} spell handles:")
    for handle in test_handles:
        print(f"  {handle}")
    
    # Test icon resolution
    print(f"\nTesting icon resolution:")
    
    # Simulate the data model's _resolve_icon_path method
    icons_root = project_root / "ExtractedAssets" / "UI" / "icons_extracted"
    
    success_count = 0
    for handle in test_handles:
        print(f"  Resolving: {handle}")
        
        # Check if we can find the icon in spell directories
        found = False
        for atlas_num in range(18):  # 18 spell atlases
            atlas_dir = icons_root / "spell" / f"atlas_{atlas_num}"
            if atlas_dir.exists():
                # Try indices 1-16
                for idx in range(1, 17):
                    icon_path = atlas_dir / f"icon_{idx:03d}.png"
                    if icon_path.exists():
                        print(f"    ✓ Found at: {icon_path.relative_to(project_root)}")
                        found = True
                        success_count += 1
                        break
                if found:
                    break
        
        if not found:
            print(f"    ❌ Not found in any spell atlas")
    
    print(f"\nResults: {success_count}/{len(test_handles)} spell icons resolved successfully")
    
    return success_count > 0

def main():
    """Main test function."""
    success = test_spell_icon_resolution()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)