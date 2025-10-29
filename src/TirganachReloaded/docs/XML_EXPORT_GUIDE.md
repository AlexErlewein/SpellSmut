# GameData.cff XML Export - Complete Guide

## Summary

✅ The entire GameData.cff file has been successfully exported to human-readable XML format!

**Output File:** `H:\SpellSmut\ModdedGameFiles\GameData.xml` (64 MB)

---

## What Was Exported

### Complete Game Database

The XML file contains **ALL** game data from GameData.cff:

| Table | Entries | What It Contains |
|-------|---------|------------------|
| **spells** | 3,455 | All spells with properties |
| **spell_names** | 235 | Spell names |
| **spell_effects** | 1,918 | Spell effect data |
| **items** | 7,101 | All items (base data) |
| **armor** | 635 | Armor/ring stats (HP, Mana, etc.) |
| **weapons** | 721 | Weapon stats (damage, etc.) |
| **item_requirements** | 4,105 | Item usage requirements |
| **item_effects** | 4,030 | Item bonuses and effects |
| **item_ui** | 8,311 | Item UI/inventory data |
| **item_sets** | 19 | Item set bonuses |
| **creatures** | 2,617 | All units/monsters |
| **creature_stats** | 2,536 | Unit stat blocks |
| **creature_skills** | 1,374 | Unit skill levels |
| **creature_equipment** | 5,905 | Unit equipment |
| **creature_spells** | 791 | Unit spell lists |
| **creature_resources** | 128 | Resource costs |
| **drops** | 1,360 | Loot tables |
| **buildings** | 207 | All buildings |
| **building_graphics** | 2,857 | Building visuals |
| **building_requirements** | 166 | Building prerequisites |
| **skills** | 48 | Skill definitions |
| **skill_requirements** | 140 | Skill prerequisites |
| **heads** | 1,024 | Character head models |
| **races** | 129 | Race definitions |
| **localisation** | 176,318 | All text strings (!) |
| **descriptions** | 660 | Item/spell descriptions |
| **advanced_descriptions** | 463 | Extended descriptions |
| **quests** | 308 | Quest data |
| **maps** | 58 | Map definitions |
| **portals** | 80 | Portal locations |
| **levels** | 48 | Level/XP data |
| **objects** | 2,223 | Map objects |
| **object_graphics** | 130 | Object visuals |
| **object_loot** | 2,006 | Object loot tables |
| **merchant_inventories** | 22 | Merchant shops |
| **merchant_inventory_items** | 1,942 | Items sold |
| **merchant_price_multipliers** | 100 | Price adjustments |
| **resource_names** | 3 | Resource names |
| **npc_names** | 3,462 | NPC names |
| **weapon_type_names** | 6 | Weapon type strings |
| **weapon_material_names** | 2 | Material names |
| **terrain** | 13 | Terrain definitions |
| **upgrades** | 76 | Building/unit upgrades |

**Total:** 43 tables with complete data!

---

## Example: Ring Item Data

Here's what a ring item looks like in the XML:

```xml
<armor>
  <item_id>531</item_id>
  <health>0</health>
  <mana>0</mana>
  <stamina>0</stamina>
  <strength>0</strength>
  <dexterity>0</dexterity>
  <agility>0</agility>
  <intelligence>0</intelligence>
  <wisdom>0</wisdom>
  <charisma>5</charisma>
  <armor>1</armor>
  <resist_fire>0</resist_fire>
  <resist_ice>0</resist_ice>
  <resist_black>0</resist_black>
  <resist_mind>0</resist_mind>
  <speed_cast>0</speed_cast>
  <speed_fight>0</speed_fight>
  <speed_run>0</speed_run>
</armor>
```

And the corresponding item entry:

```xml
<item>
  <item_id>531</item_id>
  <name>Soulguard</name>
  <item_type>ItemType.EQUIPMENT</item_type>
  <item_subtype>EquipmentType.RING</item_subtype>
  ...other properties...
</item>
```

---

## How to View the Data

### Option 1: Text Editor

Open `GameData.xml` in any text editor:
- **Notepad++** (recommended for large files)
- **VS Code**
- **Sublime Text**
- **Notepad** (will be slow)

### Option 2: XML Viewer

Use a dedicated XML viewer for better navigation:
- **XMLNotepad** (Microsoft)
- **Oxygen XML Editor**
- **Browser** (Firefox, Chrome) - may be slow

### Option 3: Search Tool (Included)

Use the provided search script:

```bash
cd H:\SpellSmut\ModdingTools\TirganachReloaded
python search_xml_data.py
```

This displays formatted examples of:
- Ring items with all properties
- All rings summary
- High-value items
- Fire spells

---

## Searching the XML

### Find Specific Data

**Find all rings:**
- Search for: `<armor>`
- Look for entries with various stat values

**Find a specific item by ID:**
- Search for: `<item_id>531</item_id>`
- This will find item ID 531 (Soulguard ring)

**Find all fire spells:**
- Search for: `<req1_class>School.FIRE</req1_class>`

**Find level 20 spells:**
- Search for: `<req1_level>20</req1_level>`

**Find all creatures:**
- Search for: `<creatures count=`
- Browse through creature entries

**Find text strings:**
- Search for: `<localisation count=`
- Browse 176,318 localization entries

---

## XML Structure

### File Format

```xml
<?xml version="1.0" encoding="utf-8"?>
<SpellForceGameData source="..." export_date="...">
  <Summary>
    <TotalSpells>3455</TotalSpells>
    <TotalItems>7101</TotalItems>
    ...
  </Summary>

  <spells count="3455">
    <spell>
      <spell_id>1</spell_id>
      <spell_name_id>1</spell_name_id>
      ...
    </spell>
    ...
  </spells>

  <items count="7101">
    <item>
      <item_id>1</item_id>
      <name>Item Name</name>
      ...
    </item>
    ...
  </items>

  ...more tables...

</SpellForceGameData>
```

