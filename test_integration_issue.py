#!/usr/bin/env python3
"""
Test to identify the specific issue with ITM integration
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_path_resolution():
    """Test the icon path resolution logic"""
    print("🔍 Testing ITM Integration Path Resolution")
    print("=" * 50)
    
    # Check extracted assets
    itm_dir = project_root / "ExtractedAssets" / "UI" / "icons_extracted" / "itm"
    spell_dir = project_root / "ExtractedAssets" / "UI" / "icons_extracted" / "spell"
    
    print(f"ITM directory exists: {itm_dir.exists()}")
    print(f"Spell directory exists: {spell_dir.exists()}")
    
    if itm_dir.exists():
        atlas_dirs = list(itm_dir.glob("atlas_*"))
        print(f"Number of ITM atlas directories: {len(atlas_dirs)}")
        
        # Check for a sample icon
        if atlas_dirs:
            first_atlas = atlas_dirs[0]
            icons = list(first_atlas.glob("icon_*.png"))
            print(f"Icons in first atlas ({first_atlas.name}): {len(icons)}")
            
            if icons:
                print(f"Sample icon: {icons[0].name}")
    
    # Check ITM mapping file
    from cff_editor_itm_integration import CFFEditorITMIntegration
    
    original_path = project_root / "OriginalGameFiles" / "data" / "GameData.cff"
    if original_path.exists():
        print(f"\n🎮 Testing ITM Integration with GameData...")
        integration = CFFEditorITMIntegration(str(original_path), str(original_path))
        
        print(f"Found {len(integration.original_mapper.get_all_itm_mappings())} ITM mappings")
        
        # Test getting an icon path
        mappings = integration.original_mapper.get_all_itm_mappings()
        if mappings:
            sample_mapping = mappings[0]  # Get first mapping
            icon_path = integration.get_icon_path(sample_mapping)
            print(f"Sample mapping: Item {sample_mapping.item_id} -> ITM {sample_mapping.itm_index}")
            print(f"Icon path: {icon_path}")
            print(f"Icon exists: {icon_path.exists() if icon_path else False}")
    else:
        print(f"\n⚠️  Original GameData.cff not found at {original_path}")
        
    # Check the data model integration
    print(f"\n🔍 Testing Data Model Integration...")
    try:
        from src.TirganachReloaded.cff_editor.data_model import CFFDataModel
        model = CFFDataModel()
        
        print(f"Data model initialized successfully")
        print(f"ITM integration available: {model.itm_integration is not None}")
        
        if model.itm_integration:
            print(f"ITM mappings in data model: {len(model.itm_integration.original_mapper.get_all_itm_mappings())}")
            
    except Exception as e:
        print(f"Error initializing data model: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_path_resolution()