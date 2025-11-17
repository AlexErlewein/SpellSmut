# Quest Editor Enhancement TODO List

**Last Updated**: November 17, 2025  
**Project**: SpellSmut Quest Wizard  

## Overview

This document tracks the enhancement tasks for the Quest Editor system. Tasks are organized by priority and status.

---

## ✅ Completed Tasks

### NPC Chooser/Browser
**Status**: ✅ COMPLETE
**Priority**: High
**Date Completed**: November 16, 2025

A searchable, filterable NPC browser for selecting quest givers, dialogue speakers, and involved NPCs.

**Features Implemented**:
- ✅ Load NPCs from GameData.cff
- ✅ Search by name, ID, faction, and map
- ✅ Filter by race, faction, and map/region
- ✅ Single and multi-selection modes
- ✅ Live preview pane with NPC details
- ✅ Background thread loading (non-blocking UI)
- ✅ German language support (primary) with English fallback
- ✅ Optimized loading (2000 most relevant NPCs, ~1-2 second load time)

**Files**:
- `src/TirganachReloaded/cff_editor/widgets/npc_browser_dialog.py`
- `docs/Development/NPC_BROWSER_INTEGRATION.md`
- `test_npc_browser.py`

**Usage**:
```python
from TirganachReloaded.cff_editor.widgets.npc_browser_dialog import choose_quest_giver

npc = choose_quest_giver(parent=self)
if npc:
    quest_giver_id = npc.npc_id
    quest_giver_name = npc.name
```

---

### Item Browser Data Expansion
**Status**: ✅ COMPLETE
**Priority**: High
**Date Completed**: November 17, 2025

Expanded the item browser from 20 sample items to 11,000+ real SpellForce game items with full CFF data integration.

**Features Implemented**:
- ✅ Load complete item database from GameData.cff (weapons, armor, items, creatures, quests, materials)
- ✅ Real-time data loading with 721 weapons, 635 armor pieces, 7101 general items, 2617 creatures
- ✅ Comprehensive item stats and properties (damage, defense, requirements, effects, icons)
- ✅ Category filtering with proper selection (Weapons/Armor/Creatures/etc.)
- ✅ Icon support using extracted UI assets (6237+ icon mappings)
- ✅ Integrated with all objective editors and quest creation workflows
- ✅ Fixed CFF file path resolution for reliable data loading

**Files Modified**:
- `src/TirganachReloaded/cff_editor/widgets/item_browser_widget.py` - Core item loading and display
- `src/TirganachReloaded/cff_editor/widgets/objective_editor.py` - Data model integration
- `src/TirganachReloaded/cff_editor/widgets/objective_editor_simple.py` - Data model integration
- `src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py` - CFF path fix
- `test_item_browser.py` - Enhanced testing

**Impact**:
- Quest creators can now select from actual SpellForce items instead of sample data
- Supports all item types: weapons, armor, consumables, quest items, materials, creatures
- Real item IDs, stats, and properties for accurate quest design
- Foundation for reward builder and item-based quest objectives

---

## 🔴 High Priority Tasks

### 1. Reward Builder UI
**Status**: 🔄 PENDING  
**Priority**: High  
**Complexity**: Medium

Build item/XP/gold reward configuration interface for quest rewards.

**Requirements**:
- Item browser integration for selecting reward items
- XP amount input with level suggestions
- Gold amount input
- Multiple reward support (choose 1 of N items)
- Reward preview
- Export to Lua format

**Related Files**:
- `src/TirganachReloaded/cff_editor/widgets/reward_builder.py` (exists, needs enhancement)
- `ProjectPlanning/Components/QuestSystem/REWARD_BUILDER_UI_SPEC.md`

**Estimated Effort**: 4-6 hours

---

### 2. Condition Builder
**Status**: 🔄 PENDING  
**Priority**: High  
**Complexity**: High

Visual builder for quest conditions with AND/OR/NOT logic.

**Requirements**:
- Visual condition tree builder
- Support for AND/OR/NOT operators
- Condition types:
  - Item possession (has item X)
  - Quest state (quest Y completed)
  - Level requirement
  - Flag state (NPC flag, global flag)
  - Faction reputation
- Nested conditions support
- Preview/validation

**Related Files**:
- `ProjectPlanning/Components/QuestSystem/TEMPLATES_AND_CONDITION_BUILDER_SPEC.md`

**Estimated Effort**: 8-12 hours

---

### 3. AnswerId Management
**Status**: 🔄 PENDING  
**Priority**: High  
**Complexity**: Medium

Auto-assign and track unique AnswerIds in dialogue system.

**Requirements**:
- Auto-increment AnswerId system
- Track used IDs across all dialogues
- Prevent ID collisions
- ID reservation/release
- Visual ID assignment in dialogue builder
- Export ID mappings

