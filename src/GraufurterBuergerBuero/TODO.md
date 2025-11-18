# Graufurter Bürger Büro - TODO List

## Priority Issues & Feature Improvements

---

## 🔴 CRITICAL - Usability Issues

### TODO-001: Fix "Create New NPC" Wizard Flow
**Status:** 🔴 BLOCKING  
**Priority:** URGENT

**Problem:**
User gets stuck after entering name - can't click "Next" button.

**Root Cause:**
The wizard requires clicking "Allocate NPC ID" button on first page before proceeding. This is not intuitive.

**Solution Options:**
1. **Auto-allocate ID on page load** (Recommended)
   - When "Create New" mode is selected
   - Automatically allocate next available ID
   - Remove "Allocate NPC ID" button for new mode
   - Keep manual allocation only for edit/duplicate modes

2. **Better UI flow**
   - Show clear instructions: "Click 'Allocate NPC ID' to continue"
   - Disable name/fields until ID is allocated
   - Add validation message

**Files to Modify:**
- `npc_creator_wizard.py` - `ModeSelectionPage` class
- Specifically: `__init__()`, `isComplete()`, `allocate_npc_id()`

**Implementation:**
```python
def __init__(self):
    # ...existing code...
    
    # Auto-allocate for new mode
    self.new_radio.toggled.connect(self._on_new_mode_selected)
    
def _on_new_mode_selected(self, checked):
    if checked:
        # Auto-allocate ID for new NPCs
        self.allocate_npc_id()
```

**Testing:**
- Click "Create NPC" → Should auto-allocate ID
- Enter name → Should be able to click "Next" immediately
- Verify ID shows in status label

---

### TODO-002: Remove "Browse NPCs" Button from Main Window
**Status:** ✅ COMPLETE  
**Priority:** LOW

**Question from User:**
> "Do we need the browse NPC button and the underlying browser anymore?"

**Analysis:**
- Main window already has tree browser (left panel)
- "Browse NPCs" button opened `EnhancedNpcBrowser` dialog
- Provided duplicate functionality (edit/duplicate/delete)
- Main tree provides better browsing experience

**Solution Implemented:**
Removed button from main window, kept browser code for wizard.

**Changes Made:**
1. Removed "Browse NPCs" button from header layout (lines 122-127)
2. Removed `browse_npcs()` method (lines 566-576)
3. Removed `EnhancedNpcBrowser` import from main window
4. Kept `EnhancedNpcBrowser` class for wizard edit/duplicate functionality

**Files Modified:**
- `graufurter_buerger_buero.py` - Removed button, method, and import
- `enhanced_npc_browser.py` - Kept intact (still used by wizard)

**Testing:**
- ✅ Application imports successfully
- ✅ browse_npcs method removed
- ✅ EnhancedNpcBrowser still available for wizard
- ✅ Wizard functionality preserved

---

## 🟡 MEDIUM - Data Quality Issues

### TODO-003: Load Real NPC Types (not all "friendly")
**Status:** 🟡 NEEDS INVESTIGATION  
**Priority:** MEDIUM

**Problem:**
All NPCs show as "friendly" type and "warrior" class.

**Root Cause:**
CFF loader uses hardcoded defaults (line 128 in `cff_npc_loader.py`):
```python
npc_type = "friendly"  # Default
character_class = "warrior"  # Default
```

**Investigation Needed:**
1. Check what attributes GameData creatures have for determining type/class
2. Look for faction/alignment data
3. Check if there's a creature_type or behavior field

**Files to Check:**
```bash
# Check creature attributes
python3 -c "from TirganachReloaded.tirganach import GameData; \
gd = GameData('../OriginalGameFiles/data/GameData.cff'); \
c = list(gd.creatures)[100]; \
print([a for a in dir(c) if not a.startswith('_')])"
```

**Potential Solutions:**
- Map creature faction to NPC type
- Infer from equipment (weapons = warrior, no weapons = mage)
- Check creature stats (high STR = warrior, high INT = mage)
- Look up in creature_stats table via stats_id

**Files to Modify:**
- `cff_npc_loader.py` - `_convert_npc_from_gamedata()` method

---

### TODO-004: Load Real Character Classes
**Status:** 🟡 NEEDS INVESTIGATION  
**Priority:** MEDIUM

**Problem:**
All NPCs default to "warrior" class.

