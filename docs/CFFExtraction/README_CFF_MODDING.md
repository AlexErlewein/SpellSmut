# SpellForce GameData.cff Modding Suite

Complete toolkit for modifying SpellForce Platinum Edition's game data.

## 🎯 What This Is

A complete Python-based modding solution that allows you to:
- ✅ **Extract** all data from GameData.cff
- ✅ **Modify** items, spells, creatures, buildings, and more
- ✅ **Repack** the modified data back into a working CFF file
- ✅ **Compare** different versions to see changes

## 📦 What's Included

### Documentation
- **CFF_MODDING_GUIDE.md** - Comprehensive modding guide (read this first!)
- **CFF_QUICK_REFERENCE.md** - Quick reference card for common tasks
- **CFF_EXTRACTION_SUMMARY.md** - Setup summary and technical details

### Scripts (in ModdingTools/TiganachReloaded/)
- **test_cff_extract.py** - Test that everything works
- **cff_modding_examples.py** - 7 examples of querying and modifying data
- **create_mod.py** - Ready-to-use template for creating mods

### Tools
- **ModdingTools/TiganachReloaded/** - Python library for CFF file manipulation

## 🚀 Quick Start (3 Steps)

### 1. Verify Installation
```bash
cd H:\SpellSmut\ModdingTools\TiganachReloaded
python test_cff_extract.py
```

You should see:
```
[OK] GameData.cff loaded successfully!
Total Spells: 3455
Total Items: 7101
...
```

### 2. Explore Examples
```bash
cd H:\SpellSmut\ModdingTools\TiganachReloaded
python cff_modding_examples.py
```

This shows you how to:
- Find and modify items
- Query spells by school/level
- Modify hero units
- Change localization text
- And more!

### 3. Create Your First Mod
```bash
cd H:\SpellSmut\ModdingTools\TiganachReloaded
# Edit create_mod.py (uncomment the modifications you want)
python create_mod.py
```

## 📖 Documentation

Start here: **[CFF_MODDING_GUIDE.md](CFF_MODDING_GUIDE.md)**

Quick reference: **[CFF_QUICK_REFERENCE.md](CFF_QUICK_REFERENCE.md)**

## 💡 Example: Make Rings Overpowered

```python
from tirganach import GameData
from tirganach.types import *

# Load
gd = GameData('H:/SpellSmut/OriginalGameFiles/data/GameData.cff')

# Find all rings
rings = [item for item in gd.items
         if item.item_type == ItemType.EQUIPMENT
         and item.item_subtype == EquipmentType.RING]

# Boost them!
for ring_item in rings:
    armor = gd.armor.where(item_id=ring_item.item_id)
    if armor:
        armor[0].health = 1000
        armor[0].mana = 1000

# Save
gd.save('H:/SpellSmut/ModdedGameFiles/GameData_SuperRings.cff')
```

## 🛡️ Safety First

**ALWAYS** backup your original GameData.cff before testing mods:

```bash
copy "H:\SpellSmut\OriginalGameFiles\data\GameData.cff" "H:\SpellSmut\OriginalGameFiles\data\GameData_BACKUP.cff"
```

## 📊 What You Can Modify

| Category | What You Can Change |
|----------|-------------------|
| **Items** | Stats, names, requirements, effects |
| **Spells** | Mana cost, damage, range, effects |
| **Creatures** | Stats, skills, spells, equipment |
| **Heroes** | Stats, skills, spell lists, appearance |
| **Buildings** | Costs, build time, HP, requirements |
| **Text** | All game text and descriptions |

## 🎮 Game Data Statistics

- 3,455 Spells
- 7,101 Items
- 2,617 Creatures
- 207 Buildings
- 635 Armor pieces
- 721 Weapons
- 176,318 Text strings

## 🔧 System Requirements

- Python 3.11+ (you have 3.11.9 ✓)
- pip (for installing tirganach)
- ~200MB free disk space (for modded files)

## 📁 Directory Structure

```
H:\SpellSmut\
├── OriginalGameFiles\
│   └── data\
│       └── GameData.cff          # Original game data (97 MB)
├── ModdedGameFiles\              # Your mods go here
├── ModdingTools\
│   └── TiganachReloaded\         # Python library
│       ├── tirganach\            # Library code
│       ├── test_cff_extract.py  # Test script
│       ├── cff_modding_examples.py  # Examples
│       └── create_mod.py        # Mod template
├── CFF_MODDING_GUIDE.md          # Full guide
├── CFF_QUICK_REFERENCE.md        # Quick ref
└── CFF_EXTRACTION_SUMMARY.md     # Technical summary
```

## 🐛 Troubleshooting

**Game crashes after loading modded CFF?**
- Restore backup immediately
- You probably exceeded a string length limit or created invalid references

**Changes don't appear in game?**
- Verify you copied the modded file to the correct location
- Check file size (should be ~97MB)

**Script errors?**
- Make sure tirganach is installed: `pip install -e ModdingTools/TiganachReloaded`
- Check Python version: `python --version` (need 3.11+)

## 📚 Resources

### Included
- Full modding guide with examples
- Quick reference card
- Working example scripts
- Mod creation template

### External
- [Hokan-Ashir/SFGameDataEditor](https://github.com/Hokan-Ashir/SFGameDataEditor) - Java-based editor
- [leszekd25/spellforce_data_editor](https://github.com/leszekd25/spellforce_data_editor) - C#-based editor

## ✨ Features

✅ **Complete Access** - All 48 data tables accessible
✅ **Type Safety** - Python enums for all game constants
✅ **Easy Queries** - Simple where() and filter syntax
✅ **Safe Workflow** - Modify copies, compare before deploying
✅ **Well Documented** - Comprehensive guides and examples
✅ **Battle Tested** - Based on proven reverse engineering work

## 🎉 You're Ready!

Everything is set up and tested. Start with the examples, read the guide, and create your first mod!

**Happy modding!** 🎮

---

*For detailed documentation, see: [CFF_MODDING_GUIDE.md](CFF_MODDING_GUIDE.md)*
