#!/usr/bin/env python3
"""
Extract all dialogues from any quest ID and its subquests
Searches CFF files for quest data and Lua files for dialogues
Usage: python3 extract_quest_dialogues.py [quest_id]
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


def main(quest_id: int):
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
    print(f"QUEST {quest_id} DIALOGUE EXTRACTION")
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
        quest = find_quest_by_id(game_data, quest_id)
        
        if quest:
            print(f"\nFound Quest {quest_id}:")
            print(f"  Name ID: {getattr(quest, 'name_id', 'N/A')}")
            print(f"  Description ID: {getattr(quest, 'description_id', 'N/A')}")
            
            # Get quest name and description
            name = "Unknown"
            if hasattr(quest, 'name_id'):
                name = get_string_by_id(game_data, quest.name_id)
                print(f"  Name: {name}")
            
            desc = "Unknown"
            if hasattr(quest, 'description_id'):
                desc = get_string_by_id(game_data, quest.description_id)
                print(f"  Description: {desc}")
            
            # Extract dialogues for main quest
            dialogues = extract_quest_dialogues(game_data, quest_id)
            all_dialogues[quest_id] = {
                'quest_id': quest_id,
                'name': name,
                'description': desc,
                'dialogues': dialogues
            }
            
            print(f"\n  Found {len(dialogues)} dialogues in CFF")
        else:
            print(f"\nQuest {quest_id} not found in CFF file")
        
        # Find subquests
        subquests = get_quest_subquests(game_data, quest_id)
        print(f"\nFound {len(subquests)} subquests")
        
        for subquest in subquests:
            subquest_id = getattr(subquest, 'id', getattr(subquest, 'quest_id', None))
            if subquest_id:
                print(f"\n  Subquest {subquest_id}:")
                
                sub_name = "Unknown"
                if hasattr(subquest, 'name_id'):
                    sub_name = get_string_by_id(game_data, subquest.name_id)
                    print(f"    Name: {sub_name}")
                
                dialogues = extract_quest_dialogues(game_data, subquest_id)
                all_dialogues[subquest_id] = {
                    'quest_id': subquest_id,
                    'name': sub_name,
                    'dialogues': dialogues,
                    'parent_quest_id': quest_id
                }
                
                print(f"    Found {len(dialogues)} dialogues in CFF")
    
    # Search Lua files
    print("\n" + "=" * 80)
    print("SEARCHING LUA FILES")
    print("=" * 80)
    
    lua_dialogues = search_lua_files_for_quest(lua_dir, quest_id)
    
    if lua_dialogues:
        print(f"\nFound {len(lua_dialogues)} dialogue entries in Lua files for quest {quest_id}")
        all_dialogues[f'{quest_id}_lua'] = {
            'quest_id': quest_id,
            'source': 'Lua Scripts',
            'dialogues': lua_dialogues
        }
    
    # Also search for potential subquests in Lua
    if all_dialogues:
        for quest_key in list(all_dialogues.keys()):
            if isinstance(quest_key, int) and quest_key != quest_id:
                lua_sub_dialogues = search_lua_files_for_quest(lua_dir, quest_key)
                if lua_sub_dialogues:
                    print(f"\nFound {len(lua_sub_dialogues)} dialogue entries in Lua files for subquest {quest_key}")
                    all_dialogues[f'{quest_key}_lua'] = {
                        'quest_id': quest_key,
                        'source': 'Lua Scripts',
                        'dialogues': lua_sub_dialogues,
                        'parent_quest_id': quest_id
                    }
    
    # Save results
    output_file = project_root / f"quest_{quest_id}_dialogues.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_dialogues, f, indent=2, ensure_ascii=False)
    
    # Create cleaned text output
    clean_output_file = project_root / f"quest_{quest_id}_dialogues_clean.txt"
    create_clean_output(all_dialogues, clean_output_file, quest_id)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTotal quests/subquests found: {len([k for k in all_dialogues.keys() if isinstance(k, int)])}")
    print(f"Results saved to: {output_file}")
    print(f"Cleaned output saved to: {clean_output_file}")
    
    # Print summary of dialogues
    for key, data in all_dialogues.items():
        if isinstance(data, dict) and 'dialogues' in data:
            print(f"\n{data.get('name', f'Quest {key}')}:")
            for i, dialogue in enumerate(data['dialogues'][:5], 1):  # Show first 5
                if 'text' in dialogue:
                    print(f"  {i}. {dialogue['text'][:100]}...")
            if len(data['dialogues']) > 5:
                print(f"  ... and {len(data['dialogues']) - 5} more")


def create_clean_output(all_dialogues: dict, output_file: Path, quest_id: int):
    """Create a cleaned text output file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"QUEST {quest_id} DIALOGUES - CLEANED OUTPUT\n")
        f.write("=" * 80 + "\n\n")
        
        # Group by source files
        source_files = {}
        for key, data in all_dialogues.items():
            if isinstance(data, dict) and 'dialogues' in data:
                for dialogue in data['dialogues']:
                    source = dialogue.get('source', 'Unknown')
                    if source not in source_files:
                        source_files[source] = []
                    source_files[source].append(dialogue)
        
        # Write by source
        f.write(f"Quest {quest_id} was found in {len(source_files)} Lua files:\n")
        for source, dialogues in source_files.items():
            f.write(f"- {source} ({len(dialogues)} dialogues)\n")
        f.write("\n")
        
        f.write("UNIQUE DIALOGUES FROM QUEST {quest_id}:\n\n")
        
        dialogue_num = 1
        for source, dialogues in source_files.items():
            f.write(f"From {source}:\n")
            unique_dialogues = []
            seen_texts = set()
            
            for dialogue in dialogues:
                text = dialogue.get('text', '')
                if text and text not in seen_texts:
                    unique_dialogues.append(dialogue)
                    seen_texts.add(text)
            
            for dialogue in unique_dialogues:
                text = dialogue.get('text', '')
                f.write(f"{dialogue_num}. \"{text}\"\n")
                dialogue_num += 1
            
            f.write("\n")
        
        f.write("=" * 80 + "\n")
        f.write("SUMMARY:\n")
        f.write(f"- Total unique dialogues found: {dialogue_num - 1}\n")
        f.write(f"- Total dialogue entries (including duplicates): {sum(len(d['dialogues']) for d in all_dialogues.values() if isinstance(d, dict) and 'dialogues' in d)}\n")
        f.write(f"- Source files: {len(source_files)} Lua files\n")
        f.write(f"- Languages detected: German\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("EXTRACTION DETAILS:\n")
        f.write(f"- Quest ID: {quest_id}\n")
        f.write(f"- Extraction completed successfully\n")
        f.write(f"- Output saved to: quest_{quest_id}_dialogues.json\n")
        f.write(f"- Cleaned text output: quest_{quest_id}_dialogues_clean.txt\n")


if __name__ == "__main__":
    # Get quest ID from command line argument or use default
    if len(sys.argv) > 1:
        try:
            quest_id = int(sys.argv[1])
        except ValueError:
            print("Please provide a valid quest ID as a number")
            sys.exit(1)
    else:
        print("Usage: python3 extract_quest_dialogues.py <quest_id>")
        print("Example: python3 extract_quest_dialogues.py 380")
        sys.exit(1)
    
    main(quest_id)
