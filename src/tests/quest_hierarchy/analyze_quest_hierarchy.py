#!/usr/bin/env python3
"""
Analyze quest hierarchy and location names from CSV data
"""

import csv
from pathlib import Path
from collections import defaultdict

def analyze_quest_hierarchy():
    """Analyze multi-level quest hierarchies"""
    
    project_root = Path(__file__).parent.parent.parent
    csv_file = project_root / "ModdingTools/SpellForceLUASources/QuestKnowledge/QuestRewards.csv"
    
    if not csv_file.exists():
        print("ERROR: CSV file not found!")
        return
    
    # Load quest data
    quests = {}
    parent_to_children = defaultdict(list)
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                quest_id = int(row['quest_id']) if row['quest_id'] else None
                if quest_id is None:
                    continue
                
                parent_id = int(row['parent_quest_id']) if row['parent_quest_id'] and row['parent_quest_id'].strip() else None
                
                quests[quest_id] = {
                    'name': row['quest_name'] or row['quest_name_de'] or f"Quest {quest_id}",
                    'parent_id': parent_id,
                    'platform_name': row['platform_name'],
                    'quest_giver': row['quest_giver_name'],
                }
                
                if parent_id:
                    parent_to_children[parent_id].append(quest_id)
                    
            except (ValueError, KeyError) as e:
                continue
    
    print("=== Quest Hierarchy Analysis ===")
    print(f"Total quests: {len(quests)}")
    print(f"Quests with parents: {len([q for q in quests.values() if q['parent_id']])}")
    print(f"Parent quests with children: {len(parent_to_children)}")
    
    # Find multi-level hierarchies
    print("\n=== Multi-Level Quest Hierarchies ===")
    
    def get_hierarchy_depth(quest_id, depth=0, visited=None):
        """Recursively calculate hierarchy depth"""
        if visited is None:
            visited = set()
        
        if quest_id in visited or depth > 10:  # Prevent infinite loops
            return depth
        
        visited.add(quest_id)
        max_child_depth = depth
        
        for child_id in parent_to_children.get(quest_id, []):
            child_depth = get_hierarchy_depth(child_id, depth + 1, visited)
            max_child_depth = max(max_child_depth, child_depth)
        
        visited.remove(quest_id)
        return max_child_depth
    
    # Find all quest hierarchies with their depths
    hierarchy_depths = {}
    for quest_id in quests:
        if quest_id in parent_to_children:  # Only check quests that have children
            depth = get_hierarchy_depth(quest_id)
            if depth > 1:  # More than one level
                hierarchy_depths[quest_id] = depth
    
    # Sort by depth and show the deepest hierarchies
    for quest_id, depth in sorted(hierarchy_depths.items(), key=lambda x: x[1], reverse=True):
        quest = quests[quest_id]
        print(f"Quest {quest_id} ({quest['name']}): {depth} levels deep")
        
        # Show the hierarchy
        def print_hierarchy(q_id, indent=0):
            if q_id in quests:
                quest_info = quests[q_id]
                print("  " * indent + f"├─ Quest {q_id}: {quest_info['name']}")
                for child_id in sorted(parent_to_children.get(q_id, [])):
                    print_hierarchy(child_id, indent + 1)
        
        print_hierarchy(quest_id)
        print()
    
    # Specifically look for quests 151-155 as mentioned by user
    print("=== Specific Quest Analysis (151-155 range) ===")
    for quest_id in range(151, 156):
        if quest_id in quests:
            quest = quests[quest_id]
            print(f"Quest {quest_id}: {quest['name']}")
            print(f"  Parent: {quest['parent_id']}")
            print(f"  Children: {parent_to_children.get(quest_id, [])}")
            
            # Show if this quest is a child of someone
            for potential_parent, children in parent_to_children.items():
                if quest_id in children:
                    print(f"  Is child of: Quest {potential_parent} ({quests[potential_parent]['name']})")
            print()

def analyze_location_names():
    """Analyze location names and check for German alternatives"""
    
    project_root = Path(__file__).parent.parent.parent
    csv_file = project_root / "ModdingTools/SpellForceLUASources/QuestKnowledge/QuestRewards.csv"
    
    if not csv_file.exists():
        print("ERROR: CSV file not found!")
        return
    
    # Load unique platform names
    platforms = set()
    platform_data = {}
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                platform_id = row['platform_id']
                platform_name = row['platform_name']
                
                if platform_id and platform_name:
                    platforms.add((platform_id, platform_name))
                    if platform_id not in platform_data:
                        platform_data[platform_id] = platform_name
                        
            except (ValueError, KeyError):
                continue
    
    print("=== Location/Platform Names Analysis ===")
    print(f"Unique platforms found: {len(platforms)}")
    
    # Sort by platform ID
    for platform_id, platform_name in sorted(platforms, key=lambda x: int(x[0]) if x[0].isdigit() else 999):
        print(f"  ID {platform_id}: {platform_name}")
    
    # Check if we have any German location names in other files
    print("\n=== Looking for German Location Names ===")
    
    # Check other files in QuestKnowledge directory
    quest_knowledge_dir = project_root / "ModdingTools/SpellForceLUASources/QuestKnowledge"
    for file_path in quest_knowledge_dir.glob("*.md"):
        if "location" in file_path.name.lower() or "platform" in file_path.name.lower():
            print(f"Found potential location file: {file_path.name}")
            # Could read this file to look for German names
    
    # Suggest creating a mapping for German location names
    print("\n=== Suggested German Location Name Mapping ===")
    english_to_german = {
        "liannon": "Liannon",
        "eloni": "Eloni", 
        "leafshade": "Laubschatten",
        "wildland pass": "Wildlandpass",
        "shiel": "Shiel",
        "icegate marsh": "Eispfortensumpf",
        "northern windwalls": "Nördliche Windmauern",
        "southern windwalls": "Südliche Windmauern",
        "stoneblade mountain": "Steinklippenberg",
        "greydusk vale": "Graudämmtal",
        "howling mounds": "Heulende Hügel",
        "whisper": "Flüstern",
        "godwall": "Gottwall",
        "mulandir": "Mulandir",
        "farlorns hope": "Farlorns Hoffnung",
        "the rift": "Der Spalt",
        "southern godmark": "Südliches Gottesmal",
        "nightwhisper dale": "Nachtflüstertal",
        "breathing forest": "Atmender Wald",
        "sharrowdale": "Scharrental",
        "greyfell": "Graufell",
        "swamp city": "Sumpfstadt",
        "onyx shores": "Onyxküsten",
        "empyiria": "Empyria",
        "dryad cove": "Dryadenbucht",
        "red wastes": "Rote Wüsten",
        "raven pass": "Rabenpass",
        "blazing stones": "Flammende Steine",
        "kathai": "Kathai",
        "colloseum": "Kolosseum",
        "blackwater coast": "Schwarzwasser Küste",
        "city of souls": "Stadt der Seelen",
    }
    
    for platform_id in sorted(platform_data.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        english_name = platform_data[platform_id]
        german_name = english_to_german.get(english_name.lower(), english_name)
        print(f"  {platform_id}: {english_name} -> {german_name}")

if __name__ == "__main__":
    analyze_quest_hierarchy()
    print("\n" + "="*60 + "\n")
    analyze_location_names()
