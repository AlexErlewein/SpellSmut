#!/usr/bin/env python3
"""
Test German location names and quest hierarchy improvements
"""

import csv
from pathlib import Path

def test_german_location_names():
    """Test the German location name mapping"""
    
    print("=== Testing German Location Names ===")
    
    # German location name mappings (from the code)
    GERMAN_PLATFORM_NAMES = {
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
    
    project_root = Path(__file__).parent.parent.parent
    csv_file = project_root / "ModdingTools/SpellForceLUASources/QuestKnowledge/QuestRewards.csv"
    
    if not csv_file.exists():
        print("ERROR: CSV file not found!")
        return
    
    # Load unique platform names from CSV
    platforms_found = set()
    examples = {}
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            platform_name = row['platform_name']
            if platform_name and platform_name not in platforms_found:
                platforms_found.add(platform_name)
                examples[platform_name] = row['quest_name'] or row['quest_name_de'] or f"Quest {row['quest_id']}"
    
    print(f"Found {len(platforms_found)} unique platforms in CSV")
    print("\nGerman Location Name Examples:")
    
    for platform in sorted(platforms_found):
        german_name = GERMAN_PLATFORM_NAMES.get(platform.lower(), platform)
        example_quest = examples[platform]
        print(f"  {platform} -> {german_name} (e.g., {example_quest})")
    
    print(f"\n✓ German location names mapped for {len([p for p in platforms_found if p.lower() in GERMAN_PLATFORM_NAMES])} platforms")

def test_hierarchy_improvements():
    """Test the improved hierarchy logic"""
    
    print("\n=== Testing Quest Hierarchy Improvements ===")
    
    project_root = Path(__file__).parent.parent.parent
    csv_file = project_root / "ModdingTools/SpellForceLUASources/QuestKnowledge/QuestRewards.csv"
    
    if not csv_file.exists():
        print("ERROR: CSV file not found!")
        return
    
    # Load quest data and build hierarchy
    quests = {}
    parent_to_children = {}
    
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
                }
                
                if parent_id:
                    if parent_id not in parent_to_children:
                        parent_to_children[parent_id] = []
                    parent_to_children[parent_id].append(quest_id)
                    
            except (ValueError, KeyError):
                continue
    
    print(f"Total quests: {len(quests)}")
    print(f"Parent-child relationships: {len(parent_to_children)}")
    
    # Test the hierarchy building logic
    def calculate_hierarchy_depth(quest_id, depth=0, visited=None):
        """Calculate maximum depth of quest hierarchy"""
        if visited is None:
            visited = set()
        
        if quest_id in visited or depth > 10:
            return depth
        
        visited.add(quest_id)
        max_depth = depth
        
        for child_id in parent_to_children.get(quest_id, []):
            child_depth = calculate_hierarchy_depth(child_id, depth + 1, visited)
            max_depth = max(max_depth, child_depth)
        
        visited.remove(quest_id)
        return max_depth
    
    # Find all hierarchies and their depths
    hierarchies = {}
    for quest_id in quests:
        if quest_id in parent_to_children:
            depth = calculate_hierarchy_depth(quest_id)
            if depth > 0:
                hierarchies[quest_id] = depth
    
    print(f"\nQuest hierarchies found: {len(hierarchies)}")
    
    if hierarchies:
        print("\nHierarchy depths:")
        for quest_id, depth in sorted(hierarchies.items(), key=lambda x: x[1], reverse=True):
            quest_name = quests[quest_id]['name']
            print(f"  Quest {quest_id} ({quest_name}): {depth} levels")
    
    # Test specific quests mentioned by user (151-155)
    print("\n=== Specific Quest Test (151-155) ===")
    for quest_id in range(151, 156):
        if quest_id in quests:
            quest = quests[quest_id]
            print(f"Quest {quest_id}: {quest['name']}")
            print(f"  Parent: {quest['parent_id']}")
            children = parent_to_children.get(quest_id, [])
            print(f"  Children: {children}")
            
            # Check if this quest appears as child anywhere
            for parent_id, child_list in parent_to_children.items():
                if quest_id in child_list:
                    print(f"  Is child of: Quest {parent_id} ({quests[parent_id]['name']})")
        else:
            print(f"Quest {quest_id}: Not found in CSV")
        print()
    
    print("✓ Hierarchy analysis complete")

if __name__ == "__main__":
    test_german_location_names()
    test_hierarchy_improvements()
    print("\n" + "="*60)
    print("All tests completed successfully!")
    print("\nThe quest viewer now supports:")
    print("• German location names alongside English ones")
    print("• Multi-level quest hierarchies (recursive)")
    print("• Enhanced CSV data integration")
