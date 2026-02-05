#!/usr/bin/env python3
"""
Quick Allwissende Almacht Test
==============================

Test the Allwissende Almacht components and ITM integration without launching the full GUI.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_allwissende_almacht_components():
    """Test Allwissende Almacht data loading and ITM integration"""
    print("🧪 Testing Allwissende Almacht Components...")
    
    try:
        from TirganachReloaded.cff_editor.data_model import CFFDataModel
        
        # Create data model
        print("📊 Creating data model...")
        data_model = CFFDataModel()
        
        # Check icon data loading
        print(f"✅ Icon mappings loaded: {len(data_model.icon_mapping):,}")
        print(f"✅ Handle cache size: {len(data_model.handle_cache):,}")
        print(f"✅ Icon index size: {len(data_model.icon_index):,}")
        
        # Test category detection
        categories = set()
        for icon_data in data_model.icon_index.values():
            categories.add(icon_data.get('category', 'unknown'))
        
        print(f"✅ Available categories: {sorted(categories)}")
        
        # Test ITM icon access
        itm_icons = [key for key, data in data_model.icon_index.items() 
                    if data.get('category') == 'itm']
        print(f"✅ ITM icons available: {len(itm_icons):,}")
        
        # Test getting a few ITM icon paths
        if itm_icons:
            sample_itm = itm_icons[:5]
            print("📁 Sample ITM icon paths:")
            for icon_key in sample_itm:
                icon_path = data_model.get_icon_path(icon_key)
                if icon_path:
                    print(f"   {icon_key}: {icon_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing components: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_itm_specific_functionality():
    """Test ITM-specific functionality"""
    print("\n🎮 Testing ITM-Specific Functionality...")
    
    try:
        # Test ITM integration module
        from cff_editor_itm_integration import CFFEditorITMIntegration
        
        original_path = Path("OriginalGameFiles/data/GameData.cff")
        if original_path.exists():
            integration = CFFEditorITMIntegration(str(original_path))
            print(f"✅ ITM integration initialized")
            print(f"✅ ITM mappings found: {len(integration.original_mapper.itm_mappings)}")
            
            # Test specific item
            mapping = integration.original_mapper.get_itm_mapping(2389)
            if mapping:
                icon_path = integration.get_icon_path(mapping)
                print(f"✅ Item 2389 icon: {Path(icon_path).name if icon_path else 'None'}")
        else:
            print("⚠️  GameData.cff not found - skipping ITM integration test")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ITM functionality: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Allwissende Almacht Test Suite")
    print("=" * 50)
    
    success = True
    
    # Test components
    if not test_allwissende_almacht_components():
        success = False
    
    # Test ITM functionality
    if not test_itm_specific_functionality():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Allwissende Almacht is ready for ITM icons!")
        print("📱 Run 'python3 AllwissendeAlmacht/run_allwissende_almacht.py' to launch the GUI")
    else:
        print("❌ Some tests failed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)