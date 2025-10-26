"""
GameData.cff to XML Exporter
=============================

This script exports the entire GameData.cff file to XML format for human-readable viewing.
All game data (items, spells, creatures, etc.) will be exported with all their properties.

Usage:
    python export_to_xml.py

Output:
    Creates GameData.xml in the current directory with all game data.
"""

from tirganach import GameData
from tirganach.types import *
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
from datetime import datetime

def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding='utf-8')

def value_to_string(value):
    """Convert any value to a string representation."""
    if value is None:
        return ""
    elif isinstance(value, (int, float, str, bool)):
        return str(value)
    elif isinstance(value, bytes):
        return value.hex()
    elif hasattr(value, '__class__') and hasattr(value, 'name'):
        # Enum values
        return f"{value.__class__.__name__}.{value.name}"
    elif hasattr(value, 'value'):
        # Other enum-like objects
        return str(value.value)
    else:
        return str(value)

def export_entity_to_xml(entity, parent_element, entity_name):
    """Export a single entity to XML."""
    entity_elem = ET.SubElement(parent_element, entity_name)

    # Add all fields from the entity
    for field_name, field_info in entity._fields.items():
        try:
            value = getattr(entity, field_name)
            value_str = value_to_string(value)

            # Create element for this field
            field_elem = ET.SubElement(entity_elem, field_name)
            field_elem.text = value_str

        except Exception as e:
            # If we can't get the value, add an error note
            field_elem = ET.SubElement(entity_elem, field_name)
            field_elem.text = f"[Error: {str(e)}]"

    return entity_elem

def export_table_to_xml(table, parent_element, table_name):
    """Export an entire table to XML."""
    print(f"  Exporting {table_name}... ({len(table)} entries)")

    table_elem = ET.SubElement(parent_element, table_name)
    table_elem.set('count', str(len(table)))

    for idx, entity in enumerate(table):
        if idx % 100 == 0 and idx > 0:
            print(f"    Progress: {idx}/{len(table)}")

        export_entity_to_xml(entity, table_elem, f'{table_name[:-1]}')  # Remove 's' from plural

    return table_elem

# ============================================================================
# MAIN EXPORT
# ============================================================================

print("="*80)
print("GameData.cff XML Exporter")
print("="*80)
print()

# Configuration
SOURCE_CFF = 'H:/SpellSmut/OriginalGameFiles/data/GameData.cff'
OUTPUT_XML = 'H:/SpellSmut/ModdedGameFiles/GameData.xml'

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_XML), exist_ok=True)

# Load GameData
print(f"Loading GameData from: {SOURCE_CFF}")
gd = GameData(SOURCE_CFF)
print(f"[OK] Loaded successfully!")
print()

# Create root XML element
root = ET.Element('SpellForceGameData')
root.set('source', SOURCE_CFF)
root.set('export_date', datetime.now().isoformat())

# Add summary
summary = ET.SubElement(root, 'Summary')
ET.SubElement(summary, 'TotalSpells').text = str(len(gd.spells))
ET.SubElement(summary, 'TotalItems').text = str(len(gd.items))
ET.SubElement(summary, 'TotalCreatures').text = str(len(gd.creatures))
ET.SubElement(summary, 'TotalBuildings').text = str(len(gd.buildings))
ET.SubElement(summary, 'TotalArmor').text = str(len(gd.armor))
ET.SubElement(summary, 'TotalWeapons').text = str(len(gd.weapons))
ET.SubElement(summary, 'TotalLocalization').text = str(len(gd.localisation))

print("Exporting tables to XML...")
print()

# Export all tables
tables_to_export = [
    ('spells', gd.spells),
    ('spell_names', gd.spell_names),
    ('spell_effects', gd.spell_effects),
    ('items', gd.items),
    ('armor', gd.armor),
    ('weapons', gd.weapons),
    ('item_requirements', gd.item_requirements),
    ('item_effects', gd.item_effects),
    ('item_ui', gd.item_ui),
    ('item_sets', gd.item_sets),
    ('creatures', gd.creatures),
    ('creature_stats', gd.creature_stats),
    ('creature_skills', gd.creature_skills),
    ('creature_equipment', gd.creature_equipment),
    ('creature_spells', gd.creature_spells),
    ('creature_resources', gd.creature_resources),
    ('drops', gd.drops),
    ('buildings', gd.buildings),
    ('building_graphics', gd.building_graphics),
    ('building_requirements', gd.building_requirements),
    ('skills', gd.skills),
    ('skill_requirements', gd.skill_requirements),
    ('heads', gd.heads),
    ('races', gd.races),
    ('localisation', gd.localisation),
    ('descriptions', gd.descriptions),
    ('advanced_descriptions', gd.advanced_descriptions),
    ('quests', gd.quests),
    ('maps', gd.maps),
    ('portals', gd.portals),
    ('levels', gd.levels),
    ('objects', gd.objects),
    ('object_graphics', gd.object_graphics),
    ('object_loot', gd.object_loot),
    ('merchant_inventories', gd.merchant_inventories),
    ('merchant_inventory_items', gd.merchant_inventory_items),
    ('merchant_price_multipliers', gd.merchant_price_multipliers),
    ('resource_names', gd.resource_names),
    ('npc_names', gd.npc_names),
    ('weapon_type_names', gd.weapon_type_names),
    ('weapon_material_names', gd.weapon_material_names),
    ('terrain', gd.terrain),
    ('upgrades', gd.upgrades),
]

for table_name, table in tables_to_export:
    try:
        export_table_to_xml(table, root, table_name)
    except Exception as e:
        print(f"  [ERROR] Failed to export {table_name}: {str(e)}")
        # Add error element
        error_elem = ET.SubElement(root, table_name)
        error_elem.set('error', str(e))

print()
print("Writing XML file...")

# Write to file with pretty formatting
xml_bytes = prettify_xml(root)

with open(OUTPUT_XML, 'wb') as f:
    f.write(xml_bytes)

# Get file size
file_size_mb = os.path.getsize(OUTPUT_XML) / (1024 * 1024)

print()
print("="*80)
print("[OK] Export Complete!")
print("="*80)
print(f"Output file: {OUTPUT_XML}")
print(f"File size: {file_size_mb:.2f} MB")
print()
print("You can now open GameData.xml in any text editor or XML viewer.")
print()
print("Example - View rings:")
print('  Search for: <armor>')
print('  Look for entries with item_subtype: EquipmentType.RING')
print()
print("Example - View spells:")
print('  Search for: <spells>')
print('  Browse all spell entries with their properties')
print()
