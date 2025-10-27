#!/usr/bin/env python3
"""
Test script to validate spell icon path resolution.
"""

import json
import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    """Fixture providing the project root path"""
    return Path(__file__).parent.parent.parent


def test_spell_icon_paths(project_root):
    """Test spell icon path resolution."""
    print("Testing Spell Icon Path Resolution")
    print("=" * 50)
    
    # Define paths
    icons_root = project_root / "ExtractedAssets" / "UI" / "icons_extracted"
    mapping_path = project_root / "src" / "TirganachReloaded" / "data" / "ui_icon_mapping.json"
    
    print(f"Icons root: {icons_root}")
    print(f"Mapping path: {mapping_path}")
    print()
    
    # Load mapping
    if not mapping_path.exists():
        print("❌ Mapping file not found")
        return
    
    with open(mapping_path, 'r') as f:
        mapping = json.load(f)
    
    # Find a spell handle to test
    item_to_icons = mapping.get('item_to_icons', {})
    
    spell_handles = []
    for item_id, icons in item_to_icons.items():
        for icon in icons:
            handle = icon.get('handle', '')
            if handle.startswith('ui_spell_'):
                spell_handles.append((item_id, handle))
                if len(spell_handles) >= 5:  # Just test first 5
                    break
        if len(spell_handles) >= 5:
            break
    
    print(f"Found {len(spell_handles)} spell handles to test:")
    for item_id, handle in spell_handles:
        print(f"  Item {item_id}: {handle}")
    
    print()
    
    # Test path resolution
    print("Testing path resolution:")
    for item_id, handle in spell_handles[:3]:  # Test first 3
        print(f"  Testing: {handle}")
        
        # Try to find in spell atlases (atlas_0 through atlas_17)
        found = False
        for atlas_num in range(18):  # 18 spell atlases
            # Try primary icon (index 1)
            icon_path = icons_root / "spell" / f"atlas_{atlas_num}" / "icon_001.png"
            if icon_path.exists():
                print(f"    ✓ Found in atlas_{atlas_num}/icon_001.png")
                found = True
                break
        
        if not found:
            # Try other indices
            for atlas_num in range(18):
                # Try indices 1-16
                for idx in range(1, 17):
                    icon_path = icons_root / "spell" / f"atlas_{atlas_num}" / f"icon_{idx:03d}.png"
                    if icon_path.exists():
                        print(f"    ✓ Found in atlas_{atlas_num}/icon_{idx:03d}.png")
                        found = True
                        break
                if found:
                    break
            
            if not found:
                print(f"    ❌ Not found in any spell atlas")
    
    print()
    
    # Show what actually exists
    print("Actual spell atlas contents:")
    spell_dir = icons_root / "spell"
    if spell_dir.exists():
        atlas_dirs = list(spell_dir.glob("atlas_*"))
        print(f"  Found {len(atlas_dirs)} spell atlas directories")
        
        for atlas_dir in sorted(atlas_dirs)[:3]:  # Show first 3
            icons = list(atlas_dir.glob("icon_*.png"))
            print(f"    {atlas_dir.name}: {len(icons)} icons")
        
        if len(atlas_dirs) > 3:
            print(f"    ... and {len(atlas_dirs) - 3} more")
    else:
        print("  ❌ Spell directory not found")

def main():
    """Main test function."""
    project_root = Path(__file__).parent.parent.parent
    test_spell_icon_paths(project_root)

if __name__ == "__main__":
    main()