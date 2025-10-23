#!/usr/bin/env python3
"""
Test script to check if QuestDetailsWidget can be created without errors
"""

import sys
sys.path.append('TirganachReloaded')

from PySide6.QtWidgets import QApplication
from tirganach import GameData

class MockDataModel:
    """Mock data model for testing"""
    def __init__(self):
        self.game_data = GameData('/Users/alex/Desktop/code/Others/SpellSmut/OriginalGameFiles/data/GameData.cff')
        self.current_category = "quests"

        # Mock signals (just dummy objects)
        self.category_changed = MockSignal()
        self.element_selected = MockSignal()

    def get_elements(self, category):
        """Get elements from category"""
        if category == "localisation":
            return list(self.game_data.localisation)
        elif category == "quests":
            # Return a mock quest object
            return [MockQuest()]
        return []

class MockSignal:
    """Mock signal for testing"""
    def connect(self, func):
        pass

class MockQuest:
    """Mock quest object"""
    def __init__(self):
        self.quest_id = 1
        self.name = "Test Quest"
        self.description = "This is a test quest for dialog functionality"

def test_widget_creation():
    """Test creating the QuestDetailsWidget"""
    print("Testing QuestDetailsWidget creation...")

    # Create QApplication
    app = QApplication(sys.argv)

    try:
        # Create mock data model
        data_model = MockDataModel()

        # Import the quest details widget
        from TirganachReloaded.cff_editor.widgets.quest_details import QuestDetailsWidget

        # Create widget
        widget = QuestDetailsWidget(data_model)
        print("✓ QuestDetailsWidget created successfully")

        # Check if UI attributes exist
        ui_attrs = ['quest_id_label', 'quest_name_label', 'description_text', 'dialogs_tree', 'hierarchy_tree']
        for attr in ui_attrs:
            if hasattr(widget, attr):
                print(f"✓ Attribute {attr} exists")
            else:
                print(f"✗ Attribute {attr} missing")

        # Test updating quest details
        widget.update_quest_details()
        print("✓ update_quest_details() called successfully")

        print("QuestDetailsWidget creation test completed successfully!")

    except Exception as e:
        print(f"✗ Error creating QuestDetailsWidget: {e}")
        import traceback
        traceback.print_exc()

    finally:
        app.quit()

if __name__ == "__main__":
    test_widget_creation()