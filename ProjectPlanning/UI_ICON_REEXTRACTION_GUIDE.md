# UI Icon Re-extraction Guide

**Status**: Ready to Execute ✅  
**Last Updated**: 2024  
**Estimated Time**: 2-3 hours (mostly automated)

---

## Overview

This guide walks you through re-extracting SpellForce UI assets **with their original filenames preserved**, which is critical for the icon integration system to work.

### Why Re-extract?

The previous extraction numbered files as `ui_item0.png`, `ui_item1.png`, etc., which are **useless** because we can't map them to the `item_ui_handle` values in the game data (e.g., `"ui_item_equip_weapon_dagger_flame"`).

**The UIHandle IS the filename!** We need files like:
- `ui_item_equip_weapon_dagger_flame.png`
- `ui_spell_EM_Fire_FireBurst.png`
- `ui_spell_WM_Life_Healing.png`

---

## Prerequisites

✅ **Already Set Up:**
- QuickBMS installed in `ModdingTools/quickbms/`
- BMS script created: `src/helper_tools/SpellForce_PAK_script.bms`
- PAK files available in `OriginalGameFiles/pak/` (23 files)
- Python extraction scripts created
- Batch execution script created

🔧 **You Need to Install:**
1. **ImageMagick** (for DDS → PNG conversion)
   - Windows: `choco install imagemagick` or download from https://imagemagick.org
   - macOS: `brew install imagemagick`
   - Linux: `sudo apt install imagemagick`

2. **Python Pillow** (for PNG rotation)
   - Run: `uv pip install Pillow`

---

## Step-by-Step Execution

### Option A: Automated Pipeline (Recommended)

**On Windows:**

```batch
cd H:\SpellSmut\src\helper_tools
run_ui_icon_integration.bat
```

This batch script will automatically:
1. Extract UI assets from all PAK files
2. Convert DDS files to PNG
3. Rotate PNGs by 180° (SpellForce uses inverted Y-axis)
4. Organize assets into categories

**On macOS/Linux:**

```bash
cd SpellSmut/src/helper_tools

# Step 1: Extract
python extract_ui_with_names.py

# Step 2: Convert
uv run convert_ui_textures.py

# Step 3: Rotate
uv run rotate_ui_pngs.py

# Step 4: Organize
uv run organize_ui_assets.py
```

---

### Option B: Manual Step-by-Step

If you want to run each step individually or troubleshoot:

#### Step 1: Extract UI Assets with Original Names

```bash
cd SpellSmut/src/helper_tools
uv run extract_ui_with_names.py
```

**What it does:**
- Scans `OriginalGameFiles/pak/` for all `.pak` files (23 files found)
- Uses QuickBMS with the SpellForce BMS script to extract
- Preserves original directory structure and filenames
- Filters only UI-related files (`ui_*.dds`, `font_*.tga`)
- Outputs to: `ExtractedAssets/UI/raw_reextraction/`

**Expected Output:**
```
Found 23 PAK files:
  - sf0.pak          (123.4 MB)
  - sf1.pak          (456.7 MB)
  ...
  
Extracting: sf5.pak
[OK] Successfully extracted sf5.pak
  1234 files found

Filtered 892 UI assets to ExtractedAssets/UI/raw_reextraction/
```

**Time**: ~10-15 minutes (depending on disk speed)

---

#### Step 2: Convert DDS to PNG

```bash
uv run convert_ui_textures.py
```

**What it does:**
- Finds all `.dds` files in the extracted directory
- Converts each to `.png` using ImageMagick
- Preserves original filenames (just changes extension)
- Creates PNG files alongside DDS files

**Expected Output:**
```
Found 892 DDS files to convert
[1/892] Converting: ui_item_equip_weapon_dagger_flame.dds → .png
[2/892] Converting: ui_spell_EM_Fire_FireBurst.dds → .png
...

Conversion Summary:
  Total files: 892
  Successful: 892
  Failed: 0
```

**Time**: ~5-10 minutes

**Troubleshooting:**
- If ImageMagick not found, install it first
- Windows: `winget install ImageMagick.ImageMagick` or `choco install imagemagick`
- macOS: `brew install imagemagick`

---

#### Step 3: Rotate PNGs by 180°

```bash
uv run rotate_ui_pngs.py
```

**Why?** SpellForce uses an inverted Y-axis for textures. Without rotation, icons appear upside-down in the GUI.

**What it does:**
- Finds all `.png` files
- Rotates each by 180° using Pillow
- Overwrites original file with rotated version

