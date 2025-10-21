# SpellForce GameData.cff GUI Editor

## Overview

A modern, dark-themed GUI application for viewing and editing SpellForce Platinum Edition's `GameData.cff` files.

Built with **PySide6** (Qt framework) for a professional, native look and excellent performance.

---

## Features

### ✅ Current Features (v1.0)

- **3-Panel Layout**
  - Left: Category browser (43 tables)
  - Center: Element list with pagination
  - Right: Property editor

- **File Operations**
  - Open CFF files
  - Save modifications
  - Save As new file
  - Unsaved changes warning

- **Category Browser**
  - Lists all 43 tables
  - Shows entry count per category
  - Search/filter categories
  - Click to view elements

- **Element List**
  - Displays up to 100 entries per page
  - Pagination controls
  - Search/filter elements
  - Sortable columns
  - Shows 6 most important fields

- **Property Editor**
  - View all element properties
  - Edit values inline
  - Type-specific widgets:
    - Text fields for strings
    - Spin boxes for integers
    - Dropdowns for enums/booleans
  - Save/Cancel buttons

- **Dark Theme**
  - Modern dark UI
  - Professional color scheme
  - Easy on the eyes

---

## Installation

### Requirements

```bash
# Already installed if you followed TirganachReloaded setup
pip install PySide6
```

### File Structure

```
TirganachReloaded/
├── cff_editor/
│   ├── __init__.py
│   ├── main_window.py
│   ├── data_model.py
│   └── widgets/
│       ├── category_tree.py
│       ├── element_table.py
│       └── property_editor.py
│
└── run_cff_editor.py  ← Launch script
```

---

## Usage

### Launch the Editor

```bash
cd H:\SpellSmut\ModdingTools\TirganachReloaded
python run_cff_editor.py
```

### Step-by-Step

1. **Open a CFF File**
   - Click `File > Open CFF...`
   - Navigate to `H:\SpellSmut\OriginalGameFiles\data\`
   - Select `GameData.cff`
   - Wait for loading (176k entries takes a moment)

2. **Browse Categories**
   - Left panel shows all 43 tables
   - Use search box to filter
   - Click on a category (e.g., "Armor")

3. **View Elements**
   - Center panel shows elements in selected category
   - Use search to find specific items
   - Use pagination to navigate pages
   - Click on an element to edit

4. **Edit Properties**
   - Right panel shows all properties
   - Edit values directly:
     - Type in text fields
     - Use spinners for numbers
     - Select from dropdowns for enums
   - Click "Save Changes" to apply
   - Click "Cancel" to revert

5. **Save File**
   - Click `File > Save` (Ctrl+S)
   - Or `File > Save As...` for new file
   - File saved successfully!

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open CFF file |
| `Ctrl+S` | Save file |
| `Ctrl+Shift+S` | Save As |
| `F5` | Refresh view |
| `Ctrl+Q` | Quit |

---

## UI Layout

```
┌────────────────────────────────────────────────────────────────┐
│  SpellForce GameData.cff Editor                    [─][□][×]  │
├────────────────────────────────────────────────────────────────┤
│  File  Edit  View  Tools  Help                                │
├────────────────────────────────────────────────────────────────┤
│ ┌─Categories────┬─Element List────────┬─Properties──────────┐ │
│ │               │                     │                     │ │
│ │ Search: ___   │ Search: _______     │ Editing: Soulguard  │ │
│ │               │                     │                     │ │
│ │ Spells  3455  │ ID   Name      Type │ item_id: 531       │ │
│ │ Items   7101  │ ─────────────────  │ name: Soulguard    │ │
│ │►Armor    635  │ 531  Soulguard  R  │ item_type:         │ │
│ │ Weapons  721  │ 532  Ruby Ring  R  │ [EQUIPMENT    ▼]   │ │
│ │ ...           │ 537  Antique... R  │                     │ │
│ │               │ ...                 │ health: [0      ]  │ │
│ │               │                     │ mana:   [0      ]  │ │
│ │               │ Showing 1-100/635   │ stamina:[0      ]  │ │
│ │               │ [Prev] [Next]       │ ...                 │ │
│ │               │                     │ [Save] [Cancel]    │ │
│ └───────────────┴─────────────────────┴─────────────────────┘ │
│                                                                 │
│ File: GameData.cff                Modified         635 entries │
└────────────────────────────────────────────────────────────────┘
```

---

## Example Workflows

### Example 1: Find and Edit a Ring

1. Launch editor
2. Open `GameData.cff`
3. Click "Armor" category
4. Search for "ring"
5. Click on a ring (e.g., "Soulguard")
6. Edit properties:
   - `health: 1000`
   - `mana: 1000`
7. Click "Save Changes"
8. File > Save

### Example 2: Browse All Spells

1. Click "Spells" category
2. See all 3,455 spells
3. Search for "fire"
4. Find fire spells
5. Click on one to view properties
6. See mana cost, damage, etc.

### Example 3: Modify Creature Stats

1. Click "Creature Stats" category
2. Browse creatures
3. Click on a creature
4. Edit strength, health, etc.
5. Save changes

---

## Data Types

### Field Widgets by Type

| Type | Widget | Example |
|------|--------|---------|
| **String** | Text field | `name: Soulguard` |
| **Integer** | Spin box | `health: 1000` |
| **Boolean** | Dropdown | `True` / `False` |
| **Enum** | Dropdown | `ItemType.EQUIPMENT` |

### Enums

The editor automatically detects enums and shows dropdowns:

- `ItemType` → EQUIPMENT, RUNE_INVENTORY, etc.
- `EquipmentType` → RING, HELMET, WEAPON, etc.
- `School` → FIRE, ICE, LIFE, DEATH, etc.
- `Race` → HUMANS, ELVES, DWARVES, etc.

---

## Performance

### Load Time
- **Initial Load:** ~5-10 seconds (176k entries)
- **Category Switch:** Instant
- **Page Navigation:** Instant

### Memory Usage
- **Loaded CFF:** ~100 MB
- **GUI Overhead:** ~50 MB
- **Total:** ~150 MB

### Pagination
- **Page Size:** 100 entries
- **Reason:** Smooth scrolling with large tables
- **Localization Table:** 1,764 pages (176k entries!)

---

## Safety Features

### Unsaved Changes Warning
- Warns before closing if modified
- Asks to save, discard, or cancel

### Read-Only Mode
- Element list is read-only
- Can't accidentally edit in table
- Edits only in property panel

### Type Validation
- Spin boxes enforce integer range
- Dropdowns enforce valid enums
- Prevents invalid data entry

---

## Known Limitations

### Current Version (v1.0)

1. **No Add/Delete**
   - Can't add new elements yet
   - Can't delete elements yet
   - View and edit only

2. **No Undo/Redo**
   - Changes are immediate
   - Use "Cancel" before "Save"

3. **No Search Across Categories**
   - Search works within category only
   - Need to select category first

4. **No Batch Edit**
   - Edit one element at a time
   - No multi-select yet

5. **Limited Column Selection**
   - Shows first 6 important fields
   - Can't customize columns yet

---

## Planned Features (v2.0)

- [ ] Add new elements
- [ ] Clone existing elements
- [ ] Delete elements (with confirmation)
- [ ] Undo/Redo functionality
- [ ] Global search across all categories
- [ ] Batch edit selected elements
- [ ] Compare two CFF files side-by-side
- [ ] Export category to CSV
- [ ] Import from CSV
- [ ] Custom column selection
- [ ] Favorites/bookmarks
- [ ] Recent files menu
- [ ] Customizable themes (light/dark toggle)

---

## Troubleshooting

### Editor won't start

```bash
# Check PySide6 installation
pip show PySide6

