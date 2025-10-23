# ID Mapping System - Implementation Summary

**Date:** 2025-10-23
**Status:** ✅ Phase 1 & 2.5 Complete - Name Display Enhancement Ready

---

## 🎯 Project Goal

Enhance the GameData.cff editor to display human-readable names alongside IDs for all game elements.

**Display Format:** `Name [ID]` (e.g., "One-handed Sword [4]")

---

## ✅ Completed Work

### 1. Lua Mapping Extractor (`extract_lua_mappings.py`)

**Location:** `src/helper_tools/extract_lua_mappings.py`

**Purpose:** Automatically extracts ID-to-name mappings from SpellForce Lua source files and generates a comprehensive JSON database.

**Extracted Categories:**
- ✅ **Weapon Types** (20 entries) - kDrwWt* constants with sound mappings
- ✅ **Spell Lines** (227 entries) - kGdSpellLine* constants
- ✅ **Effect Types** (39 entries) - kGdEffect* constants
- ✅ **Job/Animation Types** (20 entries) - kGdJob* constants
- ✅ **Races** (6 entries) - kGtRace* constants
- ✅ **Equipment Slots** (7 entries) - SlotHead, SlotRightHand, etc.
- ✅ **Quest States** (5 entries) - State constants
- ✅ **Figure Tasks** (11 entries) - TASK_* constants
- ✅ **Directions** (8 entries) - Cardinal and intercardinal
- ✅ **Target Types** (5 entries) - Figure, Building, Object, etc.
- ✅ **Variable Operators** (3 entries) - Add, InvertBool, SetRandom
- ✅ **Movement Modes** (2 entries) - Walk, Run
- ✅ **Monument Types** (7 entries) - Race-specific monuments

**Total:** 360+ mappings extracted

**Usage:**
```bash
python3 src/helper_tools/extract_lua_mappings.py
```

**Output:** `TirganachReloaded/data/id_name_mappings.json`

---

### 2. JSON Mapping Database

**Location:** `TirganachReloaded/data/id_name_mappings.json`

**Format:**
```json
{
  "weapon_types": {
    "4": {
      "name": "One-handed Sword",
      "constant": "kDrwWt1HSword",
      "display": "One-handed Sword [4]",
      "sound_hit": "battle_hit_1hsword",
      "sound_miss": "battle_miss_sword"
    }
  }
}
```

**Features:**
- Pre-formatted display strings
- Additional metadata (sounds, constants, hex IDs)
- Sorted by ID for easy lookup
- Human-readable names

---

### 3. MappingResolver Utility Class

**Location:** `TirganachReloaded/gui_editor/utils/mapping_resolver.py`

**Purpose:** Provides convenient API for resolving IDs to names in the editor.

**Key Methods:**

```python
from TirganachReloaded.gui_editor.utils import MappingResolver

resolver = MappingResolver()

# Get formatted display name
display = resolver.get_display_name(4, "weapon_types")
# Returns: "One-handed Sword [4]"

# Get name only
name = resolver.get_name_only(4, "weapon_types")
# Returns: "One-handed Sword"

# Get constant
const = resolver.get_constant(4, "weapon_types")
# Returns: "kDrwWt1HSword"

# Get all info
info = resolver.get_full_info(4, "weapon_types")
# Returns: {"name": "One-handed Sword", "constant": "kDrwWt1HSword", ...}

# Get dropdown options
options = resolver.get_dropdown_options("weapon_types")
# Returns: [(0, "Default/Fist [0]"), (1, "Mouth/Bite [1]"), ...]

# Search by name
results = resolver.search_by_name("sword", "weapon_types")
# Returns: [{"name": "One-handed Sword", "id": "4", ...}, ...]

# Auto-detect category
category = resolver.guess_category("weapon_type")
# Returns: "weapon_types"

# Check if field needs resolution
is_id = resolver.is_id_field("weapon_type")
# Returns: True
```

**Features:**
- Singleton pattern for easy global access: `get_resolver()`
- Smart category detection from field names
- Search functionality
- Dropdown menu support
- Comprehensive error handling

**Test Results:**
```
✅ Loaded 13 mapping categories
🔍 Sample Lookups:
  Weapon ID 4: One-handed Sword [4]
  Race ID 1: Human [1]
  Effect ID 1: Spell Cast [1]
  Direction ID 0: East [0]
```

---

### 3.5. Weapon & Armor Name Display System

**Purpose:** Display meaningful weapon and armor names in the editor instead of generic item IDs.

