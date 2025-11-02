#!/usr/bin/env python3
"""
Test script to verify enhanced quest view functionality
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def test_quest_data_service():
    """Test QuestDataService initialization and data loading"""
    print("🧪 Testing QuestDataService...")
    
    try:
        from TirganachReloaded.cff_editor.services import QuestDataService
        print("✅ QuestDataService import successful")
        
        # Initialize service
        project_root = Path(__file__).parent
        service = QuestDataService(project_root)
        print("✅ QuestDataService initialized successfully")
        
        # Test getting enhanced data for a known quest
        enhanced_data = service.get_enhanced_quest_data(380, {
            'name': 'Test Quest',
            'description': 'Test Description',
            'parent_quest_id': 0,
            'order_index': 0,
            'name_id': 0,
            'description_id': 0,
        })
        
        if enhanced_data:
            print(f"✅ Enhanced data loaded for quest 380:")
            print(f"   - Map locations: {len(enhanced_data.map_locations)}")
            print(f"   - Dialogues: {len(enhanced_data.dialogues)}")
            print(f"   - Rewards: {enhanced_data.rewards}")
        else:
            print("⚠️  No enhanced data found for quest 380")
            
        return True
        
    except Exception as e:
        print(f"❌ QuestDataService test failed: {e}")
        return False

def test_quest_details_viewer():
    """Test QuestDetailsViewer initialization"""
    print("\n🧪 Testing QuestDetailsViewer...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from TirganachReloaded.cff_editor.data_model import CFFDataModel
        from TirganachReloaded.cff_editor.widgets.quest_details_viewer import QuestDetailsViewer
        
        # Create minimal Qt application
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create data model
        data_model = CFFDataModel()
        print("✅ CFFDataModel created")
        
        # Create quest details viewer
        viewer = QuestDetailsViewer(data_model)
        print("✅ QuestDetailsViewer created")
        
        # Check if it has the enhanced features
        if hasattr(viewer, 'enhanced_quest_data'):
            print("✅ Enhanced quest data attribute present")
        if hasattr(viewer, 'quest_service'):
            print(f"✅ Quest service: {'initialized' if viewer.quest_service else 'not initialized'}")
            
        return True
        
    except Exception as e:
        print(f"❌ QuestDetailsViewer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_model_quest_id():
    """Test that data model properly extracts quest IDs"""
    print("\n🧪 Testing quest ID extraction...")
    
    try:
        from TirganachReloaded.cff_editor.data_model import CFFDataModel
        
        data_model = CFFDataModel()
        
        # Create a mock quest object
        class MockQuest:
            def __init__(self):
                self.quest_id = 380
                self.name = "Test Quest"
                
        mock_quest = MockQuest()
        quest_id = data_model._get_element_id("quests", mock_quest)
        
        if quest_id == 380:
            print("✅ Quest ID extraction working correctly")
            return True
        else:
            print(f"❌ Expected quest ID 380, got {quest_id}")
            return False
            
    except Exception as e:
        print(f"❌ Quest ID extraction test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting enhanced quest view tests...\n")
    
    tests = [
        test_quest_data_service,
        test_quest_details_viewer,
        test_data_model_quest_id,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print(f"\n📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All tests passed! Enhanced quest view should be working.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)