**Expected Output:**
```
Found 892 PNG files to rotate
[1/892] Rotating: ui_item_equip_weapon_dagger_flame.png
[2/892] Rotating: ui_spell_EM_Fire_FireBurst.png
...

Rotation Summary:
  Total files: 892
  Successful: 892
  Failed: 0
```

**Time**: ~2-3 minutes

**Troubleshooting:**
- If Pillow not found: `uv pip install Pillow`

---

#### Step 4: Organize by Category

```bash
uv run organize_ui_assets.py
```

**What it does:**
- Scans all extracted/converted/rotated files
- Categorizes by filename prefix:
  - `ui_item_*` → `items/`
  - `ui_spell_*` → `spells/`
  - `ui_cursor_*` → `cursors/`
  - `ui_btn_*` → `buttons/`
  - `font_*` → `fonts/`
  - etc.
- Copies files to organized structure

**Expected Output:**
```
Organization Summary:
  items       :   234 files
  spells      :   178 files
  cursors     :    45 files
  buttons     :    89 files
  backgrounds :    23 files
  mainmenu    :    12 files
  fonts       :    78 files
  other       :   233 files
  ─────────────────────────
  TOTAL       :   892 files
```

**Time**: ~1-2 minutes

---

## Final Directory Structure

After completion, you'll have:

```
ExtractedAssets/
└── UI/
    ├── raw_reextraction/          # Raw extraction (can delete after)
    │   ├── sf5/
    │   │   └── texture/
    │   │       ├── ui_item_equip_weapon_dagger_flame.dds
    │   │       ├── ui_item_equip_weapon_dagger_flame.png  (rotated)
    │   │       └── ...
    │   └── ...
    │
    └── extracted/                  # Final organized assets ✅
        ├── items/
        │   ├── ui_item_equip_weapon_dagger_flame.png
        │   ├── ui_item_equip_weapon_sword_fire.png
        │   └── ...
        ├── spells/
        │   ├── ui_spell_EM_Fire_FireBurst.png
        │   ├── ui_spell_WM_Life_Healing.png
        │   └── ...
        ├── cursors/
        ├── buttons/
        ├── backgrounds/
        ├── mainmenu/
        ├── fonts/
        └── other/
```

---

## Verification

### Quick Test

Check that files have correct names:

```bash
# Should show actual game asset names, not numbers
ls ExtractedAssets/UI/extracted/items/ | head -10
ls ExtractedAssets/UI/extracted/spells/ | head -10
```

**Expected:**
```
ui_item_equip_weapon_dagger_flame.png
ui_item_equip_weapon_sword_fire.png
ui_item_equip_armor_leather_chest.png
...
```

**NOT:**
```
ui_item0.png
ui_item1.png
ui_item2.png
```

### File Count Check

Expected file counts (approximate):
- **Items**: ~200-300 files
- **Spells**: ~150-200 files
- **Cursors**: ~40-50 files
- **Buttons**: ~80-100 files
- **Other UI**: ~200-300 files

---

## How the Icon System Works

Once extraction is complete, the GUI editor will use this logic:

```
User selects item (item_id: 27)
         ↓
Look up in item_ui table:
  item_id: 27 → item_ui_handle: "ui_item_equip_weapon_dagger_flame"
         ↓
Construct path:
  "ExtractedAssets/UI/extracted/items/ui_item_equip_weapon_dagger_flame.png"
         ↓
Load PNG and display in GUI:
  QPixmap(icon_path).scaled(64, 64)
         ↓
Icon appears in table and property editor! 🎉
```

**Key Point**: The `item_ui_handle` value **exactly matches** the filename (without extension).

---

## Common Issues & Solutions

### Issue 1: QuickBMS Not Found

**Error**: `[ERROR] QuickBMS not found`

**Solution**: The script should auto-download QuickBMS. If it fails:
1. Download manually from: https://aluigi.altervista.org/papers/quickbms.zip
2. Extract to `ModdingTools/quickbms/`
3. Ensure `quickbms.exe` (Windows) or `quickbms` (macOS/Linux) exists

---

### Issue 2: ImageMagick Not Found

**Error**: `[WARNING] ImageMagick not found`

**Solution**:
- **Windows**: 
  - `winget install ImageMagick.ImageMagick` (recommended)
  - Or: `choco install imagemagick`
  - Or download from https://imagemagick.org/script/download.php
  - Add to PATH during installation
  
- **macOS**: `brew install imagemagick`
  
- **Linux**: `sudo apt install imagemagick`

**Verify**: Run `magick -version` in terminal

---

### Issue 3: Pillow Not Installed

**Error**: `[ERROR] Pillow not found`

