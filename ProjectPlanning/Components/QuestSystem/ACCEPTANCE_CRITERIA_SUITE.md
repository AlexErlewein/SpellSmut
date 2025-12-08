# Acceptance Criteria Suite

## Overview
Comprehensive acceptance criteria and test scenarios for all quest editor features.

## Feature: Text Mode (ASCII) Overview

### Acceptance Criteria
- ✅ Users can view quest structure in ASCII/text format
- ✅ Edits in Text Mode reflect in Visual Mode immediately
- ✅ Edits in Visual Mode reflect in Text Mode immediately
- ✅ Users can add/edit/remove nodes, choices, speakers via keyboard
- ✅ Search/jump-to navigates large dialogue trees quickly
- ✅ Exported Lua matches Visual-only output for equivalent data

### Test Scenarios
1. **Create quest in Text Mode, verify in Visual Mode**
   - Create new quest with dialogue tree in Text Mode
   - Switch to Visual Mode, verify nodes appear correctly
   - Edit node in Visual Mode, verify change in Text Mode

2. **Large dialogue tree performance**
   - Create quest with 50+ dialogue nodes
   - Verify Text Mode renders quickly
   - Verify search/jump-to works efficiently

## Feature: Pre-Start Requirements

### Acceptance Criteria
- ✅ Users can add/edit/delete pre-start conditions
- ✅ Users can create AND/OR groups of conditions
- ✅ Preview shows readable human logic
- ✅ Validation highlights type/reference issues
- ✅ Export produces correct Lua Conditions blocks

### Test Scenarios
1. **Simple requirement**
   - Add requirement: PlayerHasItem(1234)
   - Verify preview shows: "IF PlayerHasItem(1234)"
   - Export and verify Lua contains: `PlayerHasItem{ItemId = 1234}`

2. **Complex requirement with grouping**
   - Add requirement: (PlayerHasItem(1234) AND QuestState(9001, Completed)) OR IsGlobalFlagTrue("AlternativePath")
   - Verify preview shows readable logic
   - Export and verify Lua contains correct nested conditions

3. **Invalid requirement**
   - Add requirement with invalid item ID
   - Verify validation shows error
   - Verify export is blocked

## Feature: NPC Chooser / Browser

### Acceptance Criteria
- ✅ Users can search/filter NPCs by name, race, faction
- ✅ Users can select quest giver (single selection)
- ✅ Users can select involved NPCs (multi-selection)
- ✅ Users can set speaker for dialogue nodes
- ✅ Selected NPCs reflected immediately in Overview and Visual editors
- ✅ Invalid/missing NPC references flagged by validation

### Test Scenarios
1. **Select quest giver**
   - Open NPC chooser
   - Search for "Rolf"
   - Select Rolf as quest giver
   - Verify quest_giver_npc_id is set correctly

2. **Set dialogue speaker**
   - Create dialogue node
   - Open speaker picker
   - Select NPC
   - Verify speaker_npc_id is set on node

3. **Invalid NPC reference**
   - Set quest giver to non-existent NPC ID
   - Verify validation shows error
   - Verify export is blocked

## Feature: Reward Builder

### Acceptance Criteria
- ✅ Users can add/edit/remove item rewards
- ✅ Users can set XP and gold rewards
- ✅ Users can search items from CFF database
- ✅ Validation blocks export on invalid item IDs
- ✅ Exported Lua reflects configured rewards accurately

### Test Scenarios
1. **Add item reward**
   - Open Reward Builder
   - Search for "Iron Hammer"
   - Add item with quantity 1
   - Export and verify Lua contains: `TransferItem{GiveItem = 3421, Flag = Give}`

2. **Add XP and gold**
   - Set XP reward to 500
   - Set gold reward to 100
   - Export and verify Lua contains: `UpdateVariable{Name = "PlayerXP", Value = 500}` and `UpdateVariable{Name = "PlayerGold", Value = 100}`

3. **Invalid item ID**
   - Add reward with invalid item ID
   - Verify validation shows error
   - Verify export is blocked

## Feature: CFF Export / Save Flow

### Acceptance Criteria
- ✅ Dry-run shows accurate preview of changes
- ✅ ID conflict detection works correctly
- ✅ Next-free ID suggestion is accurate
- ✅ Localization keys are generated correctly
- ✅ Export creates backup before writing
- ✅ Export produces success/failure report

