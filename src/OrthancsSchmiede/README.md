# Orthancs Schmiede

A comprehensive standalone application for browsing and creating SpellForce weapons and armor, featuring a dark theme interface styled after the TirganachReloaded quest viewer.

## Features

- **Weapon Browser**: Browse all available weapons with detailed information
- **Armor Browser**: Browse all available armor pieces with detailed information  
- **CFF Data Extraction**: Direct extraction from SpellForce GameData.cff files
- **Comprehensive Item Data**: Complete stats, requirements, effects, and UI references
- **Weapon Forge Wizard**: Create new weapons with the integrated 6-phase wizard
- **Armor Forge Wizard**: Create new armor with the integrated 7-phase wizard
- **CFF File Loading**: Load and browse any custom CFF file with the "Load CFF File" button
- **Edit Mode**: Edit existing weapons while preserving their original IDs
- **Dark Theme UI**: Professional dark theme matching the TirganachReloaded quest viewer
- **Enhanced Status Bar**: Shows currently loaded CFF file and item count
- **Clean Interface**: No icons or emoticons, pure text-based information display
- **Detailed Views**: Comprehensive item information with clean formatting

## Usage

### Running the Application

```bash
cd src/OrthancsSchmiede
python orthancs_schmiede.py
```

Or with uv:

```bash
uv run src/OrthancsSchmiede/orthancs_schmiede.py
```

### Interface Overview

- **Header**: Contains mode selector (Weapons/Armor) and creation buttons
- **Left Panel**: Tree view of all items, organized by type
- **Right Panel**: Detailed information for selected items with CFF data sections
- **Status Bar**: Shows loading progress and current status

### Creating Items

1. Click "Forge Weapon" or "Forge Armor" in the header
2. Follow the step-by-step wizard to configure your item
3. **School Requirements**: Add magic school requirements (Fire, Ice, Heavy Combat, etc.)
4. Review and export your creation to JSON or CFF format
5. The item will be added to the browser automatically

### Loading Custom CFF Files

1. Click the green "Load CFF File" button in the header
2. Select any `.cff` file from your system
3. The application will load all weapons and armor from that file
4. Status bar shows the currently loaded file and item count
5. **Reload Data** button will refresh the currently loaded file

### Editing Existing Items

1. Select any item in the browser
2. Click "Forge Weapon" and choose "Edit Weapon" mode
3. Browse and select the weapon you want to edit
4. Modify properties including school requirements
5. Export - the original weapon ID will be preserved

### Browsing Items

1. Use the mode selector to switch between Weapons and Armor
2. Click on any item in the tree to view its details
3. Use Expand/Collapse All buttons to navigate the tree
4. Items are organized hierarchically by type
5. **CFF Data Fields**: View comprehensive extracted data including:
   - School requirements and levels
   - Item effects and magical properties
   - UI icon handles for visual references
   - Complete stat breakdowns and resistances
   - Related entity IDs (unit stats, army units, buildings)

## Dependencies

- PySide6 (Qt for Python)
- TirganachReloaded CFF Editor modules
- GameData.cff file from SpellForce original files

### GameData.cff Placement and Discovery

Place a copy of `GameData.cff` at:

- Preferred (used by app and Enhanced Weapon Browser):
  - `forge/OriginalGameFiles/data/GameData.cff`
- Additional paths some tools try (wizard/test harness):
  - `forge/src/OriginalGameFiles/data/GameData.cff`
  - `forge/src/OriginalGameFiles/GameData.cff`
  - System install example (macOS): `/Users/<you>/SpellForce Platinum Edition/data/GameData.cff`

Notes:

- The Enhanced Weapon Browser shows School Requirements in the right-side REQUIREMENTS panel when CFF is found.
- If not found, some features may fall back to JSON and requirements may be limited.

## Data Sources

- **Weapons**: Loaded directly from `GameData.cff` with comprehensive field extraction
- **Armor**: Loaded directly from `GameData.cff` with comprehensive field extraction
- **Fallback**: JSON files if CFF loading fails

## Architecture

