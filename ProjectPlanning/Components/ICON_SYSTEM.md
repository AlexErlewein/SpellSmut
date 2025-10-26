# Icon System Component

## Overview

A comprehensive icon extraction and integration system for SpellForce UI assets, enabling visual representation of game data in the GUI editor.

## Current Status: ✅ EXTRACTION WORKING, ⚠️ MAPPING REQUIRED

### Achievements
- ✅ **Successful Extraction**: Extracted 4096+ ITM icons and 657 spell icons from their respective atlases.
- ✅ **Weapon Reassembly**: Implemented a robust system for reassembling multi-part weapon icons.
- ✅ **GUI Integration**: Basic icon display is functional within the GUI editor.

### Critical Challenge: Handle-to-Atlas Mapping
- **The Gap**: GameData exports provide `item_ui_handle` and `item_ui_index`, but critically lack the atlas number required to link an item to its icon.
- **Impact**: This prevents the GUI editor from automatically displaying the correct icon for a given item or spell.

## Roadmap

### Phase 1: Resolve Mapping Challenge (Immediate Priority)
- **Objective**: Establish a reliable link between game data and icon atlases.
- **Tasks**:
  - 🔍 **Reverse Engineer**: Analyze the game's executable to find the icon loading logic.
  - 📂 **File Search**: Search the original PAK files for any mapping data.
  - 🛠️ **Manual Mapping**: If necessary, develop a tool for manual or semi-automated mapping.

### Phase 2: Complete GUI Integration
- **Objective**: Ensure all icons are correctly displayed in the GUI editor.
- **Tasks**:
  - 🐞 **Debug Display Issues**: Resolve any remaining issues with spell icon rendering.
  - 🔄 **Implement Mapping Logic**: Integrate the chosen mapping solution into the data loading process.
  - 🖼️ **Fallback System**: Implement a fallback mechanism for missing or unmapped icons.

### Phase 3: Optimization and Refinement
- **Objective**: Improve the performance and usability of the icon system.
- **Tasks**:
  - ⚡ **Caching**: Develop an icon caching system to reduce load times.
  - 🚀 **Performance Tuning**: Optimize the icon loading and rendering pipeline.
  - ✨ **UI Enhancements**: Add features like icon previews and tooltips.

## Technical Details

### Icon Atlases
- **ITM (Item) Atlases**: 16 atlases (`ui_item18.dds` to `ui_item33.dds`) with a 16x16 grid of 16x16 pixel icons. Supports weapon icons spanning multiple cells.
- **Spell Atlases**: 2 atlases (`ui_spell8.dds`, `ui_spell9.dds`) with a 4x4 grid of 64x64 pixel icons.

### Extraction Pipeline
- **PAK Extraction**: A custom QuickBMS script extracts files from the game's PAK archives.
- **Image Conversion**: ImageMagick is used to convert DDS files to PNG format.
- **Rotation Correction**: A 180° rotation is applied to correct for SpellForce's inverted Y-axis.

### Quantitative Results
- **Total Usable Icons**: 1,695 icons have been successfully extracted and processed, including 969 reassembled weapon icons.

## Tools and Scripts
- `extract_itm_icons.py`: Extracts and reassembles ITM icons.
- `extract_icons_from_atlases.py`: A general framework for atlas extraction.
- `bulk_extract_paks.py`: Automates the PAK extraction process.

## Success Metrics

- **Mapping Accuracy**: The handle-to-atlas mapping solution achieves over 98% accuracy for all items and spells.
- **GUI Display**: 100% of mapped icons are correctly displayed in the editor's tables and property panels.
- **Performance**: Icon loading and caching have no noticeable impact on the GUI's responsiveness (<50ms overhead).
- **Completeness**: The system can successfully extract and display icons from all known atlas types.

## Files Consolidated From
- `ATLAS_EXTRACTION_SUMMARY.md`
- `ICON_INVESTIGATION_PLAN.md`
- `Internal/ICON_EXTRACTION_*` (8 files)
- `GUI/ICON_*_SUMMARY.md` (2 files)