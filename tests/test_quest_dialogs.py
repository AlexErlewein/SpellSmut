#!/usr/bin/env python3
"""
Test script to verify quest dialog functionality
"""

import sys
sys.path.append('TirganachReloaded')

from tirganach import GameData
from tirganach.types import Language

def test_localisation_loading():
    """Test loading localisation table"""
    print("Loading GameData.cff...")

    try:
        gd = GameData('/Users/alex/Desktop/code/Others/SpellSmut/OriginalGameFiles/data/GameData.cff')
        print(f"Successfully loaded game data")
        print(f"Localisation table size: {len(gd.localisation)}")

        # Count dialogues
        dialogues = [loc for loc in gd.localisation if loc.is_dialogue]
        print(f"Total dialogues: {len(dialogues)}")

        # Count English dialogues
        english_dialogues = [loc for loc in dialogues if loc.language == Language.ENGLISH]
        print(f"English dialogues: {len(english_dialogues)}")

        # Show sample English dialogues
        print("\nSample English dialogues:")
        for i, dialogue in enumerate(english_dialogues[:5]):
            print(f"{i+1}. Name: '{dialogue.dialogue_name}', Text: '{dialogue.text[:100]}...'")

        # Test quest keyword search
        quest_keywords = ['quest', 'mission', 'task', 'objective', 'duty', 'assignment']
        quest_related = []

        for dialogue in english_dialogues:
            if dialogue.text:
                text_lower = dialogue.text.lower()
                if any(keyword in text_lower for keyword in quest_keywords):
                    quest_related.append(dialogue)
                    if len(quest_related) >= 10:
                        break

        print(f"\nFound {len(quest_related)} quest-related dialogues:")
        for i, dialogue in enumerate(quest_related[:5]):
            print(f"{i+1}. '{dialogue.dialogue_name}': '{dialogue.text[:150]}...'")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_localisation_loading()