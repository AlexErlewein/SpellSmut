# Icon Extraction - Master Status Document

**Project**: SpellSmut - SpellForce Modding Tool  
**Task**: Re-extract UI assets with original filenames  
**Status**: ✅ READY TO EXECUTE  
**Last Updated**: 2024-01-20

---

## Executive Summary

All scripts, tools, and documentation are in place to re-extract SpellForce UI assets with their **original filenames preserved**. This is critical for the icon integration system to function.

**Status:** Everything is ready. Just run the batch/shell script to begin!

---

## Why We Need This

### The Problem

Current extracted files are numbered:
- `ui_item0.png`, `ui_item1.png`, `ui_item2.png`...
- `ui_spell0.png`, `ui_spell1.png`, `ui_spell2.png`...

**These are USELESS** - we can't map them to the database!

### The Database

```json
{
  "item_id": 27,
  "item_ui_handle": "ui_item_equip_weapon_dagger_flame"
}
```

**The UIHandle IS the filename!** No mapping file exists. The game loads textures directly by name.

### The Solution

Re-extract with original names preserved:
- `ui_item_equip_weapon_dagger_flame.png` ✅
- `ui_spell_EM_Fire_FireBurst.png` ✅
- `ui_spell_WM_Life_Healing.png` ✅

Then the GUI can load icons with simple direct lookup!

---

## Readiness Status

### ✅ Tools Ready

| Tool | Status | Location |
|------|--------|----------|
| QuickBMS | ✅ Installed | `ModdingTools/quickbms/quickbms.exe` |
| BMS Script | ✅ Created | `src/helper_tools/SpellForce_PAK_script.bms` |
| PAK Files | ✅ Present | `OriginalGameFiles/pak/` (23 files) |

### ✅ Scripts Ready

| Script | Status | Purpose |
|--------|--------|---------|
| `extract_ui_with_names.py` | ✅ Created | Extract from PAK with original names |
| `convert_ui_textures.py` | ✅ Created | Convert DDS → PNG |
| `rotate_ui_pngs.py` | ✅ Created | Rotate 180° (inverted Y-axis) |
| `organize_ui_assets.py` | ✅ Created | Organize by category |
| `run_ui_icon_integration.bat` | ✅ Created | Windows automation |
| `run_ui_icon_integration.sh` | ✅ Created | macOS/Linux automation |

All scripts located in: `src/helper_tools/`

### ✅ Documentation Ready

| Document | Status | Purpose |
|----------|--------|---------|
| `UI_ICON_REEXTRACTION_GUIDE.md` | ✅ Complete | Comprehensive step-by-step guide |
| `ICON_REEXTRACTION_CHECKLIST.md` | ✅ Complete | Detailed execution checklist |
| `ICON_EXTRACTION_BEFORE_AFTER.md` | ✅ Complete | Visual before/after comparison |
| `README_ICON_EXTRACTION.md` | ✅ Complete | Quick reference guide |
| `QUICK_START_ICON_EXTRACTION.md` | ✅ Complete | Fast command reference |
| `GUI_ICON_INTEGRATION_PLAN.md` | ✅ Complete | Technical integration plan |
| `GUI_ICON_INTEGRATION_SUMMARY.md` | ✅ Complete | Planning summary |

All documentation in: `ProjectPlanning/` and `ExtractedAssets/UI/`

---

## Prerequisites Status

### Required (Must Install)

- [ ] **ImageMagick** - DDS → PNG conversion
  - Windows: `winget install ImageMagick.ImageMagick` or `choco install imagemagick`
  - macOS: `brew install imagemagick`
  - Linux: `sudo apt install imagemagick`
  - Verify: `magick -version`

- [ ] **Pillow** - PNG rotation
  - Install: `uv pip install Pillow`
  - Verify: `uv run python -c "from PIL import Image"`

### Already Available

- ✅ **UV** - Python package manager (project standard)
- ✅ **Python 3** - Script execution
- ✅ **QuickBMS** - PAK extraction (already downloaded)
- ✅ **PAK Files** - Source data (already present)
- ✅ **winget** - Windows package manager (v1.11.510)
- ✅ **chocolatey** - Windows package manager (v2.5.0)

