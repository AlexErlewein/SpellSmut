# GameData.json Export Guide

This guide explains how to export and use the GameData.cff file in JSON format for easier analysis and programmatic access.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Exporting to JSON](#exporting-to-json)
3. [JSON Structure](#json-structure)
4. [Using the JSON Data](#using-the-json-data)
5. [Performance Comparison](#performance-comparison)
6. [Common Use Cases](#common-use-cases)
7. [Tips and Best Practices](#tips-and-best-practices)

---

## Quick Start

### Export GameData.cff to JSON

```bash
cd src/TiganachReloaded
python3 export_to_json.py
```

This creates `GameData.json` (~73 MB) with all game data.

### Use the JSON Data

```python
import json

with open("GameData.json") as f:
    data = json.load(f)

# Access data
spells = data["spells"]
items = data["items"]
creatures = data["creatures"]

print(f"Total spells: {len(spells)}")
```

---

## Exporting to JSON

### Script: `export_to_json.py`

The export script reads `GameData.cff` and converts it to JSON format.

**Features:**
- Exports all game tables (40+ tables)
- Converts enums to readable format
- Includes metadata (source file, export date)
- Provides summary statistics
- Pretty-printed JSON (2-space indent)

**Configuration:**

The script automatically detects paths relative to the project:
- **Input:** `OriginalGameFiles/data/GameData.cff`
- **Output:** `src/TiganachReloaded/GameData.json`

### What Gets Exported

All game data tables are exported:

| Category | Tables |
|----------|--------|
| **Spells** | spells, spell_names, spell_effects |
| **Items** | items, armor, weapons, item_requirements, item_effects, item_ui, item_sets |
| **Creatures** | creatures, creature_stats, creature_skills, creature_equipment, creature_spells, creature_resources |
| **Buildings** | buildings, building_graphics, building_requirements |
| **Skills** | skills, skill_requirements |
| **World** | maps, portals, levels, objects, object_graphics, object_loot, terrain, quests |
| **NPCs** | drops, merchant_inventories, merchant_inventory_items, merchant_price_multipliers |
| **Localization** | localisation, descriptions, advanced_descriptions |
| **Misc** | heads, races, upgrades, resource_names, npc_names, weapon_type_names, weapon_material_names |

---

## JSON Structure

### Root Object

```json
{
  "_metadata": {
    "source": "/path/to/GameData.cff",
    "export_date": "2025-10-20T07:36:15.435184",
    "format_version": "1.0"
  },
  "_summary": {
    "total_spells": 3455,
    "total_items": 7101,
    "total_creatures": 2617,
    "total_buildings": 207,
    "total_armor": 635,
    "total_weapons": 721,
    "total_localization": 176318
  },
  "spells": [...],
  "items": [...],
  "creatures": [...]
}
```

### Data Tables

Each table is an array of objects:

```json
"spells": [
  {
    "spell_id": 1,
    "spell_name_id": 1,
    "mana": 15,
    "cast_time": 1000,
    "cooldown": 2000,
    "min_range": 1,
    "max_range": 15,
    ...
  },
  ...
]
```

### Enum Values

Enums are exported with full context:

```json
"req1_class": {
  "_type": "enum",
  "class": "School",
  "name": "FIRE",
  "value": [5, 1]
}
```

**Fields:**
- `_type`: Always "enum"
- `class`: Enum class name (e.g., "School", "ItemType")
- `name`: Enum member name (e.g., "FIRE", "WEAPON")
- `value`: Internal value (usually array or integer)

### Special Values

- `null`: Missing/empty values
- `"[Error: ...]"`: Fields that couldn't be read
- Hex strings: Binary data (e.g., `"a1b2c3d4"`)

---

## Using the JSON Data

### Loading the Data

```python
import json
from pathlib import Path

# Load GameData.json
json_path = Path("GameData.json")
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)
```

### Accessing Tables

```python
# Get all spells
spells = data["spells"]

# Get all items
items = data["items"]

# Get summary
summary = data["_summary"]
print(f"Total spells: {summary['total_spells']}")
```

### Filtering Data

#### Find Spells by School

```python
def find_fire_spells(data, min_level=1, max_level=10):
    """Find all Fire magic spells in level range"""
    results = []
    
    for spell in data["spells"]:
        req1 = spell.get("req1_class", {})
        
        # Check if it's a Fire spell
        if isinstance(req1, dict) and req1.get("name") == "FIRE":
            level = spell.get("req1_level", 0)
            if min_level <= level <= max_level:
                results.append(spell)
    
    return results

# Usage
fire_spells = find_fire_spells(data, min_level=5, max_level=10)
print(f"Found {len(fire_spells)} fire spells")
```

#### Find Items by Type

```python
def find_items_by_type(data, item_type_name):
    """Find all items of a specific type"""
    results = []
    
    for item in data["items"]:
        item_type = item.get("item_type", {})
        
        if isinstance(item_type, dict) and item_type.get("name") == item_type_name:
            results.append(item)
    
    return results

# Find all weapons
weapons = find_items_by_type(data, "WEAPON")
print(f"Found {len(weapons)} weapons")
```

#### Find Powerful Armor

```python
def find_powerful_armor(data, min_total_stats=100):
    """Find armor with high stat bonuses"""
    results = []
    
    for armor in data["armor"]:
        # Sum all stat bonuses
        strength = armor.get("strength", 0) or 0
        dexterity = armor.get("dexterity", 0) or 0
        intelligence = armor.get("intelligence", 0) or 0
        agility = armor.get("agility", 0) or 0
        
        total = strength + dexterity + intelligence + agility
        
        if total >= min_total_stats:
            results.append({
                "item_id": armor.get("item_id"),
                "total_stats": total,
                "strength": strength,
                "dexterity": dexterity,
                "intelligence": intelligence,
                "agility": agility
            })
    
    # Sort by total stats
    results.sort(key=lambda x: x["total_stats"], reverse=True)
    return results

# Find epic armor
epic_armor = find_powerful_armor(data, min_total_stats=100)
```

### Lookup Tables

Create lookup dictionaries for fast access:

```python
# Create spell lookup by ID
spell_by_id = {spell["spell_id"]: spell for spell in data["spells"]}

# Get spell #42
spell_42 = spell_by_id[42]

# Create localization lookup
loc_by_id = {
    loc["text_id"]: loc["text"] 
    for loc in data["localisation"]
    if loc.get("text_id") is not None
}

# Get localized text
spell_name = loc_by_id.get(spell_42["spell_name_id"], "Unknown")
```

### Cross-Referencing Tables

```python
def get_spell_with_name(data, spell_id):
    """Get spell with its localized name"""
    
    # Create lookups
    spells = {s["spell_id"]: s for s in data["spells"]}
    spell_names = {n["spell_name_id"]: n for n in data["spell_names"]}
    localisation = {l["text_id"]: l for l in data["localisation"]}
    
    # Get spell
    spell = spells.get(spell_id)
    if not spell:
        return None
    
    # Get spell name entry
    name_id = spell.get("spell_name_id")
    spell_name = spell_names.get(name_id)
    if not spell_name:
        return spell
    
    # Get localized text
    text_id = spell_name.get("name_id")
    loc_entry = localisation.get(text_id)
    
    return {
        **spell,
        "localized_name": loc_entry.get("text") if loc_entry else "Unknown"
    }

# Usage
spell_with_name = get_spell_with_name(data, 1)
print(f"Spell: {spell_with_name['localized_name']}")
```

---

## Performance Comparison

### Loading Time

| Format | Load Time | Memory Usage |
|--------|-----------|--------------|
| GameData.cff (via tirganach) | ~30-60 seconds | ~500 MB |
| GameData.json | ~2-3 seconds | ~300 MB |
| GameData.xml | ~10-15 seconds | ~400 MB |

**Recommendation:** Use JSON for read-only analysis and queries. Use `.cff` (via tirganach) for modifications.

### Query Performance

JSON allows fast filtering with Python list comprehensions:

```python
# Find all level 10 fire spells (executes in milliseconds)
fire_10 = [
    s for s in data["spells"]
    if s.get("req1_class", {}).get("name") == "FIRE"
    and s.get("req1_level") == 10
]
```

---

## Common Use Cases

### 1. Export Spell List to CSV

```python
import csv
import json

with open("GameData.json") as f:
    data = json.load(f)

# Export spells to CSV
with open("spells.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["ID", "Name ID", "Mana", "Cast Time", "Cooldown", "Range"])
    
    for spell in data["spells"]:
        writer.writerow([
            spell["spell_id"],
            spell["spell_name_id"],
            spell["mana"],
            spell["cast_time"],
            spell["cooldown"],
            spell["max_range"]
        ])

print("Exported spells.csv")
```

### 2. Create Item Database

```python
import sqlite3
import json

# Load data
with open("GameData.json") as f:
    data = json.load(f)

# Create SQLite database
conn = sqlite3.connect("spellforce_items.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
    CREATE TABLE items (
        item_id INTEGER PRIMARY KEY,
        item_type TEXT,
        item_subtype TEXT,
        level INTEGER,
        value INTEGER
    )
""")

# Insert items
for item in data["items"]:
    item_type = item.get("item_type", {})
    item_subtype = item.get("item_subtype", {})
    
    cursor.execute("""
        INSERT INTO items VALUES (?, ?, ?, ?, ?)
    """, (
        item["item_id"],
        item_type.get("name") if isinstance(item_type, dict) else str(item_type),
        item_subtype.get("name") if isinstance(item_subtype, dict) else str(item_subtype),
        item.get("level", 0),
        item.get("value", 0)
    ))

conn.commit()
conn.close()
print("Created spellforce_items.db")
```

### 3. Generate Spell Damage Table

```python
import json
import pandas as pd

with open("GameData.json") as f:
    data = json.load(f)

# Extract spell damage data
spell_data = []

for spell in data["spells"]:
    req1 = spell.get("req1_class", {})
    school = req1.get("name") if isinstance(req1, dict) else "Unknown"
    
    spell_data.append({
        "ID": spell["spell_id"],
        "School": school,
        "Level": spell.get("req1_level", 0),
        "Mana": spell["mana"],
        "Cast Time": spell["cast_time"],
        "Cooldown": spell["cooldown"],
        "Min Range": spell["min_range"],
        "Max Range": spell["max_range"]
    })

# Create DataFrame
df = pd.DataFrame(spell_data)

# Export to Excel
df.to_excel("spell_analysis.xlsx", index=False)
print("Created spell_analysis.xlsx")
```

### 4. Find Quest Items

```python
def find_quest_items(data):
    """Find all quest-related items"""
    quest_items = []
    
    for item in data["items"]:
        item_type = item.get("item_type", {})
        
        if isinstance(item_type, dict):
            type_name = item_type.get("name", "")
            
            # Check for quest-related types
            if "QUEST" in type_name or "BOOK" in type_name:
                quest_items.append(item)
    
    return quest_items

# Usage
quest_items = find_quest_items(data)
print(f"Found {len(quest_items)} quest items")
```

---

## Tips and Best Practices

### 1. Handle Enum Values Correctly

```python
# ✅ Correct: Check if value is a dict
req1 = spell.get("req1_class", {})
if isinstance(req1, dict) and req1.get("name") == "FIRE":
    print("Fire spell!")

# ❌ Wrong: Assumes enum format
if spell["req1_class"]["name"] == "FIRE":  # May crash!
    print("Fire spell!")
```

### 2. Handle None/Null Values

```python
# ✅ Correct: Use .get() with default
mana = spell.get("mana", 0) or 0

# ✅ Correct: Check for None
if spell.get("description") is not None:
    print(spell["description"])

# ❌ Wrong: Direct access
mana = spell["mana"]  # May raise KeyError
```

### 3. Use List Comprehensions for Filtering

```python
# ✅ Fast and Pythonic
fire_spells = [
    s for s in data["spells"]
    if s.get("req1_class", {}).get("name") == "FIRE"
]

# ❌ Slower
fire_spells = []
for s in data["spells"]:
    if s.get("req1_class", {}).get("name") == "FIRE":
        fire_spells.append(s)
```

### 4. Create Index Dictionaries

```python
# ✅ Create once, use many times
spell_by_id = {s["spell_id"]: s for s in data["spells"]}

# Fast lookups
spell_1 = spell_by_id[1]
spell_100 = spell_by_id[100]

# ❌ Linear search every time
spell_1 = next(s for s in data["spells"] if s["spell_id"] == 1)
```

### 5. Validate Data After Loading

```python
def validate_gamedata(data):
    """Validate loaded JSON structure"""
    required_keys = ["_metadata", "_summary", "spells", "items", "creatures"]
    
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")
    
    # Check summary counts match
    if len(data["spells"]) != data["_summary"]["total_spells"]:
        print("⚠️  Warning: Spell count mismatch!")
    
    print("✅ GameData validated")

# Use it
validate_gamedata(data)
```

### 6. Memory Optimization

For large datasets, consider loading only what you need:

```python
import json

# Load only metadata and summary
with open("GameData.json") as f:
    # Read first 1000 lines (metadata + summary)
    partial = ""
    for i, line in enumerate(f):
        partial += line
        if i > 1000:
            break
    
    # This won't work for partial JSON, but you can stream parse
    # with libraries like ijson for very large files
```

---

## Troubleshooting

### Error: File Not Found

```bash
# Make sure you're in the right directory
cd src/TiganachReloaded

# Check if file exists
ls -lh GameData.json

# Re-export if needed
python3 export_to_json.py
```

### Error: JSON Decode Error

```bash
# File may be corrupted, re-export
rm GameData.json
python3 export_to_json.py
```

### Large Memory Usage

```python
# Don't load everything if you only need part
import ijson

# Stream parse large JSON
with open("GameData.json", "r") as f:
    # Get only spells without loading entire file
    spells = []
    parser = ijson.items(f, "spells.item")
    for spell in parser:
        if spell["spell_id"] < 100:  # Only first 100
            spells.append(spell)
```

---

## Comparison: JSON vs XML vs CFF

| Feature | JSON | XML | CFF (tirganach) |
|---------|------|-----|-----------------|
| **Read Speed** | ⚡ Fast | 🐢 Slow | 🐌 Very Slow |
| **File Size** | 73 MB | 66 MB | 19 MB |
| **Human Readable** | ✅ Yes | ✅ Yes | ❌ No |
| **Programmatic Access** | ⚡ Easy | 🔧 Moderate | 🔧 Moderate |
| **Can Modify** | ❌ No | ❌ No | ✅ Yes |
| **Query Performance** | ⚡ Fast | 🐢 Slow | 🐌 Very Slow |
| **Best For** | Analysis, Queries | Viewing, Documentation | Actual Modding |

**Workflow Recommendation:**

1. **Analysis/Research:** Use JSON (fast queries)
2. **Documentation:** Use XML (human-readable structure)
3. **Modding:** Use tirganach with `.cff` (only way to save changes)

---

## Example Scripts

See `example_use_json.py` for complete working examples including:
- Loading GameData.json
- Filtering spells by school
- Finding powerful items
- Analyzing creatures
- Searching localization strings

```bash
python3 example_use_json.py
```

---

## Further Reading

- [XML Export Guide](XML_EXPORT_GUIDE.md) - Export to XML format
- [CFF Editor README](CFF_EDITOR_README.md) - Modify GameData.cff
- [Modding Examples](cff_modding_examples.py) - Create mods with tirganach

---

**Created:** 2025-10-20  
**Format Version:** 1.0