# GameData.cff Modding Guide

## Overview

The `GameData.cff` file is the heart of SpellForce's game data. It contains:
- **Spells** (3,455 entries)
- **Items** (7,101 entries)
- **Creatures** (2,617 entries)
- **Buildings** (207 entries)
- **Armor** (635 pieces)
- **Weapons** (721 items)
- **Localization** (176,318 text strings)
- And much more!

This file uses a custom binary format that acts like a relational database.

---

## Tools Required

### TiganachReloaded Python Library

The **tirganach** library (located in `ModdingTools/TiganachReloaded/`) is a complete solution for:
- ✅ **Unpacking** the CFF file into Python objects
- ✅ **Reading and querying** all game data
- ✅ **Modifying** any values
- ✅ **Repacking** the CFF file back to binary format

**Installation:**
```bash
cd H:\SpellSmut\ModdingTools\TiganachReloaded
pip install -e .
```

---

## Quick Start

### 1. Load the GameData.cff File

```python
from tirganach import GameData
from tirganach.types import *

# Load the file
gd = GameData('H:/SpellSmut/OriginalGameFiles/data/GameData.cff')

# Access any table
print(f"Total spells: {len(gd.spells)}")
print(f"Total items: {len(gd.items)}")
```

### 2. Query Data

```python
# Find items by ID
ring = gd.armor.where(item_id=7065)

# Find spells by school and level
fire_spells = gd.spells.where(level=20, req1_class=School.FIRE)

# Find hero runes
heroes = gd.items.where(item_type=ItemType.RUNE_INVENTORY)

# Filter with Python list comprehensions
rings = [item for item in gd.items
         if item.item_type == ItemType.EQUIPMENT
         and item.item_subtype == EquipmentType.RING]
```

### 3. Modify Data

```python
# Modify item stats
ring = gd.armor.where(item_id=7065)[0]
ring.health = 500
ring.mana = 500
ring.item.name = "Ring of Ultimate Power"

# Modify hero skills
hero = gd.items.where(item_id=4425)[0]
hero.unit_stats.skills[0].set(
    skill_school=School.LIGHT_COMBAT,
    skill_level=20
)

# Modify spells (if needed)
spell = gd.spells[0]
spell.level = 25
```

### 4. Save Changes

```python
# IMPORTANT: Always backup the original first!
gd.save('H:/SpellSmut/ModdedGameFiles/GameData_modified.cff')
```

---

## Available Tables

The `GameData` object contains these tables:

| Table Name | Description | Count |
|-----------|-------------|-------|
| `spells` | All spells in the game | 3,455 |
| `spell_names` | Spell name localization | - |
| `spell_effects` | Spell visual/mechanical effects | - |
| `items` | All items (equipment, scrolls, runes, etc.) | 7,101 |
| `armor` | Armor stats (linked to items) | 635 |
| `weapons` | Weapon stats (linked to items) | 721 |
| `item_requirements` | Item usage requirements | - |
| `item_effects` | Item bonuses and effects | - |
| `item_ui` | Item UI/inventory data | - |
| `item_sets` | Item set bonuses | - |
| `creatures` | All creatures/units | 2,617 |
| `creature_stats` | Creature stat blocks | - |
| `creature_skills` | Creature skill levels | - |
| `creature_equipment` | Creature default equipment | - |
| `creature_spells` | Creature spell lists | - |
| `creature_resources` | Resource costs to train | - |
| `drops` | Creature loot tables | - |
| `buildings` | All buildings | 207 |
| `building_graphics` | Building visuals | - |
| `building_requirements` | Building prerequisites | - |
| `skills` | Skill definitions | - |
| `skill_requirements` | Skill prerequisites | - |
| `heads` | Character head models | - |
| `races` | Race definitions | - |
| `localisation` | All text strings | 176,318 |
| `descriptions` | Item/spell descriptions | - |
| `advanced_descriptions` | Extended descriptions | - |
| `quests` | Quest data | - |
| `maps` | Map definitions | - |
| `portals` | Portal locations | - |
| `levels` | Level/XP data | - |
| `objects` | Map objects | - |
| `object_graphics` | Object visuals | - |
| `object_loot` | Object loot tables | - |
| `merchant_inventories` | Merchant shop data | - |
| `merchant_inventory_items` | Items sold by merchants | - |
| `merchant_price_multipliers` | Price adjustments | - |
| `resource_names` | Resource name strings | - |
| `npc_names` | NPC name strings | - |
| `weapon_type_names` | Weapon type strings | - |
| `weapon_material_names` | Material name strings | - |
| `terrain` | Terrain definitions | - |
| `upgrades` | Building/unit upgrades | - |

