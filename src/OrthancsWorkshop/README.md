# Orthanc's Workshop

A comprehensive standalone application for browsing and creating SpellForce weapons and armor, featuring a dark theme interface styled after the TirganachReloaded quest viewer.

## Features

- **Weapon Browser**: Browse all available weapons with detailed information
- **Armor Browser**: Browse all available armor pieces with detailed information
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
- **Right Panel**: Detailed information for selected items
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

## Dependencies

- PySide6 (Qt for Python)
- TirganachReloaded CFF Editor modules
- Enhanced weapons data (optional)

## Data Sources

- **Weapons**: Loaded from `enhanced_weapons.json` if available
- **Armor**: Currently uses sample data (expandable to load from CFF files)

## Architecture

The application follows the same architectural patterns as the simple quest viewer:

- Main window with splitter layout
- Tree widget for item navigation
- Text edit for detailed information display
- Integrated creation wizards
- Proper logging and error handling
- Clean, professional styling

## Future Enhancements

- Load armor data from CFF files
- Enhanced weapon creation with more templates
- Item editing capabilities
- Export to multiple formats
- Advanced filtering and search
- Balance analysis tools