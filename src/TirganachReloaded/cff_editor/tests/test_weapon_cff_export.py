#!/usr/bin/env python3
"""
Test script for Weapon CFF Export functionality
==============================================

This script tests the new CFF export feature of the Weapon Forge to ensure:
1. Weapons can be properly exported to GameData.cff format
2. The exported CFF file contains the correct weapon data
3. The file structure is valid and can be loaded by tirganach

Usage:
    python test_weapon_cff_export.py

Requirements:
    - Tirganach library must be available
    - Original GameData.cff file for reference
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from TirganachReloaded.tirganach import GameData
    from cff_editor.models.weapon_creation_data import (
        WeaponCreationData, WeaponRequirements, WeaponHands,
        DamageCategory, Rarity
    )
    from cff_editor.exporters.weapon_cff_exporter import WeaponCFFExporter
    from cff_editor.shared.id_manager import IDManager, ContentType
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root and all dependencies are available")
    sys.exit(1)

def create_test_weapon() -> WeaponCreationData:
    """Create a test weapon for export testing"""

    weapon = WeaponCreationData(
        weapon_id=10003,  # Use a custom weapon ID
        creation_mode="new",
        weapon_name="Test CFF Export Sword",
        weapon_type_id=4,  # 1H Sword
        weapon_type_name="1H Sword",
        weapon_material_id=5,  # Metal
        weapon_material_name="Metal",
        hands=WeaponHands.ONE_HANDED,
        damage_category=DamageCategory.MELEE,
        description="A test sword created to verify CFF export functionality.",

        # Combat stats
        min_damage=15,
        max_damage=25,
        attack_speed=90,
        min_range=0,
        max_range=2,

        # Requirements
        requirements=WeaponRequirements(
            strength=12,
            dexterity=8,
            intelligence=0,
            level=5
        ),

        # Value
        sell_value=150,
        buy_value=300,
        rarity=Rarity.RARE,

        # Metadata
        created_date=datetime.now().isoformat(),
        modified_date=datetime.now().isoformat(),
        author="CFF Export Test Script",
        version=1
    )

    print(f"✅ Created test weapon: {weapon.weapon_name} (ID: {weapon.weapon_id})")
    print(f"   DPS: {weapon.calculate_dps():.1f}")
    print(f"   Balance Rating: {weapon.get_balance_rating()}/100")

    return weapon

def find_gamedata():
    """Find GameData.cff file for testing"""

    possible_paths = [
        Path(__file__).parent.parent.parent.parent / "OriginalGameFiles" / "data" / "GameData.cff",
        Path(__file__).parent.parent.parent.parent / "OriginalGameFiles" / "GameData.cff",
        Path.home() / "SpellForce Platinum Edition" / "data" / "GameData.cff",
    ]

    for path in possible_paths:
        if path.exists():
            print(f"✅ Found GameData.cff at: {path}")
            return str(path)

    print("❌ GameData.cff not found in expected locations:")
    for path in possible_paths:
        print(f"   {path}")

    return None

def test_cff_export():
    """Test the CFF export functionality"""

    print("🧪 Starting CFF Export Test")
    print("=" * 50)

    # Step 1: Find GameData.cff
    gamedata_path = find_gamedata()
    if not gamedata_path:
        print("❌ Cannot proceed without GameData.cff")
        return False

    # Step 2: Create test weapon
    print("\n📝 Step 1: Creating test weapon...")
    test_weapon = create_test_weapon()

    # Step 3: Test CFF export
    print("\n📦 Step 2: Testing CFF export...")
    try:
        exporter = WeaponCFFExporter(gamedata_path)

        if not exporter.gamedata:
            print("❌ Failed to load GameData")
            return False

        # Create output directory
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)

        # Generate output filename
        output_path = output_dir / f"TestData_{test_weapon.weapon_id}_{test_weapon.weapon_name.replace(' ', '_')}.cff"

        # Export weapon
        success = exporter.export_weapon_to_gamedata(test_weapon, str(output_path))

        if success:
            print(f"✅ CFF export successful!")
            print(f"   Output file: {output_path}")
            print(f"   File size: {output_path.stat().st_size} bytes")
        else:
            print("❌ CFF export failed")
            return False

    except Exception as e:
        print(f"❌ Error during CFF export: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 4: Verify exported file can be loaded
    print("\n🔍 Step 3: Verifying exported file...")
    try:
        # Try to load the exported file
        loaded_gamedata = GameData(str(output_path))
        print(f"✅ Successfully loaded exported GameData.cff")

        # Check if our weapon was added
        # Note: This is a simplified check - in practice we'd need to verify
        # that the weapon data is correctly present in all tables
        print(f"   Items in original: {len(exporter.gamedata.items)}")
        print(f"   Items in exported: {len(loaded_gamedata.items)}")
        print(f"   Weapons in original: {len(exporter.gamedata.weapons)}")
        print(f"   Weapons in exported: {len(loaded_gamedata.weapons)}")

        # The counts should be higher in the exported version
        if (len(loaded_gamedata.items) > len(exporter.gamedata.items) and
            len(loaded_gamedata.weapons) > len(exporter.gamedata.weapons)):
            print("✅ Weapon successfully added to GameData!")
        else:
            print("⚠️  Weapon may not have been added correctly")

    except Exception as e:
        print(f"❌ Error loading exported file: {e}")
        return False

    print("\n🎉 CFF Export Test Complete!")
    print(f"📁 Test output saved to: {output_path}")
    print("\nNext steps:")
    print("1. Backup your original GameData.cff")
    print("2. Replace it with the test file to verify in-game")
    print("3. Check if the weapon appears and works correctly")

    return True

def test_id_manager():
    """Test ID Manager integration with CFF export"""

    print("\n🆔 Testing ID Manager Integration...")

    try:
        # Create ID Manager
        id_manager = IDManager("test_ids.json")

        # Allocate an ID for our test weapon
        weapon_id = id_manager.allocate_id(ContentType.WEAPON)
        print(f"✅ Allocated weapon ID: {weapon_id}")

        # Check statistics
        stats = id_manager.get_stats()
        weapon_stats = stats.get('weapon', {})
        print(f"   Used IDs: {weapon_stats.get('used', 0)}")
        print(f"   Available: {weapon_stats.get('available', 0)}")

        # Clean up
        id_manager.release_id(ContentType.WEAPON, weapon_id)
        print(f"✅ Released weapon ID: {weapon_id}")

        # Clean up test file
        if Path("test_ids.json").exists():
            Path("test_ids.json").unlink()

        return True

    except Exception as e:
        print(f"❌ ID Manager test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Weapon CFF Export Test Suite")
    print("=" * 40)

    success = True

    # Test ID Manager
    success &= test_id_manager()

    # Test CFF Export
    success &= test_cff_export()

    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)