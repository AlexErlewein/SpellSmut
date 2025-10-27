# Quest Editor Enhancements Plan

## Overview
This plan outlines enhancements to the existing Quest Editor based on analysis of SpellForce quest system guides and current codebase. The goal is to add missing data fields, improve UI visuals, enable quest bundling, and support a custom quest creator tool for generating Lua scripts.

## Current State Analysis
- **Existing Features**: Quest hierarchy tree, basic properties (ID, name, description), dialog branching editor.
- **Missing Elements**: Rewards (XP, Items, Money), requirements (conditions like PlayerHasItem, QuestState), visual dialogue enhancements, quest bundling by type/campaign.
- **Source**: Based on docs/Guides/SpellForce_Quest_System_Guide.md, docs/Guides/SpellForce_Quest_Campaign_Creation_Guide.md, and src/TirganachReloaded/cff_editor/widgets/quest_*.py.

## Planned Enhancements

### 1. Add Missing Quest Data Fields
- **Rewards Integration**:
  - Add fields in quest properties UI for XP, Items, Money (from GdsQuestRewards.lua).
  - UI: Dropdowns for item selection, input fields for amounts, triggered by SetRewardFlagTrue.
  - Implementation: Extend QuestNode class to include reward data; update save/load logic to sync with CFF.
- **Requirements/Conditions**:
  - Add condition builder in properties tab for prerequisites (e.g., PlayerHasItem, QuestState, FigureAlive).
  - UI: Tree or list for adding/removing conditions; validate against GdsConditions.lua functions.
  - Implementation: New ConditionNode class; integrate with dialog editor for branching based on conditions.

### 2. Visual Enhancements for Quest Dialogues
- **Branching Choices**:
  - Enhance DialogBranchingEditorWidget with visual buttons for player choices (e.g., styled QButtons with icons for accept/decline).
  - Add tooltips, colors (green for positive, red for negative), and animations for better appeal.
  - Implementation: Use QButtonGroup for choices; add icons from UI assets; support multi-language previews.
- **Overall UI**:
  - Improve tree view with icons (e.g., quest icons, dialogue bubbles); add search/filter for dialogues.
  - Ensure responsive design for large quest trees.

### 3. Quest Bundling in Overview
- **Grouping Options**:
  - Add filters/tabs in QuestTreeEditorWidget: By type (Main, Side, Sub-quest), campaign, map (e.g., P9 Northern Windwalls).
  - UI: QComboBox for filters, collapsible groups in tree; color-coding (e.g., blue for main quests).
  - Implementation: Extend QuestNode with type/campaign fields; update load_quest_hierarchy to support grouping.

### 4. Custom Quest Creator Editor
- **Overview**: Standalone tool or tab in QuestEditorWidget to generate Lua scripts from GUI inputs, enabling non-coders to create quests.
- **Features**:
  - Input forms for quest basics (ID, name, description), objectives, rewards, requirements.
  - Visual condition/action builder (drag-drop from GdsActions.lua/GdsConditions.lua).
  - Preview and export Lua script (e.g., for nXXXX.lua files).
  - Integration: Generate QuestNode and DialogNode objects; export to script/ directory.
- **Implementation Steps**:
  1. Create QuestCreatorWidget class.
  2. Build form UIs for each section.
  3. Add Lua generation logic (template-based from guides).
  4. Test with sample quests; integrate with existing editor for editing generated quests.

## Implementation Timeline
1. **Phase 1**: Add rewards/requirements fields (1-2 weeks).
2. **Phase 2**: Enhance dialogue visuals (1 week).
3. **Phase 3**: Implement quest bundling (1 week).
4. **Phase 4**: Build quest creator tool (2-3 weeks).
5. **Testing**: Validate against SpellForce Lua scripts; ensure CFF compatibility.

## Dependencies
- Update src/TirganachReloaded/cff_editor/widgets/quest_*.py.
- Reference docs/Guides/ for Lua syntax.
- Ensure compatibility with existing CFF data model.

## Risks and Mitigations
- **Complexity**: Start with simple additions; use modular design.
- **Testing**: Use sample quests from guides; validate Lua output.
- **User Feedback**: Iterate based on modder needs.

## Next Steps
- Review and update Components/QUEST_EDITOR.md with this content.
- Assign tasks in project management tool.
- Gather feedback from team on priorities.

---

**Document Version**: 1.0  
**Last Updated**: Current Session  
**Author**: SpellSmut Development Team