#!/usr/bin/env python3
"""
Debug script to check quest data loading
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def debug_quest_data_service():
    """Debug quest data service loading"""
    print("🔍 Debugging QuestDataService...")
    
    try:
        from TirganachReloaded.cff_editor.services import QuestDataService
        
        # Initialize service
        project_root = Path(__file__).parent
        service = QuestDataService(project_root)
        
        print(f"Project root: {project_root}")
        print(f"Data dir: {service.data_dir}")
        
        # Check what files exist
        maps_file = service.data_dir / "quest_maps_and_descriptions.json"
        rewards_file = service.data_dir / "quest_reward_mappings.json"
        descriptions_file = service.data_dir / "quest_descriptions_complete.json"
        
        print(f"\n📁 File checks:")
        print(f"  Maps file exists: {maps_file.exists()}")
        print(f"  Rewards file exists: {rewards_file.exists()}")
        print(f"  Descriptions file exists: {descriptions_file.exists()}")
        
        # Try to load data
        print(f"\n📊 Loading data:")
        maps_data = service._load_quest_maps()
        print(f"  Maps loaded: {len(maps_data)} entries")
        
        rewards_data = service._load_quest_rewards()
        print(f"  Rewards loaded: {len(rewards_data)} entries")
        
        descriptions_data = service._load_quest_descriptions()
        print(f"  Descriptions loaded: {len(descriptions_data)} entries")
        
        # Test getting enhanced data for quest 380
        print(f"\n🧪 Testing enhanced data for quest 380:")
        enhanced_data = service.get_enhanced_quest_data(380, {
            'name': 'Test Quest',
            'description': 'Test Description',
            'parent_quest_id': 0,
            'order_index': 0,
            'name_id': 0,
            'description_id': 0,
        })
        
        if enhanced_data:
            print(f"  ✅ Enhanced data loaded:")
            print(f"     - Map locations: {len(enhanced_data.map_locations)}")
            print(f"     - Dialogues: {len(enhanced_data.dialogues)}")
            print(f"     - Rewards: {enhanced_data.rewards}")
            print(f"     - File references: {len(enhanced_data.file_references)}")
        else:
            print(f"  ❌ No enhanced data loaded")
            
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_quest_data_service()