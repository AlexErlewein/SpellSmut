#!/usr/bin/env python3
"""
Test script to verify spell icon loading in the data model.
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "TirganachReloaded"))

from cff_editor.data_model import CFFDataModel
from tirganach import GameData

def test_spell_icon_loading():
    """Test that spell icons can be loaded correctly."""
    print("Testing Spell Icon Loading")
    print("=" * 50)
    
    # Initialize data model
    data_model = CFFDataModel()
    
    # Load GameData directly
    gamedata_path = project_root / "TirganachReloaded" / "GameData.json"
    if not gamedata_path.exists():
        print(f"❌ GameData not found: {gamedata_path}")
        return False
    
    print(f"✓ Loading GameData from: {gamedata_path}")
    
    try:
        game_data = GameData(str(gamedata_path))
        data_model.game_data = game_data
        print("✓ GameData loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load GameData: {e}")
        return False
    
    # Check available categories
    categories = data_model.get_categories()
    spell_categories = [cat for cat in categories if 'spell' in cat[0].lower()]
    print(f"\nSpell-related categories found:")
    for cat in spell_categories:
        print(f"  {cat[0]}: {cat[2]} entries")
    
    # Look for spell data
    spells_table = data_model.get_table("spells")
    if not spells_table:
        print("❌ No 'spells' table found")
        return False
    
    print(f"\n✓ Found 'spells' table with {len(spells_table)} entries")
    
    # Try to find a few spell entries to test
    test_spells = []
    for i, spell in enumerate(spells_table[:5]):  # Test first 5
        spell_id = getattr(spell, "spell_id", None)
        if spell_id is not None:
            test_spells.append((spell_id, spell))
    
    print(f"\nTesting icon loading for {len(test_spells)} spells:")
    
    success_count = 0
    for spell_id, spell in test_spells:
        print(f"  Spell ID {spell_id}:")
        
        # Try to get icon path
        icon_path = data_model.get_icon_path("spells", spell)
        if icon_path:
            print(f"    ✓ Icon path found: {icon_path}")
            success_count += 1
        else:
            print(f"    ❌ No icon path found")
            
            # Debug: Check spell entry
            spell_entry = data_model._find_spell_entry(spell_id)
            if spell_entry:
                print(f"      Spell entry: {spell_entry}")
                handle = spell_entry.get("spell_ui_handle", "")
                if handle:
                    print(f"      UI Handle: {handle}")
                    
                    # Try direct resolution
                    resolved_path = data_model._resolve_icon_path(handle, "spells")
                    if resolved_path:
                        print(f"      Resolved path: {resolved_path}")
                    else:
                        print(f"      ❌ Could not resolve handle")
                else:
                    print(f"      ❌ No UI handle in spell entry")
            else:
                print(f"      ❌ Could not find spell entry")
    
    print(f"\nResults: {success_count}/{len(test_spells)} spell icons successfully located")
    
    return success_count > 0

def main():
    """Main test function."""
    success = test_spell_icon_loading()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)