---

## Execution Instructions

### Windows (Recommended)

```batch
cd H:\SpellSmut\src\helper_tools
run_ui_icon_integration.bat
```

### macOS/Linux

```bash
cd SpellSmut/src/helper_tools
chmod +x run_ui_icon_integration.sh
./run_ui_icon_integration.sh
```

**Estimated Time:** 20-30 minutes (fully automated)

---

## What Will Happen

### Pipeline Steps

1. **Extract** (10-15 min)
   - QuickBMS extracts all 23 PAK files
   - Preserves original directory structure and filenames
   - Filters only UI-related files
   - Output: `ExtractedAssets/UI/raw_reextraction/`

2. **Convert** (5-10 min)
   - ImageMagick converts DDS → PNG
   - Preserves filenames (just changes extension)
   - Creates PNG alongside DDS

3. **Rotate** (2-3 min)
   - Pillow rotates all PNGs by 180°
   - Fixes SpellForce's inverted Y-axis
   - Overwrites original PNGs

4. **Organize** (1-2 min)
   - Categorizes by filename prefix
   - Copies to organized structure
   - Output: `ExtractedAssets/UI/extracted/`

### Final Output

```
ExtractedAssets/UI/extracted/
├── items/          (~200-300 PNG files)
├── spells/         (~150-200 PNG files)
├── cursors/        (~40-50 PNG files)
├── buttons/        (~80-100 PNG files)
├── backgrounds/    (~20-30 PNG files)
├── mainmenu/       (~10-20 PNG files)
├── fonts/          (~70-80 PNG files)
└── other/          (~200-300 PNG files)

TOTAL: ~800-900 UI assets with original names ✅
```

---

## Verification Checklist

After extraction completes:

- [ ] Files have original names (e.g., `ui_item_equip_weapon_dagger_flame.png`)
- [ ] NOT numbered (e.g., NOT `ui_item0.png`)
- [ ] ~800-900 total PNG files extracted
- [ ] Files organized by category
- [ ] No errors in console output

Quick check:
```bash
ls ExtractedAssets/UI/extracted/items/ | head -5
ls ExtractedAssets/UI/extracted/spells/ | head -5
```

Expected output:
```
ui_item_equip_weapon_dagger_flame.png
ui_item_equip_weapon_sword_fire.png
ui_spell_EM_Fire_FireBurst.png
ui_spell_WM_Life_Healing.png
```

---

## Testing Instructions

After successful extraction:

```bash
cd TirganachReloaded
uv run tirganach
```

**Verify in GUI:**
- [ ] Icons display in table view (icon column)
- [ ] Icons display in property editor (large preview)
- [ ] Icons are right-side-up (not upside-down)
- [ ] Icons are clear and recognizable
- [ ] No excessive "Icon not found" errors
- [ ] GUI remains responsive

---

## Success Criteria

All must be true:

✅ **Extraction Complete**
- All 23 PAK files extracted without errors
- ~800-900 UI assets extracted
- Files organized by category

✅ **Filenames Correct**
- Files have original names (e.g., `ui_item_equip_weapon_dagger_flame.png`)
- NOT numbered (e.g., NOT `ui_item0.png`)

✅ **Images Correct**
- PNG files created successfully
- PNGs rotated 180° (right-side-up in GUI)
- Images not corrupt
- Transparent backgrounds preserved

✅ **GUI Integration Works**
- GUI editor launches without errors
- Icons display in table view
- Icons display in property editor
- No excessive "Icon not found" errors
- GUI remains responsive

---

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| ImageMagick not found | Install: `winget install ImageMagick.ImageMagick` or `choco install imagemagick` |
| Pillow not found | Install: `uv pip install Pillow` |
| PAK files missing | Check: `OriginalGameFiles/pak/` has 23 `.pak` files |
| QuickBMS not found | Script auto-downloads, or get from https://aluigi.altervista.org |
| Extraction too slow | Normal on HDD. SSD recommended. ~20-30 min expected. |
| Some icons missing | Normal. Game doesn't have icons for all items. |

