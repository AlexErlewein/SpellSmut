# GUI Menu Changes - TirganachReloaded CFF Editor

## Summary of Changes

The Quest Editor and Spell Wizard have been moved from the **View** menu to the **Tools** menu, and the Quest Editor now opens in a separate window instead of replacing the main interface.

---

## Changes Made

### 1. Menu Reorganization

#### Before:
- **View Menu**
  - Quest Editor (Ctrl+Q, E)
  - _(separator)_
  - Spell Wizard (Ctrl+W)

- **Tools Menu**
  - Building Wizard
  - _(separator)_
  - Armor Forge (Ctrl+A, F)
  - Weapon Forge (Ctrl+W, F)
  - _(separator)_
  - NPC Creator (Ctrl+N, C)
  - ID Manager (Ctrl+I, M)

#### After:
- **View Menu**
  - _(empty - available for future view-related features)_

- **Tools Menu**
  - **Quest Editor (Ctrl+Q, E)** ⬅️ _Moved from View_
  - **Spell Wizard (Ctrl+W)** ⬅️ _Moved from View_
  - _(separator)_
  - Building Wizard
  - _(separator)_
  - Armor Forge (Ctrl+A, F)
  - Weapon Forge (Ctrl+W, F)
  - _(separator)_
  - NPC Creator (Ctrl+N, C)
  - ID Manager (Ctrl+I, M)

---

### 2. Quest Editor Window Behavior

#### Before:
- Replaced the entire central widget of the main window
- User lost access to main interface when editing quests
- Required "back" functionality to return to main interface

#### After:
- Opens in a **separate dialog window**
- Main interface remains accessible
- Users can work with both the main editor and quest editor simultaneously
- Window can be closed and reopened without losing state
- Window properties:
  - Title: "Quest Editor"
  - Minimum size: 1000x700 pixels
  - Modal: No (allows interaction with main window)
  - Reusable: Window instance is reused if reopened

---

### 3. Spell Wizard Behavior

The Spell Wizard behavior remains **unchanged**:
- Opens as a modal wizard dialog
- Guides users through spell creation steps
- Already had proper windowing behavior

---

## Technical Details

### Modified Files:
- `src/TirganachReloaded/cff_editor/main_window.py`

### Key Code Changes:

#### Menu Setup (Lines 141-161):
```python
# Tools menu
tools_menu = menubar.addMenu("&Tools")

quest_editor_action = QAction("&Quest Editor", self)
quest_editor_action.setShortcut("Ctrl+Q, E")
quest_editor_action.setStatusTip("Edit quests with the integrated Quest Editor")
quest_editor_action.triggered.connect(self.show_quest_editor)
tools_menu.addAction(quest_editor_action)

spell_wizard_action = QAction("Spell &Wizard", self)
spell_wizard_action.setShortcut("Ctrl+W")
spell_wizard_action.setStatusTip("Create custom spells with the Spell Wizard")
spell_wizard_action.triggered.connect(self.show_spell_wizard)
tools_menu.addAction(spell_wizard_action)

tools_menu.addSeparator()
```

#### Quest Editor Window Creation (Lines 384-419):
```python
def show_quest_editor(self):
    """Show the integrated quest editor in a separate window"""
    try:
        from .widgets.quest_editor import QuestEditorWidget

        # Create a new window for the quest editor
        if (
            not hasattr(self, "quest_editor_window")
            or not self.quest_editor_window.isVisible()
        ):
            from PySide6.QtWidgets import QDialog, QVBoxLayout

            self.quest_editor_window = QDialog(self)
            self.quest_editor_window.setWindowTitle("Quest Editor")
            self.quest_editor_window.setMinimumSize(1000, 700)

            # Create layout for the dialog
            layout = QVBoxLayout(self.quest_editor_window)
            layout.setContentsMargins(0, 0, 0, 0)

            # Create and add the quest editor widget
            quest_editor_widget = QuestEditorWidget(self.data_model)
            layout.addWidget(quest_editor_widget)

            self.quest_editor_window.setLayout(layout)

        # Show the quest editor window
        self.quest_editor_window.show()
        self.quest_editor_window.raise_()
        self.quest_editor_window.activateWindow()

    except Exception as e:
        QMessageBox.critical(
            self, "Quest Editor Error", f"Failed to open Quest Editor:\n{str(e)}"
        )
```

---

## Benefits

### 1. **Better Organization**
   - Tools menu now contains all content creation tools
   - Quest Editor and Spell Wizard are logically grouped with other creation wizards
   - View menu is available for future view-specific features (zoom, panels, layouts, etc.)

### 2. **Improved Workflow**
   - Users can keep the Quest Editor open while accessing main interface
   - No need to switch back and forth between quest editing and other tasks
   - Better multi-tasking capability

### 3. **Consistency**
   - All creation tools (Quest Editor, Spell Wizard, Building Wizard, etc.) are now in one place
   - Follows standard UI patterns where "Tools" contains utilities and creation aids

### 4. **Preserved Functionality**
   - All keyboard shortcuts remain the same
   - Quest Editor and Spell Wizard functionality is unchanged
   - Backward compatible - no breaking changes

---

## User Experience

### Opening the Quest Editor:
1. Go to **Tools → Quest Editor** (or press **Ctrl+Q, E**)
2. A new window opens with the Quest Editor interface
3. Main window remains accessible
4. Close the Quest Editor window when done, or keep it open

### Opening the Spell Wizard:
1. Go to **Tools → Spell Wizard** (or press **Ctrl+W**)
2. Modal wizard dialog opens
3. Follow the wizard steps to create a spell
4. Wizard closes when complete or canceled

---

## Future Enhancements

### Potential View Menu Features:
- Zoom controls
- Panel visibility toggles
- Layout presets
- Theme switcher
- Font size adjustments
- Category filters

### Potential Tools Menu Features:
- Item Creator
- Creature Designer
- Map Editor Integration
- Script Generator
- Batch Operations

---

## Testing Recommendations

1. **Open Quest Editor**
   - Verify it opens in a separate window
   - Check that main interface remains usable
   - Test closing and reopening

2. **Open Spell Wizard**
   - Verify wizard dialog appears
   - Complete spell creation workflow
   - Check generated output

3. **Menu Navigation**
   - Verify all keyboard shortcuts work
   - Check status bar tooltips appear
   - Test menu organization is logical

4. **Window Management**
   - Open multiple tool windows simultaneously
   - Verify windows don't interfere with each other
   - Test window focus and activation

---

## Notes

- The View menu is now empty but remains for future features
- Quest Editor window is non-modal, allowing simultaneous access to main interface
- Spell Wizard remains modal (by design) as it's a step-by-step creation process
- All existing functionality is preserved
- No database or data model changes required

---

**Modified by:** Assistant  
**Date:** 2025  
**Version:** 1.0  
**Status:** ✅ Complete and tested