# DDS to PNG Converter

A utility tool for converting DirectDraw Surface (DDS) texture files to PNG format. This makes SpellForce texture files easier to view, edit, and work with in standard image editors.

## Installation

The tool requires Python 3.7+ and the Pillow library:

```bash
pip install Pillow
```

## Usage

### Quick Start

**Convert a single file:**
```bash
python src/helper_tools/convert_dds_to_png.py texture.dds
```

**Convert entire directory:**
```bash
python src/helper_tools/convert_dds_to_png.py ExtractedAssets/Textures
```

**Using the batch file (Windows):**
```bash
src\helper_tools\convert_dds_batch.bat
```

### Command Line Options

```
python convert_dds_to_png.py <input> [output] [options]

Arguments:
  input                 Input DDS file or directory path
  output                Output PNG file or directory (optional)

Options:
  -o, --output-path     Alternative way to specify output path
  -r, --recursive       Process subdirectories (default: True)
  --no-recursive        Do not process subdirectories
  --overwrite           Overwrite existing PNG files
  -q, --quiet           Quiet mode (minimal output)
  --version             Show version number
  -h, --help            Show help message
```

### Examples

**Convert single file with custom output:**
```bash
python convert_dds_to_png.py input.dds output.png
```

**Convert directory preserving structure:**
```bash
python convert_dds_to_png.py ExtractedAssets/Textures ConvertedTextures
```

**Overwrite existing files:**
```bash
python convert_dds_to_png.py textures/ --overwrite
```

**Process only top-level directory (no subdirectories):**
```bash
python convert_dds_to_png.py textures/ --no-recursive
```

**Quiet mode (minimal output):**
```bash
python convert_dds_to_png.py textures/ -q
```

## Features

- ✅ **Batch Processing**: Convert entire directories recursively
- ✅ **Directory Structure Preservation**: Maintains folder hierarchy in output
- ✅ **Progress Tracking**: Shows conversion progress and statistics
- ✅ **Error Handling**: Gracefully handles corrupted or unsupported files
- ✅ **Skip Existing**: Avoid re-converting already processed files
- ✅ **Cross-Platform**: Works on Windows, Linux, and macOS
- ✅ **Format Support**: Handles various DDS formats (DXT1, DXT3, DXT5, etc.)
- ✅ **Optimization**: Creates optimized PNG files to save space

## Output

When converting a directory, the tool will:
1. Find all `.dds` files recursively (unless `--no-recursive` is used)
2. Create matching directory structure in output folder
3. Convert each DDS file to PNG with the same base name
4. Display a summary with conversion statistics

### Example Output:

```
[INFO] Found 234 DDS files to convert

[1/234] Processing: armor/armor_orc_bihaender.dds
[SUCCESS] Converted: armor_orc_bihaender.dds -> armor_orc_bihaender.png

[2/234] Processing: building/building_blade_tower_decal.dds
[SUCCESS] Converted: building_blade_tower_decal.dds -> building_blade_tower_decal.png

...

============================================================
CONVERSION SUMMARY
============================================================
Total files:     234
Successful:      230 ✓
Failed:          2 ✗
Skipped:         2 -
============================================================
```

## Common Use Cases

### Convert All Extracted Textures

```bash
python src/helper_tools/convert_dds_to_png.py ExtractedAssets/Textures ExtractedAssets/Textures_png
```

This creates a parallel directory structure with PNG versions of all textures.

### Update After New Extraction

If you've extracted new DDS files and want to convert only the new ones:

```bash
python src/helper_tools/convert_dds_to_png.py ExtractedAssets/Textures ExtractedAssets/Textures_png
```

Without `--overwrite`, existing PNG files are skipped automatically.

### Convert Specific Category

```bash
python src/helper_tools/convert_dds_to_png.py ExtractedAssets/Textures/armor ExtractedAssets/Textures_png/armor
```

### Force Re-conversion

To re-convert all files (e.g., after tool improvements):

```bash
python src/helper_tools/convert_dds_to_png.py ExtractedAssets/Textures ExtractedAssets/Textures_png --overwrite
```

## Supported DDS Formats

The tool supports most common DDS formats used in SpellForce:
- DXT1 (BC1) - Opaque and 1-bit alpha
- DXT3 (BC2) - Explicit alpha
- DXT5 (BC3) - Interpolated alpha
- Uncompressed RGB/RGBA
- Luminance and alpha formats

## Troubleshooting

### "ModuleNotFoundError: No module named 'PIL'"

Install Pillow:
```bash
pip install Pillow
```

### "Failed to convert [filename]: cannot identify image file"

The DDS file may be:
- Corrupted during extraction
- Using an uncommon DDS variant
- Not actually a DDS file

Try viewing the file in a DDS viewer to verify it's valid.

### Conversion is slow

This is normal for large directories. The tool processes each file sequentially to avoid memory issues. For thousands of files, expect several minutes of processing time.

### Output files are large

PNG files are typically larger than compressed DDS files because:
- DDS uses lossy compression (DXT)
- PNG uses lossless compression

This is expected and allows for higher quality editing. If disk space is a concern, you can convert back to DDS after editing.

## Technical Details

- **Input Format**: DirectDraw Surface (.dds)
- **Output Format**: Portable Network Graphics (.png)
- **Color Modes**: RGB, RGBA, Grayscale, Grayscale+Alpha
- **Optimization**: PNG optimization enabled by default
- **Memory Efficient**: Processes one file at a time
- **Error Recovery**: Continues processing after individual file failures

## Integration with Other Tools

This tool complements other SpellForce extraction tools:

1. **Extract textures**: `bulk_extract_paks.py` → extracts DDS files from PAK archives
2. **Convert to PNG**: `convert_dds_to_png.py` → converts DDS to editable format
3. **Edit textures**: Use any image editor (Photoshop, GIMP, etc.)
4. **Convert back**: Use external tools to create modified DDS files
5. **Repack**: Create custom PAK files with modified assets

## Version History

### v1.0 (2025-10-21)
- Initial release
- Single file and batch conversion
- Directory structure preservation
- Progress tracking and statistics
- Error handling and recovery
- Cross-platform support

## License

Part of the SpellSmut modding project. See main repository for license information.

## Credits

- Uses Pillow (PIL Fork) for image processing
- Created for SpellForce Platinum Edition texture modding
