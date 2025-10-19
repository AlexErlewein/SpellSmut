# TiganachReloaded - Scripts Guide

This folder contains the **tirganach** library and all CFF modding scripts.

---

## 📁 What's in This Folder

### Library Code
- **tirganach/** - Main library directory
  - `structure.py` - CFF file parser
  - `entities.py` - Game entity definitions
  - `fields.py` - Field parsers (with encoding fixes)
  - `types.py` - Enum definitions (ItemType, School, Race, etc.)
  - `compare.py` - File comparison tool

### Scripts
- **test_cff_extract.py** - Verify library installation
- **cff_modding_examples.py** - 7 working examples
- **create_mod.py** - Mod creation template

### Documentation
- **README_INSTALLATION.md** - Installation guide
- **README_SCRIPTS.md** - This file
- **README.md** - Original library documentation
- **EXPLANATION.md** - Technical file format details

---

## 🚀 Quick Start

### 1. Test Installation
```bash
cd H:\SpellSmut\ModdingTools\TiganachReloaded
python test_cff_extract.py
```

**Expected Output:**
```
[OK] GameData.cff loaded successfully!
Total Spells: 3455
Total Items: 7101
...
```

### 2. Explore Examples
```bash
python cff_modding_examples.py
```

This shows:
- How to find items by type
- How to query spells by school/level
- How to modify stats
- How to work with heroes
- And more!

### 3. Create Your First Mod
```bash
python create_mod.py
```

**Before running:**
1. Open `create_mod.py` in a text editor
2. Uncomment the modifications you want (remove the `#` at the start of lines)
3. Save the file
4. Run it!

---

## 📜 Script Details

### test_cff_extract.py

**Purpose:** Verify the library is working correctly

**Usage:**
```bash
python test_cff_extract.py
```

**What it does:**
- Loads GameData.cff
- Shows statistics (spell count, item count, etc.)
- Displays sample items and spells
- Confirms everything is working

**When to use:**
- After installing the library
- After making changes to the library code
- To verify GameData.cff is accessible

---

### cff_modding_examples.py

**Purpose:** Demonstrate common modding patterns

**Usage:**
```bash
python cff_modding_examples.py
```

**Examples included:**

1. **Finding and modifying items**
   - Query items by type (rings, weapons, etc.)
   - Modify item stats

2. **Finding spells by school and level**
   - Filter spells by magic school
   - Query by level

3. **Browsing creatures**
   - List all creatures
   - Access creature data

4. **Working with hero units**
   - Find hero runes
   - Modify hero stats/skills

5. **Finding items by race**
   - Query race-specific equipment
   - Filter by race

6. **Buildings**
   - List all buildings
   - Access building data

7. **Localization strings**
   - Browse game text
   - Find specific strings

**When to use:**
- Learning the query syntax
- Understanding data structure
- Finding examples for your own mods

---

### create_mod.py

**Purpose:** Template for creating mods

**Usage:**
1. Edit the file
2. Uncomment desired modifications
3. Run: `python create_mod.py`

**Built-in Examples:**

1. **Boost Ring Stats** (Lines 49-63)
   - Doubles health/mana for all rings

2. **Cheaper Fire Spells** (Lines 68-78)
   - Reduces fire spell mana cost by 50%

3. **Buff Elf Units** (Lines 83-97)
   - Increases elf unit stats by 20

4. **Increase Hero XP Gain** (Lines 102-110)
   - Reduces XP needed per level

5. **Custom Item Names** (Lines 115-120)
   - Rename specific items

**To enable an example:**
1. Find the example in the file
2. Remove the `#` from the start of each line
3. Save and run

**To add your own:**
- Scroll to the "ADD YOUR OWN MODIFICATIONS" section (Line 125)
- Use the examples above as templates
- Add your custom code

**Output:**
- Creates a timestamped file in `H:\SpellSmut\ModdedGameFiles\`
- Example: `GameData_MyCustomMod_20251019_123456.cff`

---

## 📖 Common Tasks

### Task: Find all items of a specific type

```python
from tirganach import GameData
from tirganach.types import *

gd = GameData('H:/SpellSmut/OriginalGameFiles/data/GameData.cff')

# Find all rings
rings = [item for item in gd.items
         if item.item_type == ItemType.EQUIPMENT
         and item.item_subtype == EquipmentType.RING]

print(f"Found {len(rings)} rings")
```

### Task: Modify item stats

```python
# Find specific item
ring = gd.armor.where(item_id=7065)[0]

# Modify
ring.health = 1000
ring.mana = 1000

# Save
gd.save('H:/SpellSmut/ModdedGameFiles/GameData_modified.cff')
```

### Task: Query spells

```python
# Find all level 20 fire spells
fire_spells = gd.spells.where(level=20, req1_class=School.FIRE)

for spell in fire_spells:
    print(spell)
```

### Task: Modify hero

```python
# Find hero
hero = gd.items.where(item_id=4425)[0]

# Modify stats
hero.unit_stats.strength = 150
hero.unit_stats.dexterity = 150

# Modify skills
hero.unit_stats.skills[0].set(
    skill_school=School.LIGHT_COMBAT,
    skill_level=20
)

# Save
gd.save('H:/SpellSmut/ModdedGameFiles/GameData_modified.cff')
```

---

## 🛡️ Safety Guidelines

### Always:
- ✅ Backup original GameData.cff before testing
- ✅ Save to ModdedGameFiles folder (not original location)
- ✅ Test mods incrementally (small changes first)
- ✅ Verify file size (~97MB for valid files)

### Never:
- ❌ Delete entities (breaks references)
- ❌ Exceed string length limits
- ❌ Use invalid enum values
- ❌ Modify original GameData.cff directly

---

## 📚 Documentation

### In This Folder
- **README_INSTALLATION.md** - How to install/reinstall
- **EXPLANATION.md** - CFF file format technical details
- **README.md** - Original library documentation

### In Project Root
- **CFF_MODDING_GUIDE.md** - Complete modding guide
- **CFF_QUICK_REFERENCE.md** - Quick reference card
- **INDEX.md** - Master navigation document

---

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'tirganach'"
```bash
# Install the library
pip install -e .
```

### "FileNotFoundError: GameData.cff"
- Check the path in the script
- Verify GameData.cff exists at: `H:\SpellSmut\OriginalGameFiles\data\GameData.cff`

### Scripts don't run
```bash
# Make sure you're in the correct directory
cd H:\SpellSmut\ModdingTools\TiganachReloaded

# Then run
python test_cff_extract.py
```

### Changes don't appear in game
- Did you copy the modded CFF to the game directory?
- Check file size (should be ~97MB)
- Verify you're not running the wrong version

---

## 💡 Tips

1. **Start Simple**
   - Begin with stat modifications
   - Test after each change
   - Build complexity gradually

2. **Use Examples**
   - Run `cff_modding_examples.py` to see patterns
   - Copy-paste and modify examples
   - Refer to the guide for more details

3. **Read the Types**
   - Check `tirganach/types.py` for all enums
   - See what schools, races, item types exist
   - Use proper enum values

4. **Test Frequently**
   - Create small mods
   - Test in-game
   - Iterate quickly

---

## 🎯 Next Steps

1. **Run the test script** to verify everything works
2. **Try the examples** to learn query patterns
3. **Edit create_mod.py** to make your first mod
4. **Read the full guide** at `../../CFF_MODDING_GUIDE.md`

---

**Happy Modding!** 🎮

*For more help, see the main documentation in the project root.*
