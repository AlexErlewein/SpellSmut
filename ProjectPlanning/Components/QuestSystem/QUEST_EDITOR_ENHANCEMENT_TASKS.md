# Quest Editor Enhancement Tasks

**Last Updated**: November 14, 2025  
**Status**: 🟡 Planning Complete - Ready for Implementation  
**Focus**: Text-based dialogue editor enhancements based on George from Jungle example

---

## 🎯 High Priority Tasks

### Quest Editor Core Enhancements

#### 1. Location & NPC Tab Enhancement
**Task ID**: `quest_npc_giver_dropdown`  
**Priority**: High  
**Status**: Pending

**Description**: Add dropdown menu for Quest giver selection with existing NPCs (ID and name). Research and test if object NPCs (gravestones, etc.) are included in NPC IDs or need separate handling.

**Implementation Details**:
- Create NPC data loader from game files
- Build dropdown with NPC ID and name display
- Research object NPCs (gravestones, etc.) handling
- Test NPC ID validation

---

#### 2. Objectives Tab Data Research  
**Task ID**: `quest_objectives_data_research`  
**Priority**: High  
**Status**: Pending

**Description**: Investigate game's objective/requirement data format. Determine correct data structure needed for game compatibility and plan UI improvements (dropdown menus, predefined elements) based on findings.

**Research Areas**:
- Analyze existing quest objective formats in LUA files
- Document requirement types (kill, collect, talk, reach)
- Design UI components for each objective type
- Create data validation rules

---

### Dialogue System Core Enhancements

#### 3. AnswerId Management System
**Task ID**: `dialogue_answerid_system`  
**Priority**: High  
**Status**: Pending

**Description**: Implement automatic AnswerId assignment and tracking for dialogue steps. Ensure unique IDs across the entire dialogue tree and provide visual indicators of AnswerId usage.

**Features**:
- Auto-assign unique AnswerIds to dialogue steps
- Track AnswerId usage across dialogue tree
- Visual indicators showing AnswerId mapping
- AnswerId conflict detection and resolution
- Import existing AnswerId patterns from George example

**Technical Implementation**:
```python
class AnswerIdManager:
    def assign_answer_id(self, step: DialogueStep) -> int
    def get_answer_id_usage(self) -> Dict[int, List[str]]
    def validate_answer_id_uniqueness(self) -> List[Conflict]
    def generate_answer_id_preview(self) -> str
```

---

#### 4. Conditional Logic Builder
**Task ID**: `dialogue_conditional_builder`  
**Priority**: High  
**Status**: Pending

**Description**: Create visual interface for building complex conditions like UND(), UND9(), Negated() with flag checks (IsNpcFlagTrue/False, IsGlobalFlagTrue/False). Include condition preview and validation.

**Condition Types from George Example**:
- `IsNpcFlagTrue {Name = "flag_name"}`
- `IsNpcFlagFalse {Name = "flag_name"}`
- `IsGlobalFlagTrue {Name = "flag_name"}`
- `IsGlobalFlagFalse {Name = "flag_name"}`
- `UND(condition1, condition2, ...)` - AND operator
- `UND9(condition1, condition2, ...)` - Alternative AND
- `Negated(condition)` - NOT operator

**UI Components**:
- Condition type selector
- Flag name autocomplete
- Logical operator builder
- Live condition preview
- Validation feedback

---

#### 5. State Flag Management Interface
**Task ID**: `dialogue_flag_management`  
**Priority**: High  
**Status**: Pending

**Description**: Build comprehensive flag management system for NPC flags, global flags, and choice deactivation flags. Provide flag browser, creation wizard, and usage tracking.

**Flag Types from George Example**:
- **NPC Flags**: `n_P213_Talked`, `n_P213HeilerFolgen`, `known`
- **Global Flags**: `DschungelWeisenDialog`, `PleaseRemoveDialog_10983`
- **Choice Deactivation**: `ChoiceMitAnswerId[6]Abgeschaltet`
- **Reward Flags**: `SetRewardFlagTrue`

