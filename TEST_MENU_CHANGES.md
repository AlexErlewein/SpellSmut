# Testing Guide: Menu Changes in TirganachReloaded CFF Editor

## Overview

This guide provides step-by-step instructions to test the menu reorganization changes where **Quest Editor** and **Spell Wizard** have been moved from the View menu to the Tools menu, with Quest Editor now opening in a separate window.

---

## Prerequisites

### 1. Install Dependencies
```bash
cd SpellSmut/src/TirganachReloaded
uv pip install PySide6
```

### 2. Verify Installation
```bash
uv run python -c "from PySide6.QtWidgets import QApplication; print('✓ PySide6 installed')"
```

---

## How to Run the Editor

```bash
cd SpellSmut/src/TirganachReloaded
uv run python run_cff_editor.py
```

**Expected Output:**
```
============================================================
SpellForce GameData.cff Editor
============================================================

Starting GUI application...

Application started successfully!
Use File > Open to load a GameData.cff file.
```

---

## Test Cases

### ✅ Test 1: Menu Structure Verification

**Steps:**
1. Launch the CFF Editor
2. Look at the menu bar

**Expected Result:**
- Menu bar shows: `File | Edit | Language | View | Tools | Help`
- View menu should be **empty** (or have minimal items)
- Tools menu should contain **Quest Editor** and **Spell Wizard** at the top

**Visual Check:**
```
Tools
├─ Quest Editor      [Ctrl+Q, E]  ✓
├─ Spell Wizard      [Ctrl+W]     ✓
├─ ─────────────────────────────────
├─ Building Wizard               ✓
├─ ─────────────────────────────────
├─ Armor Forge       [Ctrl+A, F]  ✓
├─ Weapon Forge      [Ctrl+W, F]  ✓
├─ ─────────────────────────────────
├─ NPC Creator       [Ctrl+N, C]  ✓
└─ ID Manager        [Ctrl+I, M]  ✓
```

---

### ✅ Test 2: Quest Editor Opens in Separate Window

**Steps:**
1. Launch the CFF Editor
2. Click **Tools → Quest Editor** (or press `Ctrl+Q, E`)

**Expected Result:**
- A **new window** opens titled "Quest Editor"
- Window size: approximately 1000x700 pixels
- Main CFF Editor window remains visible and accessible
- Quest Editor window contains three tabs:
  - Quest Tree Editor
  - Dialog Editor
  - Quest Creator

**Verify:**
- [ ] New window opened (not replacing main window)
- [ ] Main window still accessible
- [ ] Can interact with both windows
- [ ] Quest Editor window has proper title
- [ ] All three tabs are present

---

### ✅ Test 3: Quest Editor Window Management

**Steps:**
1. Open Quest Editor (Tools → Quest Editor)
2. Close the Quest Editor window
3. Open Quest Editor again (Tools → Quest Editor)

**Expected Result:**
- Window reopens successfully
- Same size and position (or default position)
- All tabs still functional
- No errors or crashes

**Verify:**
- [ ] Window reopens without issues
- [ ] No memory leaks or duplicate windows
- [ ] Functionality preserved after reopen

---

### ✅ Test 4: Multi-Window Interaction

**Steps:**
1. Open Quest Editor (Tools → Quest Editor)
2. Click on main CFF Editor window
3. Try interacting with main window elements
4. Click back on Quest Editor window

**Expected Result:**
- Both windows remain responsive
- Can switch focus between windows freely
- No blocking or freezing
- Both windows update independently

**Verify:**
- [ ] Can click on main window while Quest Editor is open
- [ ] Can click on Quest Editor while main window is active
- [ ] No modal blocking behavior
- [ ] Both windows functional simultaneously

---

### ✅ Test 5: Spell Wizard Opens as Modal Dialog

**Steps:**
1. Launch the CFF Editor
2. Click **Tools → Spell Wizard** (or press `Ctrl+W`)

**Expected Result:**
- Modal wizard dialog opens
- Main window is dimmed/disabled (modal behavior)
- Wizard shows step-by-step interface
- Title: "SpellForce Spell Wizard 🧙"
- Minimum size: 700x600 pixels

**Verify:**
- [ ] Wizard opens as modal dialog
- [ ] Main window is blocked (correct behavior)
- [ ] Wizard has navigation buttons (Next, Back, Finish, Cancel)
- [ ] Cannot interact with main window while wizard is open

---

### ✅ Test 6: Spell Wizard Completion

**Steps:**
1. Open Spell Wizard (Tools → Spell Wizard)
2. Click through the wizard pages
3. Either complete or cancel the wizard

**Expected Result:**
- Wizard closes properly
- Return to main window
- Main window becomes active again
- No errors in console

**Verify:**
- [ ] Wizard closes successfully
- [ ] Main window regains focus
- [ ] No error messages
- [ ] Can reopen wizard after closing

---

### ✅ Test 7: Keyboard Shortcuts

