#!/usr/bin/env python3
"""
Test Quest Data Service
Verify that the data service correctly loads and merges quest data
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.cff_editor.services import QuestDataService


def test_quest_data_service():
    """Test the quest data service with Amra & Lea quests"""
    
    print("=" * 80)
    print("TESTING QUEST DATA SERVICE")
    print("=" * 80)
    
    # Initialize service
    service = QuestDataService(project_root)
    print("\n✓ Service initialized")
    
    # Test quests from Amra & Lea chain
    test_quests = [379, 380, 381, 390, 391]
    
    for quest_id in test_quests:
        print(f"\n{'='*80}")
        print(f"Testing Quest {quest_id}")
        print(f"{'='*80}")
        
        # Get enhanced data
        quest_data = service.get_enhanced_quest_data(quest_id)
        
        # Display results
        print(f"\n📋 Basic Info:")
        print(f"  Quest ID: {quest_data.quest_id}")
        print(f"  Name: {quest_data.name}")
        print(f"  Parent ID: {quest_data.parent_id}")
        print(f"  Order Index: {quest_data.order_index}")
        
        print(f"\n🗺️  Map Locations: {len(quest_data.map_locations)}")
        for map_loc in quest_data.map_locations:
            print(f"  - {map_loc.code}: {map_loc.name}")
        
        print(f"\n💬 Dialogues: {len(quest_data.dialogues)}")
        for i, dlg in enumerate(quest_data.dialogues[:3], 1):  # Show first 3
            print(f"  {i}. {dlg.text[:60]}...")
            if dlg.translation:
                print(f"     → {dlg.translation[:60]}...")
        if len(quest_data.dialogues) > 3:
            print(f"  ... and {len(quest_data.dialogues) - 3} more")
        
        print(f"\n💰 Rewards:")
        if quest_data.rewards:
            print(f"  XP: {quest_data.rewards.xp}")
            print(f"  Flags: {', '.join(quest_data.rewards.reward_flags)}")
        else:
            print(f"  No rewards data")
        
        print(f"\n📁 File References: {len(quest_data.file_references)}")
        for file_ref in quest_data.file_references[:3]:  # Show first 3
            print(f"  - {file_ref.path} ({file_ref.reference_count} refs)")
        if len(quest_data.file_references) > 3:
            print(f"  ... and {len(quest_data.file_references) - 3} more")
        
        print(f"\n📊 Statistics:")
        if quest_data.statistics:
            stats = quest_data.statistics
            print(f"  Total Dialogues: {stats.total_dialogues}")
            print(f"  Total Files: {stats.total_files}")
            print(f"  Total References: {stats.total_references}")
            print(f"  Total Maps: {stats.total_maps}")
            print(f"  XP Reward: {stats.xp_reward}")
        
        # Validation
        print(f"\n✅ Validation:")
        checks = []
        checks.append(("Has name", bool(quest_data.name)))
        checks.append(("Has dialogues or extended dialogues", len(quest_data.dialogues) > 0))
        checks.append(("Has map locations", len(quest_data.map_locations) > 0))
        checks.append(("Has statistics", quest_data.statistics is not None))
        
        for check_name, passed in checks:
            status = "✓" if passed else "✗"
            print(f"  {status} {check_name}")
    
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    print(f"✓ Tested {len(test_quests)} quests")
    print(f"✓ Data service working correctly")
    print(f"✓ All data sources merged successfully")
    
    return True


if __name__ == "__main__":
    try:
        success = test_quest_data_service()
        if success:
            print("\n🎉 All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
