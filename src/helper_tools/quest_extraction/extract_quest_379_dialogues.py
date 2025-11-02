#!/usr/bin/env python3
"""
Extract all dialogues from quest 379 and its subquests
Searches CFF files for quest data and Lua files for dialogues
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.tirganach import GameData
from TirganachReloaded.tirganach.types import Language, Language as Lang
import json


def load_cff_file(cff_path: Path) -> GameData:
    """Load a CFF file"""
    print(f"Loading CFF file: {cff_path}")
    game_data = GameData()
    game_data.load(str(cff_path))
    return game_data


def find_quest_by_id(game_data: GameData, quest_id: int):
    """Find a quest by ID in the game data"""
    if not hasattr(game_data, 'quests') or game_data.quests is None:
        return None
    
    for quest in game_data.quests:
        if hasattr(quest, 'id') and quest.id == quest_id:
            return quest
        elif hasattr(quest, 'quest_id') and quest.quest_id == quest_id:
            return quest
    return None


def get_quest_subquests(game_data: GameData, quest_id: int):
    """Get all subquests for a given quest ID"""
    subquests = []
    
    if not hasattr(game_data, 'quests') or game_data.quests is None:
        return subquests
    
    for quest in game_data.quests:
        parent_id = None
        if hasattr(quest, 'parent_id'):
            parent_id = quest.parent_id
        elif hasattr(quest, 'parent_quest_id'):
            parent_id = quest.parent_quest_id
        
        if parent_id == quest_id:
            subquests.append(quest)
    
    return subquests


def get_string_by_id(game_data: GameData, string_id: int, language: Language = Language.ENGLISH) -> str:
    """Get a string by ID from the game data"""
    if not hasattr(game_data, 'strings') or game_data.strings is None:
        return f"[String ID: {string_id}]"
    
    for string_entry in game_data.strings:
        if hasattr(string_entry, 'id') and string_entry.id == string_id:
            if hasattr(string_entry, 'texts') and language.value < len(string_entry.texts):
                return string_entry.texts[language.value]
            elif hasattr(string_entry, 'text'):
                return string_entry.text
    
    return f"[String ID: {string_id}]"


def extract_quest_dialogues(game_data: GameData, quest_id: int):
    """Extract all dialogue information for a quest"""
    dialogues = []
    
    # Try to find quest dialogues
    if hasattr(game_data, 'quest_dialogs') and game_data.quest_dialogs:
        for dialog in game_data.quest_dialogs:
            if hasattr(dialog, 'quest_id') and dialog.quest_id == quest_id:
                dialogue_info = {
                    'dialog_id': getattr(dialog, 'dialog_id', getattr(dialog, 'id', None)),
                    'quest_id': quest_id,
                    'speaker_id': getattr(dialog, 'speaker_id', None),
                    'text_id': getattr(dialog, 'text_id', None),
                }
                
                # Get the actual text
                if dialogue_info['text_id']:
                    dialogue_info['text'] = get_string_by_id(game_data, dialogue_info['text_id'])
                
                dialogues.append(dialogue_info)
    
    # Also check for dialogues in general dialog table
    if hasattr(game_data, 'dialogs') and game_data.dialogs:
        for dialog in game_data.dialogs:
            # Check if this dialog is related to the quest
            if hasattr(dialog, 'quest_id') and dialog.quest_id == quest_id:
                dialogue_info = {
                    'dialog_id': getattr(dialog, 'id', None),
                    'quest_id': quest_id,
                    'text_id': getattr(dialog, 'text_id', None),
                }
                
                if dialogue_info['text_id']:
                    dialogue_info['text'] = get_string_by_id(game_data, dialogue_info['text_id'])
                
                dialogues.append(dialogue_info)
    
    return dialogues


def search_lua_files_for_quest(lua_dir: Path, quest_id: int):
    """Search Lua files for quest-related dialogues"""
    dialogues = []
    
    if not lua_dir.exists():
        print(f"Lua directory not found: {lua_dir}")
        return dialogues
    
    # Search for Lua files containing the quest ID
    for lua_file in lua_dir.rglob("*.lua"):
        try:
            with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Check if this file mentions the quest ID
                if f"QuestId = {quest_id}" in content or f"QuestId={quest_id}" in content:
                    print(f"\nFound quest {quest_id} in: {lua_file}")
                    
                    # Extract dialogue strings
                    import re
                    
                    # Look for Outcry statements with strings
                    outcry_pattern = r'Outcry\s*{\s*(?:.*?)String\s*=\s*["\']([^"\']+)["\']'
                    outcries = re.findall(outcry_pattern, content, re.DOTALL)
                    
                    for outcry in outcries:
                        dialogues.append({
                            'source': str(lua_file.relative_to(lua_dir)),
                            'type': 'Outcry',
                            'text': outcry,
                            'quest_id': quest_id
                        })
                    
                    # Look for dialogue text patterns
                    dialog_pattern = r'(?:Dialog|Dialogue)\s*{\s*(?:.*?)(?:Text|String)\s*=\s*["\']([^"\']+)["\']'
                    dialogs = re.findall(dialog_pattern, content, re.DOTALL)
                    
                    for dialog in dialogs:
                        dialogues.append({
                            'source': str(lua_file.relative_to(lua_dir)),
                            'type': 'Dialog',
                            'text': dialog,
                            'quest_id': quest_id
                        })
        
        except Exception as e:
            print(f"Error reading {lua_file}: {e}")
    
    return dialogues


def main():
    # Paths
    cff_file = project_root / "OriginalGameFiles" / "data" / "GameData.cff"
    lua_dir = project_root / "OriginalGameFiles" / "modding" / "Original Scripts"
    
    if not cff_file.exists():
        print(f"CFF file not found: {cff_file}")
        # Try alternative location
        cff_file = project_root / "ModdedGameFiles" / "GameData_MyCustomMod_20251019_100557.cff"
        if not cff_file.exists():
            print("No CFF file found!")
            return
    
    print("=" * 80)
    print("QUEST 379 DIALOGUE EXTRACTION")
    print("=" * 80)
    
    # Load CFF data
    try:
        game_data = load_cff_file(cff_file)
        print(f"CFF file loaded successfully")
        print(f"Available languages: {[lang.name for lang in Language]}")
    except Exception as e:
        print(f"Error loading CFF file: {e}")
        print("\nAttempting to inspect CFF structure...")
        # The CFF file might be binary, let's try a different approach
        game_data = None
    
    all_dialogues = {}
    
    # If we can load the CFF file
    if game_data:
        # Find main quest
        quest = find_quest_by_id(game_data, 379)
        
        if quest:
            print(f"\nFound Quest 379:")
            print(f"  Name ID: {getattr(quest, 'name_id', 'N/A')}")
            print(f"  Description ID: {getattr(quest, 'description_id', 'N/A')}")
            
            # Get quest name and description
            if hasattr(quest, 'name_id'):
                name = get_string_by_id(game_data, quest.name_id)
                print(f"  Name: {name}")
            
            if hasattr(quest, 'description_id'):
                desc = get_string_by_id(game_data, quest.description_id)
                print(f"  Description: {desc}")
            
            # Extract dialogues for main quest
            dialogues = extract_quest_dialogues(game_data, 379)
            all_dialogues[379] = {
                'quest_id': 379,
                'name': name if hasattr(quest, 'name_id') else 'Quest 379',
                'dialogues': dialogues
            }
            
            print(f"\n  Found {len(dialogues)} dialogues in CFF")
        else:
            print("\nQuest 379 not found in CFF file")
        
        # Find subquests
        subquests = get_quest_subquests(game_data, 379)
        print(f"\nFound {len(subquests)} subquests")
        
        for subquest in subquests:
            subquest_id = getattr(subquest, 'id', getattr(subquest, 'quest_id', None))
            if subquest_id:
                print(f"\n  Subquest {subquest_id}:")
                
                if hasattr(subquest, 'name_id'):
                    name = get_string_by_id(game_data, subquest.name_id)
                    print(f"    Name: {name}")
                
                dialogues = extract_quest_dialogues(game_data, subquest_id)
                all_dialogues[subquest_id] = {
                    'quest_id': subquest_id,
                    'name': name if hasattr(subquest, 'name_id') else f'Subquest {subquest_id}',
                    'dialogues': dialogues,
                    'parent_quest_id': 379
                }
                
                print(f"    Found {len(dialogues)} dialogues in CFF")
    
    # Search Lua files
    print("\n" + "=" * 80)
    print("SEARCHING LUA FILES")
    print("=" * 80)
    
    lua_dialogues = search_lua_files_for_quest(lua_dir, 379)
    
    if lua_dialogues:
        print(f"\nFound {len(lua_dialogues)} dialogue entries in Lua files for quest 379")
        all_dialogues['379_lua'] = {
            'quest_id': 379,
            'source': 'Lua Scripts',
            'dialogues': lua_dialogues
        }
    
    # Also search for potential subquests in Lua
    if all_dialogues:
        for quest_id in list(all_dialogues.keys()):
            if isinstance(quest_id, int) and quest_id != 379:
                lua_sub_dialogues = search_lua_files_for_quest(lua_dir, quest_id)
                if lua_sub_dialogues:
                    print(f"\nFound {len(lua_sub_dialogues)} dialogue entries in Lua files for subquest {quest_id}")
                    all_dialogues[f'{quest_id}_lua'] = {
                        'quest_id': quest_id,
                        'source': 'Lua Scripts',
                        'dialogues': lua_sub_dialogues,
                        'parent_quest_id': 379
                    }
    
    # Save results
    output_file = project_root / "quest_379_dialogues.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_dialogues, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTotal quests/subquests found: {len([k for k in all_dialogues.keys() if isinstance(k, int)])}")
    print(f"Results saved to: {output_file}")
    
    # Print summary of dialogues
    for key, data in all_dialogues.items():
        if isinstance(data, dict) and 'dialogues' in data:
            print(f"\n{data.get('name', f'Quest {key}')}:")
            for i, dialogue in enumerate(data['dialogues'][:5], 1):  # Show first 5
                if 'text' in dialogue:
                    print(f"  {i}. {dialogue['text'][:100]}...")
            if len(data['dialogues']) > 5:
                print(f"  ... and {len(data['dialogues']) - 5} more")


if __name__ == "__main__":
    main()