**Data Sources:**
- `TirganachReloaded/enhanced_weapons.json` - 719 weapon names
- `TirganachReloaded/enhanced_armor.json` - 635 armor names

**Integration:**
- Extended `ElementTableWidget` to resolve and display item names
- Added name columns alongside existing ID columns
- Real-time name resolution for improved user experience

**Example Transformation:**
```
Before: Item 27 - Type: 4, Name: (empty)
After:  Flameblade Dagger [27] - Type: One-handed Sword [4], Name: Flameblade Dagger
```

**Statistics:**
- **Weapons:** 719 unique named weapons (swords, axes, maces, bows, staves, etc.)
- **Armor:** 635 unique named armor pieces (helmets, chest, gloves, boots, etc.)
- **Total:** 1,354 items with proper display names

**Files Created:**
- `TirganachReloaded/enhanced_weapons.json`
- `TirganachReloaded/enhanced_armor.json`

---

## 📁 Project Structure

```
SpellSmut/
├── src/
│   ├── TirganachReloaded/
│   │   ├── data/
│   │   │   └── id_name_mappings.json       # ✅ Generated mappings
│   │   ├── enhanced_weapons.json           # ✅ 719 weapon names
│   │   ├── enhanced_armor.json             # ✅ 635 armor names
│   │   └── gui_editor/
│   │       └── utils/
│   │           ├── __init__.py              # ✅ Package init
│   │           └── mapping_resolver.py      # ✅ Resolver class
│   └── helper_tools/
│       └── extract_lua_mappings.py          # ✅ Extraction script
└── docs/
    └── IMPLEMENTATION_SUMMARY.md            # ✅ This file
```

---

## 🔄 Extraction Process

The extractor parses these Lua files:

1. **`script/DrwSound.lua`**
   - Weapon type to sound mappings
   - BattleData structure with hits/misses

2. **`script/GdsDefines.lua`**
   - Quest states
   - Equipment slots
   - Target types
   - Variable operators
   - Directions
   - Movement modes

3. **`object/object_effect_register.lua`**
   - Effect types
   - Spell line registrations
   - Monument types
   - Race IDs (from RegisterEffect calls)

4. **Hardcoded Knowledge from ID_MAPPINGS.md**
   - Effect type IDs
   - Figure task IDs
   - Job type constants

---

## 📊 Statistics

| Category | Entries | Has Numeric IDs |
|----------|---------|-----------------|
| Weapon Types | 20 | ✅ Yes |
| Spell Lines | 227 | ⚠️ Constants only |
| Effect Types | 39 | ✅ Yes |
| Job Types | 20 | ⚠️ Constants only |
| Races | 6 | ✅ Yes |
| Equipment Slots | 7 | ✅ Yes |
| Quest States | 5 | ✅ Yes |
| Figure Tasks | 11 | ✅ Yes |
| Directions | 8 | ✅ Yes |
| Target Types | 5 | ✅ Yes |
| Variable Operators | 3 | ✅ Yes |
| Movement Modes | 2 | ✅ Yes |
| Monument Types | 7 | ✅ Yes (hex) |
| **Weapon Names** | **719** | ✅ Yes |
| **Armor Names** | **635** | ✅ Yes |

**Total Mappings:** 360+ | **Total Item Names:** 1,354

---

## 🎨 Display Format Examples

### Weapon Types
```
ID: 4  →  Display: "One-handed Sword [4]"
ID: 10 →  Display: "Two-handed Sword [10]"
ID: 18 →  Display: "Two-handed Crossbow [18]"
```

### Races
```
ID: 1 →  Display: "Human [1]"
ID: 2 →  Display: "Elf [2]"
ID: 6 →  Display: "Dark Elf [6]"
```

### Effect Types
```
ID: 0  →  Display: "None [0]"
ID: 1  →  Display: "Spell Cast [1]"
ID: 24 →  Display: "Projectile [24]"
```

### Directions
```
ID: 0 →  Display: "East [0]"        (0°)
ID: 1 →  Display: "Southeast [1]"   (45°)
ID: 2 →  Display: "South [2]"       (90°)
```

---

## 🔧 Integration Guide

### For Editor Widgets

#### Example 1: Property Editor Field
```python
from TirganachReloaded.gui_editor.utils import get_resolver

class PropertyEditorWidget(QWidget):
    def create_field_widget(self, field_name, field_value, field_type):
        resolver = get_resolver()
        
        # Check if this field should show names
        if resolver.is_id_field(field_name):
            category = resolver.guess_category(field_name)
            if category:
                # Show: "One-handed Sword [4]" instead of just "4"
                display_text = resolver.get_display_name(field_value, category)
                label = QLabel(display_text)
                
                # Add tooltip with constant name
                constant = resolver.get_constant(field_value, category)
                if constant:
                    label.setToolTip(f"Constant: {constant}")
                
                return label
```

