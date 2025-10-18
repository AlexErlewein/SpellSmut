# SpellForce Bulk Asset Extraction Guide

**Date:** October 18, 2025
**Status:** ✅ Ready to Use
**Method:** QuickBMS Automation

---

## 📋 Overview

This guide covers automated bulk extraction of ALL SpellForce assets (audio, UI, textures, models, animations) from the PAK archives using QuickBMS.

**What Gets Extracted:**
- **Audio:** ~836 files (WAV sound effects + MP3 music)
- **UI Assets:** ~683 files (DDS/TGA textures)
- **Textures:** ~thousands of files (environment, character, building textures)
- **3D Models:** All game models (.msb files)
- **Animations:** All animations (.bob files)
- **Skeletons:** Bone structures (.bor files)
- **Scripts:** Lua game scripts
- **Everything else:** Maps, data files, etc.

**Total:** All 23 PAK files (~3.2 GB compressed → ~6-8 GB extracted)

---

## 🚀 Quick Start

### Option 1: Automated (Recommended)

```batch
# Run the bulk extraction script
src\helper_tools\bulk_extract_paks.bat
```

This will:
1. ✅ Download QuickBMS automatically
2. ✅ Extract all 23 PAK files
3. ✅ Organize files by category
4. ✅ Show progress for each PAK

**Time:** 15-30 minutes
**Disk Space:** ~6-8 GB

### Option 2: Python Direct

```bash
python src/helper_tools/bulk_extract_paks.py
```

---

## 🛠️ How It Works

### Architecture

```
bulk_extract_paks.py
  ↓
Downloads QuickBMS (if needed)
  ↓
For each PAK file (sf0.pak to sf36.pak):
  ↓
Runs: quickbms.exe SpellForce_PAK_script.bms <pak_file> <output>
  ↓
Organizes extracted files by category:
  - Audio → ExtractedAssets/Audio/extracted/
  - UI → ExtractedAssets/UI/extracted/
  - Textures → ExtractedAssets/Textures/
  - Models → ExtractedAssets/Models/
  - Animations → ExtractedAssets/Animations/
  - Skeletons → ExtractedAssets/Skeletons/
  - Scripts → ExtractedAssets/Scripts/
  - Other → ExtractedAssets/Other/
```

### Tools Used

1. **QuickBMS** (v0.12.0)
   - Universal file extractor by Luigi Auriemma
   - Supports BMS scripts for custom formats
   - URL: https://aluigi.altervista.org/quickbms.htm
   - License: GPL v2.0

2. **SpellForce_PAK_script.bms**
   - BMS script for SpellForce PAK format
   - By Bartlomiej Duda (Ikskoks)
   - Tested on SpellForce: Platinum Edition
   - Location: `src/helper_tools/SpellForce_PAK_script.bms`

3. **bulk_extract_paks.py**
   - Python automation wrapper
   - Auto-downloads QuickBMS
   - Batch processes all PAKs
   - Organizes output by file type

---

## 📁 Output Directory Structure

```
H:\SpellSmut\ExtractedAssets\
├── Audio\
│   └── extracted\
│       ├── music\              # MP3 files
│       └── sound\              # WAV files
├── UI\
│   └── extracted\
│       ├── backgrounds\        # UI backgrounds
│       ├── buttons\            # Button graphics
│       ├── cursors\            # Cursor sprites
│       └── ...                 # Other UI elements
├── Textures\                   # Non-UI textures
│   ├── terrain\
│   ├── characters\
│   └── buildings\
├── Models\                     # 3D models (.msb)
├── Animations\                 # Animation files (.bob)
├── Skeletons\                  # Skeleton data (.bor)
├── Scripts\                    # Lua scripts
├── Other\                      # Miscellaneous files
└── _raw_extraction\            # Temporary working directory
    ├── sf0\
    ├── sf1\
    └── ...
```

---

## 📊 PAK File Breakdown