---

## Common Enums

### ItemType
```python
ItemType.EQUIPMENT           # Armor, weapons, rings, etc.
ItemType.RUNE_INVENTORY      # Worker/warrior runes
ItemType.RUNE_ADDED          # Runes added to monument
ItemType.SCROLL              # Spell scrolls
ItemType.SPELL               # Spell items
ItemType.UNIT_PLAN_INVENTORY # Unit plans in inventory
ItemType.BUILDING_PLAN_INVENTORY  # Building plans
ItemType.QUEST_ITEM          # Quest items
```

### EquipmentType
```python
EquipmentType.HELMET
EquipmentType.UPPER          # Chest armor
EquipmentType.LOWER          # Leg armor
EquipmentType.RING
EquipmentType.ONEHANDED_WEAPON
EquipmentType.TWOHANDED_WEAPON
EquipmentType.SHIELD
EquipmentType.BOW
EquipmentType.FULL_BODY      # Full armor sets
```

### Magic Schools
```python
# Combat skills
School.LIGHT_COMBAT
School.HEAVY_COMBAT
School.RANGED_COMBAT

# Weapon skills
School.LIGHT_BLADE_WEAPONS
School.HEAVY_BLADE_WEAPONS
School.BOWS
School.CROSSBOWS
School.SHIELDS

# Magic schools
School.WHITE_MAGIC
School.LIFE
School.NATURE
School.BOONS

School.ELEMENTAL_MAGIC
School.FIRE
School.ICE
School.EARTH

School.MIND_MAGIC
School.ENCHANTMENT
School.OFFENSIVE
School.DEFENSIVE

School.BLACK_MAGIC
School.DEATH
School.NECROMANCY
School.CURSE
```

### Races
```python
# Playable races
Race.HUMANS
Race.ELVES
Race.DWARVES
Race.TROLLS
Race.ORCS
Race.DARKELVES

# For runes (slightly different)
RuneRace.HEROES
RuneRace.HUMANS
RuneRace.ELVES
RuneRace.DWARVES
RuneRace.ORCS
RuneRace.TROLLS
RuneRace.DARKELVES
```

### Languages
```python
Language.ENGLISH
Language.GERMAN
Language.FRENCH
Language.SPANISH
Language.ITALIAN
```

---

## Practical Examples

### Example 1: Create an Overpowered Ring

```python
from tirganach import GameData
from tirganach.types import *

gd = GameData('H:/SpellSmut/OriginalGameFiles/data/GameData.cff')

# Find a ring to modify
ring = gd.armor.where(item_id=7065)[0]

# Boost its stats
ring.health = 1000
ring.mana = 1000
ring.stamina = 1000
ring.strength = 50
ring.intelligence = 50
ring.wisdom = 50
ring.dexterity = 50
ring.agility = 50

# Rename it
ring.item.name = "Ring of the Gods"

# Save
gd.save('H:/SpellSmut/ModdedGameFiles/GameData_OP.cff')
```

### Example 2: Make Elves Overpowered

```python
# Find all elf rune workers/warriors
elf_runes = gd.items.where(
    item_type=ItemType.RUNE_INVENTORY,
    item_subtype=RuneRace.ELVES
)

# Boost all elf units
for rune in elf_runes:
    if rune.unit_stats:
        rune.unit_stats.set(
            strength=150,
            dexterity=150,
            agility=150,
            intelligence=150,
            wisdom=150
        )

gd.save('H:/SpellSmut/ModdedGameFiles/GameData_ElfPower.cff')
```

### Example 3: Create a Custom Hero

```python
# Find an existing hero to clone
original = gd.items.where(item_id=4425)[0]  # Sondra
custom_hero = original.clone()

# Modify the clone
custom_hero.name = "Princess Azula"
custom_hero.inventory_match.name = "Rune Princess Azula"
custom_hero.unit_stats.head_id = 27
custom_hero.unit_stats.size = 90

# Set skills
custom_hero.unit_stats.skills[0].set(
    skill_school=School.LIGHT_COMBAT,
    skill_level=20
)
custom_hero.unit_stats.skills[1].set(
    skill_school=School.ELEMENTAL_MAGIC,
    skill_level=20
)
custom_hero.unit_stats.skills[2].set(
    skill_school=School.FIRE,
    skill_level=20
)

# Add fire spells
fire_spells = gd.spells.where(level=20, req1_class=School.FIRE)
custom_hero.unit_stats.hero_spells[0].set(spell_id=fire_spells[0].spell_id)
custom_hero.unit_stats.hero_spells[1].set(spell_id=fire_spells[1].spell_id)

# Add to items table
gd.items.append(custom_hero)

gd.save('H:/SpellSmut/ModdedGameFiles/GameData_CustomHero.cff')
```

