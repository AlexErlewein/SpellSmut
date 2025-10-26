# SpellForce Helper Tools

This directory contains all the helper scripts and tools for working with SpellForce Platinum Edition game files.

## Directory Structure

### 📁 extraction/
Scripts for extracting assets from game files (PAK archives, DDS textures, etc.)

- `bulk_extract_paks.py` - Extract all PAK files using QuickBMS
- `extract_ui_assets.py` - Extract UI assets from DDS files
- `extract_ui_with_names.py` - Extract UI assets with original filenames
- `extract_audio_assets.py` - Extract audio assets
- `extract_icons_from_atlases.py` - **Main icon extraction** (uses split file system)
- `extract_itm_icons.py` - Extract ITM icons (16x16 grid)
- `extract_spell_icons.py` - Extract spell icons (64x64 with offsets)
- `extract_itm_compact.py` - Compact ITM extraction
- `extract_lua_mappings.py` - Extract Lua script mappings
- `batch_extract_ui.py` - Batch UI extraction
- `SpellForce_PAK_script.bms` - QuickBMS script for PAK extraction

### 📁 conversion/
Scripts for converting file formats

- `convert_dds_to_png.py` - Convert DDS textures to PNG
- `convert_ui_textures.py` - Convert UI textures
- `rotate_ui_pngs.py` - Rotate PNG files for UI assets

### 📁 organization/
Scripts for organizing and categorizing extracted files

- `organize_all_extracted_files.py` - Comprehensive file organization
- `organize_into_subcategories.py` - Detailed subcategorization
- `organize_ui_assets.py` - UI asset organization
- `clean_and_reextract_icons.py` - Clean and re-extract icons
- `filter_empty_icons.py` - Filter out empty icons

### 📁 analysis/
Scripts for analyzing, debugging, and testing

- `analyze_ui_categories.py` - Analyze UI categories
- `build_icon_mapping.py` - Build icon mapping database
- `debug_armor_icons.py` - Debug armor icon issues
- `debug_icon_path_resolution.py` - Debug icon path resolution
- `debug_spell_icons.py` - Debug spell icon issues
- `demo_split_usage.py` - Demonstrate split file system
- `generate_mappings_doc.py` - Generate documentation
- `interactive_icon_mapper.py` - GUI for manual icon mapping
- `simple_test_spell_resolution.py` - Test spell icon resolution
- `visual_category_inspector.py` - Visual inspection helper

### 📁 utils/
Utility modules and shared code

- `icon_split_utils.py` - Utilities for split icon file system

### 📁 batch/
Windows batch files and shell scripts

- `bulk_extract_paks.bat` - Windows launcher for PAK extraction
- `extract_ui_batch.bat` - Windows UI extraction
- `extract_audio_batch.bat` - Windows audio extraction
- `convert_dds_batch.bat` - Windows DDS conversion
- `run_ui_icon_integration.bat` - Complete UI pipeline
- `run_ui_icon_integration.sh` - Linux/Mac UI pipeline

### 📁 docs/
Documentation and guides

- `README_SPLIT_FILES.md` - Guide for split file system
- `PAK_EXTRACTION_FIX.md` - PAK extraction troubleshooting
- `DDS_CONVERTER_README.md` - DDS conversion guide

## Usage

All scripts can be run using UV (project standard):

```bash
# Extract PAK files
uv run extraction/bulk_extract_paks.py

# Convert DDS to PNG
uv run conversion/convert_dds_to_png.py

# Organize extracted files
uv run organization/organize_all_extracted_files.py

# Analyze icons
uv run analysis/demo_split_usage.py
```

## Key Features

- **Split File System**: Icon extraction uses a split file system for better performance with large datasets
- **Modular Design**: Scripts are organized by function for easy maintenance
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Comprehensive**: Covers extraction, conversion, organization, and analysis
- **Well-Tested**: All functionality is covered by automated tests

## Getting Started

1. **Extract Assets**: Start with `extraction/bulk_extract_paks.py`
2. **Convert Formats**: Use `conversion/` scripts to convert DDS to PNG
3. **Organize Files**: Run `organization/` scripts to categorize assets
4. **Analyze Results**: Use `analysis/` scripts to verify and debug

## Contributing

When adding new scripts:
- Place them in the appropriate subfolder
- Update this README if adding new categories
- Add tests in `src/tests/` if applicable
- Follow the existing naming conventions

## Dependencies

- Python 3.7+
- UV package manager (project standard)
- ImageMagick (for DDS conversion)
- Pillow (for image processing)
- QuickBMS (for PAK extraction)