#### Example 2: Dropdown/Combobox
```python
def populate_weapon_dropdown(self):
    resolver = get_resolver()
    options = resolver.get_dropdown_options("weapon_types")
    
    for weapon_id, display_name in options:
        self.weapon_combo.addItem(display_name, weapon_id)
```

#### Example 3: Table Display
```python
def populate_table(self, elements):
    resolver = get_resolver()
    
    for row, element in enumerate(elements):
        # ID column
        self.table.setItem(row, 0, QTableWidgetItem(str(element.id)))
        
        # Name column (resolved from weapon_type field)
        weapon_name = resolver.get_display_name(
            element.weapon_type, 
            "weapon_types"
        )
        self.table.setItem(row, 1, QTableWidgetItem(weapon_name))
```

---

## 📝 Next Steps

### Phase 2.5: Name Display Enhancement ✅ COMPLETE
- [x] Load 719 weapon names from enhanced_weapons.json
- [x] Load 635 armor names from enhanced_armor.json
- [x] Integrate name display into ElementTableWidget
- [x] Show meaningful names instead of generic IDs
- [x] Extend data model for item name resolution

### Phase 3: Full Editor Integration (Pending)
- [ ] Integrate MappingResolver into PropertyEditorWidget for remaining ID fields
- [ ] Update ElementTableWidget to show resolved names for all categories
- [ ] Add search by name functionality
- [ ] Create ID field custom widget with dropdown
- [ ] Add tooltips showing constant names

### Phase 3: Documentation Enhancement (Pending)
- [ ] Auto-generate enhanced ID_MAPPINGS.md from JSON
- [ ] Create separate reference documents (SPELL_REFERENCE.md, etc.)
- [ ] Add cross-reference tables
- [ ] Generate weapon type table with sound mappings

### Phase 4: Future Enhancements (Planned)
- [ ] Extract item IDs from game data files
- [ ] Extract building type IDs
- [ ] Add image/icon support for visual preview
- [ ] Create validation warnings for invalid IDs
- [ ] Export mappings to CSV/Excel for reference

---

## 🐛 Known Limitations

1. **Spell Line IDs:** Currently only have constant names, not numeric IDs
   - **Solution:** Will need to extract from GameData.cff files
   
2. **Job Type IDs:** Constants extracted but numeric IDs unknown
   - **Solution:** Reverse engineer from game executable or data files

3. **Item Types:** Not yet extracted
   - **Solution:** Parse from GameData.cff item definitions

---

## 🧪 Testing

### Unit Tests
```bash
# Test extractor
python3 src/helper_tools/extract_lua_mappings.py

# Test resolver
python3 TirganachReloaded/gui_editor/utils/mapping_resolver.py
```

### Expected Output
```
✅ Extracted 20 weapon types
✅ Extracted 227 spell line constants
✅ Extracted 39 effect types
...
✅ Loaded 13 mapping categories
🔍 Sample Lookups:
  Weapon ID 4: One-handed Sword [4]
  Race ID 1: Human [1]
```

---

## 📚 References

- **ID_MAPPINGS.md** - Original manual mapping documentation
- **Lua Source Files** - `ModdingTools/SpellForceLUASources/`
- **Editor Planning** - `ProjectPlanning/EDITOR_PLANNING.md`

---

## ✨ Success Criteria

✅ **Phase 1 Complete:**
- [x] Extract all mappable ID categories from Lua sources
- [x] Generate comprehensive JSON mapping database
- [x] Create MappingResolver utility class
- [x] Test all functionality
- [x] Document implementation

✅ **Phase 2.5 Complete:**
- [x] Load weapon names from enhanced_weapons.json (719 entries)
- [x] Load armor names from enhanced_armor.json (635 entries)
- [x] Integrate name display into ElementTableWidget
- [x] Show meaningful names instead of generic IDs
- [x] Test real-time name display functionality

**Ready for Phase 3:** Full editor integration

---

## 🙏 Acknowledgments

**Data Sources:**
- SpellForce Lua source files (Phenomic/THQ Nordic)
- ID_MAPPINGS.md documentation
- Community modding knowledge

**Tools Used:**
- Python 3 with regex for parsing
- JSON for data storage
- Pathlib for cross-platform paths

---

**Last Updated:** 2025-10-23
**Author:** Alex + Claude
**Version:** 1.1.0
