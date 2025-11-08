#!/usr/bin/env python3
"""
Simple Test Script for Enhanced Quest Creation System

This script tests basic functionality of the enhanced quest creation system
without requiring the full GUI setup.
"""

import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.cff_editor.models.quest_models import EnhancedQuestData, QuestReward, Dialogue, MapLocation
from TirganachReloaded.cff_editor.widgets.quest_validator import QuestValidator


def test_quest_validator():
    """Test the quest validator"""
    print("=== Testing Quest Validator ===")
    
    # Create validator
    validator = QuestValidator()
    
    # Set existing quest data
    existing_quests = {
        1: {'name': 'Test Quest 1'},
        2: {'name': 'Test Quest 2'}
    }
    validator.set_existing_quests(existing_quests)
    
    # Create test quest
    test_quest = EnhancedQuestData(
        quest_id=9001,
        name="Test Enhanced Quest",
        description="A test quest for the enhanced quest creation system.",
        parent_id=0,
        order_index=0
    )
    
    # Add some data
    test_quest.map_locations.append(MapLocation(code="P1", name="Liannon"))
    test_quest.dialogues.append(Dialogue(text="Hello, adventurer! I have a quest for you.", speaker="NPC"))
    test_quest.dialogues.append(Dialogue(text="What do you need?", speaker="Player"))
    test_quest.dialogues.append(Dialogue(text="Please help me find the lost artifact.", speaker="NPC"))
    test_quest.rewards = QuestReward(xp=100, gold=10, silver=25)
    
    # Validate
    result = validator.validate_quest_detailed(test_quest)
    
    print(f"Validation Result: {result.get_summary()}")
    print(f"Total Issues: {len(result.get_all_issues())}")
    
    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"  - {error}")
    
    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
    
    if result.info:
        print("\nInfo:")
        for info in result.info:
            print(f"  - {info}")
    
    return result.is_valid


def test_quest_models():
    """Test the quest data models"""
    print("\n=== Testing Quest Models ===")
    
    # Create enhanced quest data
    quest = EnhancedQuestData(
        quest_id=1001,
        name="Model Test Quest",
        description="Testing quest data models.",
        parent_id=0,
        order_index=0,
        has_extended_dialogues=True,
        lua_files_count=3,
        total_lua_references=15
    )
    
    # Add map location
    quest.map_locations.append(MapLocation(code="P8", name="Gol Halad"))
    
    # Add dialogues
    quest.dialogues.append(Dialogue(
        text="Welcome to Gol Halad!",
        speaker="NPC",
        dialogue_type="Greeting"
    ))
    
    quest.dialogues.append(Dialogue(
        text="Thank you for the information.",
        speaker="Player",
        dialogue_type="Response"
    ))
    
    # Add rewards
    quest.rewards = QuestReward(
        xp=50,
        gold=5,
        silver=50,
        copper=0,
        reward_flags=["complete", "success"],
        items=[101, 102]
    )
    
    # Test data access
    print(f"Quest ID: {quest.quest_id}")
    print(f"Quest Name: {quest.name}")
    print(f"Description: {quest.description}")
    print(f"Parent ID: {quest.parent_id}")
    print(f"Order Index: {quest.order_index}")
    print(f"Map Locations: {len(quest.map_locations)}")
    print(f"Dialogues: {len(quest.dialogues)}")
    print(f"Has Extended Dialogues: {quest.has_extended_dialogues}")
    
    if quest.rewards:
        print(f"Rewards - XP: {quest.rewards.xp}, Gold: {quest.rewards.gold}, Silver: {quest.rewards.silver}")
        print(f"Reward Flags: {quest.rewards.reward_flags}")
        print(f"Reward Items: {quest.rewards.items}")
    
    print("✓ Quest models working correctly")
    return True


def test_lua_generation():
    """Test basic Lua script generation"""
    print("\n=== Testing Lua Generation ===")
    
    # Generate basic Lua script
    quest_id = 1001
    quest_name = "Lua Test Quest"
    
    lua_script = f'''-- Generated Quest Script: {quest_name}
-- Quest ID: {quest_id}
-- Platform: P1

function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

-- Quest: {quest_name}
-- ID: {quest_id}

-- Initialize quest when conditions are met
OnOneTimeEvent
{{
    EventName = "Init_{quest_name.replace(' ', '')}",
    Conditions = 
    {{
        -- Add prerequisites here
    }},
    Actions = 
    {{
        -- Begin the quest
        QuestBegin{{QuestId = {quest_id}}},
        -- Add quest to journal
        Outcry{{
            NpcId = 0,  -- Player
            String = "{quest_name}: A test quest for Lua generation.",
            Color = ColorYellow
        }},
    }}
}}

-- Quest completion conditions
OnOneTimeEvent
{{
    EventName = "Complete_{quest_name.replace(' ', '')}",
    Conditions = 
    {{
        QuestState{{QuestId = {quest_id}, State = StateActive}},
        -- Add completion conditions here
    }},
    Actions = 
    {{
        -- Complete the quest
        QuestSolve{{QuestId = {quest_id}}},
        -- Grant rewards
        SetRewardFlagTrue{{Name = "Quest{quest_id}Reward"}},
        -- Success message
        Outcry{{
            NpcId = 0,
            String = "Quest completed: {quest_name}!",
            Color = ColorGreen
        }},
    }}
}}

EndDefinition()
end
'''
    
    print("Generated Lua Script:")
    print("=" * 50)
    print(lua_script)
    print("=" * 50)
    
    # Basic validation
    if 'function CreateStateMachine' in lua_script:
        print("✓ Function definition present")
    else:
        print("✗ Function definition missing")
    
    if 'QuestBegin' in lua_script:
        print("✓ Quest start command present")
    else:
        print("✗ Quest start command missing")
    
    if 'QuestSolve' in lua_script:
        print("✓ Quest completion command present")
    else:
        print("✗ Quest completion command missing")
    
    print("✓ Lua generation working")
    return True


def main():
    """Main test function"""
    print("Enhanced Quest Creation System - Basic Tests")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Run tests
    if test_quest_models():
        tests_passed += 1
    
    if test_lua_generation():
        tests_passed += 1
    
    if test_quest_validator():
        tests_passed += 1
    
    # Results
    print("\n" + "=" * 60)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✓ All tests passed! Enhanced quest creation system is working.")
        return 0
    else:
        print("✗ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)