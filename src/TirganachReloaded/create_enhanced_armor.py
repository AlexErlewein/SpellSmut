#!/usr/bin/env python3
"""
Create enhanced_armor.json with proper armor names
Similar to how enhanced_weapons.json was created
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from tirganach import GameData
from tirganach.types import Language
from pathlib import Path

def create_enhanced_armor():
    """Create enhanced armor data with proper names"""

    # Load GameData
    project_root = Path(__file__).parent.parent
    cff_path = project_root / "OriginalGameFiles" / "data" / "GameData.cff"

    print(f"Loading GameData.cff from: {cff_path}")
    gd = GameData(str(cff_path))

    print(f"Found {len(gd.armor)} armor pieces")
    print(f"Found {len(gd.items)} items")
    print(f"Found {len(gd.localisation)} localisation entries")

    # Create a lookup for localisation by text_id (for English)
    localisation_lookup = {}
    for loc in gd.localisation:
        if hasattr(loc, 'text_id') and hasattr(loc, 'text') and hasattr(loc, 'language'):
            # Only use English localisation
            if loc.language == Language.ENGLISH:
                localisation_lookup[loc.text_id] = loc.text

    print(f"Created localisation lookup with {len(localisation_lookup)} entries")

    # Create enhanced armor data
    enhanced_armor = []

    for armor in gd.armor:
        armor_entry = {}

        # Get item_id
        item_id = getattr(armor, 'item_id', None)
        if item_id is None:
            continue

        armor_entry['item_id'] = item_id

        # Find corresponding item to get name_id
        item_data = None
        for item in gd.items:
            if getattr(item, 'item_id', None) == item_id:
                item_data = item
                break

        if item_data:
            # Get name_id from item
            name_id = getattr(item_data, 'name_id', None)
            armor_entry['name_id'] = name_id

            # Look up the actual name from localisation
            if name_id and name_id in localisation_lookup:
                armor_entry['name'] = localisation_lookup[name_id]
            else:
                armor_entry['name'] = f"Armor {item_id}"

            # Get item type info
            item_type = getattr(item_data, 'item_type', None)
            if item_type and hasattr(item_type, 'name'):
                armor_entry['item_type'] = item_type.name
            else:
                armor_entry['item_type'] = str(item_type) if item_type else "EQUIPMENT"

            item_subtype = getattr(item_data, 'item_subtype', None)
            if item_subtype and hasattr(item_subtype, 'name'):
                armor_entry['item_subtype'] = item_subtype.name
            else:
                armor_entry['item_subtype'] = str(item_subtype) if item_subtype else "ARMOR"
        else:
            armor_entry['name'] = f"Armor {item_id}"
            armor_entry['name_id'] = None
            armor_entry['item_type'] = "EQUIPMENT"
            armor_entry['item_subtype'] = "ARMOR"

        # Add armor stats
        armor_entry['strength'] = getattr(armor, 'strength', 0)
        armor_entry['stamina'] = getattr(armor, 'stamina', 0)
        armor_entry['agility'] = getattr(armor, 'agility', 0)
        armor_entry['dexterity'] = getattr(armor, 'dexterity', 0)
        armor_entry['health'] = getattr(armor, 'health', 0)
        armor_entry['charisma'] = getattr(armor, 'charisma', 0)
        armor_entry['intelligence'] = getattr(armor, 'intelligence', 0)
        armor_entry['wisdom'] = getattr(armor, 'wisdom', 0)
        armor_entry['mana'] = getattr(armor, 'mana', 0)
        armor_entry['armor'] = getattr(armor, 'armor', 0)
        armor_entry['resist_fire'] = getattr(armor, 'resist_fire', 0)
        armor_entry['resist_ice'] = getattr(armor, 'resist_ice', 0)
        armor_entry['resist_black'] = getattr(armor, 'resist_black', 0)
        armor_entry['resist_mind'] = getattr(armor, 'resist_mind', 0)
        armor_entry['speed_run'] = getattr(armor, 'speed_run', 0)
        armor_entry['speed_fight'] = getattr(armor, 'speed_fight', 0)
        armor_entry['speed_cast'] = getattr(armor, 'speed_cast', 0)

        enhanced_armor.append(armor_entry)

    # Sort by item_id
    enhanced_armor.sort(key=lambda x: x['item_id'])

    # Save to JSON
    output_path = Path(__file__).parent / "enhanced_armor.json"
    print(f"Saving enhanced armor data to: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enhanced_armor, f, indent=2, ensure_ascii=False)

    print(f"Created enhanced armor data with {len(enhanced_armor)} entries")

    # Show sample
    if enhanced_armor:
        print("\nSample enhanced armor entries:")
        for i, armor in enumerate(enhanced_armor[:5]):
            print(f"  {i+1}. ID {armor['item_id']}: '{armor['name']}' (Armor: {armor['armor']})")

if __name__ == "__main__":
    create_enhanced_armor()