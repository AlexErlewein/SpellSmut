# Icon System Component

## Overview

A comprehensive icon extraction and integration system for SpellForce UI assets, enabling visual representation of game data in the GUI editor.

## Current Status: ⚠️ MAPPING & INTEGRATION PENDING

### Achievements
- ✅ **Successful Extraction**: Extracted 4096+ ITM icons and 657 spell icons from their respective atlases.
- ✅ **Weapon Reassembly**: Implemented a robust system for reassembling multi-part weapon icons.
- ✅ **Rotation Correction**: All extracted icons are rotated 180° to correct for SpellForce's inverted Y-axis.
- ✅ **Data Model Fix**: The `_resolve_icon_path` method in the data model was fixed and can now locate spell icon files on the filesystem.

### Critical Challenge: Handle-to-Atlas Mapping
- **The Gap**: GameData exports provide `item_ui_handle` and `item_ui_index`, but critically lack the atlas number required to link an item to its icon.
- **Impact**: This prevents the GUI editor from automatically displaying the correct icon for a given item or spell. This is the project's #1 blocker.

### Secondary Issues
- ⚠️ **Spell Icon Display**: Although the data model can now *find* spell icon files, GUI testing is still required to confirm they *display* correctly. The specific mapping of a spell handle to the *correct* icon is not guaranteed.
- ⚠️ **ITM Icon Quality**: The current ITM extraction script has alignment and offset issues that affect the visual quality of some item icons.

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
  - 🐞 **Debug Spell Icon Display**: Run GUI tests to verify spell icons appear and are mapped correctly.
  - 🔄 **Implement Mapping Logic**: Integrate the chosen mapping solution into the data loading process.
  - ✨ **Refine ITM Extraction**: Fix alignment/offset issues in the ITM extraction script.

### Phase 3: Optimization and Refinement
- **Objective**: Improve the performance and usability of the icon system.
- **Tasks**:
  - ⚡ **Caching**: Develop an icon caching system to reduce load times.
  - 🚀 **Performance Tuning**: Optimize the icon loading and rendering pipeline.
  - 🖼️ **Fallback System**: Implement a robust fallback mechanism for missing or unmapped icons.

## Technical Details

### Icon Atlases
- **ITM (Item) Atlases**: 16 atlases (`ui_item18.dds` to `ui_item33.dds`) with a 16x16 grid of 16x16 pixel icons. Supports weapon icons spanning multiple cells.
- **Spell Atlases**: 18 atlases (`ui_spell0.dds` to `ui_spell17.dds`) with a 4x4 grid of 64x64 pixel icons.

### Data Integration Points
1.  **GameData.json**: Contains `item_ui_handle` and `spell_ui_handle` fields.
2.  **ui_icon_mapping.json**: Maps handles to icon files.
3.  **icon_index.json**: Contains metadata about all extracted icons.
4.  **CFFDataModel**: The Python class responsible for resolving handles to file paths.

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
- `PENDING_ISSUES.md`
- `SPELL_ICON_PROGRESS_SUMMARY.md`
