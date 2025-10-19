"""
SpellForce GameData.cff Modding Examples
========================================

This script demonstrates how to use the tirganach library to:
1. Load the GameData.cff file
2. Query and filter game data (items, spells, creatures, etc.)
3. Modify existing data
4. Save the modified file

NOTE: Always backup your original GameData.cff before making changes!
"""

from tirganach import GameData
from tirganach.types import *

# ============================================================================
# LOADING THE FILE
# ============================================================================

print("Loading GameData.cff...")
gd = GameData('H:/SpellSmut/OriginalGameFiles/data/GameData.cff')
print("[OK] Loaded successfully!\n")


# ============================================================================
# EXAMPLE 1: Finding and modifying items
# ============================================================================

print("=== EXAMPLE 1: Modifying Item Stats ===")

# Find all rings (equipment type 6)
rings = [item for item in gd.items if item.item_type == ItemType.EQUIPMENT and item.item_subtype == EquipmentType.RING]
print(f"Found {len(rings)} rings in the game")

# Find a specific ring by ID
ring = gd.armor.where(item_id=7065)
if ring:
    ring = ring[0]
    print(f"Original ring: {ring.item.name}")
    print(f"  Health: {ring.health}")
    print(f"  Mana: {ring.mana}")

    # Modify the stats (example - don't save unless you want this!)
    # ring.health = 500
    # ring.mana = 500
    # ring.item.name = "Ring of Ultimate Power"
    print("  (To modify, uncomment the lines above)")


# ============================================================================
# EXAMPLE 2: Finding spells by school and level
# ============================================================================

print("\n=== EXAMPLE 2: Finding Fire Spells ===")

# Find all level 20 fire spells
fire_spells = gd.spells.where(level=20, req1_class=School.FIRE)
print(f"Found {len(fire_spells)} level 20 fire spells:")
for i, spell in enumerate(fire_spells[:5], 1):
    print(f"  {i}. {spell}")


# ============================================================================
# EXAMPLE 3: Browsing creatures
# ============================================================================

print("\n=== EXAMPLE 3: Creature Information ===")

# Show first 10 creatures
print("First 10 creatures in the database:")
for i, creature in enumerate(gd.creatures[:10], 1):
    print(f"  {i}. {creature}")


# ============================================================================
# EXAMPLE 4: Working with hero units
# ============================================================================

print("\n=== EXAMPLE 4: Hero Units ===")

# Find hero rune items
hero_items = gd.items.where(item_type=ItemType.RUNE_INVENTORY)
print(f"Found {len(hero_items)} hero rune items")

# Example: Modify a hero (careful - this changes game balance!)
# sondra = gd.items.where(item_id=4425)
# if sondra:
#     sondra = sondra[0]
#     print(f"Found hero: {sondra.name}")
#     # Modify hero stats
#     # sondra.unit_stats.size = 90
#     # sondra.unit_stats.skills[0].set(skill_school=School.LIGHT_COMBAT, skill_level=20)


# ============================================================================
# EXAMPLE 5: Finding items by race
# ============================================================================

print("\n=== EXAMPLE 5: Race-Specific Items ===")

# Find all elf rune workers/warriors
elf_runes = gd.items.where(item_type=ItemType.RUNE_INVENTORY, item_subtype=RuneRace.ELVES)
print(f"Found {len(elf_runes)} elf rune items")


# ============================================================================
# EXAMPLE 6: Buildings
# ============================================================================

print("\n=== EXAMPLE 6: Buildings ===")

print(f"Total buildings in game: {len(gd.buildings)}")
print("First 10 buildings:")
for i, building in enumerate(gd.buildings[:10], 1):
    print(f"  {i}. {building}")


# ============================================================================
# EXAMPLE 7: Localization strings
# ============================================================================

print("\n=== EXAMPLE 7: Localization ===")

# Find English text entries
english_texts = [loc for loc in gd.localisation if loc.language == Language.ENGLISH][:5]
print(f"Sample English localization entries:")
for i, text in enumerate(english_texts, 1):
    print(f"  {i}. ID {text.text_id}: {text.text[:50]}...")  # First 50 chars


# ============================================================================
# SAVING CHANGES
# ============================================================================

print("\n=== SAVING CHANGES ===")
print("To save your modifications:")
print("  gd.save('H:/SpellSmut/ModdedGameFiles/GameData_modified.cff')")
print("\nIMPORTANT:")
print("  1. Always backup the original file first!")
print("  2. Test modifications in a separate directory")
print("  3. Some changes may crash the game if done incorrectly")
print("  4. Start with small changes and test frequently")

# Uncomment to actually save (DANGEROUS - will overwrite!)
# gd.save('H:/SpellSmut/ModdedGameFiles/GameData_modified.cff')
