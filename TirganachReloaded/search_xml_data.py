"""
GameData.xml Search Tool
========================

Search and display items from the exported GameData.xml file.

Usage:
    python search_xml_data.py
"""

import xml.etree.ElementTree as ET
from tirganach import GameData
from tirganach.types import *

# ============================================================================
# CONFIGURATION
# ============================================================================

XML_FILE = 'H:/SpellSmut/ModdedGameFiles/GameData.xml'
CFF_FILE = 'H:/SpellSmut/OriginalGameFiles/data/GameData.cff'

print("="*80)
print("GameData.xml Search Tool")
print("="*80)
print()

# ============================================================================
# EXAMPLE 1: Find and display a specific ring with all properties
# ============================================================================

print("=== EXAMPLE 1: Ring Item with All Properties ===")
print()

# Load the CFF to get the actual data
gd = GameData(CFF_FILE)

# Find a ring item
rings = [item for item in gd.items
         if item.item_type == ItemType.EQUIPMENT
         and item.item_subtype == EquipmentType.RING]

if rings:
    # Get first ring
    ring_item = rings[0]

    print(f"Item Name: {ring_item.name}")
    print(f"Item ID: {ring_item.item_id}")
    print()

    # Get armor stats for this ring
    armor_data = gd.armor.where(item_id=ring_item.item_id)
    if armor_data:
        armor = armor_data[0]

        print("=== ITEM PROPERTIES ===")
        print()

        # Basic item info
        print(f"  item_id: {ring_item.item_id}")
        print(f"  name: {ring_item.name}")
        print(f"  item_type: {ring_item.item_type}")
        print(f"  item_subtype: {ring_item.item_subtype}")
        print()

        # Armor/stats
        print("=== STATS ===")
        print()
        for field_name in ['health', 'mana', 'stamina', 'strength', 'dexterity',
                           'agility', 'intelligence', 'wisdom', 'charisma']:
            if hasattr(armor, field_name):
                value = getattr(armor, field_name)
                print(f"  {field_name}: {value}")
        print()

        # Resistances
        print("=== RESISTANCES ===")
        print()
        for field_name in ['fire_resistance', 'ice_resistance', 'black_resistance',
                           'mind_resistance']:
            if hasattr(armor, field_name):
                value = getattr(armor, field_name)
                if value and value != 0:
                    print(f"  {field_name}: {value}")

        # All other armor fields
        print()
        print("=== ALL ARMOR FIELDS ===")
        print()
        for field_name in sorted(armor._fields.keys()):
            value = getattr(armor, field_name)
            print(f"  {field_name}: {value}")

print()
print()

# ============================================================================
# EXAMPLE 2: Display all rings with their stats
# ============================================================================

print("=== EXAMPLE 2: All Rings Summary ===")
print()

print(f"Total rings found: {len(rings)}")
print()
print("First 10 rings:")
print()

for i, ring_item in enumerate(rings[:10], 1):
    armor_data = gd.armor.where(item_id=ring_item.item_id)

    if armor_data:
        armor = armor_data[0]
        print(f"{i}. {ring_item.name} (ID: {ring_item.item_id})")
        print(f"   Health: {armor.health}, Mana: {armor.mana}, Stamina: {armor.stamina}")

        # Show non-zero stats
        stats = []
        for stat in ['strength', 'dexterity', 'agility', 'intelligence', 'wisdom']:
            val = getattr(armor, stat, 0)
            if val > 0:
                stats.append(f"{stat}+{val}")

        if stats:
            print(f"   Stats: {', '.join(stats)}")
        print()

print()

# ============================================================================
# EXAMPLE 3: Find legendary/unique items
# ============================================================================

print("=== EXAMPLE 3: High-Value Rings (HP or Mana > 100) ===")
print()

high_value_rings = []
for ring_item in rings:
    armor_data = gd.armor.where(item_id=ring_item.item_id)
    if armor_data:
        armor = armor_data[0]
        if armor.health > 100 or armor.mana > 100:
            high_value_rings.append((ring_item, armor))

print(f"Found {len(high_value_rings)} high-value rings:")
print()

for ring_item, armor in high_value_rings[:10]:
    print(f"- {ring_item.name}")
    print(f"  HP: {armor.health}, Mana: {armor.mana}, Stamina: {armor.stamina}")
    stats = []
    for stat in ['strength', 'dexterity', 'agility', 'intelligence', 'wisdom']:
        val = getattr(armor, stat, 0)
        if val > 0:
            stats.append(f"{stat}+{val}")
    if stats:
        print(f"  Stats: {', '.join(stats)}")
    print()

print()

# ============================================================================
# EXAMPLE 4: Search spells by school
# ============================================================================

print("=== EXAMPLE 4: Fire Spells (Level 20) ===")
print()

fire_spells = gd.spells.where(level=20, req1_class=School.FIRE)

print(f"Found {len(fire_spells)} level 20 fire spells:")
print()

for i, spell in enumerate(fire_spells[:5], 1):
    # Get spell name
    spell_name_data = gd.spell_names.where(spell_name_id=spell.spell_name_id)
    spell_name = spell_name_data[0].name if spell_name_data else "Unknown"

    print(f"{i}. {spell_name} (ID: {spell.spell_id})")
    print(f"   Mana Cost: {spell.mana}")
    print(f"   Cast Time: {spell.cast_time}ms")
    print(f"   Cooldown: {spell.cooldown}ms")
    print(f"   Range: {spell.min_range}-{spell.max_range}")
    print()

print()
print("="*80)
print("Examples complete!")
print()
print("The XML file contains all game data in a human-readable format.")
print(f"You can open it in any text editor: {XML_FILE}")
print()
print("Search tips:")
print("  - Search for '<armor>' to find armor items")
print("  - Search for '<weapon>' to find weapons")
print("  - Search for '<spell>' to find spells")
print("  - Search for 'item_id>' followed by a number to find specific items")
print("="*80)
