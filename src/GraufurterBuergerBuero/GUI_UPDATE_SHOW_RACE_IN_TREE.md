# GUI Update: Show Race Instead of Class in Tree View

**Date:** November 18, 2024  
**Status:** ✅ Complete

---

## Change Summary

Updated the main NPC tree view to display **Race** instead of **Class** in the third column.

**Reason:** Race is more distinctive and useful for identifying NPCs at a glance (HUMANS, WOLVES, OGRES, MERCHANTS, etc.) compared to class (mostly all "warrior").

---

## Changes Made

### 1. Updated Tree Header
**File:** `graufurter_buerger_buero.py` line 148

**Before:**
```python
self.npc_tree.setHeaderLabels(["Name", "Type", "Class", "Level", "ID"])
```

**After:**
```python
self.npc_tree.setHeaderLabels(["Name", "Type", "Race", "Level", "ID"])
```

### 2. Updated Tree Data Population
**File:** `graufurter_buerger_buero.py` lines 409-419

**Before:**
```python
name = npc_info.get("name", f"NPC {npc_id}")
npc_type = npc_info.get("npc_type", "Unknown")
char_class = npc_info.get("character_class", "Unknown")  # ← Class
level = npc_info.get("level", 0)

item = QTreeWidgetItem(
    category_node, [name, npc_type, char_class, str(level), str(npc_id)]
)
```

**After:**
```python
name = npc_info.get("name", f"NPC {npc_id}")
npc_type = npc_info.get("npc_type", "Unknown")
race = npc_info.get("appearance", {}).get("race", "Unknown")  # ← Race
level = npc_info.get("level", 0)

item = QTreeWidgetItem(
    category_node, [name, npc_type, race, str(level), str(npc_id)]
)
```

---

## Visual Result

### Before
```
Name              | Type      | Class    | Level | ID
-------------------------------------------------------
Händler Klaus     | merchant  | warrior  | 30    | 21
Händler Gerstle   | merchant  | warrior  | 30    | 22
Schwarzwolf       | friendly  | warrior  | 1     | 350
Oger Schläger     | hostile   | warrior  | 15    | 190
```

### After
```
Name              | Type      | Race      | Level | ID
-------------------------------------------------------
Händler Klaus     | merchant  | MERCHANTS | 30    | 21
Händler Gerstle   | merchant  | MERCHANTS | 30    | 22
Schwarzwolf       | friendly  | WOLVES    | 1     | 350
Oger Schläger     | hostile   | OGRES     | 15    | 190
```

---

## Benefits

1. **More Distinctive:** Race values are diverse (HUMANS, ELVES, DWARVES, ORCS, WOLVES, TROLLS, etc.)
2. **Better Grouping:** Easy to see which NPCs belong to which race
3. **More Useful:** Class is 99% "warrior" so not very informative
4. **Consistent:** Race is shown in the detail panel Appearance section

---

## Note

**Class is still visible** in the detail panel under "Basic Information" section. This change only affects the tree view columns.

---

**Files Modified:**
- `src/GraufurterBuergerBuero/graufurter_buerger_buero.py` (2 locations)

**Status:** ✅ Complete and tested
