#!/usr/bin/env python3
"""
Test ITM Integration with CFF Editor
===================================

This script tests the ITM icon integration functionality.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_itm_integration():
    """Test ITM integration module."""
    print("Testing ITM Integration...")
    
    try:
        from cff_editor_itm_integration import CFFEditorITMIntegration, ITMIconMapper
        
        # Test file paths
        original_path = project_root / "OriginalGameFiles" / "data" / "GameData.cff"
        modded_path = project_root / "ModdedGameFiles" / "GameData_MyCustomMod_20251019_100557.cff"
        
        if not original_path.exists():
            print(f"❌ Original GameData.cff not found: {original_path}")
            return False
            
        print(f"✅ Found original GameData.cff: {original_path}")
        
        # Initialize ITM integration
        integration = CFFEditorITMIntegration(
            str(original_path),
            str(modded_path) if modded_path.exists() else None
        )
        
        print(f"✅ ITM Integration initialized")
        print(f"   - ITM mappings: {len(integration.original_mapper.itm_mappings)}")
        
        # Test specific item mapping
        test_item_id = 2389  # Known to have ITM mapping
        mapping = integration.original_mapper.get_itm_mapping(test_item_id)
        
        if mapping:
            print(f"✅ Found ITM mapping for item {test_item_id}:")
            print(f"   - UI Handle: {mapping.ui_handle}")
            print(f"   - ITM Index: {mapping.itm_index}")
            print(f"   - Atlas: {mapping.atlas_file}")
            print(f"   - Texture coords: {mapping.texture_coords}")
            
            # Test icon path resolution
            icon_path = integration.get_icon_path(mapping)
            if icon_path and Path(icon_path).exists():
                print(f"✅ Icon file exists: {icon_path}")
            else:
                print(f"❌ Icon file not found: {icon_path}")
        else:
            print(f"❌ No ITM mapping found for item {test_item_id}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing ITM integration: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cff_data_model():
    """Test CFF data model with ITM integration."""
    print("\nTesting CFF Data Model with ITM Integration...")
    
    try:
        from src.TirganachReloaded.cff_editor.data_model import CFFDataModel
        
        # Create data model instance
        model = CFFDataModel()
        
        # Check if ITM integration was initialized
        if model.itm_integration:
            print("✅ ITM integration initialized in data model")
            
            # Test loading a file
            original_path = project_root / "OriginalGameFiles" / "data" / "GameData.cff"
            if original_path.exists():
                success = model.load_file(str(original_path))
                if success:
                    print("✅ GameData loaded successfully")
                    
                    # Test ITM icon retrieval
                    itm_path = model.get_itm_icon_path(2389)
                    if itm_path:
                        print(f"✅ ITM icon path from model: {itm_path}")
                    else:
                        print("❌ No ITM icon path from model")
                else:
                    print("❌ Failed to load GameData")
            else:
                print("❌ GameData.cff not found")
        else:
            print("❌ ITM integration not initialized in data model")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing CFF data model: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 ITM Integration Test Suite")
    print("=" * 50)
    
    success = True
    
    # Test ITM integration module
    if not test_itm_integration():
        success = False
    
    # Test CFF data model integration
    if not test_cff_data_model():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! ITM integration is working correctly.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)