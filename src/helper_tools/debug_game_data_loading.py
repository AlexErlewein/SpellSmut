#!/usr/bin/env python3
"""
Test script to debug GameData.cff loading
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from TirganachReloaded.cff_editor.data_model import CFFDataModel

def test_game_data_loading():
    """Test loading GameData.cff file"""
    print("Testing GameData.cff loading...")
    
    # Initialize data model
    data_model = CFFDataModel()
    
    # Check default file path
    default_path = data_model.get_default_file_path()
    print(f"Default file path: {default_path}")
    print(f"File exists: {Path(default_path).exists()}")
    
    # Load the file
    print("\nLoading GameData.cff...")
    start_time = time.time()
    success = data_model.load_file(default_path)
    load_time = time.time() - start_time
    
    print(f"Load success: {success}")
    print(f"Load time: {load_time:.3f}s")
    
    if success:
        # Test getting quests
        print("\nTesting quest access...")
        start_time = time.time()
        quests = data_model.get_elements("quests")
        quest_time = time.time() - start_time
        
        print(f"Quests found: {len(quests) if quests else 0}")
        print(f"Quest access time: {quest_time:.6f}s")
        
        if quests:
            print("\nFirst few quests:")
            for i, quest in enumerate(quests[:3]):
                quest_id = getattr(quest, "quest_id", None)
                name = getattr(quest, "name", "No name")
                print(f"  {i+1}. Quest {quest_id}: {name}")
        
        # Test other categories
        categories = ["items", "weapons", "armor", "spells"]
        print(f"\nTesting other categories:")
        for category in categories:
            start_time = time.time()
            elements = data_model.get_elements(category)
            cat_time = time.time() - start_time
            print(f"  {category}: {len(elements) if elements else 0} elements ({cat_time:.6f}s)")
    
    return success and (quests is not None and len(quests) > 0)

if __name__ == "__main__":
    success = test_game_data_loading()
    print(f"\n{'✅ GameData loading SUCCESS' if success else '❌ GameData loading FAILED'}")