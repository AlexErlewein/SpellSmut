#!/usr/bin/env python3
"""
Extract quest descriptions from CFF string tables and search new Lua sources
"""

import sys
from pathlib import Path
import json
import re

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.tirganach import GameData
from TirganachReloaded.tirganach.types import Language

def get_all_strings_for_id(game_data: GameData, string_id: int):
    """Get all language versions of a string"""
    if not hasattr(game_data, 'localisation') or game_data.localisation is None:
        return None
    
    try:
        for string_entry in game_data.localisation:
            if hasattr(string_entry, 'id') and string_entry.id == string_id:
                result = {
                    'string_id': string_id,
                    'languages': {}
                }
                
                if hasattr(string_entry, 'texts'):
                    # texts is a list: [German, English, French]
                    if len(string_entry.texts) > 0:
                        result['languages']['german'] = string_entry.texts[0]
                    if len(string_entry.texts) > 1:
                        result['languages']['english'] = string_entry.texts[1]
                    if len(string_entry.texts) > 2:
                        result['languages']['french'] = string_entry.texts[2]
                
                return result
    except Exception as e:
        print(f"Error getting strings for ID {string_id}: {e}")
    
    return None

def search_lua_for_quest(lua_dir: Path, quest_id: int):
    """Search Lua files for quest references and extract ALL dialogues"""
    results = {
        'files': [],
        'total_references': 0,
        'dialogues': []
    }
    
    if not lua_dir.exists():
        return results
    
    for lua_file in lua_dir.rglob("*.lua"):
        try:
            with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check for quest ID references
            if f"QuestId = {quest_id}" in content or f"QuestId={quest_id}" in content:
                file_info = {
                    'path': str(lua_file.relative_to(lua_dir.parent)),
                    'references': content.count(f"QuestId = {quest_id}") + content.count(f"QuestId={quest_id}")
                }
                results['files'].append(file_info)
                results['total_references'] += file_info['references']
                
                # Extract ALL dialogue patterns
                # Pattern 1: Say/Answer/OfferAnswer with Text
                patterns = [
                    r'(?:Say|Answer|OfferAnswer)\s*{\s*(?:.*?)Text\s*=\s*"([^"]+)"',
                    r'(?:Say|Answer|OfferAnswer)\s*{\s*(?:.*?)Text\s*=\s*\'([^\']+)\'',
                    # Pattern 2: Outcry
                    r'Outcry\s*{\s*(?:.*?)String\s*=\s*"([^"]+)"',
                    r'Outcry\s*{\s*(?:.*?)String\s*=\s*\'([^\']+)\'',
                    # Pattern 3: Dialog
                    r'Dialog\s*{\s*(?:.*?)Text\s*=\s*"([^"]+)"',
                    r'Dialog\s*{\s*(?:.*?)Text\s*=\s*\'([^\']+)\'',
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.DOTALL)
                    for match in matches:
                        text = match.group(1)
                        # Only add if not already in list (avoid duplicates)
                        if text not in [d['text'] for d in results['dialogues']]:
                            results['dialogues'].append({
                                'text': text,
                                'file': str(lua_file.relative_to(lua_dir.parent))
                            })
        
        except Exception as e:
            continue
    
    return results

def main():
    quest_ids = [379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 393]
    
    cff_file = project_root / "OriginalGameFiles" / "data" / "GameData.cff"
    lua_dir_original = project_root / "OriginalGameFiles" / "modding" / "Original Scripts"
    lua_dir_modding = project_root / "ModdingTools" / "SpellForceLUASources"
    
    print("=" * 80)
    print("EXTRACTING QUEST DESCRIPTIONS AND DIALOGUES")
    print("=" * 80)
    
    # Load CFF
    print(f"\nLoading CFF: {cff_file.name}")
    game_data = GameData(cff_file)
    print("✓ CFF loaded")
    
    all_data = {}
    
    for quest_id in quest_ids:
        print(f"\n{'='*80}")
        print(f"Quest {quest_id}")
        print(f"{'='*80}")
        
        quest_data = {
            'quest_id': quest_id,
            'cff_data': {},
            'strings': {},
            'lua_original': {},
            'lua_modding': {}
        }
        
        # Get quest from CFF
        if hasattr(game_data, 'quests'):
            for quest in game_data.quests:
                q_id = getattr(quest, 'id', None) or getattr(quest, 'quest_id', None)
                if q_id == quest_id:
                    quest_data['cff_data'] = {
                        'name': getattr(quest, 'name', None),
                        'name_id': getattr(quest, 'name_id', None),
                        'description_id': getattr(quest, 'description_id', None),
                        'parent_id': getattr(quest, 'parent_quest_id', 0),
                        'order_index': getattr(quest, 'order_index', None)
                    }
                    
                    print(f"Name: {quest_data['cff_data']['name']}")
                    print(f"Name ID: {quest_data['cff_data']['name_id']}")
                    print(f"Description ID: {quest_data['cff_data']['description_id']}")
                    
                    # Get actual string content
                    if quest_data['cff_data']['name_id']:
                        name_strings = get_all_strings_for_id(game_data, quest_data['cff_data']['name_id'])
                        if name_strings:
                            quest_data['strings']['name'] = name_strings
                            print(f"Name (DE): {name_strings['languages'].get('german', 'N/A')}")
                            print(f"Name (EN): {name_strings['languages'].get('english', 'N/A')}")
                    
                    if quest_data['cff_data']['description_id']:
                        desc_strings = get_all_strings_for_id(game_data, quest_data['cff_data']['description_id'])
                        if desc_strings:
                            quest_data['strings']['description'] = desc_strings
                            desc_de = desc_strings['languages'].get('german', 'N/A')
                            desc_en = desc_strings['languages'].get('english', 'N/A')
                            print(f"Description (DE): {desc_de[:100]}...")
                            print(f"Description (EN): {desc_en[:100]}...")
                    
                    break
        
        # Search original Lua files
        print(f"\nSearching original Lua files...")
        lua_original = search_lua_for_quest(lua_dir_original, quest_id)
        quest_data['lua_original'] = lua_original
        print(f"Found {len(lua_original['files'])} files, {len(lua_original['dialogues'])} unique dialogues")
        
        # Search modding Lua files
        print(f"Searching modding Lua files...")
        lua_modding = search_lua_for_quest(lua_dir_modding, quest_id)
        quest_data['lua_modding'] = lua_modding
        print(f"Found {len(lua_modding['files'])} files, {len(lua_modding['dialogues'])} unique dialogues")
        
        all_data[quest_id] = quest_data
    
    # Save results
    output_file = project_root / "quest_descriptions_complete.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print("EXTRACTION COMPLETE")
    print(f"{'='*80}")
    print(f"Data saved to: {output_file}")
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    for quest_id, data in all_data.items():
        name = data['cff_data'].get('name', 'Unknown')
        desc_count = 1 if 'description' in data['strings'] else 0
        lua_orig_dlg = len(data['lua_original'].get('dialogues', []))
        lua_mod_dlg = len(data['lua_modding'].get('dialogues', []))
        print(f"\nQuest {quest_id}: {name}")
        print(f"  Description: {'✓' if desc_count else '✗'}")
        print(f"  Original Lua dialogues: {lua_orig_dlg}")
        print(f"  Modding Lua dialogues: {lua_mod_dlg}")

if __name__ == "__main__":
    main()
