#!/usr/bin/env python3
"""
Test script to verify quest details widget functionality
"""

import sys
sys.path.append('TirganachReloaded')

from tirganach import GameData
from tirganach.types import Language

class MockSignal:
    """Mock signal for testing"""
    def connect(self, func):
        pass
    def emit(self, *args):
        pass

class MockDataModel:
    """Mock data model for testing"""
    def __init__(self):
        self.game_data = GameData('/Users/alex/Desktop/code/Others/SpellSmut/OriginalGameFiles/data/GameData.cff')
        self.current_category = "quests"
        self.current_language = Language.ENGLISH

        # Mock signals
        self.category_changed = MockSignal()
        self.element_selected = MockSignal()
        self.language_changed = MockSignal()

    def get_elements(self, category):
        """Get elements from category"""
        if category == "localisation":
            return list(self.game_data.localisation)
        elif category == "quests":
            # Return a mock quest object
            return [MockQuest()]
        return []

    def get_current_language(self):
        """Get current language"""
        return self.current_language

class MockQuest:
    """Mock quest object"""
    def __init__(self):
        self.quest_id = 1
        self.name = "Test Quest"
        self.description = "This is a test quest for dialog functionality"

def test_quest_dialog_finding():
    """Test the quest dialog finding logic"""
    print("Testing quest dialog finding...")

    # Create mock data model
    data_model = MockDataModel()

    # Import the quest details widget
    from TirganachReloaded.cff_editor.widgets.quest_details import QuestDetailsWidget

    # Create widget (without showing it)
    widget = QuestDetailsWidget(data_model)

    # Test the dialog finding method
    dialogs = widget.find_quest_dialogs(1)

    print(f"Found {len(dialogs)} quest-related dialogs")
    for i, (name, text) in enumerate(dialogs[:5]):
        print(f"{i+1}. '{name}': '{text[:100]}...'")

    print("Quest dialog finding test completed successfully!")

if __name__ == "__main__":
    test_quest_dialog_finding()