**Related Files**:
- `src/TirganachReloaded/cff_editor/widgets/simple_dialogue_builder.py`
- `ProjectPlanning/Components/QuestSystem/QUEST_EDITOR_ENHANCEMENT_TASKS.md`

**Estimated Effort**: 3-5 hours

---

### 4. Flag Management Interface
**Status**: 🔄 PENDING  
**Priority**: High  
**Complexity**: Medium

System for NPC/global flags with usage tracking.

**Requirements**:
- Create/edit/delete flags
- Track flag usage across quests
- Flag categories (NPC flags, global flags)
- Flag search and filtering
- Visual flag state preview
- Export flag definitions

**Related Files**:
- `ProjectPlanning/Components/QuestSystem/QUEST_EDITOR_ENHANCEMENT_TASKS.md`

**Estimated Effort**: 4-6 hours

---

### 5. LUA Export Engine
**Status**: 🔄 PENDING  
**Priority**: High  
**Complexity**: High

Generate production-ready Lua scripts from quest data.

**Requirements**:
- Export quest definitions to Lua
- Export dialogue scripts to Lua
- Match SpellForce Lua format exactly
- Include all quest metadata
- Generate RegisterQuest() calls
- Export reward definitions
- Validate exported scripts

**Related Files**:
- `ProjectPlanning/Components/QuestSystem/QUEST_EDITOR_ENHANCEMENT_TASKS.md`
- `ModdingTools/SpellForceLUASources/` (reference)

**Estimated Effort**: 8-12 hours

---

## 🟡 Medium Priority Tasks

### 6. Quest Templates System
**Status**: 🔄 PENDING  
**Priority**: Medium  
**Complexity**: Medium

Implement built-in quest templates (Kill, Collect, Escort, etc.)

**Requirements**:
- Pre-built quest templates:
  - Kill X enemies
  - Collect X items
  - Escort NPC
  - Talk to NPC
  - Deliver item
  - Exploration/discovery
- Template customization
- Template preview
- Save custom templates

**Related Files**:
- `ProjectPlanning/Components/QuestSystem/TEMPLATES_AND_CONDITION_BUILDER_SPEC.md`

**Estimated Effort**: 6-8 hours

---

## 🟢 Low Priority Tasks

### 7. Preview Tab Visual Fix
**Status**: 🔄 PENDING  
**Priority**: Low  
**Complexity**: Low

Remove white backgrounds in preview tab for better readability.

**Requirements**:
- Fix white backgrounds in markdown preview
- Improve text contrast
- Better styling for quest preview
- Syntax highlighting for Lua preview

**Related Files**:
- `src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py`

**Estimated Effort**: 1-2 hours

---

## 📊 Progress Summary

**Total Tasks**: 9
**Completed**: 2 (22.2%)
**In Progress**: 0
**Pending**: 7 (77.8%)

### By Priority:
- **High Priority**: 6 tasks (2 completed, 4 pending)
- **Medium Priority**: 1 task (pending)
- **Low Priority**: 1 task (pending)

---

## 🎯 Recommended Next Steps

Based on priority and dependencies, the recommended order for implementation is:

1. **AnswerId Management** (3-5 hours)
   - Foundation for dialogue system
   - Blocks dialogue export functionality
   
2. **Flag Management Interface** (4-6 hours)
   - Required for quest conditions
   - Foundation for quest logic

3. **Condition Builder** (8-12 hours)
   - Depends on Flag Management
   - Core quest functionality

4. **Reward Builder UI** (4-6 hours)
   - Enhancement of existing system
   - User-facing feature

5. **Quest Templates System** (6-8 hours)
   - Quality of life improvement
   - Speeds up quest creation

6. **LUA Export Engine** (8-12 hours)
   - Final integration piece
   - Depends on all other systems

7. **Preview Tab Visual Fix** (1-2 hours)
   - Polish/cleanup task
   - Can be done anytime

---

## 📝 Notes

### Recent Changes (Nov 17, 2025)
- ✅ Completed NPC Chooser/Browser with German language support
- ✅ Completed Item Browser Data Expansion - now loads 11,000+ real SpellForce items
- ✅ Fixed CFF file path resolution for reliable data loading
- ✅ Integrated real game data across all quest creation workflows
- ✅ Enhanced item browser with proper category filtering and icon support

### Known Issues
- None currently

### Future Enhancements
- Language toggle (German/English) in NPC browser
- Portrait/icon display for NPCs
- Map integration for NPC locations
- Quest dependency graph visualization
- Bulk quest editing tools

---

**Maintainers**: SpellSmut Development Team  
**Last Review**: November 16, 2025
