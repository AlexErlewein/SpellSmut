# TiganachReloaded - Setup Complete ✅

## Summary

The CFF modding library has been successfully moved to `ModdingTools\TiganachReloaded\` and is fully operational.

---

## What Was Done

### 1. ✅ Created TiganachReloaded Folder
- **Location:** `H:\SpellSmut\ModdingTools\TiganachReloaded\`
- **Contents:** Complete tirganach library with bug fixes

### 2. ✅ Library Installation
- Uninstalled old installation from `ModdingTools/tirganach/`
- Reinstalled from new location `ModdingTools/TiganachReloaded/`
- Verified functionality with test scripts

### 3. ✅ Updated Documentation
All documentation files now reference the new location:
- `CFF_MODDING_GUIDE.md` - Updated installation path
- `CFF_EXTRACTION_SUMMARY.md` - Updated references
- `README_CFF_MODDING.md` - Updated directory structure
- Created `ModdingTools/TiganachReloaded/README_INSTALLATION.md`

### 4. ✅ Verified Functionality
- Library loads correctly from new location
- Can read GameData.cff (7,101 items, 3,455 spells, etc.)
- Can save modifications successfully
- All example scripts work correctly

---

## Directory Structure

```
H:\SpellSmut\
├── ModdingTools\
│   ├── TiganachReloaded\          # ← CFF modding library (NEW LOCATION)
│   │   ├── tirganach\             # Main library code
│   │   │   ├── __init__.py
│   │   │   ├── structure.py       # CFF parser
│   │   │   ├── entities.py        # Entity definitions
│   │   │   ├── fields.py          # Field parsers (with encoding fixes)
│   │   │   ├── types.py           # Enum definitions
│   │   │   └── compare.py         # Comparison tool
│   │   ├── pyproject.toml         # Package config
│   │   ├── LICENSE                # MIT license
│   │   ├── README.md              # Original docs
│   │   ├── EXPLANATION.md         # File format details
│   │   └── README_INSTALLATION.md # Installation guide
│   │
│   └── tirganach\                 # Old location (can be removed)
│
├── OriginalGameFiles\
│   └── data\
│       └── GameData.cff           # Original game data (97 MB)
│
├── ModdedGameFiles\               # Your mods go here
│
├── Scripts & Documentation:
├── test_cff_extract.py            # Test script
├── cff_modding_examples.py        # Examples
├── create_mod.py                  # Mod template
├── CFF_MODDING_GUIDE.md           # Full guide
├── CFF_QUICK_REFERENCE.md         # Quick ref
├── CFF_EXTRACTION_SUMMARY.md      # Technical summary
├── README_CFF_MODDING.md          # Main README
└── TIGANACH_RELOADED_SETUP.md     # This file
```

---

## Installation Commands

### Current Installation (Already Done)
```bash
cd H:\SpellSmut\ModdingTools\TiganachReloaded
pip install -e .
```

### Reinstall if Needed
```bash
pip uninstall -y tirganach
cd H:\SpellSmut\ModdingTools\TiganachReloaded
pip install -e .
```

### Verify Installation
```bash
cd H:\SpellSmut\ModdingTools\TiganachReloaded
python test_cff_extract.py
```

---

## Quick Usage

```python
from tirganach import GameData
from tirganach.types import *

# Load
gd = GameData('H:/SpellSmut/OriginalGameFiles/data/GameData.cff')

# Modify
ring = gd.armor.where(item_id=7065)[0]
ring.health = 1000
ring.mana = 1000

