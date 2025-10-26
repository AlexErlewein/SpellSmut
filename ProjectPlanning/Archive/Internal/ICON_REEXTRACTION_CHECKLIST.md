# Icon Re-extraction Execution Checklist

**Project**: SpellSmut - SpellForce Modding Tool  
**Task**: Re-extract UI assets with original filenames  
**Status**: READY TO EXECUTE ✅  
**Created**: 2024  

---

## Overview

This checklist guides you through re-extracting SpellForce UI assets with their **original filenames preserved**, which is critical for the icon integration system.

**Why?** The UIHandle in the database **IS** the filename. We need:
- `ui_item_equip_weapon_dagger_flame.png` (✅ Correct)
- NOT `ui_item0.png` (❌ Wrong - can't map to data)

---

## Pre-Flight Checklist

### ✅ Verify Prerequisites

- [ ] **Python 3** installed and accessible
  ```bash
  uv --version  # UV package manager
  ```

- [ ] **ImageMagick** installed (for DDS → PNG conversion)
  ```bash
  magick -version
  ```
  - Windows: `winget install ImageMagick.ImageMagick` or `choco install imagemagick`
  - macOS: `brew install imagemagick`
  - Linux: `sudo apt install imagemagick`

- [ ] **Pillow** installed (for PNG rotation)
  ```bash
  uv run python -c "from PIL import Image; print('OK')"
  ```
  - Install: `uv pip install Pillow`

### ✅ Verify Files Present

- [ ] **QuickBMS** executable exists
  - Windows: `ModdingTools/quickbms/quickbms.exe`
  - macOS/Linux: `ModdingTools/quickbms/quickbms`

- [ ] **BMS script** exists
  - `src/helper_tools/SpellForce_PAK_script.bms`

- [ ] **PAK files** exist (23 files)
  - `OriginalGameFiles/pak/sf0.pak`
  - `OriginalGameFiles/pak/sf1.pak`
  - ...through sf36.pak

- [ ] **Extraction scripts** exist
  - `src/helper_tools/extract_ui_with_names.py`
  - `src/helper_tools/convert_ui_textures.py`
  - `src/helper_tools/rotate_ui_pngs.py`
  - `src/helper_tools/organize_ui_assets.py`

- [ ] **Automation scripts** exist
  - Windows: `src/helper_tools/run_ui_icon_integration.bat`
  - macOS/Linux: `src/helper_tools/run_ui_icon_integration.sh`

### ✅ Disk Space Check

- [ ] **Minimum 5GB** free space available
  - Raw extraction: ~2GB
  - DDS files: ~1.5GB
  - PNG files: ~1GB
  - Working space: ~500MB

---

## Execution Checklist

### Option 1: Automated (RECOMMENDED)

#### Windows

- [ ] Open Command Prompt or PowerShell
- [ ] Navigate to helper_tools directory
  ```batch
  cd H:\SpellSmut\src\helper_tools
  ```
- [ ] Run automation script
  ```batch
  run_ui_icon_integration.bat
  ```
- [ ] Wait for completion (~20-30 minutes)
- [ ] Verify no errors in output

#### macOS/Linux

- [ ] Open Terminal
- [ ] Navigate to helper_tools directory
  ```bash
  cd SpellSmut/src/helper_tools
  ```
- [ ] Make script executable (if not already)
  ```bash
  chmod +x run_ui_icon_integration.sh
  ```
- [ ] Run automation script
  ```bash
  ./run_ui_icon_integration.sh
  ```
- [ ] Wait for completion (~20-30 minutes)
- [ ] Verify no errors in output

---

### Option 2: Manual Step-by-Step

If automation fails or you want to run steps individually:

#### Step 1: Extract UI Assets

- [ ] Navigate to helper_tools
  ```bash
  cd SpellSmut/src/helper_tools
  ```

- [ ] Run extraction script
  ```bash
  uv run extract_ui_with_names.py
  ```

- [ ] Wait for extraction (~10-15 minutes)

- [ ] Verify output
  - [ ] "Successfully extracted" messages for all PAK files
  - [ ] "Filtered XXX UI assets" message
  - [ ] Directory created: `ExtractedAssets/UI/raw_reextraction/`

#### Step 2: Convert DDS to PNG

- [ ] Run conversion script
  ```bash
  uv run convert_ui_textures.py
  ```

- [ ] Wait for conversion (~5-10 minutes)

- [ ] Verify output
  - [ ] "Found XXX DDS files to convert"
  - [ ] "Successful: XXX" (should match total files)
  - [ ] "Failed: 0" (no failures)
  - [ ] PNG files created alongside DDS files

#### Step 3: Rotate PNGs 180°

- [ ] Run rotation script
  ```bash
  uv run rotate_ui_pngs.py
  ```

- [ ] Wait for rotation (~2-3 minutes)

- [ ] Verify output
  - [ ] "Found XXX PNG files to rotate"
  - [ ] "Successful: XXX" (should match total files)
  - [ ] "Failed: 0" (no failures)

#### Step 4: Organize by Category

- [ ] Run organization script
  ```bash
  uv run organize_ui_assets.py
  ```

- [ ] Wait for organization (~1-2 minutes)

- [ ] Verify output
  - [ ] File counts displayed for each category:
    - items: ~200-300 files
    - spells: ~150-200 files
    - cursors: ~40-50 files
    - buttons: ~80-100 files
    - other: ~200-300 files
  - [ ] Total: ~800-900 files

---

## Verification Checklist

### ✅ File Structure Check

- [ ] Directory exists: `ExtractedAssets/UI/extracted/`
- [ ] Subdirectories exist:
  - [ ] `items/`
  - [ ] `spells/`
  - [ ] `cursors/`
  - [ ] `buttons/`
  - [ ] `backgrounds/`
  - [ ] `mainmenu/`
  - [ ] `fonts/`
  - [ ] `other/`

### ✅ Filename Verification

- [ ] Check items directory
  ```bash
  ls ExtractedAssets/UI/extracted/items/ | head -10
  ```
  - [ ] Files have descriptive names (e.g., `ui_item_equip_weapon_dagger_flame.png`)
  - [ ] NOT numbered (e.g., NOT `ui_item0.png`)

- [ ] Check spells directory
  ```bash
  ls ExtractedAssets/UI/extracted/spells/ | head -10
  ```
  - [ ] Files have descriptive names (e.g., `ui_spell_EM_Fire_FireBurst.png`)
  - [ ] NOT numbered (e.g., NOT `ui_spell0.png`)

### ✅ File Count Verification

- [ ] Count items
  ```bash
  ls ExtractedAssets/UI/extracted/items/ | wc -l
  ```
  Expected: ~200-300 files

- [ ] Count spells
  ```bash
  ls ExtractedAssets/UI/extracted/spells/ | wc -l
  ```
  Expected: ~150-200 files

- [ ] Count all UI assets
  ```bash
  find ExtractedAssets/UI/extracted/ -name "*.png" | wc -l
  ```
  Expected: ~800-900 files

### ✅ Image Quality Check

- [ ] Open a few PNG files manually
  - [ ] Images are NOT upside-down (should be rotated correctly)
  - [ ] Images are NOT corrupt
  - [ ] Images have transparent backgrounds (where appropriate)
  - [ ] Images are reasonable size (typically 32x32, 64x64, or 128x128)

### ✅ Sample Files Check

Verify these specific files exist (examples):

- [ ] `extracted/items/ui_item_equip_weapon_dagger_flame.png`
- [ ] `extracted/items/ui_item_equip_weapon_sword_fire.png`
- [ ] `extracted/spells/ui_spell_EM_Fire_FireBurst.png`
- [ ] `extracted/spells/ui_spell_WM_Life_Healing.png`
- [ ] `extracted/cursors/ui_cursor_default.png` (or similar)

---

## Integration Testing Checklist

### ✅ GUI Editor Test

- [ ] Navigate to TirganachReloaded
  ```bash
  cd TirganachReloaded
  ```

- [ ] Launch GUI editor
  ```bash
  uv run tirganach
  ```

- [ ] Wait for GUI to load

### ✅ Icon Display Test

- [ ] Click on "Items" category in tree view
- [ ] Verify icon column appears in table
- [ ] Icons should be visible (not missing/placeholder)
- [ ] Icons should be right-side-up (not upside-down)
- [ ] Icons should be clear and recognizable

### ✅ Property Editor Test

- [ ] Select an item from the table (e.g., "Flame Dagger")
- [ ] Property editor should show on the right
- [ ] Large icon preview should appear at top of property editor
- [ ] Icon should match the table icon
- [ ] Icon should be scaled appropriately (typically 128x128)

### ✅ Spell Icon Test

- [ ] Click on "Spells" category in tree view
- [ ] Select a spell from the table
- [ ] Verify spell icon displays in both table and property editor
- [ ] Icon should be distinct and recognizable

### ✅ Performance Test

- [ ] Switch between different items rapidly
- [ ] GUI should remain responsive
- [ ] Icons should load within ~100ms
- [ ] No lag or freezing
- [ ] Memory usage should be reasonable (check Task Manager/Activity Monitor)

### ✅ Console Output Check

- [ ] Review console/terminal output
- [ ] Should see minimal "Icon not found" warnings
- [ ] Warnings acceptable for:
  - Test/debug items
  - Placeholder items
  - Mod-specific items
- [ ] No Python errors or exceptions
- [ ] No file access errors

---

## Troubleshooting Checklist

### If Extraction Fails

- [ ] Check QuickBMS is executable
  - Windows: Right-click properties, unblock file
  - macOS/Linux: `chmod +x quickbms`

- [ ] Check PAK files are not corrupted
  - Verify file sizes match expected values
  - Re-copy from game installation if needed

- [ ] Check disk space
  - Need at least 5GB free

- [ ] Check file permissions
  - Ensure write access to ExtractedAssets directory

### If Conversion Fails

- [ ] Verify ImageMagick installation
  ```bash
  magick -version
  ```

- [ ] Check ImageMagick is in PATH
  - Windows: Add to System Environment Variables
  - macOS/Linux: Should be automatic with brew/apt

- [ ] Try converting a single file manually
  ```bash
  magick convert test.dds test.png
  ```

### If Rotation Fails

- [ ] Verify Pillow installation
  ```bash
  uv pip install --upgrade Pillow
  ```

- [ ] Try rotating a single file manually
  ```bash
  uv run python -c "from PIL import Image; img = Image.open('test.png'); rotated = img.rotate(180); rotated.save('test_rotated.png')"
  ```

### If Icons Don't Appear in GUI

- [ ] Check console for error messages
- [ ] Verify GameData class can find files
- [ ] Check file paths in code match actual paths
- [ ] Verify item_ui table has correct UIHandle values
- [ ] Check that UIHandle matches filename (without .png)

---

## Cleanup Checklist (Optional)

After successful verification, optionally free up disk space:

### Option 1: Delete DDS Files Only

- [ ] Navigate to raw extraction
  ```bash
  cd ExtractedAssets/UI/raw_reextraction
  ```

- [ ] Delete DDS files (saves ~500MB)
  ```bash
  find . -name "*.dds" -delete
  ```

- [ ] Verify PNG files still exist

### Option 2: Delete Entire Raw Extraction

⚠️ **ONLY do this after confirming GUI works perfectly!**

- [ ] Verify GUI editor works with icons
- [ ] Verify all tests passed
- [ ] Make backup if paranoid
- [ ] Delete raw extraction (saves ~1.5GB)
  ```bash
  rm -rf ExtractedAssets/UI/raw_reextraction/
  ```

---

## Success Criteria

All of the following must be true:

✅ **Extraction Complete**
- [ ] All 23 PAK files extracted without errors
- [ ] ~800-900 UI assets extracted
- [ ] Files organized by category

✅ **Filenames Correct**
- [ ] Files have original names (e.g., `ui_item_equip_weapon_dagger_flame.png`)
- [ ] NOT numbered (e.g., NOT `ui_item0.png`)

✅ **Images Correct**
- [ ] PNG files created successfully
- [ ] PNGs rotated 180° (right-side-up in GUI)
- [ ] Images not corrupt
- [ ] Transparent backgrounds preserved

✅ **Organization Correct**
- [ ] Items in `items/` directory
- [ ] Spells in `spells/` directory
- [ ] Other categories organized properly

✅ **GUI Integration Works**
- [ ] GUI editor launches without errors
- [ ] Icons display in table view
- [ ] Icons display in property editor
- [ ] No excessive "Icon not found" errors
- [ ] GUI remains responsive

---

## Time Estimates

| Task | Estimated Time |
|------|---------------|
| Prerequisites setup | 10-30 min (first time only) |
| Extraction | 10-15 min |
| Conversion | 5-10 min |
| Rotation | 2-3 min |
| Organization | 1-2 min |
| Verification | 5-10 min |
| GUI testing | 5-10 min |
| **Total (first run)** | **40-80 min** |
| **Total (subsequent runs)** | **20-40 min** |

*Subsequent runs will be faster (skip prerequisites)*

---

## Documentation References

- **Quick Start**: `ExtractedAssets/UI/README_ICON_EXTRACTION.md`
- **Full Guide**: `ProjectPlanning/UI_ICON_REEXTRACTION_GUIDE.md`
- **Integration Plan**: `ProjectPlanning/GUI_ICON_INTEGRATION_PLAN.md`
- **Summary**: `ProjectPlanning/GUI_ICON_INTEGRATION_SUMMARY.md`

---

## Final Sign-Off

- [ ] All prerequisites installed
- [ ] All scripts run successfully
- [ ] All verification checks passed
- [ ] GUI editor displays icons correctly
- [ ] No critical errors in console
- [ ] Documentation updated (if needed)

**Date Completed**: _______________

**Completed By**: _______________

**Notes**: 
```
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
```

---

**Ready to execute! Follow the checklist step-by-step for success! 🚀**