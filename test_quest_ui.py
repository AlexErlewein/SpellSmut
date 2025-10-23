#!/usr/bin/env python3
"""
Test script to verify quest UI functionality
"""

import sys
sys.path.append('TirganachReloaded')

from tirganach import GameData

def test_quest_ui():
    """Test quest UI functionality"""
    print("Loading GameData.cff...")

    try:
        gd = GameData('/Users/alex/Desktop/code/Others/SpellSmut/OriginalGameFiles/data/GameData.cff')
        print(f"Successfully loaded game data")
        print(f"Quests table size: {len(gd.quests)}")

        # Test data model category handling
        from TirganachReloaded.cff_editor.data_model import CFFDataModel

        data_model = CFFDataModel()
        data_model.game_data = gd
        data_model.file_path = '/Users/alex/Desktop/code/Others/SpellSmut/OriginalGameFiles/data/GameData.cff'

        # Test getting categories
        categories = data_model.get_categories()
        print(f"Found {len(categories)} categories")

        # Check if quests is in categories
        quest_category = None
        for internal_name, display_name, count in categories:
            if internal_name == "quests":
                quest_category = (internal_name, display_name, count)
                break

        if quest_category:
            print(f"Found quests category: {quest_category}")
        else:
            print("ERROR: Quests category not found!")
            return

        # Test getting quest elements
        quests = data_model.get_elements("quests")
        print(f"Retrieved {len(quests)} quest elements")

        if quests:
            # Test element access
            first_quest = quests[0]
            quest_id = getattr(first_quest, 'quest_id', None)
            name = getattr(first_quest, 'name', 'Unknown')
            print(f"First quest: ID={quest_id}, Name='{name}'")

            # Test quest details widget logic (without GUI)
            from TirganachReloaded.cff_editor.widgets.quest_details import QuestDetailsWidget

            # Create widget instance (without showing it)
            widget = QuestDetailsWidget.__new__(QuestDetailsWidget)
            widget.data_model = data_model

            # Test on_element_selected method
            print("Testing element selection...")
            widget.on_element_selected("quests", 0)  # Select first quest

            if hasattr(widget, 'current_quest') and widget.current_quest:
                print("SUCCESS: Quest details widget received element selection")
                print(f"Current quest: {getattr(widget.current_quest, 'name', 'Unknown')}")
            else:
                print("ERROR: Quest details widget did not receive element selection")

        print("Quest UI test completed!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_quest_ui()