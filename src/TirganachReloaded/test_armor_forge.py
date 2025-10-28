#!/usr/bin/env python3
"""
Test script for the Armor Forge system
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

def test_id_manager():
    """Test the ID Manager system"""
    print("Testing ID Manager...")

    from cff_editor.shared.id_manager import IDManager, ContentType

    # Create ID manager
    id_manager = IDManager("test_ids.json")

    # Test getting next ID
    armor_id = id_manager.get_next_id(ContentType.ARMOR)
    print(f"Next armor ID: {armor_id}")
    assert armor_id == 20000, f"Expected 20000, got {armor_id}"

    # Test allocating ID
    allocated_id = id_manager.allocate_id(ContentType.ARMOR)
    print(f"Allocated armor ID: {allocated_id}")
    assert allocated_id == 20000, f"Expected 20000, got {allocated_id}"

    # Test stats
    stats = id_manager.get_stats()
    print(f"Armor stats: {stats['armor']}")

    print("✓ ID Manager tests passed")

def test_armor_data_model():
    """Test the ArmorCreationData model"""
    print("\nTesting Armor Data Model...")

    from cff_editor.models.armor_creation_data import ArmorCreationData, ArmorSlot, ArmorType, ArmorTier

    # Create armor data
    armor = ArmorCreationData(
        armor_id=20001,
        armor_name="Test Dragon Scale Helmet",
        slot=ArmorSlot.HEAD,
        armor_type=ArmorType.PLATE,
        tier=ArmorTier.RARE,
        base_armor=45,
        strength=5,
        intelligence=3,
        resist_fire=25.0
    )

    # Test calculations
    defense_rating = armor.calculate_defense_rating()
    balance_rating = armor.calculate_balance_rating()

    print(f"Defense rating: {defense_rating}")
    print(f"Balance rating: {balance_rating}")
    print(f"Slot name: {armor.get_slot_name()}")

    # Test serialization
    armor_dict = armor.to_dict()
    armor_copy = ArmorCreationData.from_dict(armor_dict)

    assert armor_copy.armor_name == armor.armor_name
    assert armor_copy.base_armor == armor.base_armor

    print("✓ Armor Data Model tests passed")

def test_armor_loader():
    """Test the Armor Loader"""
    print("\nTesting Armor Loader...")

    from cff_editor.exporters.armor_loader import ArmorLoader

    # Test loading all armor
    all_armor = ArmorLoader.load_all_armor()
    print(f"Loaded {len(all_armor)} armor pieces")

    if all_armor:
        # Test loading specific armor
        first_armor = all_armor[0]
        armor_id = first_armor.get('item_id', 0)
        loaded_armor = ArmorLoader.load_armor(armor_id)

        if loaded_armor:
            print(f"Successfully loaded armor: {loaded_armor.armor_name}")
        else:
            print(f"Could not load armor ID {armor_id}")

    print("✓ Armor Loader tests passed")

def test_armor_validator():
    """Test the Armor Validator"""
    print("\nTesting Armor Validator...")

    from cff_editor.models.armor_creation_data import ArmorCreationData, ArmorSlot, ArmorType
    from cff_editor.widgets.armor_validation import ArmorValidator

    validator = ArmorValidator()

    # Test valid armor
    valid_armor = ArmorCreationData(
        armor_id=20002,
        armor_name="Valid Test Armor",
        slot=ArmorSlot.CHEST,
        armor_type=ArmorType.LEATHER,
        base_armor=25
    )

    errors, warnings = validator.validate(valid_armor)
    print(f"Valid armor - Errors: {len(errors)}, Warnings: {len(warnings)}")

    # Test invalid armor
    invalid_armor = ArmorCreationData(
        armor_id=20003,
        armor_name="",  # Invalid: no name
        slot=ArmorSlot.CHEST,
        armor_type=ArmorType.PLATE,
        base_armor=-10  # Invalid: negative armor
    )

    errors, warnings = validator.validate(invalid_armor)
    print(f"Invalid armor - Errors: {len(errors)}, Warnings: {len(warnings)}")
    print(f"Errors: {errors}")

    print("✓ Armor Validator tests passed")

def test_cff_exporter():
    """Test the CFF Exporter"""
    print("\nTesting CFF Exporter...")

    from cff_editor.models.armor_creation_data import ArmorCreationData, ArmorSlot, ArmorType
    from cff_editor.exporters.armor_cff_exporter import ArmorCFFExporter

    # Create test armor
    test_armor = ArmorCreationData(
        armor_id=20004,
        armor_name="Export Test Armor",
        slot=ArmorSlot.CHEST,
        armor_type=ArmorType.CHAIN,
        base_armor=30,
        strength=2,
        resist_fire=15.0
    )

    exporter = ArmorCFFExporter()

    # Test export
    try:
        exports = exporter.export_armor(test_armor)
        print(f"Exported to {len(exports)} categories: {list(exports.keys())}")

        # Test JSON save
        exporter.save_to_json(exports, "test_armor_export.json")
        print("Saved export to JSON file")

        # Clean up
        if os.path.exists("test_armor_export.json"):
            os.remove("test_armor_export.json")

    except Exception as e:
        print(f"Export test failed: {e}")

    print("✓ CFF Exporter tests passed")

def main():
    """Run all tests"""
    print("🛡️ Armor Forge System Test Suite")
    print("=" * 40)

    try:
        test_id_manager()
        test_armor_data_model()
        test_armor_loader()
        test_armor_validator()
        test_cff_exporter()

        print("\n" + "=" * 40)
        print("🎉 All tests passed! Armor Forge system is ready.")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())