"""
GameData.cff Mod Creator
========================

This is a template script for creating your own mods.
Modify the sections below to create your custom modifications.
"""

from tirganach import GameData
from tirganach.types import *
import os
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

SOURCE_CFF = 'H:/SpellSmut/OriginalGameFiles/data/GameData.cff'
OUTPUT_DIR = 'H:/SpellSmut/ModdedGameFiles'
MOD_NAME = 'MyCustomMod'

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Generate output filename with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
OUTPUT_CFF = f'{OUTPUT_DIR}/GameData_{MOD_NAME}_{timestamp}.cff'

# ============================================================================
# LOAD GAMEDATA
# ============================================================================

print(f"Loading GameData from: {SOURCE_CFF}")
gd = GameData(SOURCE_CFF)
print(f"[OK] Loaded successfully!")
print(f"  - Spells: {len(gd.spells)}")
print(f"  - Items: {len(gd.items)}")
print(f"  - Creatures: {len(gd.creatures)}")
print()

# ============================================================================
# YOUR MODIFICATIONS GO HERE
# ============================================================================

print("=== APPLYING MODIFICATIONS ===\n")

# ----------------------------------------------------------------------------
# Example 1: Boost Ring Stats
# ----------------------------------------------------------------------------
# Uncomment to enable:

# print("1. Boosting ring stats...")
# rings = [item for item in gd.items
#          if item.item_type == ItemType.EQUIPMENT
#          and item.item_subtype == EquipmentType.RING]
#
# for ring in rings:
#     armor_data = gd.armor.where(item_id=ring.item_id)
#     if armor_data:
#         armor = armor_data[0]
#         armor.health = min(armor.health * 2, 2000)  # Double health, cap at 2000
#         armor.mana = min(armor.mana * 2, 2000)      # Double mana, cap at 2000
#
# print(f"   Modified {len(rings)} rings")


# ----------------------------------------------------------------------------
# Example 2: Cheaper Fire Spells
# ----------------------------------------------------------------------------
# Uncomment to enable:

# print("2. Reducing fire spell costs...")
# count = 0
# for spell in gd.spells:
#     if spell.req1_class == School.FIRE:
#         spell.mana_cost = max(1, spell.mana_cost // 2)  # Half cost, minimum 1
#         count += 1
#
# print(f"   Modified {count} fire spells")


# ----------------------------------------------------------------------------
# Example 3: Buff Elf Units
# ----------------------------------------------------------------------------
# Uncomment to enable:

# print("3. Buffing elf units...")
# elf_runes = gd.items.where(
#     item_type=ItemType.RUNE_INVENTORY,
#     item_subtype=RuneRace.ELVES
# )
#
# for rune in elf_runes:
#     if hasattr(rune, 'unit_stats') and rune.unit_stats:
#         rune.unit_stats.strength = min(rune.unit_stats.strength + 20, 150)
#         rune.unit_stats.dexterity = min(rune.unit_stats.dexterity + 20, 150)
#         rune.unit_stats.agility = min(rune.unit_stats.agility + 20, 150)
#
# print(f"   Modified {len(elf_runes)} elf runes")


# ----------------------------------------------------------------------------
# Example 4: Increase Hero XP Gain
# ----------------------------------------------------------------------------
# Uncomment to enable:

# print("4. Increasing hero XP gain...")
# # This would require finding XP multipliers in the levels table
# # (Exact implementation depends on game mechanics)
# for level in gd.levels:
#     # Example: reduce XP needed for each level
#     if hasattr(level, 'xp_required'):
#         level.xp_required = max(1, level.xp_required // 2)
#
# print(f"   Modified {len(gd.levels)} levels")


# ----------------------------------------------------------------------------
# Example 5: Custom Item Names
# ----------------------------------------------------------------------------
# Uncomment to enable:

# print("5. Renaming specific items...")
# ring_of_fools = gd.armor.where(item_id=7065)
# if ring_of_fools:
#     ring_of_fools[0].item.name = "Ring of Awesome"
#     print("   Renamed 'Ring of Fools' to 'Ring of Awesome'")


# ----------------------------------------------------------------------------
# ADD YOUR OWN MODIFICATIONS BELOW
# ----------------------------------------------------------------------------

# Example template:
# print("X. Your modification description...")
# # Your code here
# print("   Done!")


# ============================================================================
# SAVE MODIFIED FILE
# ============================================================================

print("\n=== SAVING MODIFICATIONS ===")
print(f"Output file: {OUTPUT_CFF}")

# Save the modified game data
gd.save(OUTPUT_CFF)

print("[OK] Mod created successfully!")
print()
print("=== NEXT STEPS ===")
print("1. Backup your original GameData.cff file:")
print("   H:\\SpellSmut\\OriginalGameFiles\\data\\GameData.cff")
print()
print("2. Copy the modded file to your game directory:")
print(f"   copy \"{OUTPUT_CFF}\" \"H:\\SpellSmut\\OriginalGameFiles\\data\\GameData.cff\"")
print()
print("3. Launch the game and test your changes")
print()
print("4. If something breaks, restore the backup immediately!")
print()
print("Happy modding! :)")