**Solution**: `uv pip install Pillow`

**Verify**: `uv run python -c "from PIL import Image; print('OK')"`

---

### Issue 4: PAK Files Not Found

**Error**: `[ERROR] No PAK files found`

**Solution**: 
- Verify PAK files exist in `OriginalGameFiles/pak/`
- Should see: `sf0.pak`, `sf1.pak`, ..., `sf36.pak`
- Copy from game installation if missing

---

### Issue 5: Extraction Takes Too Long

**Normal**: Extracting 23 PAK files containing ~4GB of data takes time.

**Tips**:
- First run: ~15-20 minutes is normal
- SSD vs HDD makes a big difference
- You can cancel and resume (script will skip existing files)

---

### Issue 6: Some Icons Missing

**Expected**: Not all items/spells have icons. The game uses fallback icons for some content.

**Solution**: The GUI editor will handle missing icons gracefully:
- Display a placeholder icon
- Log a warning
- Continue functioning normally

---

## Cleanup (Optional)

After successful extraction and verification, you can save disk space:

### Delete DDS Files (saves ~500MB)

```bash
cd ExtractedAssets/UI/raw_reextraction
find . -name "*.dds" -delete
```

### Delete Raw Extraction (saves ~1.5GB)

```bash
# Only after verifying extracted/ is complete!
rm -rf ExtractedAssets/UI/raw_reextraction/
```

**Warning**: Only do this after confirming everything works in the GUI editor!

---

## Next Steps

After successful re-extraction:

1. ✅ **Test in GUI Editor**
   ```bash
   cd TirganachReloaded
   uv run -m tirganach.gui_editor
   ```

2. ✅ **Verify Icon Display**
   - Open Items category
   - Check that icons appear in the table's icon column
   - Select an item and verify icon shows in property editor
   - Test with multiple items and spells

3. ✅ **Check Console for Errors**
   - No "Icon not found" errors for common items
   - Fallback icons used for items without graphics

4. ✅ **Performance Test**
   - Loading speed should be acceptable
   - GUI should remain responsive
   - Icons should load within 100ms

---

## File Locations Reference

### Scripts
- `src/helper_tools/extract_ui_with_names.py` - Main extraction script
- `src/helper_tools/convert_ui_textures.py` - DDS → PNG conversion
- `src/helper_tools/rotate_ui_pngs.py` - 180° rotation
- `src/helper_tools/organize_ui_assets.py` - Category organization
- `src/helper_tools/run_ui_icon_integration.bat` - Windows batch runner

### Tools
- `ModdingTools/quickbms/quickbms.exe` - PAK extraction tool
- `src/helper_tools/SpellForce_PAK_script.bms` - PAK format script

### Data
- `OriginalGameFiles/pak/*.pak` - Source PAK files (23 files)
- `ExtractedAssets/UI/raw_reextraction/` - Raw extraction output
- `ExtractedAssets/UI/extracted/` - Final organized assets

### Integration
- `TirganachReloaded/tirganach/gamedata.py` - Icon loading logic
- `TirganachReloaded/tirganach/gui_editor.py` - GUI display

---

## Success Criteria

✅ All scripts run without errors  
✅ ~800-900 UI assets extracted  
✅ Files have original names (not numbered)  
✅ Icons organized by category  
✅ PNGs are right-side-up (rotated 180°)  
✅ GUI editor displays icons correctly  
✅ No missing icon errors for common items  

---

## Estimated Total Time

| Step | Time |
|------|------|
| 1. Extraction | 10-15 min |
| 2. Conversion | 5-10 min |
| 3. Rotation | 2-3 min |
| 4. Organization | 1-2 min |
| **Total** | **~20-30 min** |

*Plus initial setup time if installing ImageMagick/Pillow*

---

## Support

If you encounter issues:

1. Check the "Common Issues & Solutions" section above
2. Review the console output for specific error messages
3. Verify all prerequisites are installed
4. Check file permissions on the extraction directories
5. Consult `GUI_ICON_INTEGRATION_PLAN.md` for technical details

---

## References

- **Main Plan**: `ProjectPlanning/GUI_ICON_INTEGRATION_PLAN.md`
- **Summary**: `ProjectPlanning/GUI_ICON_INTEGRATION_SUMMARY.md`
- **SpellForce Data Editor Source**: Analyzed C# code that revealed UIHandle = filename
- **QuickBMS**: https://aluigi.altervista.org/quickbms.htm
- **ImageMagick**: https://imagemagick.org

---

**Ready to go! Run the batch script and icons will be extracted with correct names! 🚀**