#!/usr/bin/env python3
"""
Test Quest Viewer App (Non-GUI)
Tests the quest viewer functionality without launching GUI
"""

import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.cff_editor.logging_config import configure_logging, get_logger
from TirganachReloaded.cff_editor.services.quest_data_service import QuestDataService
from TirganachReloaded.cff_editor.lua_parser.lua_data_manager import LuaDataManager

def test_quest_services():
    """Test quest data services initialization"""
    print("Testing Quest Viewer Services...")
    
    # Configure logging
    configure_logging(project_root=project_root)
    logger = get_logger("quest_test")
    
    try:
        # Test Lua data manager
        print("\n1. Testing Lua Data Manager...")
        cache_dir = project_root / "src" / "TirganachReloaded" / "data" / "cache"
        lua_manager = LuaDataManager(cache_dir=cache_dir)
        print(f"   ✓ Lua manager initialized")
        print(f"   ✓ Cache directory: {cache_dir}")
        print(f"   ✓ Cache loaded: {lua_manager.cache_loaded}")
        
        # Test quest data service
        print("\n2. Testing Quest Data Service...")
        quest_service = QuestDataService(project_root=project_root, use_cache=True)
        print(f"   ✓ Quest service initialized")
        
        # Try to get quest data
        print("\n3. Testing Quest Data Access...")
        quests = quest_service.get_all_quests()
        print(f"   ✓ Found {len(quests)} quests")
        
        if quests:
            # Show first few quest IDs
            quest_ids = sorted(quests.keys())[:5]
            print(f"   ✓ Sample quest IDs: {quest_ids}")
            
            # Try to get details for first quest
            first_quest_id = quest_ids[0]
            quest_data = quest_service.get_quest(first_quest_id)
            if quest_data:
                print(f"   ✓ Quest {first_quest_id}: {quest_data.name}")
            else:
                print(f"   ⚠ No details available for quest {first_quest_id}")
        
        print("\n✅ Quest services test completed successfully!")
        return True
        
    except Exception as e:
        logger.exception(f"Test failed: {e}")
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_quest_services()
    sys.exit(0 if success else 1)