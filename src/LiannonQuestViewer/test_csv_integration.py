#!/usr/bin/env python3
"""
Test script to verify CSV data loading functionality
"""

import csv
from pathlib import Path

def test_csv_loading():
    """Test loading and parsing the CSV data"""
    
    # Get the project root (assuming this script is run from the same directory as the viewer)
    project_root = Path(__file__).parent.parent.parent
    csv_file = project_root / "ModdingTools/SpellForceLUASources/QuestKnowledge/QuestRewards.csv"
    
    print(f"Looking for CSV file at: {csv_file}")
    print(f"CSV file exists: {csv_file.exists()}")
    
    if not csv_file.exists():
        print("ERROR: CSV file not found!")
        return False
    
    try:
        csv_data = {}
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    quest_id = int(row['quest_id']) if row['quest_id'] else None
                    if quest_id is None:
                        continue
                        
                    csv_data[quest_id] = {
                        'quest_name': row['quest_name'],
                        'quest_name_de': row['quest_name_de'],
                        'quest_description_de': row['quest_description_de'],
                        'quest_giver_npc_id': int(row['quest_giver_npc_id']) if row['quest_giver_npc_id'] and row['quest_giver_npc_id'].strip() else None,
                        'quest_giver_name': row['quest_giver_name'],
                        'parent_quest_id': int(row['parent_quest_id']) if row['parent_quest_id'] and row['parent_quest_id'].strip() else None,
                        'xp': int(row['xp']) if row['xp'] and row['xp'].strip() else 0,
                        'gold': int(row['gold']) if row['gold'] and row['gold'].strip() else 0,
                        'silver': int(row['silver']) if row['silver'] and row['silver'].strip() else 0,
                        'copper': int(row['copper']) if row['copper'] and row['copper'].strip() else 0,
                        'items_given': row['items_given'],
                        'items_taken': row['items_taken'],
                    }
                except ValueError as e:
                    print(f"Warning: Skipping row due to parsing error: {e}")
                    print(f"Row data: {row}")
                    continue
        
        print(f"Successfully loaded {len(csv_data)} quest entries from CSV")
        
        # Show some sample data
        print("\nSample quest data from CSV:")
        for i, (quest_id, data) in enumerate(list(csv_data.items())[:5]):
            print(f"Quest {quest_id}:")
            print(f"  Name: {data['quest_name']}")
            print(f"  German Name: {data['quest_name_de']}")
            print(f"  Quest Giver: {data['quest_giver_name']} (ID: {data['quest_giver_npc_id']})")
            print(f"  Rewards: XP={data['xp']}, Gold={data['gold']}, Silver={data['silver']}, Copper={data['copper']}")
            if data['items_given']:
                print(f"  Items Given: {data['items_given']}")
            print()
        
        # Test specific quests that should have good data
        test_quests = [14, 382, 381]  # Some quest IDs from the CSV
        
        print("\nTesting specific quests:")
        for quest_id in test_quests:
            if quest_id in csv_data:
                data = csv_data[quest_id]
                print(f"Quest {quest_id} - {data['quest_name'] or 'Unnamed'}:")
                if data['quest_giver_name']:
                    print(f"  ✓ Has quest giver: {data['quest_giver_name']}")
                if data['xp'] > 0:
                    print(f"  ✓ Has XP reward: {data['xp']}")
                if data['gold'] > 0:
                    print(f"  ✓ Has gold reward: {data['gold']}")
                if data['quest_name_de']:
                    print(f"  ✓ Has German name: {data['quest_name_de']}")
                if data['items_given']:
                    print(f"  ✓ Has items: {data['items_given']}")
                print()
            else:
                print(f"Quest {quest_id}: Not found in CSV")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to load CSV data: {e}")
        return False

if __name__ == "__main__":
    print("Testing CSV Data Loading for Quest Viewer")
    print("=" * 50)
    success = test_csv_loading()
    print("=" * 50)
    if success:
        print("✓ CSV loading test PASSED")
    else:
        print("✗ CSV loading test FAILED")
