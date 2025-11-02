#!/usr/bin/env python3
"""
Extract map locations and quest descriptions
"""

import sys
from pathlib import Path
import json
import re

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.tirganach import GameData
from TirganachReloaded.tirganach.types import Language

# Map codes to names (from file paths like P1, P6, P15, etc.)
MAP_NAMES = {
    "P1": "Liannon",
    "P6": "Wildland Pass / Greyfell area",
    "P7": "Ice Gate",
    "P15": "Desert / Burning Sands",
    "P25": "Godmark / Mountains",
    "P63": "Greyfell",
    "P110": "Whisper",
}

def extract_descriptions_from_strings(game_data: GameData, quest_id: int, desc_id: int):
    """Try to get description from localisation table"""
    if not hasattr(game_data, 'localisation'):
        return None
    
    try:
        for entry in game_data.localisation:
            if hasattr(entry, 'id') and entry.id == desc_id:
                result = {}
                if hasattr(entry, 'texts') and len(entry.texts) > 0:
                    if len(entry.texts) > 0:
                        result['german'] = entry.texts[0]
                    if len(entry.texts) > 1:
                        result['english'] = entry.texts[1]
                return result
    except Exception as e:
        print(f"Error extracting description for quest {quest_id}: {e}")
    
    return None

def extract_map_locations(lua_dir: Path, quest_id: int):
    """Extract map locations from file paths"""
    maps = set()
    
    for lua_file in lua_dir.rglob("*.lua"):
        try:
            with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if f"QuestId = {quest_id}" in content or f"QuestId={quest_id}" in content:
                # Extract map code from path (e.g., script/P1/... -> P1)
                path_str = str(lua_file)
                match = re.search(r'/script/(P\d+)/', path_str)
                if match:
                    map_code = match.group(1)
                    map_name = MAP_NAMES.get(map_code, f"Map {map_code}")
                    maps.add((map_code, map_name))
        except:
            continue
    
    return sorted(maps)

def main():
    quest_ids = [379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 393]
    
    cff_file = project_root / "OriginalGameFiles" / "data" / "GameData.cff"
    lua_dir = project_root / "ModdingTools" / "SpellForceLUASources"
    
    print("=" * 80)
    print("EXTRACTING MAP LOCATIONS AND DESCRIPTIONS")
    print("=" * 80)
    
    # Load CFF
    print(f"\nLoading CFF: {cff_file.name}")
    game_data = GameData(cff_file)
    print("✓ CFF loaded")
    
    results = {}
    
    for quest_id in quest_ids:
        print(f"\n{'='*80}")
        print(f"Quest {quest_id}")
        print(f"{'='*80}")
        
        quest_info = {
            'quest_id': quest_id,
            'name': None,
            'description': None,
            'maps': []
        }
        
        # Get quest from CFF
        if hasattr(game_data, 'quests'):
            for quest in game_data.quests:
                q_id = getattr(quest, 'id', None) or getattr(quest, 'quest_id', None)
                if q_id == quest_id:
                    quest_info['name'] = getattr(quest, 'name', None)
                    desc_id = getattr(quest, 'description_id', None)
                    
                    print(f"Name: {quest_info['name']}")
                    print(f"Description ID: {desc_id}")
                    
                    # Try to get description
                    if desc_id:
                        desc = extract_descriptions_from_strings(game_data, quest_id, desc_id)
                        if desc:
                            quest_info['description'] = desc
                            print(f"Description (DE): {desc.get('german', 'N/A')[:100]}...")
                            print(f"Description (EN): {desc.get('english', 'N/A')[:100]}...")
                        else:
                            print("Description: Not found in localisation table")
                    
                    break
        
        # Get map locations
        maps = extract_map_locations(lua_dir, quest_id)
        quest_info['maps'] = [{'code': code, 'name': name} for code, name in maps]
        
        print(f"\nMap Locations: {len(maps)}")
        for code, name in maps:
            print(f"  - {code}: {name}")
        
        results[quest_id] = quest_info
    
    # Save results
    output_file = project_root / "quest_maps_and_descriptions.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print("EXTRACTION COMPLETE")
    print(f"{'='*80}")
    print(f"Data saved to: {output_file}")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    total_maps = sum(len(q['maps']) for q in results.values())
    quests_with_desc = sum(1 for q in results.values() if q['description'])
    
    print(f"Total quests: {len(results)}")
    print(f"Quests with descriptions: {quests_with_desc}")
    print(f"Total map locations: {total_maps}")
    print(f"Unique maps: {len(set(m['code'] for q in results.values() for m in q['maps']))}")

if __name__ == "__main__":
    main()
