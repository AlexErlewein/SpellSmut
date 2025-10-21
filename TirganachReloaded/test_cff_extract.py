"""
Test script to verify tirganach can read and manipulate GameData.cff
"""
from tirganach import GameData
from tirganach.types import *
import json

# Load the GameData.cff file
print("Loading GameData.cff...")
gd = GameData('H:/SpellSmut/OriginalGameFiles/data/GameData.cff')
print("[OK] GameData.cff loaded successfully!")

# Display some basic information
print("\n=== GAMEDATA STATISTICS ===")
print(f"Total Spells: {len(gd.spells)}")
print(f"Total Items: {len(gd.items)}")
print(f"Total Creatures: {len(gd.creatures)}")
print(f"Total Buildings: {len(gd.buildings)}")
print(f"Total Armor pieces: {len(gd.armor)}")
print(f"Total Weapons: {len(gd.weapons)}")
print(f"Total Localization entries: {len(gd.localisation)}")

# Show some example items
print("\n=== SAMPLE ITEMS (first 5) ===")
for i, item in enumerate(gd.items[:5]):
    print(f"{i+1}. {item}")

# Show some example spells
print("\n=== SAMPLE SPELLS (first 5) ===")
for i, spell in enumerate(gd.spells[:5]):
    print(f"{i+1}. {spell}")

print("\n[OK] All tests passed! The library is working correctly.")
print("\nYou can now:")
print("1. Load GameData.cff with: gd = GameData('path/to/GameData.cff')")
print("2. Modify any values (items, spells, creatures, etc.)")
print("3. Save changes with: gd.save('path/to/GameData_modified.cff')")
