#!/usr/bin/env python3
"""
Test script to identify quest loading performance bottleneck
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from TirganachReloaded.cff_editor.data_model import CFFDataModel

def test_quest_loading_performance():
    """Test the performance of quest loading steps"""
    print("Testing quest loading performance...")
    
    # Initialize data model
    print("1. Initializing CFFDataModel...")
    start_time = time.time()
    data_model = CFFDataModel()
    init_time = time.time() - start_time
    print(f"   CFFDataModel initialization: {init_time:.3f}s")
    
    # Test get_elements("quests") performance
    print("\n2. Testing get_elements('quests')...")
    start_time = time.time()
    quests = data_model.get_elements("quests")
    get_elements_time = time.time() - start_time
    print(f"   get_elements('quests'): {get_elements_time:.3f}s")
    print(f"   Number of quests: {len(quests) if quests else 0}")
    
    # Test quest hierarchy building
    if quests:
        print("\n3. Testing quest hierarchy building...")
        start_time = time.time()
        
        quest_nodes = {}
        for i, quest in enumerate(quests):
            quest_id = getattr(quest, "quest_id", None)
            if quest_id is not None:
                parent_id = getattr(quest, "parent_quest_id", None)
                order_index = getattr(quest, "order_index", 0)
                
                # Get quest name (try localized first)
                name_start = time.time()
                name = data_model.get_localised_text(quest, "name")
                name_time = time.time() - name_start
                
                if not name:
                    name = getattr(quest, "name", f"Quest {quest_id}")
                
                quest_nodes[quest_id] = {
                    "quest": quest,
                    "quest_id": quest_id,
                    "name": name,
                    "parent_id": parent_id,
                    "order_index": order_index,
                    "children": [],
                    "element_index": i,
                }
                
                if i < 5:  # Show first few name lookup times
                    print(f"     Quest {quest_id} name lookup: {name_time:.6f}s")
        
        hierarchy_time = time.time() - start_time
        print(f"   Quest hierarchy building: {hierarchy_time:.3f}s")
        print(f"   Number of quest nodes: {len(quest_nodes)}")
    
    # Test enhanced quest data loading
    if quests:
        print("\n4. Testing enhanced quest data loading...")
        from TirganachReloaded.cff_editor.services.quest_data_service import QuestDataService
        
        start_time = time.time()
        quest_service = QuestDataService(Path(__file__).parent)
        service_init_time = time.time() - start_time
        print(f"   QuestDataService initialization: {service_init_time:.3f}s")
        
        # Test loading a few quests
        for i, quest in enumerate(quests[:3]):
            quest_id = getattr(quest, "quest_id", None)
            if quest_id:
                start_time = time.time()
                enhanced_data = quest_service.get_enhanced_quest_data(quest_id)
                enhanced_time = time.time() - start_time
                print(f"   Enhanced quest {quest_id}: {enhanced_time:.6f}s")
    
    print(f"\n=== PERFORMANCE SUMMARY ===")
    print(f"CFFDataModel init: {init_time:.3f}s")
    print(f"get_elements('quests'): {get_elements_time:.3f}s")
    if quests:
        print(f"Hierarchy building: {hierarchy_time:.3f}s")
        print(f"QuestDataService init: {service_init_time:.3f}s")
    
    total_time = init_time + get_elements_time
    print(f"Total quest loading time: {total_time:.3f}s")
    
    return total_time < 2.0  # Should be under 2 seconds

if __name__ == "__main__":
    success = test_quest_loading_performance()
    print(f"\n{'✅ Quest loading performance OK' if success else '❌ Quest loading too slow'}")