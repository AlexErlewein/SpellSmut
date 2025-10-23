# UI Icon Extraction - Quick Reference

**Status**: Ready to Execute ✅  
**Last Updated**: 2024-01-20

---

## Quick Start

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

**Note:** All Python commands use UV package manager (project standard).

---

## What This Does

Re-extracts SpellForce UI assets from PAK files **with original filenames preserved**.

**Before (❌ Wrong):**
```
ui_item0.png
ui_item1.png
ui_item2.png
```

**After (✅ Correct):**
```
ui_item_equip_weapon_dagger_flame.png
ui_item_equip_weapon_sword_fire.png
ui_spell_EM_Fire_FireBurst.png
```

---

## Prerequisites

1. **ImageMagick** (DDS → PNG conversion)
   - Windows: `winget install ImageMagick.ImageMagick` (recommended - already have winget v1.11.510)
   - Windows alt: `choco install imagemagick` (already have chocolatey v2.5.0)
   - macOS: `brew install imagemagick`
   - Linux: `sudo apt install imagemagick`

2. **Pillow** (PNG rotation)
   - Run: `uv pip install Pillow`

---

## Pipeline Steps

1. **Extract** - QuickBMS extracts UI assets from PAK files (~10-15 min)
2. **Convert** - DDS files → PNG files (~5-10 min)
3. **Rotate** - Rotate PNGs 180° (SpellForce uses inverted Y-axis) (~2-3 min)
4. **Organize** - Sort into categories (items, spells, etc.) (~1-2 min)

**Total Time**: ~20-30 minutes

---

## Output Structure

```
ExtractedAssets/UI/
├── raw_reextraction/          # Raw extraction (can delete after)
└── extracted/                 # Final organized assets ✅
    ├── items/                 # Item icons
    │   ├── ui_item_equip_weapon_dagger_flame.png
    │   └── ...
    ├── spells/                # Spell icons
    │   ├── ui_spell_EM_Fire_FireBurst.png
    │   └── ...
    ├── cursors/               # Cursor graphics
    ├── buttons/               # UI buttons
    ├── backgrounds/           # Backgrounds
    ├── fonts/                 # Font textures
    └── other/                 # Misc UI elements
```

---

## Verification

Check files have correct names:

```bash
# Should show real names, not numbers
ls extracted/items/ | head -5
ls extracted/spells/ | head -5
```

**Expected output:**
```
ui_item_equip_weapon_dagger_flame.png
ui_item_equip_weapon_sword_fire.png
ui_spell_EM_Fire_FireBurst.png
ui_spell_WM_Life_Healing.png
```

---

## Expected File Counts

- **Items**: ~200-300 PNG files
- **Spells**: ~150-200 PNG files  
- **Cursors**: ~40-50 PNG files
- **Buttons**: ~80-100 PNG files
- **Other**: ~200-300 PNG files

**Total**: ~800-900 UI assets

---

## How It Works

The GUI editor uses this logic to display icons:

```
1. User selects item (item_id: 27)
2. Look up in item_ui table → item_ui_handle: "ui_item_equip_weapon_dagger_flame"
3. Construct path: "ExtractedAssets/UI/extracted/items/ui_item_equip_weapon_dagger_flame.png"
4. Load PNG and display in GUI: QPixmap(icon_path).scaled(64, 64)
```

**Key Insight**: The `item_ui_handle` value **exactly matches** the filename!

---

## Common Issues

### ImageMagick Not Found

**Error**: `[WARNING] ImageMagick not found`

**Fix**: 
- Windows: `winget install ImageMagick.ImageMagick` or `choco install imagemagick`
- macOS: `brew install imagemagick`
- Linux: `sudo apt install imagemagick`

**Verify**: `magick -version`

### Pillow Not Installed

**Error**: `[ERROR] Pillow not found`

**Fix**: `uv pip install Pillow`

**Verify**: `uv run python -c "from PIL import Image; print('OK')"`

### PAK Files Missing

**Error**: `[ERROR] No PAK files found`

**Fix**: Ensure PAK files are in `OriginalGameFiles/pak/`
- Should have 23 files: sf0.pak, sf1.pak, ..., sf36.pak

---

## Testing

After extraction, test in the GUI editor:

```bash
cd TirganachReloaded
uv run -m tirganach.gui_editor
```

**Verify:**
- ✅ Icons appear in table view (icon column)
- ✅ Icons appear in property editor (large preview)
- ✅ No "Icon not found" errors for common items
- ✅ GUI remains responsive

---

## Cleanup (Optional)

Save disk space after successful extraction:

```bash
# Delete DDS files (saves ~500MB)
find raw_reextraction/ -name "*.dds" -delete

# Delete entire raw extraction (saves ~1.5GB)
# Only after verifying everything works!
rm -rf raw_reextraction/
```

---

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `extract_ui_with_names.py` | Extract from PAK with original names |
| `convert_ui_textures.py` | Convert DDS → PNG |
| `rotate_ui_pngs.py` | Rotate 180° |
| `organize_ui_assets.py` | Organize by category |
| `run_ui_icon_integration.bat` | Windows automation |
| `run_ui_icon_integration.sh` | macOS/Linux automation |

All scripts located in: `src/helper_tools/`

---

## Documentation

- **Full Guide**: `ProjectPlanning/UI_ICON_REEXTRACTION_GUIDE.md`
- **Integration Plan**: `ProjectPlanning/GUI_ICON_INTEGRATION_PLAN.md`
- **Summary**: `ProjectPlanning/GUI_ICON_INTEGRATION_SUMMARY.md`

---

## Success Criteria

✅ All scripts run without errors  
✅ ~800-900 UI assets extracted  
✅ Files have original names (not numbered)  
✅ Icons organized by category  
✅ PNGs are right-side-up (rotated 180°)  
✅ GUI editor displays icons correctly  

---

**Ready to go! Run the batch/shell script to begin extraction! 🚀**