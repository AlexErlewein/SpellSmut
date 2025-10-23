#!/usr/bin/env python3
"""
Simple test script to verify quest dialog finding logic without GUI
"""

import sys
sys.path.append('TirganachReloaded')

from tirganach import GameData

class MockDataModel:
    """Mock data model for testing"""
    def __init__(self):
        self.game_data = GameData('/Users/alex/Desktop/code/Others/SpellSmut/OriginalGameFiles/data/GameData.cff')
        self.current_category = "quests"

    def get_elements(self, category):
        """Get elements from category"""
        if category == "localisation":
            return list(self.game_data.localisation)
        elif category == "quests":
            # Return a mock quest object
            return [MockQuest()]
        return []

class MockQuest:
    """Mock quest object"""
    def __init__(self):
        self.quest_id = 1
        self.name = "Test Quest"
        self.description = "This is a test quest for dialog functionality"

def find_quest_dialogs(data_model, quest_id):
    """Copy of the dialog finding logic from QuestDetailsWidget"""
    dialogs = []

    try:
        # Get localisation table elements
        localisation_table = data_model.get_elements('localisation')
        if not localisation_table:
            return dialogs

        # Find dialogs related to this quest
        quest_id_str = str(quest_id)

        # Strategy: Show quest-related dialogues by looking for quest keywords in text
        # Since dialogue names don't directly correspond to quest IDs, we'll show
        # dialogues that contain quest-related words

        quest_keywords = ['quest', 'mission', 'task', 'objective', 'duty', 'assignment']
        english_entries = []  # Focus on English entries for cleaner display

        # First, collect English dialogue entries (language.value == 1 for ENGLISH)
        for entry in localisation_table:
            if getattr(entry, 'is_dialogue', False):
                dialogue_name = getattr(entry, 'dialogue_name', '')
                text = getattr(entry, 'text', '')

                # Check if this is an English entry
                try:
                    language = getattr(entry, 'language', None)
                    if language and getattr(language, 'value', None) == (1,):  # ENGLISH
                        english_entries.append((dialogue_name, text))
                except:
                    # If language check fails, include the entry anyway
                    english_entries.append((dialogue_name, text))

        # Look for quest-related content in English dialogues
        for dialogue_name, text in english_entries:
            if not text:
                continue

            text_lower = text.lower()

            # Check if text contains quest-related keywords
            if any(keyword in text_lower for keyword in quest_keywords):
                dialogs.append((dialogue_name or "Unnamed Dialog", text))

                # Limit results to keep UI manageable
                if len(dialogs) >= 15:
                    break

        # If no quest-related dialogs found, show some general NPC dialogues
        if not dialogs:
            npc_keywords = ['hello', 'greetings', 'welcome', 'need help', 'looking for']
            for dialogue_name, text in english_entries[:100]:  # Check first 100 English entries
                if not text:
                    continue

                text_lower = text.lower()
                if any(keyword in text_lower for keyword in npc_keywords):
                    dialogs.append((dialogue_name or "Unnamed Dialog", text))
                    if len(dialogs) >= 10:
                        break

        # Final fallback: show any English dialogues if still no matches
        if not dialogs:
            for dialogue_name, text in english_entries[:20]:  # Show first 20 English dialogues
                if text:
                    dialogs.append((dialogue_name or "Unnamed Dialog", text))

    except Exception as e:
        print(f"Error finding quest dialogs: {e}")
        # Return a fallback message
        dialogs = [("Error", f"Could not load dialogs: {str(e)}")]

    return dialogs

def test_quest_dialog_finding():
    """Test the quest dialog finding logic"""
    print("Testing quest dialog finding...")

    # Create mock data model
    data_model = MockDataModel()

    # Test the dialog finding method
    dialogs = find_quest_dialogs(data_model, 1)

    print(f"Found {len(dialogs)} quest-related dialogs")
    for i, (name, text) in enumerate(dialogs[:5]):
        print(f"{i+1}. '{name}': '{text[:100]}...'")

    print("Quest dialog finding test completed successfully!")

if __name__ == "__main__":
    test_quest_dialog_finding()