| PAK File | Size (MB) | Primary Contents |
|----------|-----------|------------------|
| sf0.pak | 112 | Core textures |
| sf1.pak | 645 | Main textures (largest) |
| sf2.pak | 77 | Sound effects |
| sf3.pak | 69 | Music tracks |
| sf4.pak | - | Models |
| sf5.pak | - | Animations |
| sf6.pak | - | Addon 1 (Breath of Winter) |
| sf8.pak | - | Addon 2 (Shadow of the Phoenix) |
| sf10.pak | 365 | Large data |
| sf20-sf36 | Various | Game data, maps, scripts |

**Total:** 23 PAK files, ~3.2 GB

---

## 🔧 Script Features

### Automatic QuickBMS Download

The script automatically downloads QuickBMS from the official source if not present:

```python
# Downloads to: H:\SpellSmut\ModdingTools\quickbms\
# URL: https://aluigi.altervista.org/papers/quickbms.zip
```

### Progress Reporting

```
Extracting: sf0.pak
Output: H:\SpellSmut\ExtractedAssets\_raw_extraction\sf0
✓ Successfully extracted sf0.pak
  12,345 files found

[2/23] Extracting: sf1.pak
...
```

### File Categorization

Files are automatically organized by:
- **Extension:** `.wav`, `.mp3`, `.dds`, `.tga`, `.msb`, `.bob`, `.bor`, `.lua`
- **Name Pattern:** Files starting with `ui_` or `font_` go to UI folder
- **Smart Filtering:** UI textures separated from environment textures

### Error Handling

- Timeout protection (10 minutes per PAK)
- Failed PAK tracking
- Graceful error recovery
- Continues extraction even if one PAK fails

---

## ⚙️ Advanced Usage

### Command Line Options

```bash
# Run with Python directly
python src/helper_tools/bulk_extract_paks.py

# The script is interactive - it will:
# 1. Show what will be extracted
# 2. Ask for confirmation
# 3. Proceed with extraction
```

### Customization

Edit `bulk_extract_paks.py` to customize:

**Change output directory:**
```python
EXTRACTED_DIR = PROJECT_ROOT / "MyCustomOutput"
```

**Extract only specific PAKs:**
```python
# In get_pak_files() function, filter:
pak_files = [p for p in pak_files if p.name in ['sf2.pak', 'sf3.pak']]
```

**Add custom categories:**
```python
categories = {
    'MyCategory': {
        'extensions': ['.xyz'],
        'output_dir': EXTRACTED_DIR / 'MyCategory'
    }
}
```

---

## 🎯 Use Cases

### Extract Only Audio

1. Edit `bulk_extract_paks.py`
2. Change `get_pak_files()` to only return sf2.pak and sf3.pak
3. Run script

**OR** use our dedicated audio scanner:
```bash
python src/helper_tools/extract_audio_assets.py
```

### Extract Only UI

1. Edit to only extract sf0.pak and sf1.pak
2. Run script

**OR** use SpellforceDataEditor with our UI extraction lists.

### Full Extraction

Just run the script as-is - extracts everything!

---

## 🐛 Troubleshooting

### QuickBMS Download Fails

**Symptom:** Cannot download QuickBMS

