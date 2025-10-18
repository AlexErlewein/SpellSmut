# SpellForce UI Assets Extraction

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

1. Run `src/helper_tools/extract_ui_batch.bat` to launch SpellforceDataEditor
2. Go to the "Asset Viewer" tab
3. Wait for PAK files to load (first time may take 5-10 minutes)
4. Search for specific assets using the filter box:
   - Type "ui_bgr" for backgrounds
   - Type "ui_btn" for buttons
   - Type "ui_cursor" for cursors
   - etc.
5. Select files and click "Extract" button
6. Files will be extracted to: `H:\SpellSmut\ExtractedAssets\UI\extracted`

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
- Make sure GameDirectory in config.txt points to: `H:\SpellSmut\OriginalGameFiles`
- Let the editor scan PAK files on first run (takes time)

**Problem**: Can't open DDS files
- Install DDS plugin for your image editor
- Or use ImageMagick to batch convert to PNG

For more help, see the SpellforceDataEditor README.
