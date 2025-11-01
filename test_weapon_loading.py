#!/usr/bin/env python3
"""
Test script to demonstrate improved weapon loading functionality
"""
import sys
from pathlib import Path

# Add path to import our modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

def test_weapon_loading():
    """Test loading weapons from GameData.cff with full stats"""
    
    print("=== Weapon Loading Test ===\n")
    
    try:
        from TirganachReloaded.cff_editor.exporters.weapon_loader import WeaponLoader
        
        # Test loading a few known weapons
        test_weapon_ids = [28, 27, 31]  # Flameblade Sword, Flameblade Dagger, Moonshade
        
        gamedata_path = "OriginalGameFiles/data/GameData.cff"
        
        for weapon_id in test_weapon_ids:
            print(f"Loading weapon ID {weapon_id}...")
            weapon = WeaponLoader.load_weapon(weapon_id, gamedata_path)
            
            print(f"✓ {weapon.weapon_name}")
            print(f"  ID: {weapon.weapon_id}")
            print(f"  Damage: {weapon.min_damage}-{weapon.max_damage}")
            print(f"  Speed: {weapon.attack_speed}")
            print(f"  Range: {weapon.min_range}-{weapon.max_range}")
            print(f"  Type: {weapon.weapon_type_name}")
            print(f"  Material: {weapon.weapon_material_name}")
            print(f"  Hands: {weapon.hands.value}")
            print(f"  Category: {weapon.damage_category.value}")
            print(f"  Damage Type: {weapon.damage_type.value}")
            print(f"  Value: {weapon.sell_value}/{weapon.buy_value}")
            print(f"  Icon Handle: {weapon.icon_handle}")
            print()
        
        print("=== Test completed successfully! ===")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_handles():
    """Test if we can find UI handles for weapons"""
    
    print("=== UI Handle Test ===\n")
    
    try:
        from TirganachReloaded.tirganach import GameData
        
        gd = GameData("OriginalGameFiles/data/GameData.cff")
        weapons = gd.weapons
        item_ui = gd.item_ui
        
        # Count weapons with UI handles
        weapons_with_ui = 0
        sample_weapons = []
        
        for weapon in weapons[:50]:  # Check first 50
            ui_matches = [ui for ui in item_ui if ui.item_id == weapon.item_id]
            if ui_matches and ui_matches[0].item_ui_handle:
                handle = ui_matches[0].item_ui_handle.strip()
                if handle and 'weapon' in handle.lower():
                    weapons_with_ui += 1
                    if len(sample_weapons) < 5:
                        sample_weapons.append((weapon.item_id, weapon.item.name if weapon.item else f"Weapon {weapon.item_id}", handle))
        
        print(f"Found {weapons_with_ui} weapons with UI handles in first 50")
        print("\nSample weapons with UI handles:")
        for weapon_id, name, handle in sample_weapons:
            print(f"  ID {weapon_id}: {name} -> {handle}")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ UI handle test failed: {e}")
        return False

if __name__ == "__main__":
    success1 = test_weapon_loading()
    success2 = test_ui_handles()
    
    if success1 and success2:
        print("🎉 All tests passed! Weapon loading is working with full stats and UI handles.")
    else:
        print("❌ Some tests failed.")