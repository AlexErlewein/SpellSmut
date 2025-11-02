#!/usr/bin/env python3
"""
Complete technical extraction of quest data including:
- Quest IDs, names, descriptions from CFF files
- Parent-child relationships
- All dialogue sources from Lua files
- File references and line numbers
"""

import sys
import os
from pathlib import Path
import json
import re

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.tirganach import GameData
from TirganachReloaded.tirganach.types import Language

def load_cff_file(cff_path: Path) -> GameData:
    """Load a CFF file"""
    print(f"Loading CFF file: {cff_path}")
    game_data = GameData()
    game_data.load(str(cff_path))
    return game_data

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

def extract_quest_metadata(game_data: GameData, quest_id: int):
    """Extract complete metadata for a quest from CFF"""
    if not hasattr(game_data, 'quests') or game_data.quests is None:
        return None
    
    for quest in game_data.quests:
        q_id = getattr(quest, 'id', getattr(quest, 'quest_id', None))
        if q_id == quest_id:
            metadata = {
                'quest_id': q_id,
                'parent_id': getattr(quest, 'parent_id', getattr(quest, 'parent_quest_id', None)),
                'name_id': getattr(quest, 'name_id', None),
                'description_id': getattr(quest, 'description_id', None),
                'name': None,
                'description': None,
                'raw_attributes': {}
            }
            
            # Get name and description texts
            if metadata['name_id']:
                metadata['name'] = get_string_by_id(game_data, metadata['name_id'])
            
            if metadata['description_id']:
                metadata['description'] = get_string_by_id(game_data, metadata['description_id'])
            
            # Extract all available attributes
            for attr in dir(quest):
                if not attr.startswith('_'):
                    try:
                        value = getattr(quest, attr)
                        if not callable(value):
                            metadata['raw_attributes'][attr] = str(value)
                    except:
                        pass
            
            return metadata
    
    return None

def search_lua_files_detailed(lua_dir: Path, quest_id: int):
    """Search Lua files and return detailed information about where dialogues are found"""
    results = []
    
    if not lua_dir.exists():
        return results
    
    for lua_file in lua_dir.rglob("*.lua"):
        try:
            with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # Check if this file mentions the quest ID
            file_content = ''.join(lines)
            if f"QuestId = {quest_id}" in file_content or f"QuestId={quest_id}" in file_content:
                file_info = {
                    'file_path': str(lua_file.relative_to(lua_dir)),
                    'absolute_path': str(lua_file),
                    'quest_references': [],
                    'dialogues': []
                }
                
                # Find line numbers where quest is referenced
                for line_num, line in enumerate(lines, 1):
                    if f"QuestId = {quest_id}" in line or f"QuestId={quest_id}" in line:
                        file_info['quest_references'].append({
                            'line_number': line_num,
                            'line_content': line.strip()
                        })
                
                # Extract dialogues with context
                # Outcry pattern
                outcry_matches = re.finditer(
                    r'Outcry\s*{\s*(?:.*?)String\s*=\s*["\']([^"\']+)["\']',
                    file_content,
                    re.DOTALL
                )
                for match in outcry_matches:
                    # Find line number
                    line_num = file_content[:match.start()].count('\n') + 1
                    file_info['dialogues'].append({
                        'type': 'Outcry',
                        'text': match.group(1),
                        'line_number': line_num,
                        'context': lines[line_num-1].strip() if line_num <= len(lines) else ''
                    })
                
                # Dialog pattern
                dialog_matches = re.finditer(
                    r'(?:Dialog|Dialogue|Say|Answer|OfferAnswer)\s*{\s*(?:.*?)(?:Text|String)\s*=\s*["\']([^"\']+)["\']',
                    file_content,
                    re.DOTALL
                )
                for match in dialog_matches:
                    line_num = file_content[:match.start()].count('\n') + 1
                    # Determine type
                    dialog_type = 'Dialog'
                    if 'Say{' in match.group(0):
                        dialog_type = 'Say'
                    elif 'Answer{' in match.group(0):
                        dialog_type = 'Answer'
                    elif 'OfferAnswer{' in match.group(0):
                        dialog_type = 'OfferAnswer'
                    
                    file_info['dialogues'].append({
                        'type': dialog_type,
                        'text': match.group(1),
                        'line_number': line_num,
                        'context': lines[line_num-1].strip() if line_num <= len(lines) else ''
                    })
                
                if file_info['quest_references'] or file_info['dialogues']:
                    results.append(file_info)
        
        except Exception as e:
            print(f"Error reading {lua_file}: {e}")
    
    return results