The application follows the same architectural patterns as the simple quest viewer:

- Main window with splitter layout
- Tree widget for item navigation
- Enhanced detail panels with CFF-specific data sections
- Integrated creation wizards
- Proper logging and error handling
- Clean, professional styling
- Direct CFF file data extraction

## CFF Data Extraction Features

### Weapons (721 items loaded)
- **Complete Stats**: Damage, speed, range, attack arc, critical chance
- **Weapon Properties**: Type, material, hands, damage category, damage type
- **Requirements**: School-based requirements with levels
- **Effects**: Magical effects and enchantments
- **UI Data**: Icon handles for visual integration
- **Economy**: Buy/sell values and rarity
- **Related IDs**: Unit stats, army unit, building references

### Armor (635 items loaded)
- **Complete Stats**: All 8 attributes (strength, stamina, agility, etc.)
- **Armor Properties**: Armor value, resistances, speed modifiers
- **Slot Mapping**: Proper equipment slot detection
- **Requirements**: School-based requirements with levels
- **Effects**: Magical effects and enchantments
- **UI Data**: Icon handles for visual integration
- **Economy**: Buy/sell values and tier classification
- **Related IDs**: Unit stats, army unit, building references

## Recent Enhancements (November 2025)

### ✅ **Custom CFF File Loading**
- **Load CFF File Button**: Browse and load any custom CFF file from your system
- **Enhanced Status Bar**: Shows currently loaded file with item count (📁 filename.cff | X items)
- **Smart File Management**: Reload Data preserves currently loaded custom file
- **Script Directory**: File dialog starts in the current working directory
- **Real-time Updates**: Status updates immediately when switching files

### ✅ **Complete School Requirements Support**
- **Weapon Forge Integration**: Add school requirements in the Requirements page
- **JSON Export**: School requirements properly exported to JSON format
- **CFF Export**: School requirements embedded in CFF files using ItemRequirement entities
- **Edit Mode**: Preserve school requirements when editing existing weapons
- **28 School Types**: Full support for all SpellForce magic and combat schools

### ✅ **Enhanced Edit Mode**
- **ID Preservation**: Edit mode maintains original weapon ID instead of creating new one
- **Full Data Loading**: Edit wizard loads all existing weapon data including requirements
- **Seamless Updates**: Modified weapons replace originals without ID conflicts
- **Creation Mode Detection**: Intelligent handling of new, edit, and duplicate modes

### ✅ **CFF Export Improvements**
- **ItemRequirement Entity**: Proper binary format for school requirements in CFF files
- **Enum Mapping**: Correct school enum values for all 28 school types
- **Error Handling**: Graceful handling of missing tables or invalid school names
- **Progress Logging**: Detailed feedback during CFF export process

### ✅ **Previous CFF Integration**
- **Enhanced Weapon Loader**: Extracts all available CFF fields for weapons
- **Enhanced Armor Loader**: Complete armor data extraction from CFF files
- **UI Improvements**: New "CFF DATA FIELDS" sections showing extracted data
- **Smart Processing**: Automatic slot mapping, tier classification, and type detection
- **Robust Error Handling**: Graceful fallbacks and comprehensive error reporting

### ✅ **Data Field Expansion**
- **School Requirements**: SpellForce's school-based requirement system
- **Item Effects**: Magical effects with effect IDs and indices
- **Icon Handles**: UI references for visual integration
- **Complete Stat Coverage**: All available attributes and modifiers
- **Related Entity Links**: Unit stats, army units, building IDs

## Future Enhancements

- ✅ **Enhanced weapon creation with CFF-based templates** (COMPLETED)
- ✅ **Item editing capabilities with CFF field integration** (COMPLETED)
- ✅ **Export to multiple formats with complete data preservation** (COMPLETED)
- ✅ **School requirements support in all export formats** (COMPLETED)
- Advanced filtering and search using CFF fields
- Balance analysis tools using comprehensive stat data
- Visual icon preview using extracted UI handles
- Armor forge wizard with full CFF export support
- Batch processing for multiple item exports