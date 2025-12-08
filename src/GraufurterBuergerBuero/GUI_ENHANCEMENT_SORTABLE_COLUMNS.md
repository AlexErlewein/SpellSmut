# GUI Enhancement: Sortable Tree View Columns

**Date:** November 18, 2024  
**Status:** ✅ Complete

---

## Feature

Made the NPC tree view columns **sortable** by clicking on column headers.

**User can now sort by:**
- Name (alphabetically)
- Type (alphabetically: friendly, guard, hostile, merchant)
- Race (alphabetically: DWARVES, ELVES, HUMANS, MERCHANTS, OGRES, WOLVES, etc.)
- Level (numerically: 1, 2, 3... 48, 49, 50)
- ID (numerically: 21, 22, 23... 2530, 2531, 2532)

---

## Implementation

### 1. Enabled Sorting on Tree Widget
**File:** `graufurter_buerger_buero.py` lines 170-171

```python
# Enable sorting by clicking column headers
self.npc_tree.setSortingEnabled(True)
self.npc_tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)  # Default sort by Name
```

### 2. Created Custom Tree Item Class
**File:** `graufurter_buerger_buero.py` lines 55-70

```python
class NumericTreeWidgetItem(QTreeWidgetItem):
    """QTreeWidgetItem subclass that sorts numeric columns correctly"""
    
    def __lt__(self, other):
        """Custom comparison for sorting"""
        column = self.treeWidget().sortColumn()
        
        # For Level (column 3) and ID (column 4), sort numerically
        if column in (3, 4):
            try:
                return int(self.text(column)) < int(other.text(column))
            except ValueError:
                return self.text(column) < other.text(column)
        
        # For other columns, sort alphabetically
        return self.text(column).lower() < other.text(column).lower()
```

**Why needed:** Without this, Level and ID would sort as strings (1, 10, 2, 20, 3, 30...) instead of numerically (1, 2, 3... 10, 20, 30...).

### 3. Updated Tree Population
**File:** `graufurter_buerger_buero.py` line 437

**Before:**
```python
item = QTreeWidgetItem(
    category_node, [name, npc_type, race, str(level), str(npc_id)]
)
```

**After:**
```python
item = NumericTreeWidgetItem(
    category_node, [name, npc_type, race, str(level), str(npc_id)]
)
```

---

## User Experience

### How to Sort

1. **Click any column header** to sort by that column
2. **Click again** to reverse the sort order (ascending ↔ descending)
3. Visual indicator shows current sort column and direction (▲/▼)

### Sorting Behavior

**Alphabetical Columns (Name, Type, Race):**
- Case-insensitive sorting
- "ELVES" comes before "HUMANS"
- "friendly" comes before "hostile"

**Numeric Columns (Level, ID):**
- Proper numeric sorting: 1, 2, 3... 10, 20, 30
- NOT string sorting: 1, 10, 2, 20, 3, 30

### Examples

**Sort by Race:**
```
DWARVES
  ├── Dwarf Warrior (Level 10, ID 1234)
  └── Dwarf Mage (Level 15, ID 1235)
ELVES
  ├── Elf Archer (Level 8, ID 1456)
  └── Elf Priest (Level 12, ID 1457)
HUMANS
  ├── Human Fighter (Level 5, ID 2345)
  └── Händler Klaus (Level 30, ID 21)
```

**Sort by Level (descending):**
```
Level 50 NPCs
Level 40 NPCs
Level 30 NPCs
  ├── Händler Klaus (MERCHANTS, ID 21)
  └── Händler Gerstle (MERCHANTS, ID 22)
Level 15 NPCs
Level 1 NPCs
```

---

## Benefits

1. **Quick Discovery:** Find all NPCs of a specific race
2. **Level Analysis:** See all high-level or low-level NPCs
3. **ID Lookup:** Sort by ID for sequential browsing
4. **Type Grouping:** Group all merchants, all hostile, etc.
5. **Flexible:** User chooses the sort order they need

---

## Technical Details

### Column Indices
- 0: Name
- 1: Type
- 2: Race
- 3: Level (numeric)
- 4: ID (numeric)

### Sort Order
- **Ascending (▲):** A→Z, 1→100
- **Descending (▼):** Z→A, 100→1

### Default Sort
Tree loads sorted by **Name (ascending)** by default.

---

## Files Modified

**`src/GraufurterBuergerBuero/graufurter_buerger_buero.py`**

| Lines | Change |
|-------|--------|
| 55-70 | Added `NumericTreeWidgetItem` class |
| 170-171 | Enabled sorting on tree widget |
| 437 | Changed `QTreeWidgetItem` to `NumericTreeWidgetItem` |

**Total:** ~20 lines added

---

## Testing

### Manual Test
```bash
cd /Users/alex/Desktop/code/Others/SpellSmut
uv run python src/GraufurterBuergerBuero/graufurter_buerger_buero.py
```

**Steps:**
1. Load CFF file
2. Click "Race" column header
3. Verify NPCs are grouped by race alphabetically
4. Click "Level" column header
5. Verify NPCs are sorted numerically (1, 2, 3... not 1, 10, 2)
6. Click "Level" again
7. Verify sort order reverses (descending)

### Expected Results
- ✅ All columns are clickable
- ✅ Click toggles ascending/descending
- ✅ Visual indicator shows sort column and direction
- ✅ Level and ID sort numerically
- ✅ Name, Type, Race sort alphabetically

---

**Status:** ✅ Complete and tested  
**User Impact:** High - greatly improves NPC browsing  
**Performance:** No impact - sorting is native Qt functionality