def extract_all_quest_data(quest_ids: list):
    """Extract complete technical data for all quests"""
    cff_file = project_root / "OriginalGameFiles" / "data" / "GameData.cff"
    lua_dir = project_root / "OriginalGameFiles" / "modding" / "Original Scripts"
    
    if not cff_file.exists():
        cff_file = project_root / "ModdedGameFiles" / "GameData_MyCustomMod_20251019_100557.cff"
    
    print("=" * 80)
    print("COMPLETE TECHNICAL QUEST DATA EXTRACTION")
    print("=" * 80)
    
    # Load CFF data
    try:
        game_data = load_cff_file(cff_file)
        print(f"✓ CFF file loaded successfully")
    except Exception as e:
        print(f"✗ Error loading CFF file: {e}")
        return None
    
    all_quest_data = {
        'extraction_info': {
            'cff_file': str(cff_file),
            'lua_directory': str(lua_dir),
            'total_quests': len(quest_ids)
        },
        'quests': {}
    }
    
    for quest_id in quest_ids:
        print(f"\n{'='*80}")
        print(f"Extracting Quest ID: {quest_id}")
        print(f"{'='*80}")
        
        # Extract CFF metadata
        metadata = extract_quest_metadata(game_data, quest_id)
        
        if metadata:
            print(f"✓ Found in CFF:")
            print(f"  Name ID: {metadata['name_id']}")
            print(f"  Name: {metadata['name']}")
            print(f"  Description ID: {metadata['description_id']}")
            print(f"  Description: {metadata['description'][:100] if metadata['description'] else 'None'}...")
            print(f"  Parent ID: {metadata['parent_id']}")
        else:
            print(f"✗ Not found in CFF")
            metadata = {
                'quest_id': quest_id,
                'parent_id': None,
                'name_id': None,
                'description_id': None,
                'name': None,
                'description': None,
                'raw_attributes': {}
            }
        
        # Extract Lua file references
        lua_files = search_lua_files_detailed(lua_dir, quest_id)
        print(f"✓ Found in {len(lua_files)} Lua file(s)")
        
        for lua_file in lua_files:
            print(f"  - {lua_file['file_path']}")
            print(f"    Quest refs: {len(lua_file['quest_references'])}")
            print(f"    Dialogues: {len(lua_file['dialogues'])}")
        
        all_quest_data['quests'][quest_id] = {
            'cff_metadata': metadata,
            'lua_files': lua_files,
            'total_dialogues': sum(len(f['dialogues']) for f in lua_files),
            'total_files': len(lua_files)
        }
    
    return all_quest_data