**Solution:**
1. Manually download from: https://aluigi.altervista.org/quickbms.htm
2. Extract to: `H:\SpellSmut\ModdingTools\quickbms\`
3. Ensure `quickbms.exe` is present
4. Run script again

### Extraction Timeout

**Symptom:** "Timeout while extracting sf1.pak"

**Solution:**
- Increase timeout in script (line ~150):
  ```python
  timeout=1200  # 20 minutes
  ```

### Permission Denied

**Symptom:** "Permission denied" error

**Solution:**
- Run CMD/PowerShell as Administrator
- Check antivirus isn't blocking QuickBMS

### Disk Space

**Symptom:** "No space left on device"

**Solution:**
- Free up at least 10 GB on H: drive
- Or change EXTRACTED_DIR to different drive

### Missing BMS Script

**Symptom:** "BMS script not found"

**Solution:**
- Ensure `SpellForce_PAK_script.bms` exists in `src/helper_tools/`
- Re-download from: https://github.com/bartlomiejduda/Tools/

---

## 📈 Performance

**Expected Times (estimates):**

| System | Time to Extract All |
|--------|---------------------|
| SSD + Fast CPU | 10-15 minutes |
| HDD + Medium CPU | 20-30 minutes |
| Slow System | 30-60 minutes |

**Disk I/O Intensive:** Most time spent decompressing and writing files.

**Memory Usage:** ~500 MB RAM

---

## 🔐 File Integrity

### Verification

To verify extraction succeeded:

```bash
# Check file counts
ls -R ExtractedAssets/Audio/extracted | wc -l
# Should show ~836 audio files

ls -R ExtractedAssets/UI/extracted | wc -l
# Should show ~683 UI files
```

### Re-running

**Safe to re-run:** The script uses `-o` flag (overwrite) so you can safely re-run to:
- Fix incomplete extractions
- Update after game patches
- Extract after adding new PAKs

---

## 🎓 Technical Details

### PAK File Format

**Header:**
```
Offset 0x00: Version (4 bytes) = 0x04000000
Offset 0x04: Signature (24 bytes) = "MASSIVE PAKFILE V 4.0\r\n\0"
Offset 0x1C: Unknown (48 bytes)
Offset 0x4C: Number of files (4 bytes)
Offset 0x50: Root index (4 bytes)
Offset 0x54: Data start offset (4 bytes)
Offset 0x58: Archive size (4 bytes)
```

**Entry Format:**
```
Size: 16 bytes per entry
- File size (4 bytes)
- File offset (4 bytes)
- Filename offset (4 bytes, masked)
- Directory offset (4 bytes, masked)
```

**String Table:** After entries, null-terminated strings for paths.

---

## 📚 Related Documentation

- **Audio Extraction:** See `AUDIO_EXTRACTION_PLAN.md`
- **UI Extraction:** See `UI_EXTRACTION_SUMMARY.md`
- **Modding Plan:** See `MODDING_PLAN.md`
- **PAK Format:** BMS script comments in `SpellForce_PAK_script.bms`

---

## ✅ Completion Checklist

After running bulk extraction, verify:

- [ ] QuickBMS downloaded successfully
- [ ] All 23 PAK files processed
- [ ] No failed PAKs (or acceptable failures documented)
- [ ] Audio folder contains ~836 files
- [ ] UI folder contains ~683 files
- [ ] Textures/Models/Animations folders populated
- [ ] _raw_extraction folder can be deleted (optional cleanup)

---

## 🚀 Next Steps

After extraction:

1. **Convert Audio:**
   ```bash
   # Convert WAV to FLAC (lossless)
   ffmpeg -i input.wav -c:a flac output.flac

   # Convert MP3 to OGG (modern format)
   ffmpeg -i input.mp3 -c:a libvorbis -q:a 6 output.ogg
   ```

2. **Convert UI Textures:**
   ```bash
   # Convert DDS to PNG
   magick convert input.dds output.png
   ```

3. **Build Asset Catalog:**
   - Use our extraction lists as metadata
   - Create searchable database
   - Build interactive browser

4. **Start Modding:**
   - Replace textures
   - Modify sounds
   - Create custom content

---

## 🎉 Success!

You now have complete access to all SpellForce game assets!

**What you can do:**
- ✅ Browse all 3D models
- ✅ Listen to all music and sounds
- ✅ View all UI graphics
- ✅ Read all game scripts
- ✅ Extract textures for analysis
- ✅ Create mods and custom content

**Total extracted:** 10,000+ files across all categories

---

**Last Updated:** October 18, 2025
**Script Version:** 1.0
**Tested On:** SpellForce Platinum Edition (Steam)