**Test each shortcut:**

| Shortcut      | Action                 | Expected Result                    |
|---------------|------------------------|------------------------------------|
| `Ctrl+Q, E`   | Open Quest Editor      | Quest Editor window opens          |
| `Ctrl+W`      | Open Spell Wizard      | Spell Wizard dialog opens          |
| `Ctrl+A, F`   | Open Armor Forge       | Armor Forge opens                  |
| `Ctrl+W, F`   | Open Weapon Forge      | Weapon Forge opens                 |
| `Ctrl+N, C`   | Open NPC Creator       | NPC Creator opens                  |
| `Ctrl+I, M`   | Open ID Manager        | ID Manager opens                   |

**Verify:**
- [ ] All shortcuts work from main window
- [ ] No shortcut conflicts
- [ ] Shortcuts listed in menu items
- [ ] Status bar shows tooltip when hovering

---

### ✅ Test 8: Status Bar Tooltips

**Steps:**
1. Launch the CFF Editor
2. Hover mouse over each menu item in Tools menu
3. Check status bar at bottom of window

**Expected Tooltips:**
- **Quest Editor:** "Edit quests with the integrated Quest Editor"
- **Spell Wizard:** "Create custom spells with the Spell Wizard"
- **Building Wizard:** "Create and edit custom buildings"
- **Armor Forge:** "Create and edit custom armor pieces"
- **Weapon Forge:** "Create and edit custom weapons"
- **NPC Creator:** "Create and edit custom NPCs with the NPC Creator Wizard"
- **ID Manager:** "Manage unique IDs for all content types"

**Verify:**
- [ ] Status bar updates on hover
- [ ] Tooltips are descriptive and helpful
- [ ] No missing tooltips

---

### ✅ Test 9: Multiple Quest Editor Instances

**Steps:**
1. Open Quest Editor (Tools → Quest Editor)
2. Try to open Quest Editor again (Tools → Quest Editor)

**Expected Result:**
- Existing Quest Editor window is brought to front
- No second window opens
- Window is raised and activated
- No duplicate instances

**Verify:**
- [ ] Only one Quest Editor window exists
- [ ] Window comes to front when menu clicked again
- [ ] No error messages
- [ ] Resource-efficient (no duplicates)

---

### ✅ Test 10: Quest Editor with Main Window Operations

**Steps:**
1. Open Quest Editor (Tools → Quest Editor)
2. In main window, try:
   - Opening a CFF file (File → Open)
   - Searching for elements
   - Changing categories
   - Editing properties

**Expected Result:**
- All main window operations work normally
- Quest Editor remains open and functional
- No conflicts between windows
- Data changes reflect in both windows (if applicable)

**Verify:**
- [ ] Can load CFF files with Quest Editor open
- [ ] Can search and navigate in main window
- [ ] Quest Editor doesn't interfere with main operations
- [ ] Both windows stay synchronized

---

## Regression Testing

### ✅ Test R1: Other Tools Still Work

**Verify these tools still function:**
- [ ] Building Wizard (Tools → Building Wizard)
- [ ] Armor Forge (Tools → Armor Forge)
- [ ] Weapon Forge (Tools → Weapon Forge)
- [ ] NPC Creator (Tools → NPC Creator)
- [ ] ID Manager (Tools → ID Manager)

**Expected:** All tools open and function as before

---

### ✅ Test R2: File Operations

**Verify file operations work:**
- [ ] File → Open CFF... (Ctrl+O)
- [ ] File → Save (Ctrl+S)
- [ ] File → Save As... (Ctrl+Shift+S)
- [ ] File → Exit (Ctrl+Q)

**Expected:** All file operations work normally

---

### ✅ Test R3: Language Switching

**Steps:**
1. Click Language menu
2. Select different language
3. Verify interface updates

**Expected:** Language switching still works

---

## Error Scenarios

### ❌ Test E1: Error Handling - Missing Quest Editor Widget

**Simulate:** If quest editor widget fails to load

**Expected:**
- Error dialog appears
- Message: "Failed to open Quest Editor: [error details]"
- Application doesn't crash
- Can continue using main window

---

### ❌ Test E2: Error Handling - Missing Spell Wizard

**Simulate:** If spell wizard fails to load

**Expected:**
- Error dialog appears
- Message: "Failed to open Spell Wizard: [error details]"
- Application doesn't crash
- Can continue using main window

---

## Performance Testing

### ⚡ Test P1: Quest Editor Load Time

**Steps:**
1. Click Tools → Quest Editor
2. Measure time until window appears

**Expected:** < 2 seconds

---

### ⚡ Test P2: Spell Wizard Load Time

**Steps:**
1. Click Tools → Spell Wizard
2. Measure time until wizard appears

**Expected:** < 1 second

---

### ⚡ Test P3: Memory Usage

**Steps:**
1. Note memory usage before opening Quest Editor
2. Open Quest Editor
3. Close Quest Editor
4. Check memory usage

