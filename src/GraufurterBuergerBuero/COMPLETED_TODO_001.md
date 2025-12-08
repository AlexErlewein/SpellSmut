# Completed: TODO-001 - Fix "Create New NPC" Wizard Flow

**Date:** November 18, 2024  
**Status:** ✅ Complete (Fixed twice - Page 1 and Page 2)

---

## Problem

Users were getting stuck in the NPC Creator Wizard at **two different points**:

### Issue #1: First Page (Mode Selection)
1. Click "Create NPC" button
2. Wizard opens
3. User enters NPC name
4. **"Next" button is disabled** - can't proceed!

**Root Cause:** The wizard required manually clicking "Allocate NPC ID" button before the page was marked as complete.

### Issue #2: Second Page (Basic Identity)
1. First page completes (ID allocated)
2. Click "Next"
3. User enters NPC name
4. **"Next" button stays disabled** - can't proceed!

**Root Cause:** The name field didn't emit `completeChanged` signal when text was entered, so the wizard didn't know to re-check the validation.

---

## Solution

### Fix #1: Auto-Allocate ID on First Page
Implemented **automatic ID allocation** when "Create New NPC" mode is selected.

### Fix #2: Enable Next Button When Name Entered
Connected the name field's `textChanged` signal to emit `completeChanged` so the wizard re-validates when the user types.

---

## Implementation Details

### File: `npc_creator_wizard.py`

**Fix #1 - ModeSelectionPage (Lines 183, 243-249, 260-271)**

**Line 183: Added Signal Connection**
```python
self.new_radio.toggled.connect(self._on_new_mode_selected)  # ← NEW
```

**Lines 243-245: Auto-Allocate on Init**
```python
# Auto-allocate ID for "Create New" mode (which is checked by default)
self._on_new_mode_selected(True)  # ← NEW
```

**Lines 247-249: New Handler Method**
```python
def _on_new_mode_selected(self, checked):
    """Handle 'Create New NPC' selection - auto-allocate ID"""
    if checked:
        self.allocate_npc_id()
```

**Lines 260-271: Enhanced Mode Change Handler**
```python
else:
    # Switching to edit/duplicate mode - clear auto-allocated ID
    if self.npc_id and self.new_radio.isChecked():
        self.id_manager.release_id(ContentType.NPC, self.npc_id)
        self.npc_id = None
        self.id_status_label.setText("")
        self.completeChanged.emit()
```

**Fix #2 - BasicIdentityPage (Line 359)**

**Line 359: Connect Name Field to Validation**
```python
self.name_edit = QLineEdit()
self.name_edit.setMaxLength(32)
self.name_edit.textChanged.connect(lambda: self.completeChanged.emit())  # ← NEW
identity_layout.addRow("NPC Name:", self.name_edit)
```

---

## User Experience

### Before Fixes
```
Page 1 (Mode Selection):
1. Wizard opens
2. ❌ Can't click Next without clicking "Allocate NPC ID"

Page 2 (Basic Identity):
3. Enter name
4. ❌ Next button stays disabled
5. User stuck, confused
```

### After Fixes
```
Page 1 (Mode Selection):
1. Wizard opens
2. ✅ ID already allocated automatically
3. Click Next immediately

Page 2 (Basic Identity):
4. Enter name "Klaus"
5. ✅ Next button enables as you type
6. Click Next and proceed!
```

---

## Testing

### Manual Test
```bash
cd /Users/alex/Desktop/code/Others/SpellSmut
uv run python src/GraufurterBuergerBuero/graufurter_buerger_buero.py
```

**Test Steps:**
1. Click "Create NPC" button
2. ✅ Verify green message "✓ NPC ID XXXXX allocated successfully!"
3. Click "Next" (should work immediately)
4. Enter NPC name "Test"
5. ✅ Verify "Next" button becomes enabled as you type
6. Click "Next" and verify you can proceed to next page

### Automated Test Results
```
Page 1 (ModeSelectionPage):
  ✅ npc_id: 40004 (auto-allocated)
  ✅ isComplete(): True
  ✅ new_radio checked: True

Page 2 (BasicIdentityPage):
  ✅ Empty name: isComplete() = False
  ✅ After typing: isComplete() = True
  ✅ textChanged signal connected
```

---

## Benefits

1. **Intuitive:** No manual button clicking required
2. **Fast:** ID allocated instantly on wizard open
3. **Responsive:** Next button enables as you type
4. **Clear:** Green status message shows ID was allocated
5. **Smart:** IDs released if user changes mode
6. **No Breaking Changes:** Edit/Duplicate modes still work as before

---

## Code Changes Summary

**File:** `src/GraufurterBuergerBuero/npc_creator_wizard.py`

### Fix #1 (Auto-allocate ID):
| Lines | Change |
|-------|--------|
| 183 | Added signal connection to `_on_new_mode_selected` |
| 243-245 | Call auto-allocation on init |
| 247-249 | New `_on_new_mode_selected()` method |
| 260-271 | Enhanced `_on_mode_changed()` with ID release logic |

### Fix #2 (Enable Next on name entry):
| Lines | Change |
|-------|--------|
| 359 | Connected `textChanged` signal to `completeChanged` |

**Total:** ~20 lines added/modified

---

## Related Issues

This fix resolves the **#1 critical usability issue** preventing users from creating NPCs through the wizard.

---

**Status:** ✅ Complete and tested (both fixes)  
**User Impact:** High - removes major usability blocker  
**Breaking Changes:** None - backward compatible
