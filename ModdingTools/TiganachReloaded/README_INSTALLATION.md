# TiganachReloaded - SpellForce CFF Modding Library

## What This Is

**TiganachReloaded** is a Python library for modifying SpellForce Platinum Edition's `GameData.cff` file.

This is a modified version of the original [tirganach](https://github.com/leszekd25/tirganach) library with bug fixes for encoding issues.

## Installation

### Option 1: Editable Install (Recommended for Development)

```bash
cd H:\SpellSmut\ModdingTools\TiganachReloaded
pip install -e .
```

This installs the library in "editable" mode, meaning changes to the source code are immediately available.

### Option 2: Regular Install

```bash
pip install H:\SpellSmut\ModdingTools\TiganachReloaded
```

## Quick Test

After installation, verify it works:

```bash
cd H:\SpellSmut
python test_cff_extract.py
```

You should see:
```
[OK] GameData.cff loaded successfully!
Total Spells: 3455
Total Items: 7101
...
```

## Basic Usage

```python
from tirganach import GameData
from tirganach.types import *

# Load the CFF file
gd = GameData('H:/SpellSmut/OriginalGameFiles/data/GameData.cff')

# Query data
rings = [item for item in gd.items
         if item.item_type == ItemType.EQUIPMENT
         and item.item_subtype == EquipmentType.RING]

# Modify
armor = gd.armor.where(item_id=7065)[0]
armor.health = 1000
armor.mana = 1000

# Save
gd.save('H:/SpellSmut/ModdedGameFiles/GameData_modified.cff')
```

## Documentation

For complete documentation, see:
- **../../CFF_MODDING_GUIDE.md** - Full modding guide
- **../../CFF_QUICK_REFERENCE.md** - Quick reference
- **EXPLANATION.md** - Technical file format details
- **README.md** - Original library documentation

## What's Different from Original tirganach?

### Bug Fixes Applied:

1. **Encoding Fix (Parse)** - `fields.py:70-76`
   - Added fallback to `latin-1` encoding when `windows-1252` fails
   - Prevents `UnicodeDecodeError` when reading certain CFF files

2. **Encoding Fix (Dump)** - `fields.py:78-85`
   - Added fallback to `latin-1` encoding when `windows-1252` fails
   - Prevents `UnicodeEncodeError` when saving CFF files

These fixes ensure compatibility with various GameData.cff versions that may contain non-standard characters.

## Library Structure

```
TiganachReloaded/
├── tirganach/              # Main library code
│   ├── __init__.py         # Module initialization
│   ├── structure.py        # CFF file parser
│   ├── entities.py         # Game entity definitions
│   ├── fields.py           # Field type parsers (MODIFIED)
│   ├── types.py            # Enum definitions
│   └── compare.py          # File comparison tool
├── pyproject.toml          # Package configuration
├── LICENSE                 # MIT License
├── README.md              # Original documentation
├── EXPLANATION.md         # File format documentation
└── README_INSTALLATION.md # This file
```

## Requirements

- Python 3.7+ (tested with 3.11.9)
- No external dependencies (uses only Python standard library)

## Credits

### Original Authors
- **leszekd25** - [spellforce_data_editor](https://github.com/leszekd25/spellforce_data_editor)
- **Hokan-Ashir** - [SFGameDataEditor](https://github.com/Hokan-Ashir/SFGameDataEditor)

### Modifications
- Encoding fixes for SpellSmut project compatibility (2025)

## License

MIT License (same as original tirganach)

## Support

For modding help, see the main documentation files in the project root:
- `H:\SpellSmut\CFF_MODDING_GUIDE.md`
- `H:\SpellSmut\CFF_QUICK_REFERENCE.md`

For library-specific issues, check:
- `EXPLANATION.md` - File format details
- `tirganach/entities.py` - Entity field definitions
- `tirganach/types.py` - Available enums

## Version

**TiganachReloaded v1.0** - Based on tirganach 0.0.0 with encoding fixes
