#!/usr/bin/env python3
"""
Test script to verify quest access and details widget functionality
"""

import sys
sys.path.append('TirganachReloaded')

from tirganach import GameData

def test_quest_access():
    """Test accessing quest elements"""
    print("Loading GameData.cff...")

    try:
        gd = GameData('/Users/alex/Desktop/code/Others/SpellSmut/OriginalGameFiles/data/GameData.cff')
        print(f"Successfully loaded game data")
        print(f"Quests table size: {len(gd.quests)}")

        # Test accessing first few quests
        for i in range(min(5, len(gd.quests))):
            quest = gd.quests[i]
            print(f"Quest {i}: ID={getattr(quest, 'quest_id', 'N/A')}, Name='{getattr(quest, 'name', 'N/A')}'")

        # Test quest details widget logic
        print("\nTesting quest details widget logic...")

        # Mock data model
        class MockDataModel:
            def __init__(self, game_data):
                self.game_data = game_data
                self.current_category = "quests"

            def get_elements(self, category):
                if category == "quests":
                    return list(self.game_data.quests)
                elif category == "localisation":
                    return list(self.game_data.localisation)
                return []

        data_model = MockDataModel(gd)

        # Test getting quest elements
        quests = data_model.get_elements("quests")
        print(f"Retrieved {len(quests)} quests from data model")

        if quests:
            # Test quest details access
            first_quest = quests[0]
            quest_id = getattr(first_quest, 'quest_id', None)
            name = getattr(first_quest, 'name', 'Unknown')
            description = getattr(first_quest, 'description', 'No description')

            print(f"First quest: ID={quest_id}, Name='{name}', Description='{description[:100]}...'")

            # Test dialog finding logic
            from TirganachReloaded.cff_editor.widgets.quest_details import QuestDetailsWidget

            # Create a minimal widget instance (without GUI)
            widget = QuestDetailsWidget.__new__(QuestDetailsWidget)
            widget.data_model = data_model

            # Test the dialog finding method
            dialogs = widget.find_quest_dialogs(quest_id)
            print(f"Found {len(dialogs)} dialogs for quest {quest_id}")

            for i, (name, text) in enumerate(dialogs[:3]):
                print(f"  Dialog {i+1}: '{name}' - '{text[:80]}...'")

        print("Quest access test completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_quest_access()