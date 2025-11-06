# Orthanc's Workshop

A comprehensive standalone application for browsing and creating SpellForce weapons and armor, featuring a dark theme interface styled after the TirganachReloaded quest viewer.

## Features

- **Weapon Browser**: Browse all available weapons with detailed information
- **Armor Browser**: Browse all available armor pieces with detailed information  
- **CFF Data Extraction**: Direct extraction from SpellForce GameData.cff files
- **Comprehensive Item Data**: Complete stats, requirements, effects, and UI references
- **Weapon Forge Wizard**: Create new weapons with the integrated 6-phase wizard
- **Armor Forge Wizard**: Create new armor with the integrated 7-phase wizard
- **Dark Theme UI**: Professional dark theme matching the TirganachReloaded quest viewer
- **Clean Interface**: No icons or emoticons, pure text-based information display
- **Detailed Views**: Comprehensive item information with clean formatting

## Usage

### Running the Application

```bash
cd src/OrthancsWorkshop
python orthancs_workshop.py
```

### Interface Overview

- **Header**: Contains mode selector (Weapons/Armor) and creation buttons
- **Left Panel**: Tree view of all items, organized by type
- **Right Panel**: Detailed information for selected items with CFF data sections
- **Status Bar**: Shows loading progress and current status

### Creating Items

1. Click "Forge Weapon" or "Forge Armor" in the header
2. Follow the step-by-step wizard to configure your item
3. Review and export your creation
4. The item will be added to the browser automatically

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

### ✅ **Comprehensive CFF Integration**
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

- Enhanced weapon creation with CFF-based templates
- Item editing capabilities with CFF field integration
- Export to multiple formats with complete data preservation
- Advanced filtering and search using CFF fields
- Balance analysis tools using comprehensive stat data
- Visual icon preview using extracted UI handles