**Investigation Steps:**
1. Check if creatures have a class field
2. Check creature_skills table for class detection
3. Infer from stats distribution:
   - High STR/stamina = Warrior
   - High INT/wisdom = Mage
   - High DEX/agility = Rogue/Ranger
   - Balanced = Paladin/Monk

**Files to Modify:**
- `cff_npc_loader.py` - Add `_infer_character_class()` method

---

### TODO-005: Load Real NPC Levels
**Status:** 🟡 NEEDS IMPLEMENTATION  
**Priority:** MEDIUM

**Problem:**
All NPCs show Level 1 (hardcoded default).

**Solution:**
Lookup level from `creature_stats` table using `stats_id`:
```python
stats_id = getattr(creature, "stats_id", 0)
if stats_id and hasattr(self.gamedata, "creature_stats"):
    stats = self.gamedata.creature_stats.where(stats_id=stats_id)
    if stats:
        level = getattr(stats[0], "level", 1)
```

**Files to Modify:**
- `cff_npc_loader.py` - Update `_convert_npc_from_gamedata()`

---

### TODO-006: Load Real Base Stats
**Status:** 🟡 NEEDS IMPLEMENTATION  
**Priority:** MEDIUM

**Problem:**
All stats default to 10 (not real values from game).

**Solution:**
Lookup stats from `creature_stats` table:
```python
if stats_id:
    stats_row = self.gamedata.creature_stats.where(stats_id=stats_id)[0]
    base_stats = {
        "strength": getattr(stats_row, "strength", 10),
        "stamina": getattr(stats_row, "stamina", 10),
        # ... etc
    }
```

**Files to Modify:**
- `cff_npc_loader.py` - Update stat loading logic

---

## 🟢 LOW - Enhancement Features

### TODO-007: Load Head IDs
**Status:** ✅ COMPLETE  
**Priority:** LOW

**Problem:**
Head ID defaults to 0 (not useful for visualization).

**Solution Implemented:**
- Loads `head_id` attribute from creature if available
- Note: In SpellForce, head appearance is typically stored at race/gender level, not per-creature
- Most creatures don't have individual head_id values

**Implementation:**
```python
head_id = getattr(creature, "head_id", 0)
```

**Files Modified:**
- `cff_npc_loader.py` - Updated `_convert_npc_from_gamedata()` method

---

### TODO-008: Load Equipment Data
**Status:** ✅ COMPLETE  
**Priority:** LOW

**Problem:**
Equipment slots all empty (not loading from game).

**Solution Implemented:**
- Loads equipment from `creature_equipment` table
- Maps equipment slots (HEAD, CHEST, LEGS, RIGHT_HAND, etc.) to NPC format
- Successfully loads items like weapons, armor for NPCs that have them

**Implementation:**
```python
equipment_items = [eq for eq in self.gamedata.creature_equipment 
                   if eq.creature_id == creature_id]
for eq in equipment_items:
    slot_name = str(eq.equipment_slot).split(".")[-1]
    if slot_name in slot_mapping:
        equipment_dict[slot_mapping[slot_name]] = eq.item_id
```

**Test Results:**
- Example: Händler Klaus (ID 21) has chest armor (4699) and right hand weapon (131)

**Files Modified:**
- `cff_npc_loader.py` - Added equipment loading in `_convert_npc_from_gamedata()`

---

### TODO-009: Load Localized Names
**Status:** ✅ COMPLETE  
**Priority:** LOW

**Problem:**
Using `creature.name` (may be placeholder) instead of localized name via `name_id`.

**Solution Implemented:**
- Added language parameter to `load_all_npcs()` (default: GERMAN)
- Looks up localized names via `name_id` in `localisation` table
- Falls back to creature.name if localization not found

**Implementation:**
```python
if name_id > 0 and hasattr(self.gamedata, "localisation"):
    lang_enum = getattr(Language, language, Language.GERMAN)
    loc_entries = [loc for loc in self.gamedata.localisation
                   if loc.text_id == name_id and loc.language == lang_enum]
    if loc_entries:
        name = loc_entries[0].text
```

**Test Results:**
- Example: Creature 21 now shows "Händler Klaus" instead of "Merchant Lendunot"
- Example: Creature 22 shows "Händler Gerstle" instead of "Merchant Donotbeg"

**Files Modified:**
- `cff_npc_loader.py` - Added localization lookup and language parameter
- Imported `Language` enum from Tirganach

---

### TODO-010: Load Skills and Spells
**Status:** ✅ COMPLETE  
**Priority:** LOW

**Problem:**
NPCs don't show their skills/spells from game.