**Full troubleshooting:** See `UI_ICON_REEXTRACTION_GUIDE.md`

---

## Integration Architecture

Once extraction is complete, the icon system works as follows:

```
┌─────────────────────────────────────┐
│ 1. User selects item (item_id: 27) │
└────────────┬────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ 2. Look up in item_ui table:        │
│    item_id: 27 →                     │
│    item_ui_handle:                   │
│    "ui_item_equip_weapon_dagger_..."  │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ 3. Construct path:                   │
│    "ExtractedAssets/UI/extracted/    │
│     items/ui_item_equip_weapon_      │
│     dagger_flame.png"                │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ 4. Load PNG and display:             │
│    QPixmap(path).scaled(64, 64)      │
│    🗡️ Icon appears in GUI!           │
└──────────────────────────────────────┘
```

**Key Insight:** Direct filename mapping. No intermediate lookup. Clean and simple!

---

## Next Steps After Extraction

1. ✅ **Verify Extraction**
   - Check file counts
   - Verify filenames are correct
   - Test a few icons manually

2. ✅ **Test in GUI Editor**
   - Launch: `uv run tirganach`
   - Open Items category
   - Verify icons display
   - Check property editor shows large icon

3. ✅ **Integration Testing**
   - Test multiple items
   - Test spells
   - Verify performance is acceptable
   - Check for any missing icon errors

4. ✅ **Cleanup (Optional)**
   - Delete DDS files to save space (~500MB)
   - Delete raw extraction directory (~1.5GB)
   - **Only after confirming everything works!**

---

## File Locations Summary

### Scripts
- **Windows automation:** `src/helper_tools/run_ui_icon_integration.bat`
- **macOS/Linux automation:** `src/helper_tools/run_ui_icon_integration.sh`
- **Extraction:** `src/helper_tools/extract_ui_with_names.py`
- **Conversion:** `src/helper_tools/convert_ui_textures.py`
- **Rotation:** `src/helper_tools/rotate_ui_pngs.py`
- **Organization:** `src/helper_tools/organize_ui_assets.py`

### Tools
- **QuickBMS:** `ModdingTools/quickbms/quickbms.exe`
- **BMS Script:** `src/helper_tools/SpellForce_PAK_script.bms`

### Data
- **PAK Files:** `OriginalGameFiles/pak/*.pak` (23 files)
- **Raw Output:** `ExtractedAssets/UI/raw_reextraction/` (temporary)
- **Final Output:** `ExtractedAssets/UI/extracted/` (permanent)

### Documentation
- **This file:** `ProjectPlanning/ICON_EXTRACTION_STATUS.md`
- **Full guide:** `ProjectPlanning/UI_ICON_REEXTRACTION_GUIDE.md`
- **Checklist:** `ProjectPlanning/ICON_REEXTRACTION_CHECKLIST.md`
- **Before/After:** `ProjectPlanning/ICON_EXTRACTION_BEFORE_AFTER.md`
- **Quick start:** `QUICK_START_ICON_EXTRACTION.md`
- **Quick reference:** `ExtractedAssets/UI/README_ICON_EXTRACTION.md`

---

## Time Estimates

| Phase | Time |
|-------|------|
| **Prerequisites Setup** (first time only) | 10-30 min |
| **Extraction** | 10-15 min |
| **Conversion** | 5-10 min |
| **Rotation** | 2-3 min |
| **Organization** | 1-2 min |
| **Verification** | 5-10 min |
| **GUI Testing** | 5-10 min |
| **Total (first run)** | **40-80 min** |
| **Total (subsequent runs)** | **20-40 min** |

---

## Critical Success Factors

✅ **Prerequisites Installed**
- ImageMagick for DDS conversion
- Pillow for PNG rotation

