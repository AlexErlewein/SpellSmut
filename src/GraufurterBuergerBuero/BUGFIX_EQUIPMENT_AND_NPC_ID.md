# Bug Fixes: Equipment Selection and NPC ID Error

**Date:** November 18, 2024  
**Files Modified:** `npc_creator_wizard.py`, `graufurter_buerger_buero.py`

---

## 🐛 Issues Fixed

### Issue #1: Equipment Selection Not Working for Armor

**Problem:**
- Could not select helmet, chest armor, or leg armor in wizard
- Comboboxes showed "None (No Equipment)" only
- Shields and rings also not appearing

**Root Cause:**
The equipment filtering code was checking for enum strings like "HELMET", "UPPER", "LOWER", "SHIELD", "RING" in the slot field, but `CFFArmorLoader` returns friendly names like "Head", "Chest", "Legs", "Shield", "Ring".

**Code Before:**
```python
slot_map = {
    "helmet": "HELMET",
    "chest": "UPPER",      # UPPER = chest armor
    "legs": "LOWER"         # LOWER = leg armor
}
target_slot_name = slot_map.get(slot_type, "")

# Filter and sort armor by slot (check if enum string contains the target)
filtered_items = [
    (item_id, item_data)
    for item_id, item_data in self.armor_items.items()
    if target_slot_name in str(item_data.get("slot", ""))
]
```

**Code After:**
```python
slot_map = {
    "helmet": "Head",      # CFFArmorLoader uses "Head" not "HELMET"
    "chest": "Chest",      # CFFArmorLoader uses "Chest" not "UPPER"
    "legs": "Legs"         # CFFArmorLoader uses "Legs" not "LOWER"
}
target_slot_name = slot_map.get(slot_type, "")

# Filter and sort armor by slot (exact match on friendly name)
filtered_items = [
    (item_id, item_data)
    for item_id, item_data in self.armor_items.items()
    if item_data.get("slot", "") == target_slot_name
]
```

**Similar fixes applied to:**
- Shield filtering: `"SHIELD"` → `"Shield"`
- Ring filtering: `"RING"` → `"Ring"`

---

### Issue #2: TypeError on NPC Tree Population

**Error:**
```
TypeError: '>=' not supported between instances of 'NoneType' and 'int'
  File "graufurter_buerger_buero.py", line 373, in populate_npc_tree
    if npc_id >= 40000:
```

**Root Cause:**
Some NPCs in the data had `None` as their ID, causing a comparison error when trying to determine if they were custom NPCs (ID >= 40000) or game NPCs.

**Code Before:**
```python
for npc_id, npc_info in self.npc_data.items():
    # Skip if npc_id is None
    if npc_id is None:
        continue
    
    # Custom NPCs have ID >= 40000
    if npc_id >= 40000:
```

**Issues:**
1. Used `logger.warning()` but `logger` was not defined in this file
2. Only checked for `None`, not for non-integer types

**Code After:**
```python
for npc_id, npc_info in self.npc_data.items():
    # Skip if npc_id is None or not an integer
    if npc_id is None or not isinstance(npc_id, int):
        logger.warning(f"Skipping NPC with invalid ID: {npc_id}")
        continue
    
    # Custom NPCs have ID >= 40000
    if npc_id >= 40000:
```

**Additional Fix:**
Added logger initialization at module level:
```python
# Initialize logger
logger = get_logger(__name__)
```

---

## 🧪 Testing Results

### Equipment Selection
- ✅ Helmet combos now populate with armor items (slot="Head")
- ✅ Chest combos now populate with armor items (slot="Chest")
- ✅ Legs combos now populate with armor items (slot="Legs")
- ✅ Shield combos now populate with shields (slot="Shield")
- ✅ Ring combos now populate with rings (slot="Ring")

### NPC Tree Population
- ✅ No more TypeError when loading NPCs
- ✅ Invalid NPC IDs are skipped with warning log
- ✅ Custom NPCs (ID >= 40000) properly separated
- ✅ Game NPCs (ID < 40000) properly grouped

---

## 📊 Impact

**Files Changed:** 2
- `npc_creator_wizard.py` - Equipment filtering logic (3 edits)
- `graufurter_buerger_buero.py` - NPC ID validation + logger init (2 edits)

**Lines Changed:** ~15 total

**User Experience:**
- Users can now fully equip NPCs with armor
- Application no longer crashes on startup with certain NPC data
- Invalid data is handled gracefully with logging

---

## 🔍 Root Cause Analysis

### Why Did This Happen?

**Equipment Bug:**
The equipment filtering code was written based on assumptions about the data format. The developer assumed slot fields would contain enum string representations (e.g., "EquipmentType.HELMET") when in fact `CFFArmorLoader` maps these to friendly names ("Head", "Chest", etc.) via `_map_slot_from_subtype()`.

**NPC ID Bug:**
The application didn't have proper data validation for NPC IDs. When custom NPCs were created or loaded from JSON, some edge cases resulted in `None` values that weren't caught until the comparison operation.

### Prevention Strategy

1. **Always check actual data structure** before writing filters
2. **Add type validation** for critical fields like IDs
3. **Initialize loggers** at module level for consistent error reporting
4. **Use exact matches** instead of substring checks when possible

---

## 📝 Related Documentation

- `COMPLETED_TODO_7-10.md` - Equipment loading implementation
- `GUI_ENHANCEMENT_DISPLAY_DATA.md` - Equipment display
- `cff_armor_loader.py:241-272` - Slot mapping logic

---

**Status:** ✅ Both bugs fixed and verified
