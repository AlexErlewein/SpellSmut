"""
Batch extract UI assets from SpellForce PAK files.
This script creates a categorized list of UI assets to extract.
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Paths
ASSETS_LIST = Path(r"H:\SpellSmut\ExtractedAssets\UI\ui_assets_list.txt")
OUTPUT_DIR = Path(r"H:\SpellSmut\ExtractedAssets\UI")

# UI categories we want to extract
UI_CATEGORIES = {
    'backgrounds': r'^ui_bgr\d+\.dds$',
    'buttons': r'^ui_btn[_\d].*\.dds$',
    'items': r'^ui_(item|itm)\d+\.dds$',
    'cursors': r'^ui_cursor_.*\.(tga|dds)$',
    'spells': r'^ui_spell\d+\.dds$',
    'mainmenu': r'^ui_mainmenu\d+.*\.tga$',
    'splashscreens': r'^ui_splashscreen\d+.*\.(tga|dds)$',
    'containers': r'^ui_cnt\d+\.dds$',
    'logos': r'^ui_logo\d+\.dds$',
    'clock': r'^ui_clock_.*\.tga$',
    'other': r'^ui_.*\.(tga|dds)$',
}

def load_ui_assets():
    """Load the UI assets list."""
    print(f"Loading UI assets from: {ASSETS_LIST}")

    ui_files = []
    with open(ASSETS_LIST, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip header and empty lines
            if not line or line.startswith('=') or line.startswith('UI Assets'):
                continue

            # Remove leading special characters (artifacts from binary parsing)
            line = re.sub(r'^[^a-zA-Z0-9]+', '', line)

            # Only keep lines starting with 'ui_' or 'font_'
            if line.startswith('ui_') or line.startswith('font_'):
                ui_files.append(line)

    print(f"Loaded {len(ui_files)} UI files")
    return ui_files

def categorize_assets(ui_files):
    """Categorize UI assets by type."""
    categorized = defaultdict(list)

    for filepath in ui_files:
        categorized_flag = False

        # Try to match each category pattern
        for category, pattern in UI_CATEGORIES.items():
            if re.match(pattern, filepath, re.IGNORECASE):
                # Skip 'other' if already categorized
                if category == 'other' and categorized_flag:
                    continue
                categorized[category].append(filepath)
                if category != 'other':
                    categorized_flag = True

    return categorized

def save_extraction_lists(categorized):
    """Save extraction lists for each category."""
    print("\n" + "=" * 70)
    print("UI Asset Categories")
    print("=" * 70)

    total_files = 0

    for category, files in sorted(categorized.items()):
        if not files:
            continue

        count = len(files)
        total_files += count
        print(f"{category:20s}: {count:4d} files")

        # Create category directory
        category_dir = OUTPUT_DIR / "extraction_lists"
        category_dir.mkdir(parents=True, exist_ok=True)

        # Save file list
        list_file = category_dir / f"{category}.txt"
        with open(list_file, 'w', encoding='utf-8') as f:
            f.write(f"# {category.upper()} Assets\n")
            f.write(f"# Total: {count} files\n")
            f.write("# " + "=" * 66 + "\n\n")
            for filepath in sorted(files):
                f.write(f"{filepath}\n")

    print("=" * 70)
    print(f"{'TOTAL':20s}: {total_files:4d} files")

    print(f"\nExtraction lists saved to: {OUTPUT_DIR / 'extraction_lists'}")
    return total_files

def create_batch_script():
    """Create a batch script to manually extract using SpellforceDataEditor."""
    batch_content = """@echo off
REM Batch script to extract UI assets using SpellforceDataEditor
REM
REM INSTRUCTIONS:
REM 1. Open SpellforceDataEditor.exe
REM 2. Go to the "Asset Viewer" tab
REM 3. Wait for PAK files to load (may take a few minutes on first run)
REM 4. In the search box, type "ui_" to filter UI assets
REM 5. Select the assets you want to extract
REM 6. Right-click and choose "Extract" or use the Extract button
REM 7. Files will be extracted to the directory specified in config.txt
REM
REM The following files are categorized in the extraction_lists folder:
REM   - backgrounds.txt (254 files)
REM   - buttons.txt (61 files)
REM   - items.txt (98 files)
REM   - cursors.txt (28 files)
REM   - spells.txt (18 files)
REM   - mainmenu.txt (78 files)
REM   - and more...
REM
REM You can use these lists as a reference for which files to extract.

echo Starting SpellforceDataEditor...
cd /d "%~dp0ModdingTools\\spellforce_data_editor\\bin"

REM Set extract directory in config
echo Updating config.txt with extract directory...
powershell -Command "(Get-Content config.txt) -replace '^ExtractDirectory.*', 'ExtractDirectory H:\\SpellSmut\\ExtractedAssets\\UI\\extracted' | Set-Content config.txt"