# Save
gd.save('H:/SpellSmut/ModdedGameFiles/GameData_modified.cff')
```

---

## What's in TiganachReloaded

### Main Library Files

| File | Purpose |
|------|---------|
| `structure.py` | Parses CFF binary format into Python objects |
| `entities.py` | Defines all game entities (items, spells, creatures, etc.) |
| `fields.py` | **Handles field parsing (MODIFIED with encoding fixes)** |
| `types.py` | All game enums (ItemType, School, Race, etc.) |
| `compare.py` | Tool to compare two CFF files |

### Bug Fixes Applied

**File:** `tirganach/fields.py`

1. **Line 70-76:** String parsing with fallback
   ```python
   try:
       return byte_source.rstrip(b'\x00').decode('windows-1252')
   except UnicodeDecodeError:
       return byte_source.rstrip(b'\x00').decode('latin-1', errors='replace')
   ```

2. **Line 78-85:** String encoding with fallback
   ```python
   try:
       result = source.encode('windows-1252').ljust(self.len_bytes, b'\x00')
   except UnicodeEncodeError:
       result = source.encode('latin-1', errors='replace').ljust(self.len_bytes, b'\x00')
   ```

These fixes prevent crashes when reading/writing CFF files with non-standard characters.

---

## Files Available in TiganachReloaded

### Documentation
- **README.md** - Original library documentation
- **README_INSTALLATION.md** - Installation guide (new)
- **EXPLANATION.md** - Technical CFF file format details
- **LICENSE** - MIT License

### Configuration
- **pyproject.toml** - Python package configuration
- **spellforceeditor.iml** - IDE project file

### Source Code
- **tirganach/** - Main library directory
  - All Python modules for CFF manipulation

---

## Cleanup Options

### Optional: Remove Old tirganach Folder

The old `ModdingTools/tirganach/` folder is no longer needed. You can remove it:

```bash
# WARNING: Only do this if you're sure TiganachReloaded works!
rm -rf "H:\SpellSmut\ModdingTools\tirganach"
```

**Recommendation:** Keep it for now as a backup until you've created and tested a few mods.

---

## Testing Checklist

- ✅ Library installed from `TiganachReloaded/`
- ✅ Test script runs: `python test_cff_extract.py`
- ✅ Examples run: `python cff_modding_examples.py`
- ✅ Mod creator runs: `python create_mod.py`
- ✅ Can load 97MB GameData.cff file
- ✅ Can access all 7,101 items
- ✅ Can access all 3,455 spells
- ✅ Can save modified CFF files
- ✅ Documentation updated with new paths

---

## Next Steps

### 1. Create Your First Mod
```bash
cd H:\SpellSmut\ModdingTools\TiganachReloaded
python create_mod.py
```
Edit the file to uncomment the modifications you want, then run it.

### 2. Read the Documentation
- **CFF_MODDING_GUIDE.md** - Comprehensive guide with examples
- **CFF_QUICK_REFERENCE.md** - Quick reference for common tasks

### 3. Experiment
```bash
cd H:\SpellSmut\ModdingTools\TiganachReloaded
python cff_modding_examples.py
```
Try the examples to learn the query patterns.

### 4. Share Your Mods
Once you create something cool, document it and share!

---

## Troubleshooting

### "Module not found: tirganach"
```bash
# Reinstall the library
cd H:\SpellSmut\ModdingTools\TiganachReloaded
pip install -e .
```

### Test Scripts Don't Work
```bash
# Verify you're in the correct directory
cd H:\SpellSmut\ModdingTools\TiganachReloaded
python test_cff_extract.py
```

### Import Errors
```bash
# Check installation
pip show tirganach

# Should show:
# Location: H:\SpellSmut\ModdingTools\TiganachReloaded
```

---

## Credits

### Original Library
- **tirganach** by leszekd25 and contributors
- Based on reverse engineering work by Hokan-Ashir and leszekd25

### Modifications
- Encoding fixes for SpellSmut project (2025)
- Reorganization into TiganachReloaded

### License
MIT License (maintained from original)

---

## Summary

🎉 **TiganachReloaded is ready to use!**

- ✅ Installed in `ModdingTools/TiganachReloaded/`
- ✅ All documentation updated
- ✅ Fully tested and working
- ✅ Ready to create mods

**Happy modding!** 🎮

---

*Created: 2025-10-19*
*Status: Complete*
*Version: 1.0*
