#!/usr/bin/env python3
"""
Test script to verify quest details logic without GUI
"""

import sys
sys.path.append('TirganachReloaded')

from tirganach import GameData

def test_quest_logic():
    """Test quest details logic without GUI"""
    print("Loading GameData.cff...")

    try:
        gd = GameData('/Users/alex/Desktop/code/Others/SpellSmut/OriginalGameFiles/data/GameData.cff')
        print(f"Successfully loaded game data")
        print(f"Quests table size: {len(gd.quests)}")

        # Test accessing quest elements
        quests = list(gd.quests)
        print(f"Retrieved {len(quests)} quests")

        if quests:
            # Test quest details access
            first_quest = quests[0]
            quest_id = getattr(first_quest, 'quest_id', None)
            name = getattr(first_quest, 'name', 'Unknown')
            description = getattr(first_quest, 'description', 'No description')

            print(f"First quest: ID={quest_id}, Name='{name}', Description='{description[:100]}...'")

            # Test dialog finding logic (copied from quest_details.py)
            def find_quest_dialogs(quest_id):
                """Find dialogs related to a quest"""
                dialogs = []

                try:
                    # Get localisation table elements
                    localisation_table = list(gd.localisation)
                    if not localisation_table:
                        return dialogs

                    # Find dialogs related to this quest
                    quest_id_str = str(quest_id)

                    # Strategy: Show quest-related dialogues by looking for quest keywords in text
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

            # Test the dialog finding method
            dialogs = find_quest_dialogs(quest_id)
            print(f"Found {len(dialogs)} dialogs for quest {quest_id}")

            for i, (name, text) in enumerate(dialogs[:3]):
                print(f"  Dialog {i+1}: '{name}' - '{text[:80]}...'")

        print("Quest logic test completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_quest_logic()