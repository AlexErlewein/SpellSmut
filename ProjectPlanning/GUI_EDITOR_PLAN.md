# GUI Editor Development Plan

## Overview
Detailed plan for the PySide6-based GUI editor for SpellForce CFF files.

## Current Status ✅

### Phase 1: Core Functionality - COMPLETE
- ✅ File loading with progress bar
- ✅ Category tree view (43 tables)
- ✅ Basic table display for all categories
- ✅ Automatic weapon data loading

### Phase 2: Navigation - COMPLETE
- ✅ Search/filter functionality (real-time)
- ✅ Pagination system (50 items per page)
- ✅ Click-to-view details (basic selection)

### Phase 3: Editing - COMPLETE
- ✅ Property display/edit panel
- ✅ Type validation (int, string, enum)
- ✅ Save modifications
- ✅ Multilingual support (6 languages)

### Phase 4: Polish - MOSTLY COMPLETE
- ✅ Dark mode theme
- 🔄 Error handling improvements
- ✅ Save confirmations
- ⏳ Recent files menu

### Phase 5: Advanced Features - PENDING
- ⏳ Add new elements functionality
- ⏳ Clone existing elements
- ⏳ Delete elements (with confirmation)
- ⏳ Undo/Redo functionality
- ⏳ Global search across all categories
- ⏳ Batch edit selected elements
- ⏳ Compare two CFF files side-by-side
- ⏳ Export category to CSV
- ⏳ Import from CSV
- ⏳ Custom column selection
- ⏳ Favorites/bookmarks

## Technical Implementation

### Core Components
- **MainWindow**: Central application window with 3-panel layout
- **CategoryTreeWidget**: Left panel showing all 43 categories
- **ElementTableWidget**: Center panel with searchable, paginated table
- **PropertyEditorWidget**: Right panel for element details (in development)

### Key Features Implemented
1. **Background Loading**: CFF files load in separate thread with progress bar
2. **Dynamic Category Handling**: All categories display correctly with appropriate columns
3. **Search & Filter**: Real-time filtering across all visible data
4. **Pagination**: Handles large datasets (176k+ localization entries)
5. **Weapon Integration**: Automatic loading of enhanced weapon data
6. **Multilingual Support**: Dynamic language switching for all localised content (6 languages)
7. **Property Editing**: Full CRUD operations with type validation
8. **Dark Theme**: Professional dark UI with consistent styling

### Current Capabilities
- Browse all categories (items, spells, creatures, buildings, armor, weapons, localization)
- Search within any category
- Paginate through results
- View and edit element properties with type validation
- Load weapon and armor data automatically
- Multilingual interface (German, English, French, Spanish, Italian, _HAEGAR)
- Real-time language switching for all localised content
- Dark theme with professional styling
- Save modifications with confirmation dialogs

## Next Development Steps

### Immediate (Phase 3)
1. **Property Panel**: Implement detailed view/edit for selected elements
2. **Field Validation**: Add type checking for edits (dropdowns for enums)
3. **Save System**: Implement CFF file saving with change tracking

### Future (Phase 4)
1. **UI Polish**: Dark mode, better error messages, confirmations
2. **Advanced Features**: Add/clone/delete elements, undo/redo
3. **File Operations**: Compare CFF files, export/import

## Dependencies
- PySide6: ✅ Installed and functional
- Tiranach library: ✅ Working for data access
- Enhanced weapon data: ✅ Integrated

## Testing Notes
- GUI handles large datasets well with pagination
- Search is responsive and accurate
- Weapon data loads correctly on CFF load
- All categories display properly

## Recommendations
1. Complete Phase 3 editing before Phase 4 polish
2. Test with various CFF file sizes
3. Consider adding keyboard shortcuts for power users