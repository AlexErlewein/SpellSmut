#!/usr/bin/env python3
"""
Test quest selection performance and enhanced data display
"""

import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src" / "TirganachReloaded"))

from cff_editor.data_model import CFFDataModel
from cff_editor.services.quest_data_service import QuestDataService

def test_quest_selection_performance():
    """Test performance of quest selection and enhanced data loading"""
    print("Testing Quest Selection Performance")
    print("=" * 50)
    
    # Initialize services
    print("1. Initializing services...")
    start_time = time.time()
    
    data_model = CFFDataModel()
    quest_service = QuestDataService(project_root)
    
    init_time = time.time() - start_time
    print(f"   Initialization time: {init_time:.3f}s")
    
    # Load data
    print("2. Loading quest data...")
    start_time = time.time()
    
    default_file = data_model.get_default_file_path()
    success = data_model.load_file(default_file)
    
    load_time = time.time() - start_time
    print(f"   Data loading time: {load_time:.3f}s")
    
    if not success:
        print("   Failed to load data!")
        return
    
    # Get quests
    quests = data_model.get_elements("quests")
    print(f"   Loaded {len(quests)} quests")
    
    # Test quest selection performance (simulate clicking different quests)
    test_quest_ids = [1, 12, 380]  # Test different quest types
    
    for quest_id in test_quest_ids:
        print(f"\n3. Testing quest {quest_id} selection...")
        
        # Find quest in list
        quest_index = None
        selected_quest = None
        for i, quest in enumerate(quests):
            if getattr(quest, 'quest_id', None) == quest_id:
                quest_index = i
                selected_quest = quest
                break
        
        if not selected_quest:
            print(f"   Quest {quest_id} not found!")
            continue
        
        print(f"   Found quest {quest_id} at index {quest_index}: {getattr(selected_quest, 'name', 'Unknown')}")
        
        # Test enhanced data loading
        start_time = time.time()
        
        # Convert to dict format (same as QuestDetailsViewer)
        cff_data = {
            'name': getattr(selected_quest, 'name', ''),
            'description': getattr(selected_quest, 'description', ''),
            'parent_quest_id': getattr(selected_quest, 'parent_quest_id', 0),
            'order_index': getattr(selected_quest, 'order_index', 0),
            'name_id': getattr(selected_quest, 'name_id', 0),
            'description_id': getattr(selected_quest, 'description_id', 0),
        }
        
        enhanced_data = quest_service.get_enhanced_quest_data(quest_id, cff_data)
        
        enhanced_time = time.time() - start_time
        print(f"   Enhanced data loading time: {enhanced_time:.3f}s")
        print(f"   Enhanced data: {len(enhanced_data.map_locations)} maps, {len(enhanced_data.dialogues)} dialogues")
        
        if enhanced_data.map_locations:
            for loc in enhanced_data.map_locations:
                print(f"     - {loc.code}: {loc.name}")
        
        if enhanced_data.dialogues:
            print(f"   Dialogues: {len(enhanced_data.dialogues)}")
            for i, dlg in enumerate(enhanced_data.dialogues[:3]):  # Show first 3
                print(f"     {i+1}. {dlg.dialogue_type}: {dlg.text[:50]}...")
    
    print(f"\n4. Performance Summary:")
    print(f"   QuestDataService should be fast for repeated selections")
    print(f"   If enhanced data loading is slow, check caching")

if __name__ == "__main__":
    test_quest_selection_performance()