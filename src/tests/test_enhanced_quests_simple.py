#!/usr/bin/env python3
"""
Quick test to verify enhanced quest data works without UI overhead
"""

import sys
from pathlib import Path
sys.path.append('src')

from TirganachReloaded.cff_editor.services.quest_data_service import QuestDataService
from TirganachReloaded.cff_editor.data_model import CFFDataModel

def main():
    print("=== Enhanced Quest Data Test ===")
    
    # Test data model loading
    print("1. Loading CFF data...")
    data_model = CFFDataModel()
    default_file = Path('OriginalGameFiles/data/GameData.cff')
    
    if default_file.exists():
        data_model.load_file(str(default_file))
        print("✅ CFF data loaded")
    else:
        print("❌ Default CFF file not found")
        return
    
    # Test quest service
    print("2. Initializing QuestDataService...")
    service = QuestDataService(Path('.'))
    print("✅ QuestDataService initialized")
    
    # Test enhanced data for quest 380
    print("3. Getting enhanced quest data...")
    quests = data_model.get_elements('quests')
    quest_380 = None
    
    for quest in quests:
        if hasattr(quest, 'quest_id') and quest.quest_id == 380:
            quest_380 = quest
            break
    
    if quest_380:
        cff_data = {
            'name': getattr(quest_380, 'name', ''),
            'description': getattr(quest_380, 'description', ''),
            'parent_quest_id': getattr(quest_380, 'parent_quest_id', 0),
            'order_index': getattr(quest_380, 'order_index', 0),
        }
        
        enhanced = service.get_enhanced_quest_data(380, cff_data)
        
        print(f"✅ Enhanced data loaded successfully!")
        print(f"   Quest: {enhanced.name}")
        print(f"   Maps: {len(enhanced.map_locations)}")
        for map_loc in enhanced.map_locations:
            print(f"     • {map_loc.code}: {map_loc.name}")
        
        print(f"   Dialogues: {len(enhanced.dialogues)}")
        for i, dlg in enumerate(enhanced.dialogues[:2]):
            print(f"     {i+1}. [{dlg.dialogue_type}] {dlg.text[:50]}...")
        
        print(f"   Extended Dialogues: {enhanced.has_extended_dialogues}")
        print(f"   Rewards: {enhanced.rewards.xp if enhanced.rewards else 0} XP")
        
        print("\n🎉 SUCCESS: Enhanced quest data is working perfectly!")
        print("📝 The issue in the main UI is likely:")
        print("   1. Quest details panel not visible (click 'quests' category)")
        print("   2. UI slowness from icon loading debug messages")
        
    else:
        print("❌ Quest 380 not found")

if __name__ == "__main__":
    main()