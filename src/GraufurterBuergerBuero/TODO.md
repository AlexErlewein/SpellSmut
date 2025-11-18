# Graufurter Bürger Büro - TODO List

## Priority Issues & Feature Improvements

---

## 🔴 CRITICAL - Usability Issues

### TODO-001: Fix "Create New NPC" Wizard Flow
**Status:** ✅ COMPLETE  
**Priority:** URGENT

**Problem:**
User gets stuck after entering name - can't click "Next" button.

**Root Cause:**
The wizard required clicking "Allocate NPC ID" button on first page before proceeding. This was not intuitive.

**Solution Implemented:**
Auto-allocate ID when "Create New NPC" mode is selected:

1. **Added auto-allocation on page load:**
   - When wizard opens, "Create New" is selected by default
   - ID is automatically allocated immediately
   - User can proceed to enter name without extra clicks

2. **Added signal connection:**
   - Connected `new_radio.toggled` to `_on_new_mode_selected()`
   - Automatically allocates ID when switching back to "Create New"

3. **Smart ID management:**
   - If user switches from "Create New" to Edit/Duplicate, auto-allocated ID is released
   - Prevents ID waste

**Implementation:**
```python
def __init__(self):
    # ...existing code...
    
    # Connect to auto-allocate handler
    self.new_radio.toggled.connect(self._on_new_mode_selected)
    
    # Auto-allocate immediately since "Create New" is default
    self._on_new_mode_selected(True)

def _on_new_mode_selected(self, checked):
    """Handle 'Create New NPC' selection - auto-allocate ID"""
    if checked:
        self.allocate_npc_id()
```

**Test Results:**
- ✅ Wizard opens with ID already allocated
- ✅ "Next" button is immediately available
- ✅ User can enter name and proceed without confusion
- ✅ Switching modes properly manages IDs

**Files Modified:**
- `npc_creator_wizard.py` - `ModeSelectionPage` class
  - Line 183: Added signal connection
  - Line 243-245: Auto-allocate on init
  - Lines 247-249: Added `_on_new_mode_selected()` method
  - Lines 260-271: Enhanced `_on_mode_changed()` to release IDs

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
**Status:** ✅ COMPLETE  
**Priority:** MEDIUM

**Problem:**
All NPCs showed as "friendly" type.

**Solution Implemented:**
Determines NPC type using multiple criteria:

1. **Merchant Detection:**
   - Check if race contains "MERCHANT"
   - Check if creature_id in `merchant_inventories` table
   - Result: 202 merchants detected

2. **Guard Detection:**
   - Check if race contains "GUARD" or "SOLDIER"
   - Result: 40 guards detected

3. **Hostile Detection:**
   - Check if creature has experience > 50
   - Only applied if not already classified as merchant/guard
   - Result: 1195 hostile NPCs detected

4. **Friendly (Default):**
   - All others remain friendly
   - Result: 1095 friendly NPCs

**Test Results:**
- Total NPCs: 2532
- Friendly: 1095 (43%)
- Hostile: 1195 (47%)
- Merchant: 202 (8%)
- Guard: 40 (2%)

**Files Modified:**
- `cff_npc_loader.py` - Added type detection logic

---

### TODO-004: Load Real Character Classes
**Status:** ✅ COMPLETE  
**Priority:** MEDIUM

**Problem:**
All NPCs defaulted to "warrior" class.

**Solution Implemented:**
Infers character class from skills in `creature_skills` table:

1. **Skill Analysis:**
   - Count magic skills (containing "MAGIC" or "ELEMENTAL")
   - Count combat skills (containing "BLADE", "BLUNT", "AXE")

2. **Class Determination:**
   - Magic > Combat → Mage
   - Combat > 0 → Warrior
   - Both Magic and Combat → Multi-class

**Test Results:**
- Warrior: 2530 (99.9%)
- Mage: 1
- Multi-class: 1
- Most NPCs have no skills, default to warrior

**Files Modified:**
- `cff_npc_loader.py` - Added class inference logic

---

### TODO-005: Load Real NPC Levels
**Status:** ✅ COMPLETE  
**Priority:** MEDIUM

**Problem:**
All NPCs showed Level 1 (hardcoded default).

**Solution Implemented:**
Loads level from `creature_stats` table via `stats_id`:

```python
stats_obj = next((s for s in self.gamedata.creature_stats 
                 if s.stats_id == stats_id), None)
if stats_obj:
    level = getattr(stats_obj, "level", 1)
```

**Test Results:**
- Händler Klaus (ID 21): Level 30
- Händler Gerstle (ID 22): Level 30
- Schwarzwolf (ID 350): Level 1
- Oger Schläger (ID 190): Level 15

**Files Modified:**
- `cff_npc_loader.py` - Updated `_convert_npc_from_gamedata()`

---

### TODO-006: Load Real Base Stats
**Status:** ✅ COMPLETE  
**Priority:** MEDIUM

**Problem:**
All stats default to 10 (not real values from game).

**Solution Implemented:**
Loads all 7 base stats from `creature_stats` table via `stats_id`:
- Strength
- Stamina
- Agility
- Dexterity
- Intelligence
- Wisdom
- Charisma

**Implementation:**
```python
stats_obj = next((s for s in self.gamedata.creature_stats 
                 if s.stats_id == stats_id), None)
if stats_obj:
    base_stats = {
        "strength": getattr(stats_obj, "strength", 10),
        "stamina": getattr(stats_obj, "stamina", 10),
        # ... etc
    }
```

**Test Results:**
- Händler Klaus: STR=60, STA=60, INT=60
- Schwarzwolf: STR=20, STA=40, INT=10
- Oger Schläger: STR=80, STA=70, INT=8

**Files Modified:**
- `cff_npc_loader.py` - Updated `_convert_npc_from_gamedata()` method

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
3. ✅ TODO-003: Load real NPC types
4. ✅ TODO-004: Load real character classes  
5. ✅ TODO-005: Load real levels
6. ✅ TODO-006: Load real base stats

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