### Data Types in XML

- **Integers:** `<item_id>531</item_id>`
- **Strings:** `<name>Soulguard</name>`
- **Enums:** `<item_type>ItemType.EQUIPMENT</item_type>`
- **Booleans:** `<is_dialogue>False</is_dialogue>`

---

## Understanding Ring Data

### Ring Properties (from armor table)

| Field | Description |
|-------|-------------|
| `item_id` | Links to item table |
| `health` | HP bonus |
| `mana` | Mana bonus |
| `stamina` | Stamina bonus |
| `strength` | Strength bonus |
| `dexterity` | Dexterity bonus |
| `agility` | Agility bonus |
| `intelligence` | Intelligence bonus |
| `wisdom` | Wisdom bonus |
| `charisma` | Charisma bonus |
| `armor` | Armor value |
| `resist_fire` | Fire resistance |
| `resist_ice` | Ice resistance |
| `resist_black` | Black magic resistance |
| `resist_mind` | Mind magic resistance |
| `speed_cast` | Casting speed modifier |
| `speed_fight` | Attack speed modifier |
| `speed_run` | Movement speed modifier |

### Example Rings from XML

**1. Soulguard (ID: 531)**
- Charisma: +5
- All other stats: 0

**2. Ring of Dawn and Dusk (ID: 555)**
- HP: 0, Mana: 0, Stamina: 4
- All stats: +4 (STR, DEX, AGI, INT, WIS)

**3. Antique Ring (ID: 537)**
- Wisdom: +10
- All other stats: 0

---

## Understanding Spell Data

### Spell Properties

```xml
<spell>
  <spell_id>1</spell_id>
  <spell_name_id>1</spell_name_id>
  <req1_class>School.FIRE</req1_class>
  <req1_level>1</req1_level>
  <mana>15</mana>
  <cast_time>1000</cast_time>
  <cooldown>2000</cooldown>
  <min_range>1</min_range>
  <max_range>15</max_range>
  <effect_power>0</effect_power>
  <effect_range>0</effect_range>
</spell>
```

| Field | Description |
|-------|-------------|
| `spell_id` | Unique spell ID |
| `spell_name_id` | Links to spell_names table |
| `req1_class` | Required magic school |
| `req1_level` | Required skill level |
| `mana` | Mana cost |
| `cast_time` | Casting time (ms) |
| `cooldown` | Cooldown time (ms) |
| `min_range` | Minimum range |
| `max_range` | Maximum range |

---

## Scripts Included

### 1. export_to_xml.py

**Purpose:** Export GameData.cff to XML

**Usage:**
```bash
cd H:\SpellSmut\ModdingTools\TirganachReloaded
python export_to_xml.py
```

**Output:** `H:\SpellSmut\ModdedGameFiles\GameData.xml`

### 2. search_xml_data.py

**Purpose:** Search and display data from XML

**Usage:**
```bash
cd H:\SpellSmut\ModdingTools\TirganachReloaded
python search_xml_data.py
```

**Shows:**
- Ring items with all properties
- All rings summary (120 total)
- High-value rings (HP/Mana > 100)
- Fire spells (level 20)

---

## Use Cases

### For Modders

1. **Research Item Stats**
   - See exactly what bonuses items provide
   - Compare items to design balanced mods

2. **Study Spell Data**
   - Understand mana costs, cooldowns, ranges
   - Design new spells with appropriate values

3. **Analyze Creatures**
   - See stat distributions
   - Design balanced custom units

4. **Browse Localization**
   - Find text IDs for custom items
   - See naming conventions

### For Players

1. **Item Database**
   - Look up ring stats
   - Find best equipment

2. **Spell Reference**
   - Check spell costs
   - See spell requirements

3. **Game Knowledge**
   - Understand game mechanics
   - Discover hidden items

---

## File Size & Performance

**XML File:** 64 MB (human-readable format)
**Original CFF:** 97 MB (binary format)

The XML is actually smaller due to:
- Text compression (enums as strings)
- Readable formatting
- No binary overhead

**Opening Tips:**
- Use Notepad++ for best performance
- Search is fast in most editors
- May take a few seconds to load initially

---

## Advanced: XML to CFF Conversion

**Can I convert XML back to CFF?**

Not directly from this export. The XML is for **viewing only**.

To modify game data:
1. Use the Python scripts (recommended)
2. Edit with `create_mod.py`
3. Save changes with `gd.save()`

The XML is a **read-only snapshot** for research and reference.

---

## Search Examples

### Find All +Wisdom Rings

Search for: `<wisdom>10</wisdom>` in the armor section

### Find Powerful Items

Search for: `<health>` with values > 100

### Find Quest Items

Search for: `ItemType.QUEST_ITEM`

### Find Localized Text

Search for specific text in `<localisation>` section

---

## Summary

✅ **Complete database exported to XML**
✅ **All 43 tables included**
✅ **Human-readable format**
✅ **64 MB file size**
✅ **Search scripts included**

You now have a complete, searchable reference of all SpellForce game data!

---

## Files Created

| File | Purpose | Location |
|------|---------|----------|
| **GameData.xml** | Complete game data | `ModdedGameFiles/` |
| **export_to_xml.py** | Export script | `ModdingTools/TirganachReloaded/` |
| **search_xml_data.py** | Search tool | `ModdingTools/TirganachReloaded/` |
| **XML_EXPORT_GUIDE.md** | This guide | Project root |

---

**Enjoy exploring the game data!** 🎮

*For modding, use the Python scripts. For research, use the XML file.*