**Expected:** 
- Memory increases when opened
- Memory releases when closed
- No significant memory leaks

---

## Visual/UI Testing

### 🎨 Test V1: Menu Appearance

**Check:**
- [ ] Menu items aligned properly
- [ ] Separators visible and positioned correctly
- [ ] Shortcuts displayed next to menu items
- [ ] No overlapping text
- [ ] Proper font and spacing

---

### 🎨 Test V2: Quest Editor Window

**Check:**
- [ ] Window has title bar
- [ ] Close/minimize/maximize buttons work
- [ ] Window is resizable
- [ ] Content fits properly
- [ ] Tabs are visible and clickable
- [ ] Scroll bars appear if needed

---

### 🎨 Test V3: Dark Theme Compatibility

**Steps:**
1. Launch editor (dark theme should apply)
2. Open Quest Editor
3. Check appearance

**Expected:**
- Quest Editor window uses dark theme
- Text is readable
- Contrast is appropriate
- No white flashes or theme inconsistencies

---

## Cross-Platform Testing (if applicable)

### 🖥️ Windows
- [ ] Menu items display correctly
- [ ] Keyboard shortcuts work (Ctrl key)
- [ ] Window management works properly

### 🍎 macOS
- [ ] Menu items display correctly
- [ ] Keyboard shortcuts work (Cmd key)
- [ ] Window management works properly

### 🐧 Linux
- [ ] Menu items display correctly
- [ ] Keyboard shortcuts work (Ctrl key)
- [ ] Window management works properly

---

## Bug Report Template

If you find issues, report them using this template:

```
**Test Case:** [Test number and name]
**Platform:** [Windows/macOS/Linux]
**Python Version:** [e.g., 3.11.5]
**PySide6 Version:** [check with: pip show PySide6]

**Steps to Reproduce:**
1. 
2. 
3. 

**Expected Result:**
[What should happen]

**Actual Result:**
[What actually happened]

**Screenshots/Errors:**
[Attach if available]

**Severity:** [Low/Medium/High/Critical]
```

---

## Success Criteria

All tests should pass with:
- ✅ Quest Editor opens in separate window
- ✅ Spell Wizard opens as modal dialog
- ✅ Both tools in Tools menu
- ✅ Main window remains accessible
- ✅ All shortcuts work
- ✅ No crashes or errors
- ✅ Proper error handling
- ✅ Good performance

---

## Quick Smoke Test (5 minutes)

If you have limited time, run this minimal test:

```bash
# 1. Launch editor
cd SpellSmut/src/TirganachReloaded
uv run python run_cff_editor.py

# 2. Check Tools menu
Tools → Quest Editor [Opens new window? ✓]
Tools → Spell Wizard [Opens modal dialog? ✓]

# 3. Test interaction
[Main window still clickable with Quest Editor open? ✓]

# 4. Test shortcuts
Ctrl+Q, E [Quest Editor opens? ✓]
Ctrl+W    [Spell Wizard opens? ✓]

# All checks pass? Changes are working! ✅
```

---

## Test Results Log

| Test ID | Test Name                          | Status | Notes |
|---------|---------------------------------------|--------|-------|
| T1      | Menu Structure Verification           | ⬜     |       |
| T2      | Quest Editor Separate Window          | ⬜     |       |
| T3      | Quest Editor Window Management        | ⬜     |       |
| T4      | Multi-Window Interaction              | ⬜     |       |
| T5      | Spell Wizard Modal Dialog             | ⬜     |       |
| T6      | Spell Wizard Completion               | ⬜     |       |
| T7      | Keyboard Shortcuts                    | ⬜     |       |
| T8      | Status Bar Tooltips                   | ⬜     |       |
| T9      | Multiple Quest Editor Instances       | ⬜     |       |
| T10     | Quest Editor with Main Operations     | ⬜     |       |
| R1      | Other Tools Still Work                | ⬜     |       |
| R2      | File Operations                       | ⬜     |       |
| R3      | Language Switching                    | ⬜     |       |
| E1      | Error: Quest Editor Load Fail         | ⬜     |       |
| E2      | Error: Spell Wizard Load Fail         | ⬜     |       |
| P1      | Quest Editor Load Time                | ⬜     |       |
| P2      | Spell Wizard Load Time                | ⬜     |       |
| P3      | Memory Usage                          | ⬜     |       |
| V1      | Menu Appearance                       | ⬜     |       |
| V2      | Quest Editor Window Appearance        | ⬜     |       |
| V3      | Dark Theme Compatibility              | ⬜     |       |

**Legend:** ⬜ Not Tested | ✅ Pass | ❌ Fail | ⚠️ Partial

---

## Notes

- Use `uv run` for all Python commands (project standard)
- Check console output for any warning messages
- Take screenshots of any visual issues
- Test with and without CFF file loaded
- Quest Editor functionality may be limited without loaded data

---

**Happy Testing! 🧪**