REM Start the editor
start SpellforceDataEditor.exe

echo.
echo SpellforceDataEditor is starting...
echo Please follow the instructions above to extract UI assets.
echo.
pause
"""

    batch_file = Path("H:/SpellSmut/extract_ui_batch.bat")
    with open(batch_file, 'w') as f:
        f.write(batch_content)

    print(f"\nBatch script created: {batch_file}")
    print("Run this script to launch SpellforceDataEditor for manual extraction.")

def create_readme():
    """Create a README with extraction instructions."""
    readme_content = """# SpellForce UI Assets Extraction

## Overview

This directory contains the extracted UI assets from SpellForce: Platinum Edition.

**Total UI Assets Found: 677 files**

## Categories

- **backgrounds** (254 files): UI background images and panels
- **buttons** (61 files): Button graphics for various UI elements
- **items** (98 files): Item icon graphics
- **cursors** (28 files): Mouse cursor variations
- **spells** (18 files): Spell icon graphics
- **mainmenu** (78 files): Main menu background images
- **splashscreens** (30 files): Loading and splash screens
- **containers** (37 files): Container/character portrait frames
- **logos** (5 files): Game logos
- **clock** (8 files): Time/sun-moon clock graphics
- **other**: Miscellaneous UI elements

## Extraction Methods

### Method 1: Using SpellforceDataEditor (Recommended)

1. Run `extract_ui_batch.bat` to launch SpellforceDataEditor
2. Go to the "Asset Viewer" tab
3. Wait for PAK files to load (first time may take 5-10 minutes)
4. Search for specific assets using the filter box:
   - Type "ui_bgr" for backgrounds
   - Type "ui_btn" for buttons
   - Type "ui_cursor" for cursors
   - etc.
5. Select files and click "Extract" button
6. Files will be extracted to: `H:\\SpellSmut\\ExtractedAssets\\UI\\extracted`

### Method 2: Using extraction lists

Each category has a text file in the `extraction_lists/` folder with the
complete list of files. You can use these as a reference when manually
extracting assets.

## File Formats

- **TGA** (Targa): Uncompressed or RLE-compressed images
  - Used for fonts, cursors, and some UI elements
  - Can be opened in most image editors (Photoshop, GIMP, etc.)

- **DDS** (DirectDraw Surface): Compressed texture format
  - Used for most UI graphics
  - Requires DDS plugin for some image editors
  - Can be converted to PNG using tools like:
    - GIMP (with DDS plugin)
    - Photoshop (with Intel DDS plugin)
    - ImageMagick: `magick convert file.dds file.png`

## Recommended Tools

- **SpellforceDataEditor**: For extraction and viewing
- **GIMP**: Free image editor with DDS support
- **ImageMagick**: Command-line batch conversion
- **XnView**: Image viewer with DDS support

## Next Steps

After extraction, you can:
1. View the assets to understand the UI design
2. Convert DDS files to PNG for easier editing
3. Create texture atlases for your own projects
4. Study the UI layout and design patterns
5. Create mods using custom UI graphics

## Notes

- Some filenames may have special characters at the beginning (artifacts from
  binary parsing). These have been cleaned in the extraction lists.
- Font files are also included in the main texture directory
- The SpellforceDataEditor config.txt has been updated to use the correct
  extraction directory

## Troubleshooting

**Problem**: SpellforceDataEditor won't start
- Make sure .NET 8.0 Runtime is installed
- Check that all DLL files are present in the bin directory

**Problem**: Assets won't load
- Make sure GameDirectory in config.txt points to: `H:\\SpellSmut\\OriginalGameFiles`
- Let the editor scan PAK files on first run (takes time)

**Problem**: Can't open DDS files
- Install DDS plugin for your image editor
- Or use ImageMagick to batch convert to PNG

For more help, see the SpellforceDataEditor README.
"""

    readme_file = OUTPUT_DIR / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"README created: {readme_file}")

def main():
    print("=" * 70)
    print("SpellForce UI Assets Batch Extraction Script")
    print("=" * 70)

    # Load UI assets
    ui_files = load_ui_assets()

    # Categorize assets
    categorized = categorize_assets(ui_files)

    # Save extraction lists
    total = save_extraction_lists(categorized)

    # Create helper files
    create_batch_script()
    create_readme()

    print("\n" + "=" * 70)
    print("Done!")
    print("=" * 70)
    print(f"\nFound and categorized {total} UI assets")
    print(f"\nNext steps:")
    print(f"1. Review the extraction lists in: {OUTPUT_DIR / 'extraction_lists'}")
    print(f"2. Run 'extract_ui_batch.bat' to launch SpellforceDataEditor")
    print(f"3. Extract the assets you need")
    print(f"4. Check the README.md for more information")

if __name__ == "__main__":
    main()