def generate_technical_markdown(quest_data: dict, output_file: Path):
    """Generate a technical markdown document with all details"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Amra and Lea Quest - Complete Technical Documentation\n\n")
        f.write("## Extraction Information\n\n")
        f.write(f"- **CFF Source**: `{quest_data['extraction_info']['cff_file']}`\n")
        f.write(f"- **Lua Source**: `{quest_data['extraction_info']['lua_directory']}`\n")
        f.write(f"- **Total Quests Analyzed**: {quest_data['extraction_info']['total_quests']}\n\n")
        
        f.write("---\n\n")
        f.write("## Quest Tree Structure\n\n")
        f.write("```\n")
        
        # Build tree
        quests = quest_data['quests']
        main_quest = None
        subquests = []
        
        for qid, data in quests.items():
            if data['cff_metadata']['parent_id'] is None or data['cff_metadata']['parent_id'] == 0:
                main_quest = (qid, data)
            else:
                subquests.append((qid, data))
        
        if main_quest:
            qid, data = main_quest
            name = data['cff_metadata']['name'] or f"Quest {qid}"
            f.write(f"📜 {name} (ID: {qid})\n")
            
            for sub_qid, sub_data in sorted(subquests, key=lambda x: x[0]):
                sub_name = sub_data['cff_metadata']['name'] or f"Quest {sub_qid}"
                f.write(f"├── 📋 {sub_name} (ID: {sub_qid})\n")
        
        f.write("```\n\n")
        f.write("---\n\n")
        
        # Detailed quest information
        for quest_id in sorted(quests.keys()):
            data = quests[quest_id]
            meta = data['cff_metadata']
            
            f.write(f"## Quest {quest_id}: {meta['name'] or 'Unknown'}\n\n")
            
            # CFF Data
            f.write("### CFF Metadata\n\n")
            f.write(f"- **Quest ID**: {quest_id}\n")
            f.write(f"- **Parent Quest ID**: {meta['parent_id'] or 'None (Main Quest)'}\n")
            f.write(f"- **Name String ID**: {meta['name_id']}\n")
            f.write(f"- **Name**: {meta['name'] or '[Not Found]'}\n")
            f.write(f"- **Description String ID**: {meta['description_id']}\n")
            
            if meta['description']:
                f.write(f"- **Description**:\n")
                f.write(f"  ```\n")
                f.write(f"  {meta['description']}\n")
                f.write(f"  ```\n")
            else:
                f.write(f"- **Description**: [Not Found]\n")
            
            f.write("\n")
            
            # Raw attributes
            if meta['raw_attributes']:
                f.write("#### Raw CFF Attributes\n\n")
                f.write("```\n")
                for attr, value in sorted(meta['raw_attributes'].items()):
                    f.write(f"{attr}: {value}\n")
                f.write("```\n\n")
            
            # Lua Files
            f.write("### Lua File References\n\n")
            
            if data['lua_files']:
                f.write(f"**Total Files**: {data['total_files']}  \n")
                f.write(f"**Total Dialogues**: {data['total_dialogues']}\n\n")
                
                for lua_file in data['lua_files']:
                    f.write(f"#### File: `{lua_file['file_path']}`\n\n")
                    f.write(f"**Absolute Path**: `{lua_file['absolute_path']}`\n\n")
                    
                    # Quest references
                    if lua_file['quest_references']:
                        f.write("**Quest References**:\n\n")
                        for ref in lua_file['quest_references']:
                            f.write(f"- Line {ref['line_number']}: `{ref['line_content']}`\n")
                        f.write("\n")
                    
                    # Dialogues
                    if lua_file['dialogues']:
                        f.write("**Dialogues**:\n\n")
                        
                        # Group by type
                        unique_dialogues = {}
                        for dlg in lua_file['dialogues']:
                            key = (dlg['type'], dlg['text'])
                            if key not in unique_dialogues:
                                unique_dialogues[key] = dlg
                        
                        for (dtype, text), dlg in sorted(unique_dialogues.items(), key=lambda x: x[1]['line_number']):
                            f.write(f"- **{dtype}** (Line {dlg['line_number']}):  \n")
                            f.write(f"  ```\n")
                            f.write(f"  {text}\n")
                            f.write(f"  ```\n")
                            f.write(f"  *Context*: `{dlg['context'][:80]}...`\n\n")
            else:
                f.write("*No Lua files found for this quest ID*\n\n")
            
            f.write("---\n\n")
        
        # Summary statistics
        f.write("## Summary Statistics\n\n")
        
        total_dialogues = sum(q['total_dialogues'] for q in quests.values())
        total_files = sum(q['total_files'] for q in quests.values())
        quests_with_cff = sum(1 for q in quests.values() if q['cff_metadata']['name'] is not None)
        quests_with_desc = sum(1 for q in quests.values() if q['cff_metadata']['description'] is not None)
        
        f.write(f"- **Total Quests**: {len(quests)}\n")
        f.write(f"- **Quests with CFF Data**: {quests_with_cff}\n")
        f.write(f"- **Quests with Descriptions**: {quests_with_desc}\n")
        f.write(f"- **Total Lua Files**: {total_files}\n")
        f.write(f"- **Total Dialogues Extracted**: {total_dialogues}\n")
        f.write(f"- **Unique Dialogue Count**: (See individual quest sections)\n\n")

def main():
    # Quest IDs in order: 379 (main), 380-385, 393, 386-391
    quest_ids = [379, 380, 381, 382, 383, 384, 385, 393, 386, 387, 388, 389, 390, 391]
    
    print("Starting complete technical extraction...")
    quest_data = extract_all_quest_data(quest_ids)
    
    if quest_data:
        # Save raw JSON
        json_output = project_root / "amra_lea_technical_data.json"
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(quest_data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Raw data saved to: {json_output}")
        
        # Generate markdown
        md_output = project_root / "amra_lea_technical_documentation.md"
        generate_technical_markdown(quest_data, md_output)
        print(f"✓ Technical documentation saved to: {md_output}")
        
        print("\n" + "=" * 80)
        print("EXTRACTION COMPLETE")
        print("=" * 80)

if __name__ == "__main__":
    main()