**Solution Implemented:**
- Loads skills from `creature_skills` table (linked via stats_id)
- Loads spells from `creature_spells` table (linked via creature_id)
- Added `NpcSkill` and `NpcSpell` dataclasses to `npc_creation_data.py`
- Added `skills` and `spells` fields to `NpcCreationData`

**Implementation:**
```python
# Skills (linked via stats_id)
skill_items = [sk for sk in self.gamedata.creature_skills 
               if sk.stats_id == stats_id]
for skill in skill_items:
    skills_list.append({
        "school": str(skill.skill_school).split(".")[-1],
        "level": skill.skill_level
    })

# Spells (linked via creature_id)
spell_items = [sp for sp in self.gamedata.creature_spells 
               if sp.creature_id == creature_id]
for spell in spell_items:
    spells_list.append({
        "spell_id": spell.spell_id,
        "position": spell.spell_position
    })
```

**Test Results:**
- Example: Oger Schläger (ID 190) has 2 skills: HEAVY_BLADE_WEAPONS (12), HEAVY_BLUNT_WEAPONS (14)
- Example: Händler Gerstle (ID 22) has 1 spell: spell_id=9

**Files Modified:**
- `cff_npc_loader.py` - Added skills and spells loading
- `npc_creation_data.py` - Added NpcSkill and NpcSpell dataclasses, updated NpcCreationData

---

## 📋 Implementation Order

### Phase 1: Critical Usability (Week 1)
1. ✅ TODO-001: Fix wizard flow (auto-allocate ID)
2. ✅ TODO-002: Remove "Browse NPCs" button

### Phase 2: Core Data (Week 2-3)
3. ⏳ TODO-003: Load real NPC types
4. ⏳ TODO-004: Load real character classes  
5. ⏳ TODO-005: Load real levels
6. ⏳ TODO-006: Load real base stats

### Phase 3: Enhancements (Week 4+)
7. ✅ TODO-007: Load head IDs
8. ✅ TODO-008: Load equipment data
9. ✅ TODO-009: Load localized names
10. ✅ TODO-010: Load skills and spells

---

## 🔍 Investigation Commands

### Check Creature Attributes
```bash
cd src
python3 -c "
from TirganachReloaded.tirganach import GameData
gd = GameData('../OriginalGameFiles/data/GameData.cff')
c = list(gd.creatures)[100]
print('Creature attributes:')
print([a for a in dir(c) if not a.startswith('_')])
"
```

### Check Available Tables
```bash
python3 -c "
from TirganachReloaded.tirganach import GameData
gd = GameData('../OriginalGameFiles/data/GameData.cff')
print('Available tables:')
print([a for a in dir(gd) if not a.startswith('_')][:30])
"
```

### Check Creature Stats Table
```bash
python3 -c "
from TirganachReloaded.tirganach import GameData
gd = GameData('../OriginalGameFiles/data/GameData.cff')
if hasattr(gd, 'creature_stats'):
    stats = list(gd.creature_stats)[:5]
    print(f'Found {len(stats)} stat entries')
    print('Sample:', [a for a in dir(stats[0]) if not a.startswith('_')])
"
```

---

## 📝 Notes

### Current State Summary

**Working:**
- ✅ Load 2532 creatures from CFF
- ✅ Display in tree (custom + game separated)
- ✅ Create custom NPCs with wizard
- ✅ Save to JSON
- ✅ Browse game NPCs

**Hardcoded Defaults:**
- ❌ NPC type: "friendly" (should vary)
- ❌ Character class: "warrior" (should vary)
- ❌ Level: 1 (should be actual level)
- ❌ Stats: all 10 (should be from creature_stats)
- ❌ Head ID: 0 (should be from creature)
- ❌ Equipment: empty (should be from creature_equipment)

**Impact:**
- User can **browse** game NPCs by name
- User can **duplicate** game NPCs as templates
- But duplicated NPCs have **generic** stats/class/level
- User must manually adjust after duplication

---

## 🎯 Recommended Action Plan

### Immediate (This Week)
1. Fix wizard usability (TODO-001)
2. Decide on Browse button (TODO-002)

### Short-term (Next 2 Weeks)
3. Load real types and classes (TODO-003, TODO-004)
4. Load real levels and stats (TODO-005, TODO-006)

### Long-term (Future)
5. Enhancements: equipment, heads, localization

---

**Last Updated:** 2025-11-18  
**Status:** 10 TODOs identified, prioritized, and documented
