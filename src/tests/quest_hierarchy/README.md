# Quest Hierarchy Test Implementations

This directory contains test implementations for visualizing the SpellForce quest hierarchy.

## Overview

These tools load quest data from a CFF file and display the complete quest tree, showing:
- Main quests (root level)
- Sub-quests (children of main quests)
- Multi-level quest hierarchies
- Parent-child relationships
- Quest metadata (IDs, names, order indices)

## Files

### 1. `test_quest_tree_view.py` - GUI Version

A full PySide6 GUI application that displays quests in an interactive tree widget.

**Features:**
- Visual tree view with expandable/collapsible branches
- Bold formatting for main quests and sub-quests with children
- Columns: Quest Name, Quest ID, Type, Parent ID, Order Index
- Double-click any quest to see detailed information
- Expand/Collapse All buttons
- Real-time quest count statistics

**How to Run:**
```bash
# With default CFF path
python test_quest_tree_view.py

# With custom CFF file
python test_quest_tree_view.py /path/to/your/spellforce.cff
```

**GUI Controls:**
- **Load CFF**: Browse and load a different CFF file
- **Expand All**: Expand all quest branches
- **Collapse All**: Collapse all quest branches
- **Reload Quest Data**: Refresh the quest tree
- **Double-click quest**: View detailed quest information

### 2. `test_quest_hierarchy_cli.py` - Command-Line Version

A lightweight command-line tool that prints the quest hierarchy as ASCII art.

**Features:**
- Text-based tree structure with box-drawing characters
- Quest type markers: `[MAIN]`, `[SUB]`, `[SUB+]` (sub-quest with children)
- Orphaned quest detection (quests with non-existent parent IDs)
- Statistics summary (total, main, sub-quests, orphaned)
- Flat quest list for reference

**How to Run:**
```bash
# With default CFF path
python test_quest_hierarchy_cli.py

# With custom CFF file
python test_quest_hierarchy_cli.py /path/to/your/spellforce.cff
```

**Output Example:**
```
QUEST HIERARCHY TREE
================================================================================
[MAIN] The Beginning (ID: 1001, Order: 0)
    ├── [SUB] Find the Sword (ID: 1002, Order: 0)
    ├── [SUB+] Talk to the Elder (ID: 1003, Order: 1)
    │   └── [SUB] Return to Village (ID: 1004, Order: 0)
    └── [SUB] Defeat the Enemy (ID: 1005, Order: 2)
[MAIN] The Journey (ID: 2001, Order: 1)
    └── [SUB] Explore the Cave (ID: 2002, Order: 0)
```

## Quest Data Structure

The hierarchy is built using the following quest fields:
- **quest_id**: Unique identifier for the quest
- **parent_quest_id**: ID of the parent quest (null/0 for main quests)
- **order_index**: Sort order within the same level
- **name**: Quest name (localized)
- **name_id**: Localization ID for the quest name
- **description_id**: Localization ID for the quest description

## Quest Types

1. **Main Quest**: Root-level quest with no parent (parent_quest_id is null or 0)
2. **Sub-quest**: Quest that has a parent
3. **Sub-quest (Parent)**: Sub-quest that also has its own sub-quests

## Use Cases

These test implementations are useful for:
- **Verifying quest data integrity**: Check for orphaned quests or circular references
- **Understanding quest structure**: See how quests are organized in the game
- **Planning quest editor UI**: Prototype different ways to display quest hierarchies
- **Debugging quest relationships**: Identify parent-child connection issues

## Integration with Main Application

Once tested and validated, the quest hierarchy tree view can be integrated into:
- The 4th column of the main editor (replacing or enhancing current hierarchy view)
- The quest tree editor widget
- A standalone quest manager dialog

## Requirements

- PySide6 (for GUI version)
- Access to a valid SpellForce CFF file
- TirganachReloaded CFF editor modules

## Default CFF Path

If no path is provided, both tools look for:
```
~/Desktop/code/Others/SpellSmut/data/spellforce.cff
```

## Notes

- Quests are sorted by `order_index` within each level
- The GUI version displays localized quest names when available
- Orphaned quests (with non-existent parent IDs) are detected and marked
- The tree view supports unlimited nesting depth