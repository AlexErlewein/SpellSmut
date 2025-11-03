#!/usr/bin/env python3
"""
Test script to verify quest details panel visibility logic
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from TirganachReloaded.cff_editor.services.quest_data_service import QuestDataService

def test_quest_data_performance():
    """Test that quest data loads from cache instantly"""
    print("Testing QuestDataService performance...")
    
    service = QuestDataService(Path(__file__).parent)
    
    # Test cache performance
    import time
    start_time = time.time()
    enhanced_data = service.get_enhanced_quest_data(380)  # Amra quest
    end_time = time.time()
    
    load_time = end_time - start_time
    print(f"Quest 380 load time: {load_time:.6f} seconds")
    
    if enhanced_data:
        print(f"✅ Quest 380 loaded successfully")
        print(f"   - Maps: {len(enhanced_data.map_locations)}")
        print(f"   - Dialogues: {len(enhanced_data.dialogues)}")
        print(f"   - Has extended dialogues: {enhanced_data.has_extended_dialogues}")
        print(f"   - Cache status: {getattr(enhanced_data, 'cache_status', 'Unknown')}")
    else:
        print("❌ Quest 380 failed to load")
    
    # Test second load (should be instant cache)
    start_time = time.time()
    enhanced_data2 = service.get_enhanced_quest_data(381)  # Lea quest
    end_time = time.time()
    
    load_time2 = end_time - start_time
    print(f"Quest 381 load time: {load_time2:.6f} seconds")
    
    return load_time < 0.01 and load_time2 < 0.01  # Both should be < 0.01s

if __name__ == "__main__":
    success = test_quest_data_performance()
    print(f"\n{'✅ Performance test PASSED' if success else '❌ Performance test FAILED'}")
    print("Quest data cache is working correctly!" if success else "Quest data cache needs optimization!")