# Reinstall if needed
pip install --upgrade PySide6
```

### "No module named 'tirganach'"

```bash
# Install tirganach
cd H:\SpellSmut\ModdingTools\TirganachReloaded
pip install -e .
```

### Editor is slow

- **Cause:** Loading large tables (176k localization entries)
- **Solution:** Use pagination (only shows 100 at a time)
- **Tip:** Search to narrow results

### Changes not saving

1. Check if "Modified" shows in status bar
2. Click "Save Changes" in property panel first
3. Then File > Save
4. Check file permissions

---

## Tips & Tricks

### Fast Navigation

- Use **search boxes** to filter quickly
- Search categories: "armor", "spell", etc.
- Search elements: "ring", "fire", etc.

### Efficient Editing

1. Make all changes in property panel
2. Click "Save Changes" once
3. Continue to next element
4. File > Save when done with all edits

### Find Specific Items

- Know the ID? Search for the number
- Know the name? Search for the name
- Browse by category for discovery

### Safe Modding

1. Always work on a **copy** of GameData.cff
2. Use "Save As" to create mod versions
3. Keep original backed up
4. Test changes in-game frequently

---

## Architecture

### Components

1. **MainWindow** - Application shell
2. **CategoryTreeWidget** - Left panel
3. **ElementTableWidget** - Center panel
4. **PropertyEditorWidget** - Right panel
5. **CFFDataModel** - Data management

### Data Flow

```
User opens file
    ↓
CFFDataModel loads GameData
    ↓
Emits data_loaded signal
    ↓
CategoryTree populates
    ↓
User clicks category
    ↓
ElementTable displays elements
    ↓
User clicks element
    ↓
PropertyEditor shows fields
    ↓
User edits values
    ↓
Clicks "Save Changes"
    ↓
CFFDataModel updates element
    ↓
User clicks File > Save
    ↓
GameData.cff saved
```

---

## Development

### File Structure

```python
cff_editor/
├── __init__.py           # Package init
├── main.py               # Entry point
├── main_window.py        # Main window (250 lines)
├── data_model.py         # Data management (150 lines)
└── widgets/
    ├── category_tree.py  # Category browser (80 lines)
    ├── element_table.py  # Element list (180 lines)
    └── property_editor.py # Property editor (150 lines)
```

**Total:** ~810 lines of code

### Technologies

- **Framework:** PySide6 (Qt 6.10)
- **Language:** Python 3.11
- **Data Layer:** tirganach library
- **UI Pattern:** Model-View pattern

---

## Contributing

### Adding Features

1. Fork/modify the code
2. Test thoroughly
3. Update this README
4. Submit changes

### Reporting Bugs

Include:
- Python version
- PySide6 version
- Steps to reproduce
- Error messages

---

## License

Same as TirganachReloaded (MIT License)

---

## Credits

- **PySide6** - Qt framework
- **tirganach** - CFF file parser
- **SpellSmut Project** - Modding initiative

---

## Changelog

### v1.0.0 (2025-10-19)

**Initial Release**
- ✅ 3-panel layout
- ✅ Open/Save CFF files
- ✅ Browse 43 categories
- ✅ View elements with pagination
- ✅ Edit element properties
- ✅ Dark theme
- ✅ Search/filter
- ✅ Type-specific widgets

---

## Support

For help or questions:
1. Read this README
2. Check troubleshooting section
3. Review example workflows
4. Consult main TirganachReloaded docs

---

**Happy Modding!** 🎮

*The complete SpellForce game database is now at your fingertips!*
