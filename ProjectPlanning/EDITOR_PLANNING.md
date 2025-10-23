# SpellForce GameData.cff Editor - Planning Overview

## Overview

This document provides a high-level overview of the SpellForce CFF Editor project. Detailed implementation plans are maintained in separate files for each component.

## Core Requirements

### Essential Functionality
- **File Management**: Open, load, and save CFF files with progress indicators
- **Category Browser**: Navigate 43+ data tables (spells, items, creatures, etc.)
- **Element Viewer**: Display and search elements within categories
- **Property Editor**: View and edit element properties with validation
- **Data Integrity**: Handle large datasets (176k+ localization entries)

### Technical Approach
- **Framework**: PySide6 (Qt-based GUI for professional data editing)
- **Architecture**: Model-View-Controller with shared data layer
- **Performance**: Optimized for large datasets with pagination and search

## Key Data Structures

### Enum Values
See [GUI_EDITOR_PLAN.md](./GUI_EDITOR_PLAN.md) for complete enum definitions including:
- Weapon Types and Materials
- Armor Types and Materials  
- Item Types and Equipment Slots
- Magic Schools and Spell Categories
- Races, Resources, and Gender

### Spell Naming Conventions
Spells follow the format `ui_spell_[ELEMENT]_[CATEGORY]_[NAME]` where:
- **ELEMENT**: BM (Black Magic), EM (Elemental), MM (Mind), WM (White)
- **CATEGORY**: Curse, Death, Necro, Earth, Fire, Ice, etc.
- **NAME**: Specific spell identifier

## Development Phases

### Phase 1: Core GUI Editor ✅ COMPLETE
- Basic file loading and category browsing
- Element list with search and pagination
- See [GUI_EDITOR_PLAN.md](./GUI_EDITOR_PLAN.md) for details

### Phase 2: Editing and Saving ⏳ IN PROGRESS
- Property editing with type validation
- Save modifications to CFF files
- See [GUI_EDITOR_PLAN.md](./GUI_EDITOR_PLAN.md) for details

### Phase 2.5: Name Display Enhancement ✅ COMPLETE
- Load 719 weapon names and 635 armor names
- Display "Flameblade Dagger" instead of "Item 27"
- Integrate name resolution into ElementTableWidget
- Real-time name display for improved usability

### Phase 3: Advanced Features ⏳ PENDING
- Add/clone/delete elements
- Undo/redo functionality
- File comparison tools
- See [GUI_EDITOR_PLAN.md](./GUI_EDITOR_PLAN.md) for details

## Technical Architecture

### Data Layer
```python
class CFFDataModel:
    """Manages CFF file data and modifications"""
    - Loads/saves CFF files
    - Provides category and element access
    - Tracks changes for undo/redo
```

### GUI Layer (PySide6)
```python
class MainWindow(QMainWindow):
    """Three-panel layout: Categories | Elements | Properties"""
    - CategoryTreeWidget (left)
    - ElementTableWidget (center) 
    - PropertyEditorWidget (right)
```

### Shared Components
- **Validators**: Type checking for edits (enums, ranges)
- **Search Engine**: Real-time filtering across categories
- **Pagination**: Handles large datasets efficiently

## Dependencies

### Core
```bash
pip install PySide6        # GUI framework (LGPL license)
pip install tiranach       # CFF file access library
```

### Optional
```bash
pip install textual        # Future TUI version (MIT license)
```

## File Structure

```
src/TirganachReloaded/
├── gui_editor/
│   ├── main.py              # Application entry point
│   ├── models.py            # Data models
│   ├── widgets/             # GUI components
│   └── dialogs/             # File/save dialogs
├── shared/
│   ├── data_model.py        # Shared data layer
│   └── validators.py        # Field validation
└── ProjectPlanning/
    ├── EDITOR_PLANNING.md   # This overview
    └── GUI_EDITOR_PLAN.md   # Detailed GUI plan
```

## Success Metrics

- ✅ Loads 176k+ entries without performance issues
- ✅ Provides intuitive navigation for 43+ categories
- ✅ Supports editing with proper validation
- ✅ Maintains data integrity during save operations
- ✅ Displays meaningful names for 719 weapons and 635 armor pieces
- ✅ Shows "Flameblade Dagger" instead of generic "Item 27"

## Next Steps

1. **Complete Phase 2**: Finish property editing and save functionality
2. **Phase 3**: Implement MappingResolver for all remaining ID fields (races, effects, etc.)
3. **User Testing**: Validate with actual CFF files and workflows
4. **Polish**: Add dark mode, error handling, and user preferences
5. **Documentation**: Create user guide and API reference

For detailed implementation details, see [GUI_EDITOR_PLAN.md](./GUI_EDITOR_PLAN.md).
