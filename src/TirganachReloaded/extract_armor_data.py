#!/usr/bin/env python3
"""
Extract armor data from GameData.cff and create enhanced_armor.json
Similar to how enhanced_weapons.json was created
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from tirganach import GameData
from pathlib import Path

def extract_armor_data():
    """Extract armor data from GameData.cff"""

    # Load GameData
    project_root = Path(__file__).parent.parent
    cff_path = project_root / "OriginalGameFiles" / "data" / "GameData.cff"

    print(f"Loading GameData.cff from: {cff_path}")
    gd = GameData(str(cff_path))

    print(f"Found {len(gd.armor)} armor pieces")

    # Extract armor data
    armor_data = []

    for armor in gd.armor:
        armor_entry = {}

        # Get all fields from the armor object
        for field_name in armor._fields.keys():
            try:
                value = getattr(armor, field_name)
                # Convert to serializable format
                if hasattr(value, 'name'):  # Enum
                    armor_entry[field_name] = value.name
                elif hasattr(value, 'value'):  # Other enum-like
                    armor_entry[field_name] = value.value
                else:
                    armor_entry[field_name] = value
            except Exception as e:
                armor_entry[field_name] = f"[Error: {e}]"

        armor_data.append(armor_entry)

    # Save to JSON
    output_path = Path(__file__).parent / "enhanced_armor.json"
    print(f"Saving armor data to: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(armor_data, f, indent=2, ensure_ascii=False)

    print(f"Extracted {len(armor_data)} armor pieces")

    # Show sample
    if armor_data:
        print("\nSample armor entry:")
        sample = armor_data[0]
        for key, value in list(sample.items())[:10]:  # First 10 fields
            print(f"  {key}: {value}")

if __name__ == "__main__":
    extract_armor_data()