### Example 4: Modify Spell Costs

```python
# Make all fire spells cheaper
for spell in gd.spells:
    if spell.req1_class == School.FIRE:
        spell.mana_cost = max(1, spell.mana_cost // 2)  # Half cost

gd.save('H:/SpellSmut/ModdedGameFiles/GameData_CheapFire.cff')
```

### Example 5: Modify Localization Text

```python
# Change specific text
text_entry = gd.localisation.where(text_id=100, language=Language.ENGLISH)
if text_entry:
    text_entry[0].text = "My custom text here!"

gd.save('H:/SpellSmut/ModdedGameFiles/GameData_CustomText.cff')
```

---

## Testing Your Mods

### Workflow

1. **Backup Original File**
   ```bash
   copy "H:\SpellSmut\OriginalGameFiles\data\GameData.cff" "H:\SpellSmut\OriginalGameFiles\data\GameData_BACKUP.cff"
   ```

2. **Create Your Mod**
   ```python
   # Your modding script here
   gd.save('H:/SpellSmut/ModdedGameFiles/GameData_modified.cff')
   ```

3. **Test in Game**
   - Copy modified CFF to game directory
   - Launch game
   - Check if mod works
   - **If game crashes:** restore backup immediately

4. **Iterate**
   - Start with small changes
   - Test frequently
   - Build up complexity gradually

### Safety Tips

⚠️ **WARNING:** Incorrect modifications can crash the game!

- ✅ Always backup original files
- ✅ Start with simple stat changes
- ✅ Test after each change
- ✅ Keep backup copies of working mods
- ❌ Don't modify file structure (table order, etc.)
- ❌ Don't delete entities (can break references)
- ❌ Don't exceed string length limits

---

## Comparing Two CFF Files

The tirganach library includes a comparison tool:

```bash
python -m tirganach.compare GameData.cff GameData_modified.cff
```

This will show you exactly what changed between two versions.

---

## Advanced: Adding New Entities

**WARNING:** This is advanced and may cause crashes!

```python
# Clone an existing item
original_ring = gd.armor.where(item_id=7065)[0]
new_ring = original_ring.clone()

# Modify it
new_ring.item.name = "Custom Ring"
new_ring.health = 2000

# Add to table (RISKY - may break references!)
gd.armor.append(new_ring)
gd.items.append(new_ring.item)

# Rebuild indices
gd.armor.create_index()
gd.items.create_index()

gd.save('H:/SpellSmut/ModdedGameFiles/GameData_NewItem.cff')
```

---

## Troubleshooting

### "UnicodeDecodeError" when loading
- This has been patched in the local tirganach installation
- The library now falls back to `latin-1` encoding for problematic strings

### Game crashes after loading modded CFF
- Restore backup immediately
- Check if you:
  - Modified string fields to exceed their length limit
  - Created invalid references (wrong IDs)
  - Changed enum values to invalid numbers
  - Deleted entities that are referenced elsewhere

### Changes don't appear in game
- Verify you copied the modded CFF to the correct location
- Check if the game is using a different CFF (multiple copies?)
- Ensure you saved the file correctly

### "AssertionError" when saving
- You likely exceeded a field's byte limit (e.g., string too long)
- Check the specific field and reduce the value

---

## Resources

### Documentation
- **EXPLANATION.md** - Technical details about CFF file structure
- **README.md** - Quick usage guide for tirganach library
- **cff_modding_examples.py** - Working code examples

### Source Code References
- `tirganach/structure.py` - File format parsing
- `tirganach/entities.py` - Entity definitions (all tables)
- `tirganach/types.py` - Enum definitions (all game constants)
- `tirganach/fields.py` - Field type parsers

### External Projects
- [Hokan-Ashir/SFGameDataEditor](https://github.com/Hokan-Ashir/SFGameDataEditor) - Java-based editor
- [leszekd25/spellforce_data_editor](https://github.com/leszekd25/spellforce_data_editor) - C#-based editor

---

## Next Steps

Now that you can fully unpack, modify, and repack the GameData.cff file:

1. **Explore the data** - Run `test_cff_extract.py` to see what's available
2. **Try examples** - Run `cff_modding_examples.py` to see queries in action
3. **Make small mods** - Start with simple stat changes
4. **Test thoroughly** - Always verify changes work in-game
5. **Share your mods** - Document what you've created!

Happy modding! 🎮