### Test Scenarios
1. **Successful export**
   - Create quest with ID 9031
   - Run dry-run, verify preview shows quest will be added
   - Export to GameData.cff
   - Verify backup is created
   - Verify quest is added to CFF
   - Verify localization keys are added

2. **ID conflict resolution**
   - Create quest with ID 9031 (already exists)
   - Verify conflict is detected
   - Verify next-free ID is suggested (e.g., 9032)
   - Override to 9033, verify export uses 9033

3. **Localization generation**
   - Create quest with German dialogue
   - Export and verify localization keys are generated
   - Verify stubs are created for missing languages

## Feature: Validation & Lua Syntax Checking

### Acceptance Criteria
- ✅ Validation runs automatically on changes
- ✅ Validation shows errors, warnings, info in panel
- ✅ Lua syntax checking works correctly
- ✅ Export is blocked on errors
- ✅ Users can jump to validation issues

### Test Scenarios
1. **Dialogue validation**
   - Create dialogue node without speaker
   - Verify validation shows error
   - Verify export is blocked
   - Fix issue, verify validation passes

2. **Lua syntax check**
   - Create quest with invalid Lua syntax
   - Verify Lua syntax check shows error
   - Verify error shows file/line/column
   - Fix syntax, verify check passes

3. **Reference validation**
   - Create quest with invalid NPC ID
   - Verify validation shows error
   - Verify error is clickable and jumps to issue

## Feature: Templates & Condition Builder

### Acceptance Criteria
- ✅ Users can create quests from templates
- ✅ Template-generated quests are fully editable
- ✅ Users can save custom templates
- ✅ Condition builder supports AND/OR grouping
- ✅ Condition builder supports negation
- ✅ Preview shows readable human logic

### Test Scenarios
1. **Create quest from template**
   - Select "Kill Quest" template
   - Fill in parameters (target entity, count, rewards)
   - Create quest
   - Verify quest is generated with correct structure
   - Verify quest is fully editable

2. **Condition builder**
   - Create condition: PlayerHasItem(1234) AND QuestState(9001, Completed)
   - Verify preview shows readable logic
   - Export and verify Lua contains correct conditions

3. **Custom template**
   - Create custom quest template
   - Save template
   - Load template and create quest
   - Verify quest matches template structure

## Feature: Mod Packaging / Export

### Acceptance Criteria
- ✅ Users can export quests as mod packages
- ✅ Package includes all required files
- ✅ Dependency resolution works correctly
- ✅ Conflict detection prevents incompatible mods
- ✅ Generated packages can be installed by mod manager

### Test Scenarios
1. **Export mod package**
   - Create quest with ID 9031
   - Configure mod metadata (name, version, author)
   - Export as mod package
   - Verify package includes Lua files, CFF patch, localization
   - Verify package can be installed by mod manager

2. **Dependency resolution**
   - Create mod with dependency on "OtherMod v1.0.0"
   - Verify dependency is checked before export
   - Verify export fails if dependency is missing

3. **Conflict detection**
   - Create mod with quest ID 9031 (already exists in game)
   - Verify conflict is detected
   - Verify export is blocked with clear error message

## Cross-Feature Test Scenarios

### End-to-End Quest Creation
1. Create quest from template
2. Add pre-start requirements
3. Set quest giver NPC
4. Create dialogue tree with multiple branches
5. Add rewards (items, XP, gold)
6. Validate quest
7. Export to CFF
8. Package as mod
9. Verify mod can be installed and quest works in game

### Negative Test Cases
1. **ID conflict**: Create quest with existing ID, verify conflict detection
2. **Missing localization**: Create quest without localization, verify export handles gracefully
3. **Invalid item ID**: Add reward with invalid item ID, verify validation blocks export
4. **Lua syntax error**: Create quest with invalid Lua, verify syntax check catches error
5. **Circular dependency**: Create quest chain with circular dependency, verify validation detects it

### Performance Test Cases
1. **Large dialogue tree**: Create quest with 100+ dialogue nodes, verify performance
2. **Many conditions**: Create quest with 50+ conditions, verify validation performance
3. **Large mod package**: Export mod with 50+ quests, verify package generation performance

## Success Metrics
- ✅ All acceptance criteria met
- ✅ All test scenarios pass
- ✅ Performance benchmarks met
- ✅ User feedback positive
