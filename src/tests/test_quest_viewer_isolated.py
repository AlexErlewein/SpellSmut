#!/usr/bin/env python3
"""
Test QuestDetailsViewer in isolation
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src" / "TirganachReloaded"))

from PySide6.QtWidgets import QApplication
from cff_editor.data_model import CFFDataModel
from cff_editor.widgets.quest_details_viewer import QuestDetailsViewer

def test_quest_details_viewer():
    """Test QuestDetailsViewer with actual quest data"""
    print("Testing QuestDetailsViewer in isolation")
    print("=" * 50)
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Initialize data model
    data_model = CFFDataModel()
    
    # Load default file
    default_file = data_model.get_default_file_path()
    if default_file and Path(default_file).exists():
        print(f"Loading file: {default_file}")
        success = data_model.load_file(default_file)
        print(f"Load success: {success}")
        
        if success:
            # Get quests
            quests = data_model.get_elements("quests")
            print(f"Loaded {len(quests)} quests")
            
            # Create QuestDetailsViewer
            viewer = QuestDetailsViewer(data_model)
            viewer.show()
            
            # Test with a specific quest (quest 380 should have enhanced data)
            # Find quest 380 in the list
            quest_380 = None
            quest_380_index = None
            for i, quest in enumerate(quests):
                if getattr(quest, 'quest_id', None) == 380:
                    quest_380 = quest
                    quest_380_index = i
                    break
            
            if quest_380:
                print(f"Testing with quest 380 at index {quest_380_index}: {getattr(quest_380, 'name', 'Unknown')}")
                
                # Simulate selection
                viewer.on_element_selected("quests", quest_380_index)
                
                print("QuestDetailsViewer should now show enhanced data")
                print("Check the window for map locations and dialogues")
            
            # Run the application
            return app.exec()
    else:
        print(f"Default file not found: {default_file}")
        return 1

if __name__ == "__main__":
    sys.exit(test_quest_details_viewer())