#!/usr/bin/env python3
"""
Extract quest metadata from CFF files
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.tirganach import GameData
from TirganachReloaded.tirganach.types import Language

def get_string_by_id(game_data: GameData, string_id: int, language: Language = Language.ENGLISH) -> str:
    """Get a string by ID from the game data"""
    if not hasattr(game_data, 'strings') or game_data.strings is None:
        return f"[String ID: {string_id}]"
    
    try:
        for string_entry in game_data.strings:
            if hasattr(string_entry, 'id') and string_entry.id == string_id:
                if hasattr(string_entry, 'texts') and len(string_entry.texts) > language.value:
                    return string_entry.texts[language.value]
                elif hasattr(string_entry, 'text'):
                    return string_entry.text
    except Exception as e:
        print(f"Error getting string {string_id}: {e}")
    
    return f"[String ID: {string_id}]"

def extract_quest_data(game_data: GameData, quest_id: int):
    """Extract quest metadata"""
    if not hasattr(game_data, 'quests') or game_data.quests is None:
        print(f"No quests attribute found in game data")
        return None
    
    print(f"Total quests in CFF: {len(game_data.quests)}")
    
    for quest in game_data.quests:
        try:
            # Try different attribute names for quest ID
            q_id = None
            if hasattr(quest, 'id'):
                q_id = quest.id
            elif hasattr(quest, 'quest_id'):
                q_id = quest.quest_id
            elif hasattr(quest, 'questId'):
                q_id = quest.questId
            
            if q_id == quest_id:
                print(f"\n✓ Found Quest {quest_id}!")
                
                # Extract all attributes
                quest_data = {
                    'quest_id': q_id,
                    'attributes': {}
                }
                
                # List all attributes
                for attr in dir(quest):
                    if not attr.startswith('_'):
                        try:
                            value = getattr(quest, attr)
                            if not callable(value):
                                quest_data['attributes'][attr] = value
                                print(f"  {attr}: {value}")
                        except Exception as e:
                            print(f"  {attr}: [Error: {e}]")
                
                # Try to get name and description
                if hasattr(quest, 'name_id'):
                    name_id = quest.name_id
                    name = get_string_by_id(game_data, name_id, Language.ENGLISH)
                    name_de = get_string_by_id(game_data, name_id, Language.GERMAN)
                    quest_data['name_id'] = name_id
                    quest_data['name_en'] = name
                    quest_data['name_de'] = name_de
                    print(f"\n  Name (EN): {name}")
                    print(f"  Name (DE): {name_de}")
                
                if hasattr(quest, 'description_id'):
                    desc_id = quest.description_id
                    desc = get_string_by_id(game_data, desc_id, Language.ENGLISH)
                    desc_de = get_string_by_id(game_data, desc_id, Language.GERMAN)
                    quest_data['description_id'] = desc_id
                    quest_data['description_en'] = desc
                    quest_data['description_de'] = desc_de
                    print(f"\n  Description (EN): {desc}")
                    print(f"  Description (DE): {desc_de}")
                
                # Parent quest
                if hasattr(quest, 'parent_id'):
                    quest_data['parent_id'] = quest.parent_id
                elif hasattr(quest, 'parent_quest_id'):
                    quest_data['parent_id'] = quest.parent_quest_id
                
                return quest_data
                
        except Exception as e:
            print(f"Error processing quest: {e}")
            continue
    
    print(f"\n✗ Quest {quest_id} not found in CFF")
    return None

def main():
    # Quest IDs to extract
    quest_ids = [379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 393]
    
    # Try different CFF files
    cff_files = [
        project_root / "OriginalGameFiles" / "data" / "GameData.cff",
        project_root / "OriginalGameFiles" / "data" / "GameData_orginal.cff",
        project_root / "ModdedGameFiles" / "GameData_MyCustomMod_20251019_100557.cff"
    ]
    
    all_quest_data = {}
    
    for cff_file in cff_files:
        if not cff_file.exists():
            print(f"Skipping {cff_file} (not found)")
            continue
        
        print("=" * 80)
        print(f"Loading CFF: {cff_file.name}")
        print("=" * 80)
        
        try:
            game_data = GameData(cff_file)
            print(f"✓ CFF loaded successfully")
            
            # Check what attributes are available
            print(f"\nGameData attributes:")
            for attr in dir(game_data):
                if not attr.startswith('_'):
                    try:
                        value = getattr(game_data, attr)
                        if not callable(value):
                            if hasattr(value, '__len__'):
                                print(f"  {attr}: {type(value).__name__} (length: {len(value)})")
                            else:
                                print(f"  {attr}: {type(value).__name__}")
                    except:
                        pass
            
            # Extract each quest
            for quest_id in quest_ids:
                if quest_id not in all_quest_data:
                    quest_data = extract_quest_data(game_data, quest_id)
                    if quest_data:
                        all_quest_data[quest_id] = quest_data
            
        except Exception as e:
            print(f"✗ Error loading CFF: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Save results
    output_file = project_root / "cff_quest_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_quest_data, f, indent=2, ensure_ascii=False, default=str)
    
    print("\n" + "=" * 80)
    print(f"EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"Found {len(all_quest_data)} quests")
    print(f"Data saved to: {output_file}")
    
    # Print summary
    for quest_id, data in sorted(all_quest_data.items()):
        name = data.get('name_en', 'Unknown')
        parent = data.get('parent_id', 'None')
        print(f"\nQuest {quest_id}: {name}")
        print(f"  Parent: {parent}")
        if 'description_en' in data:
            desc = data['description_en'][:100]
            print(f"  Description: {desc}...")

if __name__ == "__main__":
    main()
