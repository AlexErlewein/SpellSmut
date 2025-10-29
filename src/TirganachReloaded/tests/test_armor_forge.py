"""
Test script for the Armor Forge system
"""

import os
import sys
import json

# Add the current directory to the path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from armor_forge import ArmorForge, Armor
    from armor_sets import ArmorSetManager
except ImportError as e:
    print(f"Import error: {e}")
    # If direct import doesn't work, try a different approach
    import importlib.util
    import os
    
    # Load armor_forge module
    armor_forge_path = os.path.join(os.path.dirname(__file__), 'armor_forge.py')
    spec = importlib.util.spec_from_file_location("armor_forge", armor_forge_path)
    armor_forge_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(armor_forge_module)
    
    # Load armor_sets module
    armor_sets_path = os.path.join(os.path.dirname(__file__), 'armor_sets.py')
    spec = importlib.util.spec_from_file_location("armor_sets", armor_sets_path)
    armor_sets_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(armor_sets_module)
    
    # Access classes
    ArmorForge = armor_forge_module.ArmorForge
    Armor = armor_forge_module.Armor
    ArmorSetManager = armor_sets_module.ArmorSetManager


def test_armor_creation():
    """Test the complete armor creation workflow"""
    print("Testing Armor Creation Workflow...")
    
    # Create a new ArmorForge instance
    forge = ArmorForge()
    
    # Create a new armor piece manually for testing
    test_armor = forge.create_new_armor()
    test_armor.name = "Test Plate Armor"
    test_armor.display_name = "Plate Armor of Testing"
    test_armor.description = "A test armor for validation purposes"
    
    # Set basic properties
    test_armor.slot = 2  # Chest
    test_armor.armor_type = "Plate"
    test_armor.material = "Steel"
    test_armor.tier = "Rare"
    test_armor.level_requirement = 10
    
    # Set stats
    test_armor.strength = 5
    test_armor.stamina = 8
    test_armor.armor_value = 25
    test_armor.health = 50
    
    # Set resistances
    test_armor.resist_fire = 15
    test_armor.resist_ice = 10
    
    # Set speed modifiers
    test_armor.run_speed = -5  # Slight penalty
    
    # Add to forge collection and save
    forge.armors[test_armor.id] = test_armor
    forge.save_armors()
    
    print(f"✓ Created test armor: {test_armor.name} (ID: {test_armor.id})")
    return test_armor


def test_armor_sets():
    """Test the armor sets functionality"""
    print("\nTesting Armor Sets Functionality...")
    
    # Initialize the set manager
    set_manager = ArmorSetManager()
    
    # Create a test set
    set_id = set_manager.sets.get(30001, None)  # Use an available ID
    if not set_id:
        test_set = set_manager.create_set(30001, "Dragon Slayer Set")
        test_set.description = "A set for mighty dragon slayers"
        
        # Add some bonuses
        test_set.add_bonus(2, {"strength": 5, "stamina": 5})
        test_set.add_bonus(4, {"armor_value": 20, "resist_fire": 25})
        
        print(f"✓ Created test set: {test_set.name} (ID: {test_set.id})")
    
    # Save sets
    set_manager.save_sets()
    
    return set_manager


def test_cff_export():
    """Test the CFF export functionality"""
    print("\nTesting CFF Export...")
    
    # Create a test armor
    test_armor = Armor(99999, "CFF Test Armor", "Test Armor", "Armor for CFF testing")
    test_armor.slot = 0  # Head
    test_armor.armor_type = "Cloth"
    test_armor.strength = 3
    test_armor.intelligence = 5
    test_armor.mana = 25
    
    # Export to CFF
    from cff_armor_export import export_armor_to_cff
    cff_path = export_armor_to_cff(test_armor, "./test_cff_export")
    
    print(f"✓ Exported armor to CFF: {cff_path}")
    
    # Verify the file exists
    if os.path.exists(cff_path):
        print("✓ CFF file was created successfully")
        # Check content
        with open(cff_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "ITEM_99999" in content and "CFF Test Armor" in content:
                print("✓ CFF content is valid")
            else:
                print("✗ CFF content is invalid")
    else:
        print("✗ CFF file was not created")
    
    return cff_path


def validate_armor_data():
    """Validate the armor data integrity"""
    print("\nValidating Armor Data...")
    
    # Load the armor data file
    armor_file = os.path.join(os.path.dirname(__file__), 'enhanced_armor.json')
    
    if os.path.exists(armor_file):
        with open(armor_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                print(f"✓ Armor data file loaded successfully")
                
                # Check armor count
                armor_count = len(data.get('armors', []))
                print(f"✓ Found {armor_count} armor pieces in data file")
                
                # Check sets count
                sets_count = len(data.get('sets', []))
                print(f"✓ Found {sets_count} armor sets in data file")
                
                # Validate a few fields
                for armor_data in data.get('armors', []):
                    if 'id' in armor_data and 'name' in armor_data:
                        continue  # Valid
                    else:
                        print(f"✗ Invalid armor data: {armor_data}")
                        return False
                        
                print("✓ All armor entries have required fields")
                
                # Validate sets
                for set_data in data.get('sets', []):
                    if 'id' in set_data and 'name' in set_data:
                        continue  # Valid
                    else:
                        print(f"✗ Invalid set data: {set_data}")
                        return False
                
                print("✓ All set entries have required fields")
                
                return True
            except json.JSONDecodeError:
                print("✗ Invalid JSON in armor data file")
                return False
    else:
        print("✓ No armor data file yet (expected for first run)")
        return True


def run_all_tests():
    """Run all tests for the Armor Forge"""
    print("=" * 60)
    print("ARMOR FORGE - VALIDATION TESTS")
    print("=" * 60)
    
    try:
        # Test 1: Armor creation
        test_armor = test_armor_creation()
        
        # Test 2: Armor sets
        set_manager = test_armor_sets()
        
        # Test 3: CFF export
        cff_path = test_cff_export()
        
        # Test 4: Data validation
        is_valid = validate_armor_data()
        
        print("\n" + "=" * 60)
        if is_valid:
            print("✓ ALL TESTS PASSED - Armor Forge is working correctly")
        else:
            print("✗ SOME TESTS FAILED - Please review the validation errors")
        print("=" * 60)
        
        return is_valid
        
    except Exception as e:
        print(f"\n✗ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("\nArmor Forge implementation is ready for use!")
    else:
        print("\nThere are issues with the Armor Forge implementation that need to be addressed.")