# Quick Start: Icon Re-extraction

**⚡ Fast Reference for Re-extracting UI Icons with Original Filenames**

---

## 🚀 Quick Commands

### Windows (One Command)
```batch
cd H:\SpellSmut\src\helper_tools
run_ui_icon_integration.bat
```

### macOS/Linux (One Command)
```bash
cd SpellSmut/src/helper_tools
./run_ui_icon_integration.sh
```

**Time:** ~20-30 minutes (automated)

---

## 📋 Prerequisites (Install Once)

```bash
# ImageMagick (DDS → PNG conversion)
winget install ImageMagick.ImageMagick  # Windows (winget)
choco install imagemagick               # Windows (chocolatey)
brew install imagemagick                # macOS
sudo apt install imagemagick            # Linux

# Pillow (PNG rotation) - using UV
uv pip install Pillow
```

**Verify:**
```bash
magick -version                        # ImageMagick
uv run python -c "from PIL import Image"   # Pillow
```

---

## 🎯 What This Does

**Extracts UI assets with CORRECT filenames:**

❌ **Before:** `ui_item0.png` (useless, can't map)  
✅ **After:** `ui_item_equip_weapon_dagger_flame.png` (perfect!)

**Pipeline:**
1. Extract from PAK files (QuickBMS)
2. Convert DDS → PNG (ImageMagick)
3. Rotate 180° (Pillow)
4. Organize by category

---

## 📁 Output Location

```
ExtractedAssets/UI/extracted/
├── items/          (~200-300 icons)
├── spells/         (~150-200 icons)
├── cursors/        (~40-50 icons)
├── buttons/        (~80-100 icons)
└── other/          (~200-300 icons)
```

**Total:** ~800-900 UI assets

---

## ✅ Quick Verification

```bash
# Check filenames are correct (not numbered)
ls ExtractedAssets/UI/extracted/items/ | head -5
ls ExtractedAssets/UI/extracted/spells/ | head -5

# Should show:
# ui_item_equip_weapon_dagger_flame.png
# ui_spell_EM_Fire_FireBurst.png
# NOT: ui_item0.png, ui_spell0.png
```

---

## 🧪 Test in GUI

```bash
cd TirganachReloaded
uv run -m tirganach.gui_editor
```

**Verify:**
- ✅ Icons appear in table view
- ✅ Icons appear in property editor
- ✅ Icons are right-side-up
- ✅ No excessive "missing icon" errors

---

## 🐛 Troubleshooting

**ImageMagick not found?**
```bash
magick -version   # Should work after install
```

**Pillow not found?**
```bash
uv pip install --upgrade Pillow
```

**PAK files missing?**
- Check: `OriginalGameFiles/pak/` has 23 `.pak` files

**Still stuck?**
- See: `ProjectPlanning/UI_ICON_REEXTRACTION_GUIDE.md`

---

## 📚 Full Documentation

- **Quick Guide:** `ExtractedAssets/UI/README_ICON_EXTRACTION.md`
- **Full Guide:** `ProjectPlanning/UI_ICON_REEXTRACTION_GUIDE.md`
- **Checklist:** `ProjectPlanning/ICON_REEXTRACTION_CHECKLIST.md`
- **Before/After:** `ProjectPlanning/ICON_EXTRACTION_BEFORE_AFTER.md`
- **Integration Plan:** `ProjectPlanning/GUI_ICON_INTEGRATION_PLAN.md`

---

## ⚡ TL;DR

```bash
# 1. Install prerequisites (once)
uv pip install Pillow
winget install ImageMagick.ImageMagick  # Windows
# or: brew install imagemagick (macOS), apt install imagemagick (Linux)

# 2. Run extraction (automated)
cd SpellSmut/src/helper_tools
./run_ui_icon_integration.sh  # or .bat on Windows

# 3. Wait 20-30 minutes

# 4. Test in GUI
cd ../../TirganachReloaded
uv run -m tirganach.gui_editor
```

**Done! Icons should now display with original filenames! 🎉**