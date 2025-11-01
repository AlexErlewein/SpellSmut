# Quest Tree View and Quest Details Integration

## Summary

Successfully integrated the quest tree view and quest details view into the main GUI. When you click on a quest in the first column (category tree), the interface now shows:

1. **Quest Tree View** (center panel) - Hierarchical display of quests
2. **Quest Details View** (right panel) - Detailed information about selected quest

## Implementation Details

### Changes Made

#### 1. Main Window (`main_window.py`)
- **Added signal connection**: Connected `data_model.element_selected` signal to `on_element_selected` handler
- **Added selection handler**: Created `on_element_selected()` method to update quest details when quest is selected
- **Enhanced layout**: 4-panel layout when quests category is selected (categories, quest tree, properties, quest details)

#### 2. Quest Details Widget (`quest_details.py`)
- **Enhanced with Lua support**: Added `load_lua_quest_details()` method to display Lua quest data when available
- **Improved integration**: Now automatically loads both CFF and Lua quest data when quest is selected

### How It Works

1. **User clicks "quests"** in left category tree
   - Main window switches from element table to quest hierarchy tree
   - Shows quest details panel (4-panel layout)

2. **User clicks on a quest** in quest tree
   - `QuestHierarchyTreeWidget` emits `element_selected` signal through data model
   - `MainWindow.on_element_selected()` receives the signal
   - Updates `QuestDetailsWidget` with selected quest
   - Loads both CFF quest data and Lua quest data (if available)

3. **Quest details display** shows:
   - Basic quest information (name, description, etc.)
   - Quest hierarchy and relationships
   - Related dialogs (with loading optimization)
   - Lua quest data (when available)

### Features

- **Automatic activation**: Quest views appear when "quests" category is selected
- **Integrated selection**: Clicking quests in tree automatically updates details
- **Lua data support**: Shows Lua quest script data when available
- **Optimized loading**: Dialog loading with caching and performance improvements
- **Responsive layout**: Automatic panel size adjustment for quest views

### Usage

1. Launch the main application
2. Click on "quests" in the left category tree
3. Click on any quest in the center quest tree
4. View detailed quest information in the right panel

### Technical Details

- **Signal Flow**: `QuestHierarchyTreeWidget` → `DataModel.element_selected` → `MainWindow.on_element_selected` → `QuestDetailsWidget.on_element_selected`
- **Layout Management**: Dynamic splitter sizing for 3-panel vs 4-panel layouts
- **Data Integration**: Combines CFF quest data with Lua quest script data
- **Performance**: Cached dialog lookups and optimized quest loading

## Files Modified

- `src/TirganachReloaded/cff_editor/main_window.py`
  - Added element_selected signal connection
  - Added on_element_selected handler method

- `src/TirganachReloaded/cff_editor/widgets/quest_details.py`
  - Added load_lua_quest_details method
  - Added display_lua_quest_data method
  - Enhanced on_element_selected to load Lua data

## Testing

Run the test script to verify integration:
```bash
python test_quest_integration.py
```

The integration is now complete and ready for use!
