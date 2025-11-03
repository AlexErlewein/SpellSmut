#!/usr/bin/env python3
"""
Check quest indexing
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src" / "TirganachReloaded"))

from cff_editor.data_model import CFFDataModel

def check_quest_indexing():
    """Check how quests are indexed"""
    print("Checking Quest Indexing")
    print("=" * 50)
    
    # Initialize data model
    data_model = CFFDataModel()
    
    # Load default file
    default_file = data_model.get_default_file_path()
    if default_file and Path(default_file).exists():
        success = data_model.load_file(default_file)
        if success:
            quests = data_model.get_elements("quests")
            print(f"Total quests: {len(quests)}")
            
            # Check first few quests
            for i in range(min(5, len(quests))):
                quest = quests[i]
                quest_id = getattr(quest, 'quest_id', None)
                name = getattr(quest, 'name', 'Unknown')
                print(f"Index {i}: quest_id={quest_id}, name={name}")
            
            # Try to find quest 380
            print(f"\nLooking for quest 380:")
            found_380 = None
            for i, quest in enumerate(quests):
                quest_id = getattr(quest, 'quest_id', None)
                if quest_id == 380:
                    found_380 = quest
                    print(f"Found quest 380 at index {i}: {getattr(quest, 'name', 'Unknown')}")
                    break
            
            if not found_380:
                print("Quest 380 not found!")
                # Check what quest IDs we have
                quest_ids = []
                for quest in quests[:50]:  # Check first 50
                    quest_id = getattr(quest, 'quest_id', None)
                    if quest_id:
                        quest_ids.append(quest_id)
                print(f"First 50 quest IDs: {quest_ids}")

if __name__ == "__main__":
    check_quest_indexing()