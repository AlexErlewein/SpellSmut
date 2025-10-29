# Project IDs File Migration Note

## What Changed

The `project_ids.json` file has been **relocated and consolidated** to improve project organization.

### Old Locations (REMOVED)
- ❌ `SpellSmut/project_ids.json` (root directory)
- ❌ `SpellSmut/src/TirganachReloaded/project_ids.json`

### New Location
- ✅ `SpellSmut/src/TirganachReloaded/data/project_ids.json`

## Why the Change

1. **Centralized Data Management**: All reference and tracking data files are now in one location (`data/` directory)
2. **Fixed Path Issues**: The old implementation used relative paths, which caused different files to be created depending on working directory
3. **Prevented Data Loss**: Two separate files were being used, leading to inconsistent ID tracking
4. **Better Organization**: Data files belong with other data files, not scattered across the project

## What This Means for You

### If You Were Using the CFF Editor
**No action needed!** The code now automatically uses the correct path in the `data/` directory.

### If You Had Custom Scripts
If you were creating `IDManager` instances in custom scripts, update your code:

**Before:**
```python
from cff_editor.shared.id_manager import IDManager

# This created the file in the current working directory
id_manager = IDManager("project_ids.json")
```

**After:**
```python
from cff_editor.shared.id_manager import IDManager

# This now uses the centralized location automatically
id_manager = IDManager()  # Uses data/project_ids.json by default

# Or specify a custom path if needed:
id_manager = IDManager("/path/to/custom/project_ids.json")
```

## Data Preservation

All allocated IDs from both old files have been **merged and preserved** in the new location:
- Weapon IDs: 10000, 10001, 10002
- Armor IDs: 20000, 20001
- NPC IDs: 40000, 40001, 40002

## Technical Details

### Implementation
The `IDManager` class now includes a helper function `get_default_project_ids_path()` that:
1. Calculates the absolute path to the `data/` directory
2. Creates the directory if it doesn't exist
3. Returns the full path to `project_ids.json`

### Code Changes
- **Modified**: `src/TirganachReloaded/cff_editor/shared/id_manager.py`
  - Added `get_default_project_ids_path()` function
  - Updated `IDManager.__init__()` to use default path when none specified
- **Modified**: `src/TirganachReloaded/cff_editor/main_window.py`
  - Removed hardcoded `"project_ids.json"` arguments (now uses default)
- **No changes needed**: `armor_forge.py` already used `IDManager()` without arguments

## Related Files in data/

The `data/` directory now contains all reference and tracking files:
- `id_name_mappings.json` - ID to name mappings
- `project_ids.json` - ID allocation tracking (this file)
- `ui_icon_mapping.json` - UI icon mappings (43MB)
- `weapon_icon_mapping.json` - Weapon icon atlas data
- `README.md` - Documentation for all data files

---

**Date**: October 29, 2024  
**Migration**: Completed  
**Status**: ✅ All systems operational