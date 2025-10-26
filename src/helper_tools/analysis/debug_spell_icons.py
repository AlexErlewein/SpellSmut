#!/usr/bin/env python3
"""
Debug script to diagnose spell icon display issues in GUI.

This script helps identify why spell icons are not displaying correctly
in the GUI editor despite successful extraction.
"""

import json
import sys
from pathlib import Path
from PIL import Image

def check_spell_icon_files(project_root):
    """Check if spell icon files exist and are readable."""
    print("=" * 60)
    print("CHECKING SPELL ICON FILES")
    print("=" * 60)
    
    spell_icons_dir = project_root / "ExtractedAssets" / "UI" / "icons_extracted" / "spell"
    
    if not spell_icons_dir.exists():
        print(f"❌ Spell icons directory not found: {spell_icons_dir}")
        return False
    
    print(f"✓ Spell icons directory exists: {spell_icons_dir}")
    
    # Check atlas directories
    atlas_dirs = list(spell_icons_dir.glob("atlas_*"))
    print(f"✓ Found {len(atlas_dirs)} spell atlas directories")
    
    if not atlas_dirs:
        print("❌ No spell atlas directories found")
        return False
    
    # Check first few icons
    first_atlas = atlas_dirs[0]
    icon_files = list(first_atlas.glob("icon_*.png"))
    print(f"✓ Found {len(icon_files)} icons in {first_atlas.name}")
    
    if icon_files:
        # Try to open first icon
        try:
            first_icon = icon_files[0]
            img = Image.open(first_icon)
            print(f"✓ First icon readable: {first_icon.name} ({img.size})")
        except Exception as e:
            print(f"❌ Failed to open first icon: {e}")
            return False
    
    return True

def check_icon_index(project_root):
    """Check if icon index file exists and contains spell data."""
    print("\n" + "=" * 60)
    print("CHECKING ICON INDEX")
    print("=" * 60)
    
    icon_index_path = project_root / "ExtractedAssets" / "UI" / "icons_extracted" / "icon_index.json"
    
    if not icon_index_path.exists():
        print(f"❌ Icon index not found: {icon_index_path}")
        return False
    
    print(f"✓ Icon index exists: {icon_index_path}")
    
    try:
        with open(icon_index_path, 'r') as f:
            index_data = json.load(f)
        
        total_icons = len(index_data.get('icons', {}))
        print(f"✓ Total icons in index: {total_icons}")
        
        # Check for spell icons
        spell_icons = 0
        for key, icon_data in index_data.get('icons', {}).items():
            if icon_data.get('category') == 'spell':
                spell_icons += 1
        
        print(f"✓ Spell icons in index: {spell_icons}")
        
        if spell_icons == 0:
            print("⚠️  No spell icons found in index")
            return False
            
    except Exception as e:
        print(f"❌ Failed to read icon index: {e}")
        return False
    
    return True

def check_ui_mapping(project_root):
    """Check if UI mapping file exists and contains spell data."""
    print("\n" + "=" * 60)
    print("CHECKING UI ICON MAPPING")
    print("=" * 60)
    
    mapping_path = project_root / "TirganachReloaded" / "data" / "ui_icon_mapping.json"
    
    if not mapping_path.exists():
        print(f"❌ UI icon mapping not found: {mapping_path}")
        return False
    
    print(f"✓ UI icon mapping exists: {mapping_path}")
    
    try:
        with open(mapping_path, 'r') as f:
            mapping_data = json.load(f)
        
        # Check item_to_icons section
        item_to_icons = mapping_data.get('item_to_icons', {})
        print(f"✓ Items with icon data: {len(item_to_icons)}")
        
        # Check for spell handles
        spell_handles = 0
        for item_id, icons in item_to_icons.items():
            for icon in icons:
                handle = icon.get('handle', '')
                if handle.startswith('ui_spell_'):
                    spell_handles += 1
        
        print(f"✓ Spell handles found: {spell_handles}")
        
        # Sample check
        if spell_handles > 0:
            print("✓ Spell handles are present in mapping")
        
        # Check detailed mapping
        detailed_mapping = mapping_data.get('detailed_mapping', {})
        print(f"✓ Detailed mappings: {len(detailed_mapping)}")
        
        spell_detailed = 0
        for key, mapping in detailed_mapping.items():
            category = mapping.get('category', '')
            if category == 'spell':
                spell_detailed += 1
        
        print(f"✓ Spell detailed mappings: {spell_detailed}")
        
    except Exception as e:
        print(f"❌ Failed to read UI icon mapping: {e}")
        return False
    
    return True

def check_spell_data(project_root):
    """Check if spell data exists in GameData."""
    print("\n" + "=" * 60)
    print("CHECKING SPELL GAME DATA")
    print("=" * 60)
    
    gamedata_path = project_root / "TirganachReloaded" / "GameData.json"
    
    if not gamedata_path.exists():
        print(f"❌ GameData not found: {gamedata_path}")
        return False
    
    print(f"✓ GameData exists: {gamedata_path}")
    
    try:
        with open(gamedata_path, 'r') as f:
            gamedata = json.load(f)
        
        # Check spell_names table
        spell_names = gamedata.get('spell_names', [])
        print(f"✓ Spell names entries: {len(spell_names)}")
        
        if spell_names:
            # Check first few entries for ui_handle
            spell_with_handles = 0
            for spell in spell_names[:10]:
                if spell.get('spell_ui_handle'):
                    spell_with_handles += 1
            
            print(f"✓ Spells with UI handles (sample): {spell_with_handles}/10")
        
        # Check spells table
        spells = gamedata.get('spells', [])
        print(f"✓ Spell entries: {len(spells)}")
        
    except Exception as e:
        print(f"❌ Failed to read GameData: {e}")
        return False
    
    return True

def main():
    """Main debug function."""
    print("SpellForce GUI Spell Icon Debug Tool")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent.parent
    print(f"Project root: {project_root}")
    print()
    
    # Run all checks
    checks = [
        ("Spell Icon Files", check_spell_icon_files),
        ("Icon Index", check_icon_index),
        ("UI Icon Mapping", check_ui_mapping),
        ("Spell Game Data", check_spell_data),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        result = check_func(project_root)
        results.append((name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("DEBUG SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Checks passed: {passed}/{total}")
    
    for name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    if passed == total:
        print("\n🎉 All checks passed! Spell icons should work.")
        print("   If still not displaying, check GUI code for:")
        print("   - Correct category handling ('spells')")
        print("   - Icon path resolution")
        print("   - Size scaling (should be 64x64 -> 32x32 for table)")
    else:
        print(f"\n⚠️  {total - passed} checks failed.")
        print("   Investigate the failed components above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)