**Features**:
- Flag creation wizard with naming conventions
- Flag browser with search and filtering
- Flag usage tracking across dialogue
- Flag dependency visualization
- Import/export flag definitions

---

#### 6. LUA Export Engine
**Task ID**: `dialogue_lua_export`  
**Priority**: High  
**Status**: Pending

**Description**: Develop robust LUA code generation from dialogue data that matches George example format exactly. Handle OnBeginDialog, OnAnswer blocks, and proper indentation/structure.

**Output Format Requirements**:
```lua
OnBeginDialog{
    Conditions = {
        IsNpcFlagFalse{Name = "known"},
    },
    Actions = {
        Say{Tag = "wiseP213_001", String = "Kehrt um! Flieht..."},
        Answer{Tag = "", String = "", AnswerId = 1},
    }}

OnAnswer{1;
    Conditions = {
        UND( IsNpcFlagFalse {Name = "n_P213_Talked"}, IsNpcFlagFalse{Name = "ChoiceMitAnswerId[6]Abgeschaltet"} ),
    },
    Actions = {
        Say{Tag = "wiseP213_002", String = "Das Böse hier..."},
        Answer{Tag = "wiseP213_003PC", String = "Ein Verdammter...", AnswerId = 2},
    }}
```

**Technical Requirements**:
- Exact formatting match with George example
- Proper indentation and structure
- Condition block generation
- Action block generation
- Error handling and validation

---

## 🎨 Medium Priority Tasks

### Quest Editor UI Enhancements

#### 7. Rewards Tab Item Browser
**Task ID**: `quest_rewards_item_browser`  
**Priority**: Medium  
**Status**: Pending

**Description**: Create comprehensive item browser showing all obtainable items (weapons, armor, spells, etc.) with names and IDs. Research if existing weapon/armor/spell browsers can be reused or if new browser is needed.

**Implementation**:
- Research existing browser components
- Create unified item database
- Build item selection interface
- Add item preview and details
- Implement item filtering and search

---

#### 8. Preview Tab Visual Fix
**Task ID**: `quest_preview_visual_fix`  
**Priority**: Medium  
**Status**: Pending

**Description**: Remove white background fillings in preview tab for better readability and visual consistency.

**Fixes Required**:
- Identify white background elements
- Apply consistent theming
- Test readability improvements
- Ensure dark mode compatibility

---

### Dialogue System UI Enhancements

#### 9. Choice Availability Rules Engine
**Task ID**: `dialogue_choice_availability`  
**Priority**: Medium  
**Status**: Pending

**Description**: Implement system to control when choices are available based on conditions. Support complex conditional logic from George example and provide visual indicators of choice availability.

**Features**:
- Real-time choice availability evaluation
- Visual indicators for disabled choices
- Condition-based choice filtering
- Choice availability preview
- Debug mode for condition testing

---

#### 10. Action Assignment System
**Task ID**: `dialogue_action_system`  
**Priority**: Medium  
**Status**: Pending

**Description**: Create interface for assigning actions to dialogue steps (SetNpcFlagTrue, Follow, StopFollow, Say, etc.). Include action templates and parameter validation.

**Action Types from George Example**:
- `SetNpcFlagTrue {Name = "flag_name"}`
- `SetNpcFlagFalse {Name = "flag_name"}`
- `SetGlobalFlagTrue {Name = "flag_name"}`
- `SetRewardFlagTrue {Name = "flag_name"}`
- `Follow {Target = 0}`
- `StopFollow {Target = 0}`
- `Say{Tag = "tag_name", String = "dialogue text"}`
- `Outcry{Tag = "tag_name", NpcId = 10983, String = "text", Color = ColorWhite}`

---

#### 11. Dialogue Tree Visualization Enhancement
**Task ID**: `dialogue_tree_visualization`  
**Priority**: Medium  
**Status**: Pending

**Description**: Improve text-based tree view to show AnswerId mapping, choice connections, and conditional logic indicators. Add color coding for different step types and choice states.

