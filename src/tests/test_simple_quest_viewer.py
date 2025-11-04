#!/usr/bin/env python3
"""
Test Standalone Quest Viewer Data Loading
Tests data loading without GUI for quest_viewer_standalone.py
"""

import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.cff_editor.logging_config import configure_logging, get_logger
from TirganachReloaded.cff_editor.lua_parser.lua_data_manager import LuaDataManager


def test_data_loading():
    """Test quest data loading"""
    print("Testing Quest Data Loading...")

    # Configure logging
    configure_logging()
    logger = get_logger("quest_test")

    try:
        # Test CFF data loading
        print("\n1. Testing CFF Quest Data...")
        cff_data_path = (
            project_root / "src" / "TirganachReloaded" / "data" / "cff_quest_data.json"
        )
        if cff_data_path.exists():
            import json

            with open(cff_data_path, "r", encoding="utf-8") as f:
                cff_data = json.load(f)
            print(f"   ✓ Loaded {len(cff_data)} quests from CFF data")

            # Show sample
            sample_ids = list(cff_data.keys())[:3]
            print(f"   ✓ Sample quest IDs: {sample_ids}")
        else:
            print(f"   ⚠ CFF quest data not found at: {cff_data_path}")

        # Test Lua data manager
        print("\n2. Testing Lua Data Manager...")
        cache_dir = project_root / "src" / "TirganachReloaded" / "data" / "cache"
        lua_manager = LuaDataManager(cache_dir=cache_dir)
        print("   ✓ Lua manager initialized")
        print(f"   ✓ Cache loaded: {lua_manager.cache_loaded}")

        if lua_manager.cache_loaded:
            lua_quests = lua_manager.get_all_quests()
            print(f"   ✓ Found {len(lua_quests)} quests in Lua cache")

            if lua_quests:
                sample_quest_ids = list(lua_quests.keys())[:3]
                print(f"   ✓ Sample Lua quest IDs: {sample_quest_ids}")

                # Show details for first quest
                first_quest_id = sample_quest_ids[0]
                first_quest = lua_quests[first_quest_id]
                print(f"   ✓ Quest {first_quest_id}: {first_quest.name or 'Unnamed'}")
                if first_quest.objectives:
                    print(f"     - {len(first_quest.objectives)} objectives")
                if first_quest.requirements:
                    print(f"     - {len(first_quest.requirements)} requirements")
                if first_quest.rewards:
                    print(f"     - {len(first_quest.rewards)} rewards")
        else:
            print("   ⚠ Lua cache not loaded - may need to rebuild")

        # Test Lua source detection
        print("\n3. Testing Lua Source Detection...")
        lua_paths = [
            project_root / "ModdingTools" / "SpellForceLUASources",
            project_root / "OriginalGameFiles" / "lua",
        ]

        found_lua = False
        for path in lua_paths:
            if path.exists() and path.is_dir():
                print(f"   ✓ Found Lua source: {path}")
                found_lua = True
                # Count lua files
                lua_files = list(path.rglob("*.lua"))
                print(f"     - {len(lua_files)} Lua files found")
            else:
                print(f"   - Not found: {path}")

        if not found_lua:
            print("   ⚠ No Lua source directories found")

        print("\n✅ Data loading test completed!")
        return True

    except Exception as e:
        logger.exception(f"Test failed: {e}")
        print(f"\n❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_data_loading()
    sys.exit(0 if success else 1)
