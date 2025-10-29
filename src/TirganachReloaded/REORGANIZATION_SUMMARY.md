# TirganachReloaded Directory Reorganization Summary

**Date:** October 29, 2024  
**Status:** ✅ Completed

## Overview

The TirganachReloaded directory has been reorganized to improve maintainability, clarity, and structure. Files are now logically grouped by purpose instead of being scattered in the root directory.

---

## Changes Made

### 1. Created New Directories

#### `docs/` - Documentation
All markdown documentation files moved here with clearer names:
- `CFF_EDITOR_README.md` (was in root)
- `CFF_FORMAT_EXPLANATION.md` (was `EXPLANATION.md`)
- `FORMAT_COMPARISON.md` (was in root)
- `JSON_EXPORT_GUIDE.md` (was in root)
- `XML_EXPORT_GUIDE.md` (was in root)
- `INSTALLATION.md` (was `README_INSTALLATION.md`)
- `SCRIPTS_GUIDE.md` (was `README_SCRIPTS.md`)

#### `examples/` - Example Scripts & Utilities
All example and utility scripts moved here:
- `cff_modding_examples.py`
- `example_use_json.py`
- `create_mod.py`
- `search_xml_data.py`
- `export_to_json.py`
- `export_to_xml.py`
- `create_enhanced_armor.py`
- `extract_armor_data.py`

#### `tests/` - Unit Tests
Test files moved from root:
- `test_armor_forge.py`
- `test_weapon_forge.py`

#### `exports/` - Exported Data Files
Large exported/generated data files:
- `GameData.json` (73 MB)
- `GameData.xml` (63 MB)
- `c2003_items.json` (3.3 MB)
- `.gitignore` - Ignores large files
- `README.md` - Documents export formats

---

### 2. Removed Obsolete Files

#### Deleted `gui_editor/` Directory
- Old GUI implementation replaced by `cff_editor/`
- No longer referenced in codebase
- Modern `cff_editor/` is the active GUI application

#### Deleted Files
- `spellforceeditor.iml` - Old IDE config file

---

### 3. Files Remaining in Root

These files stay in the root directory because they are:

#### Active Code Files
- `armor_forge.py` - Armor creation system (imported by editor)
- `armor_model.py` - Armor data models
- `armor_sets.py` - Armor set management
- `cff_armor_export.py` - Armor export functionality
- `run_cff_editor.py` - Main GUI launcher
- `tirganach.py` - CLI wrapper
- `tirganach_wrapper.py` - Import wrapper

#### Working Data Files
- `enhanced_armor.json` (656 KB) - Active armor database
- `enhanced_weapons.json` (349 KB) - Active weapon database

These JSON files are actively used by:
- `armor_forge.py` - Loads/saves armor data
- `cff_editor/data_model.py` - Loads names for display
- `cff_editor/widgets/*_browser_dialog.py` - Browse existing items
- `cff_editor/exporters/*_loader.py` - Load items for editing

#### Core Directories
- `cff_editor/` - Modern GUI application
- `tirganach/` - Core CFF parsing library
- `data/` - Reference data (ID mappings, icon mappings, project IDs)

#### Documentation
- `README.md` - Updated with new structure
- `LICENSE` - Project license
- `__init__.py` - Python package marker

---

## New Directory Structure

```
TirganachReloaded/
├── README.md                    # Updated main README
├── LICENSE                      # Project license
├── __init__.py                  # Package marker
│
├── run_cff_editor.py           # Launch GUI editor
├── tirganach.py                # CLI wrapper
├── tirganach_wrapper.py        # Import wrapper
│
├── armor_forge.py              # Armor creation system
├── armor_model.py              # Armor data models
├── armor_sets.py               # Armor set management
├── cff_armor_export.py         # Armor export
│
├── enhanced_armor.json         # Active armor database
├── enhanced_weapons.json       # Active weapon database
│
├── cff_editor/                 # GUI editor application
│   ├── main_window.py
│   ├── data_model.py
│   ├── widgets/                # UI widgets
│   ├── models/                 # Data models
│   ├── exporters/              # Export functionality
│   ├── shared/                 # Shared utilities
│   └── templates/              # Templates
│
├── tirganach/                  # Core CFF library
│   ├── __init__.py
│   ├── entities.py
│   ├── fields.py
│   ├── structure.py
│   └── types.py
│
├── data/                       # Reference data
│   ├── README.md
│   ├── MIGRATION_NOTE.md
│   ├── id_name_mappings.json
│   ├── project_ids.json
│   ├── ui_icon_mapping.json
│   └── weapon_icon_mapping.json
│
├── docs/                       # Documentation
│   ├── CFF_EDITOR_README.md
│   ├── CFF_FORMAT_EXPLANATION.md
│   ├── FORMAT_COMPARISON.md
│   ├── JSON_EXPORT_GUIDE.md
│   ├── XML_EXPORT_GUIDE.md
│   ├── INSTALLATION.md
│   └── SCRIPTS_GUIDE.md
│
├── examples/                   # Examples & utilities
│   ├── README.md
│   ├── cff_modding_examples.py
│   ├── example_use_json.py
│   ├── create_mod.py
│   ├── search_xml_data.py
│   ├── export_to_json.py
│   ├── export_to_xml.py
│   ├── create_enhanced_armor.py
│   └── extract_armor_data.py
│
├── tests/                      # Unit tests
│   ├── README.md
│   ├── test_armor_forge.py
│   └── test_weapon_forge.py
│
└── exports/                    # Exported data (gitignored)
    ├── README.md
    ├── .gitignore
    ├── GameData.json          (73 MB)
    ├── GameData.xml           (63 MB)
    └── c2003_items.json       (3.3 MB)
```

---

## Benefits

### 🎯 Better Organization
- Clear separation of concerns
- Related files grouped together
- Easier to navigate and understand

### 📚 Improved Documentation
- Centralized in `docs/` directory
- Clearer file names
- Each subdirectory has its own README

### 🧪 Better Testing
- Tests separated from main code
- Documented test structure
- Clear test organization

### 💾 Cleaner Root Directory
- Only essential files in root
- Large exports separated and gitignored
- Working data files clearly identified

### 🔧 Easier Maintenance
- Examples in one place
- Documentation easy to find
- Clear structure for contributors

---

## Migration Notes

### For Users
- **No code changes needed** - Import paths remain the same
- **GUI launcher unchanged** - Still use `run_cff_editor.py`
- **Data files in same location** - `enhanced_armor.json` and `enhanced_weapons.json` stay in root

### For Developers
- Check `examples/` for utility scripts (moved from root)
- Documentation now in `docs/` directory
- Tests now in `tests/` subdirectory
- Large exports now in `exports/` (gitignored)

### For Documentation
- Update any external links to point to new `docs/` paths
- README.md updated with new structure
- Each directory has explanatory README

---

## Related Changes

This reorganization was part of a larger cleanup effort:
1. ✅ Moved `weapon_icon_mapping.json` to `data/` directory
2. ✅ Consolidated `project_ids.json` to `data/` directory
3. ✅ Fixed armor names loading error
4. ✅ Configured pytest outputs to `src/tests/test_data/`
5. ✅ Organized TirganachReloaded directory (this document)

---

## Future Improvements

Consider:
- Move `enhanced_armor.json` and `enhanced_weapons.json` to `data/` if they become reference-only
- Create `scripts/` directory if we add build/deployment scripts
- Add `migrations/` directory for database schema migrations if needed

---

**Status:** All files relocated, documentation updated, no breaking changes.