"""
GameData.cff to JSON Exporter
==============================

This script exports the entire GameData.cff file to JSON format for easy parsing
and programmatic access. All game data (items, spells, creatures, etc.) will be
exported with all their properties.

Usage:
    python export_to_json.py

Output:
    Creates GameData.json in the current directory with all game data.
"""

import json
import os
from datetime import datetime

from tirganach import GameData
from tirganach.types import *


def value_to_serializable(value):
    """Convert any value to a JSON-serializable format."""
    if value is None:
        return None
    elif isinstance(value, (int, float, str, bool)):
        return value
    elif isinstance(value, bytes):
        return value.hex()
    elif hasattr(value, "__class__") and hasattr(value, "name"):
        # Enum values - return both class and name for clarity
        return {
            "_type": "enum",
            "class": value.__class__.__name__,
            "name": value.name,
            "value": value.value if hasattr(value, "value") else None,
        }
    elif hasattr(value, "value"):
        # Other enum-like objects
        return value.value
    else:
        return str(value)


def export_entity_to_dict(entity):
    """Export a single entity to a dictionary."""
    entity_dict = {}

    # Add all fields from the entity
    for field_name, field_info in entity._fields.items():
        try:
            value = getattr(entity, field_name)
            entity_dict[field_name] = value_to_serializable(value)
        except Exception as e:
            # If we can't get the value, add an error note
            entity_dict[field_name] = f"[Error: {str(e)}]"

    return entity_dict


def export_table_to_list(table, table_name):
    """Export an entire table to a list of dictionaries."""
    print(f"  Exporting {table_name}... ({len(table)} entries)")

    result = []
    for idx, entity in enumerate(table):
        if idx % 100 == 0 and idx > 0:
            print(f"    Progress: {idx}/{len(table)}")

        result.append(export_entity_to_dict(entity))

    return result


# ============================================================================
# MAIN EXPORT
# ============================================================================

print("=" * 80)
print("GameData.cff JSON Exporter")
print("=" * 80)
print()

# Configuration
# Use relative paths from script location
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

SOURCE_CFF = project_root / "OriginalGameFiles" / "data" / "GameData.cff"
OUTPUT_JSON = script_dir / "GameData.json"

# Convert to strings for compatibility
SOURCE_CFF = str(SOURCE_CFF)
OUTPUT_JSON = str(OUTPUT_JSON)

# Load GameData
print(f"Loading GameData from: {SOURCE_CFF}")
gd = GameData(SOURCE_CFF)
print("[OK] Loaded successfully!")
print()

# Create root data structure
data = {
    "_metadata": {
        "source": SOURCE_CFF,
        "export_date": datetime.now().isoformat(),
        "format_version": "1.0",
    },
    "_summary": {
        "total_spells": len(gd.spells),
        "total_items": len(gd.items),
        "total_creatures": len(gd.creatures),
        "total_buildings": len(gd.buildings),
        "total_armor": len(gd.armor),
        "total_weapons": len(gd.weapons),
        "total_localization": len(gd.localisation),
    },
}

print("Exporting tables to JSON...")
print()

# Export all tables
tables_to_export = [
    ("spells", gd.spells),
    ("spell_names", gd.spell_names),
    ("spell_effects", gd.spell_effects),
    ("items", gd.items),
    ("armor", gd.armor),
    ("weapons", gd.weapons),
    ("item_requirements", gd.item_requirements),
    ("item_effects", gd.item_effects),
    ("item_ui", gd.item_ui),
    ("item_sets", gd.item_sets),
    ("creatures", gd.creatures),
    ("creature_stats", gd.creature_stats),
    ("creature_skills", gd.creature_skills),
    ("creature_equipment", gd.creature_equipment),
    ("creature_spells", gd.creature_spells),
    ("creature_resources", gd.creature_resources),
    ("drops", gd.drops),
    ("buildings", gd.buildings),
    ("building_graphics", gd.building_graphics),
    ("building_requirements", gd.building_requirements),
    ("skills", gd.skills),
    ("skill_requirements", gd.skill_requirements),
    ("heads", gd.heads),
    ("races", gd.races),
    ("localisation", gd.localisation),
    ("descriptions", gd.descriptions),
    ("advanced_descriptions", gd.advanced_descriptions),
    ("quests", gd.quests),
    ("maps", gd.maps),
    ("portals", gd.portals),
    ("levels", gd.levels),
    ("objects", gd.objects),
    ("object_graphics", gd.object_graphics),
    ("object_loot", gd.object_loot),
    ("merchant_inventories", gd.merchant_inventories),
    ("merchant_inventory_items", gd.merchant_inventory_items),
    ("merchant_price_multipliers", gd.merchant_price_multipliers),
    ("resource_names", gd.resource_names),
    ("npc_names", gd.npc_names),
    ("weapon_type_names", gd.weapon_type_names),
    ("weapon_material_names", gd.weapon_material_names),
    ("terrain", gd.terrain),
    ("upgrades", gd.upgrades),
]

for table_name, table in tables_to_export:
    try:
        data[table_name] = export_table_to_list(table, table_name)
    except Exception as e:
        print(f"  [ERROR] Failed to export {table_name}: {str(e)}")
        data[table_name] = {"_error": str(e), "_count": 0}

print()
print("Writing JSON file...")

# Write to file with pretty formatting
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Get file size
file_size_mb = os.path.getsize(OUTPUT_JSON) / (1024 * 1024)

print()
print("=" * 80)
print("[OK] Export Complete!")
print("=" * 80)
print(f"Output file: {OUTPUT_JSON}")
print(f"File size: {file_size_mb:.2f} MB")
print()
print("You can now load GameData.json in any JSON parser or text editor.")
print()
print("Example Python usage:")
print("  import json")
print('  with open("GameData.json") as f:')
print("      data = json.load(f)")
print('  spells = data["spells"]')
print('  print(f"Total spells: {len(spells)}")')
print()
print("Example - Access first spell:")
print('  first_spell = data["spells"][0]')
print('  print(first_spell["spell_name_id"])')
print()