✅ **Correct Execution**
- Run from correct directory: `src/helper_tools/`
- Use provided automation scripts
- Wait for full completion (don't interrupt)

✅ **Proper Verification**
- Check filenames are original (not numbered)
- Verify file counts are reasonable (~800-900)
- Test in GUI before cleanup

✅ **Testing**
- Icons display in GUI
- Icons are right-side-up
- No excessive errors
- GUI remains responsive

---

## Known Limitations

1. **Not all items have icons**
   - Some items in the game data don't have corresponding UI assets
   - This is normal - the game uses fallback icons for these
   - The GUI will handle this gracefully

2. **Windows-only extraction** (currently)
   - QuickBMS works best on Windows
   - macOS/Linux support via Wine or native quickbms binary
   - Already set up to detect platform and use correct binary

3. **Large file sizes**
   - Extraction requires ~5GB disk space
   - Can be cleaned up after verification
   - SSD recommended for faster extraction

4. **One-time process**
   - Once extracted correctly, doesn't need to be repeated
   - Unless PAK files are updated or corrupted

---

## Decision Log

### Why QuickBMS?
- Industry-standard tool for game asset extraction
- Proven support for SpellForce PAK format
- Preserves original directory structure and filenames
- Open source and well-documented

### Why ImageMagick?
- Industry-standard image conversion tool
- Excellent DDS format support
- Cross-platform compatibility
- Reliable and fast

### Why Pillow?
- Pure Python image library
- Easy to install (pip install Pillow)
- Good performance for simple rotations
- Already in most Python environments

### Why 180° rotation?
- SpellForce uses inverted Y-axis for textures
- Without rotation, icons appear upside-down
- Discovered through testing with actual game assets
- Single rotation fixes all icons

---

## Technical Details

### PAK Format
- SpellForce PAK files use version 4 format
- Header: "MASSIVE PAKFILE V 4.0"
- Contains directory structure and file metadata
- Files are stored with original names

### DDS Format
- DirectDraw Surface (Microsoft format)
- Native format for DirectX textures
- Supports compression and mipmaps
- Standard format for game assets (2000-2010 era)

### File Organization
- Items: `ui_item_*`
- Spells: `ui_spell_*`
- Cursors: `ui_cursor_*`
- Buttons: `ui_btn_*`
- Backgrounds: `ui_bgr_*`
- Fonts: `font_*`

### Database Schema
```json
{
  "item_id": 27,                                    // Primary key
  "item_ui_index": 1,                               // Display order
  "item_ui_handle": "ui_item_equip_weapon_dagger_flame",  // Filename!
  "scaled_down": 0                                  // Icon quality flag
}
```

---

## Contact & Support

**Documentation Location:** `ProjectPlanning/`

**Questions?** Review these documents:
1. Quick start: `QUICK_START_ICON_EXTRACTION.md`
2. Full guide: `UI_ICON_REEXTRACTION_GUIDE.md`
3. Troubleshooting: `UI_ICON_REEXTRACTION_GUIDE.md` (Common Issues section)
4. Before/After: `ICON_EXTRACTION_BEFORE_AFTER.md`

**External Resources:**
- QuickBMS: https://aluigi.altervista.org/quickbms.htm
- ImageMagick: https://imagemagick.org
- Pillow: https://pillow.readthedocs.io

---

## Final Checklist

Before starting:
- [ ] Read this status document
- [ ] Install ImageMagick (`winget install ImageMagick.ImageMagick`)
- [ ] Install Pillow (`uv pip install Pillow`)
- [ ] Verify PAK files exist

During extraction:
- [ ] Run automation script
- [ ] Monitor console output
- [ ] Wait for completion (don't interrupt)

After extraction:
- [ ] Verify filenames are correct
- [ ] Check file counts (~800-900)
- [ ] Test in GUI editor
- [ ] Verify icons display correctly

---

## Status: READY TO EXECUTE ✅

Everything is in place. All scripts, tools, and documentation ready.

**To begin:**

```batch
cd H:\SpellSmut\src\helper_tools
run_ui_icon_integration.bat
```

**Or on macOS/Linux:**

```bash
cd SpellSmut/src/helper_tools
./run_ui_icon_integration.sh
```

**Let's extract those icons! 🚀**

---

**Document Version:** 1.0  
**Last Updated:** 2024-01-20  
**Status:** Complete and Ready