**Enhancements**:
- Show AnswerId next to each step
- Display choice connections with arrows
- Color code step types (START, NPC_SPEECH, PLAYER_CHOICE, etc.)
- Indicate conditional logic with icons
- Show flag usage in tree view
- Add collapse/expand functionality

---

## 📚 Low Priority Tasks

#### 12. Original Quest Loading
**Task ID**: `quest_original_loading`  
**Priority**: Low  
**Status**: Pending

**Description**: Implement ability to load original game quests into editor for editing and analysis of existing quest structure (NPC locations, rewards, requirements, etc.).

**Features**:
- Parse existing LUA quest files
- Extract dialogue structure
- Load quest metadata
- Enable editing of original quests
- Import/export quest templates

---

## 🚀 Implementation Strategy

### Phase 1: Foundation (Week 1-2)
1. **AnswerId Management System** - Core ID tracking
2. **State Flag Management Interface** - Flag system foundation
3. **Location & NPC Tab Enhancement** - Basic quest setup

### Phase 2: Core Logic (Week 3-4)  
4. **Conditional Logic Builder** - Complex condition support
5. **LUA Export Engine** - Code generation
6. **Objectives Tab Data Research** - Quest structure understanding

### Phase 3: User Experience (Week 5-6)
7. **Choice Availability Rules Engine** - Dynamic choices
8. **Action Assignment System** - Step actions
9. **Dialogue Tree Visualization Enhancement** - Visual improvements

### Phase 4: Polish & Extras (Week 7-8)
10. **Rewards Tab Item Browser** - Item management
11. **Preview Tab Visual Fix** - UI consistency
12. **Original Quest Loading** - Template system

---

## 📊 Success Metrics

### Phase 1 Success Criteria
- ✅ AnswerIds are automatically assigned and unique
- ✅ Flags can be created, tracked, and managed
- ✅ NPC dropdown shows valid quest givers

### Phase 2 Success Criteria  
- ✅ Complex conditions can be built visually
- ✅ Generated LUA matches George example format
- ✅ Objective data structure is documented

### Phase 3 Success Criteria
- ✅ Choices appear/disappear based on conditions
- ✅ Actions can be assigned to dialogue steps
- ✅ Tree view shows clear dialogue flow

### Phase 4 Success Criteria
- ✅ All reward items can be selected by name
- ✅ Preview tab has consistent theming
- ✅ Original quests can be loaded and analyzed

---

## 🔗 Related Files & References

### Key Examples
- **George Dialogue**: `ModdingTools/SpellForceLUASources/script/P213/n10983.lua`
- **Castagir Dialogue**: `ModdingTools/SpellForceLUASources/script/p310/n10386.lua`
- **Darius Prison**: `ModdingTools/SpellForceLUASources/script/P213/n10986.lua`

### Current Implementation
- **Dialogue Builder**: `src/TirganachReloaded/cff_editor/widgets/simple_dialogue_builder.py`
- **Quest Editor**: `src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py`
- **Quest Creator**: `quest_creator.py`

### Planning Documents
- **Quest Creation Plan**: `ProjectPlanning/Components/QuestSystem/QUEST_CREATION_PLAN.md`
- **Current Status**: `ProjectPlanning/Status/CURRENT_STATUS.md`
- **Completed Work**: `ProjectPlanning/Status/COMPLETED_WORK.md`

---

## 📝 Notes & Decisions

### Key Insights from George Example
1. **AnswerId System**: Each choice needs unique AnswerId for branching
2. **Complex Conditions**: Multiple nested conditions control choice availability
3. **State Management**: Flags track conversation progress and choices
4. **Conditional Choices**: Same AnswerId can have different conditions
5. **Action Integration**: Dialogue steps can trigger game actions

### Design Principles
- **Simplicity First**: Text-based interface over complex visual editing
- **Pattern Matching**: Follow George example exactly for LUA generation
- **Incremental Building**: Start simple, add complexity gradually
- **User Guidance**: Provide templates and examples for common patterns

---

**Document Version**: 1.0  
**Created**: November 14, 2025  
**Author**: SpellSmut Development Team  
**Status**: 🟡 Ready for Implementation