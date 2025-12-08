# Quest Creation System Plan

## Overview

This plan defines a comprehensive **Quest Creation System** - an end-to-end workflow from concept to in-game testing. The system will provide a wizard-style interface for non-coders to create fully functional SpellForce quests with minimal technical knowledge.

**Status**: 🟢 In Development - Dialogue System Complete
**Priority**: High
**Dependencies**: Quest Editor Enhancements (✅ Completed)

---

## ✅ Completed Features: Dialogue System

### Dialogue Builder Implementation (November 2025)

**Status**: ✅ **COMPLETE**

The dialogue system has been fully implemented with the following key features:

#### 1. Step-by-Step Guided Interface
- **Top-down tree view** instead of complex node-based editing
- **Guided workflow** with "Next Part" button system
- **Single-step editing** - right panel shows only currently selected step
- **Step type selection** - users choose what type of step comes next

#### 2. Enhanced Step Types
- **START** - Beginning of dialogue
- **NPC_SPEECH** - NPC dialogue with speaker name
- **PLAYER_CHOICE** - Multiple choice options with visual connection indicators
- **PLAYER_SPEECH** - Single option player speech (distinct from choices)
- **NPC_RESPONSE** - NPC responses that can be linked to specific player choices
- **END** - Conversation endpoint

#### 3. Choice-to-Response Mapping System
- **Visual connection indicators**:
  - 🟢 **Green border** = Choice connected to NPC response
  - 🔴 **Red border** = Choice needs connection
- **Clear labels** showing "Leads to: [step_id]" or connection status
- **Grouped choice editing** with individual response mapping
- **Smart branching** support for complex dialogue trees

#### 4. User Experience Improvements
- **Clean visual design** with proper contrast (fixed white text on bright background)
- **Intuitive workflow** - click step → edit → add next step → select type
- **Real-time validation** showing connection status
- **Auto-save functionality** preserving work progress
- **Error handling** for UI widget lifecycle issues

#### 5. Technical Implementation
- **File**: `src/TirganachReloaded/cff_editor/widgets/simple_dialogue_builder.py`
- **Architecture**: Step-based data structure with choice-specific response mapping
- **Data Model**: Enhanced `DialogueStep` with `choices` containing `next_step_id` mapping
- **UI Framework**: PySide6 with Qt layouts and signal/slot patterns

#### 6. Launch System
- **Single launcher**: `quest_creator.py` (cleaned up multiple confusing launchers)
- **Dependency management**: Uses `uv` virtual environment
- **Python compatibility**: Works with Python 3.13
- **Error recovery**: Fixed QLabel deletion issues and import errors

---

## System Goals

### Primary Objectives

1. **Lower the Barrier to Entry**: Enable modders without Lua knowledge to create quests
2. **Visual Quest Building**: Drag-drop interface for quest objectives, dialogues, and rewards
3. **Rapid Prototyping**: Test quests in-game quickly with minimal setup
4. **Educational Tool**: Teach modders the SpellForce quest system through GUI
5. **Export to Lua**: Generate production-ready Lua scripts from GUI input

### Secondary Objectives

- Validate quest logic before export
- Provide quest templates for common patterns
- Enable collaborative quest design
- Support quest version control and iteration

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Quest Creation Workflow                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐│
│  │   Wizard     │────▶│   Visual     │────▶│   Export &   ││
│  │   Interface  │     │   Editor     │     │   Testing    ││
│  └──────────────┘     └──────────────┘     └──────────────┘│
│        │                     │                     │        │
│        ▼                     ▼                     ▼        │
│  Quest Basics         Quest Steps          Lua Scripts      │
│  NPC Setup            Dialogue Tree        Test Map         │
│  Rewards              Requirements         In-Game Test     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Quest Creator Wizard Interface

### 1.1 Interface Design

**Implementation**: Separate window from Quest Editor (accessed via menu: `Tools → Quest Creator`)

**Wizard Steps**:

```
Step 1: Quest Basics
  ├─ Quest ID (auto-generated or manual)
  ├─ Quest Name
  ├─ Quest Description
  ├─ Quest Type (Main Quest, Side Quest, Collection, Kill, Escort)
  └─ Target Map (P7, P9, P999, etc.)

Step 2: Quest Giver
  ├─ NPC ID (existing or new)
  ├─ NPC Name
  ├─ NPC Position (X, Y on map)
  └─ NPC Type (Human, Dwarf, Elf, etc.)

Step 3: Quest Objectives
  ├─ Objective Type (Collect Items, Kill Enemies, Talk to NPC, Reach Location)
  ├─ Target (Item IDs, Enemy IDs, NPC IDs, Coordinates)
  ├─ Quantity (if applicable)
  └─ Add Multiple Objectives

Step 4: Quest Rewards
  ├─ Experience Points
  ├─ Items (multi-select from item database)
  ├─ Money (Gold/Silver/Copper)
  └─ Additional Flags/States

Step 5: Review & Generate
  ├─ Preview quest structure
  ├─ Validate quest logic
  ├─ Generate Lua scripts
  └─ Export to test map
```

### 1.2 UI Components

**QuestCreatorWizard Class** (new file: `quest_creator_wizard.py`)

```python
class QuestCreatorWizard(QWizard):
    """Multi-step wizard for quest creation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SpellForce Quest Creator")
        
        # Add wizard pages
        self.addPage(QuestBasicsPage())
        self.addPage(QuestGiverPage())
        self.addPage(QuestObjectivesPage())
        self.addPage(QuestRewardsPage())
        self.addPage(QuestReviewPage())
```

**Key Features**:
- ✅ Navigation buttons (Back, Next, Finish)
- ✅ Progress indicator (Step 1 of 5)
- ✅ Field validation on each page
- ✅ Real-time preview panel
- ✅ Save/Load wizard state (for multi-session editing)

### 1.3 Data Collection

**Quest Data Model**:

```python
@dataclass
class QuestCreationData:
    """Data collected from quest creator wizard"""
    
    # Step 1: Basics
    quest_id: int
    quest_name: str
    quest_description: str
    quest_type: QuestType  # Enum: MAIN, SIDE, COLLECTION, KILL, ESCORT
    target_map: str  # e.g., "P999"
    
    # Step 2: Quest Giver
    npc_id: int
    npc_name: str
    npc_position: Tuple[int, int]  # (X, Y)
    npc_type: str  # "Human", "Dwarf", etc.
    
    # Step 3: Objectives
    objectives: List[QuestObjective]
    
    # Step 4: Rewards
    rewards: QuestRewards
    
    # Step 5: Advanced
    prerequisites: List[QuestPrerequisite]
    custom_flags: List[str]
```

---

## Phase 2: Test Map Creation

### 2.1 Test Map Structure

**Map ID**: P999 (Quest Testing Grounds)

**Map Layout**:

```
┌────────────────────────────────────────────────────────┐
│                   Quest Test Map (P999)                 │
│                                                         │
│  [Quest Giver NPC]     [Dialogue NPC 1]                │
│         │                     │                         │
│         ▼                     ▼                         │
│    Start Point         Test Dialogue                    │
│                                                         │
│                                                         │
│  [Treasure Chest 1]    [Treasure Chest 2]              │
│         │                     │                         │
│         ▼                     ▼                         │
│    Quest Item 1          Quest Item 2                   │
│                                                         │
│                                                         │
│  [Enemy Spawn 1]       [Enemy Spawn 2]                 │
│         │                     │                         │
│         ▼                     ▼                         │
│    Kill Quest          Collection Quest                 │
│                                                         │
│                                                         │
│  [Goal Location]       [Dialogue NPC 2]                │
│         │                     │                         │
│         ▼                     ▼                         │
│   Reach Location      Quest Turn-In                     │
│                                                         │
└────────────────────────────────────────────────────────┘
```

### 2.2 Test Map NPCs

**Pre-configured NPCs**:

| NPC ID | Name | Type | Purpose |
|--------|------|------|---------|
| 9900 | Quest Master | Human | Quest giver for all test quests |
| 9901 | Dialogue Tester 1 | Elf | Test branching conversations |
| 9902 | Dialogue Tester 2 | Dwarf | Test multi-stage dialogues |
| 9903 | Reward Vendor | Human | Verify reward items received |
| 9904 | Quest Tracker | Human | Display current quest states |

### 2.3 Test Map Objects

**Interactive Objects**:

| Object ID | Type | Purpose |
|-----------|------|---------|
| 9800 | Treasure Chest | Contains test quest items (IDs 9700-9710) |
| 9801 | Treasure Chest | Contains rare items for collection quests |
| 9802 | Portal | Test quest progression across locations |
| 9803 | Lever/Switch | Test item-based quest triggers |
| 9804 | Campfire | Test proximity-based quest events |

**Test Items** (IDs 9700-9710):
- 9700: Wolf Pelt (collection quest)
- 9701: Ancient Scroll (fetch quest)
- 9702: Dwarf Key (unlock quest)
- 9703: Healing Potion (reward test)
- 9704: Magic Ring (reward test)

### 2.4 Test Map Generation

**Auto-generation Script**: `generate_test_map.py`

```python
def generate_test_map(quest_data: QuestCreationData) -> None:
    """
    Generate test map files for quest testing
    
    Creates:
    - script/P999/n0.lua (platform script)
    - script/P999/n9900.lua (quest giver)
    - script/P999/n9901.lua (dialogue tester)
    - map/custom/quest_test_p999.map (map file)
    """
    
    # Create directory structure
    create_map_directory("P999")
    
    # Generate platform script with quest logic
    generate_platform_script(quest_data)
    
    # Generate NPC scripts
    for npc in test_npcs:
        generate_npc_script(npc, quest_data)
    
    # Generate quest rewards
    generate_quest_rewards(quest_data)
    
    # Create map file (if map editor available)
    generate_map_file(quest_data)
```

---

## Phase 3: Dialogue Choice System

### 3.1 Visual Dialogue Builder

**Enhancement to Existing Dialog Editor**:

Current state: Dialog tree with color-coded nodes (blue=Player, green=NPC)

**New Features**:

1. **Choice Node Type**:
   - Visual representation of player choices (branching)
   - Icon indicators for choice types (accept/decline/neutral)
   - Hover tooltips showing choice consequences

2. **Branching Visualization**:
   ```
   [NPC: "Will you help me?"]
         │
         ├─── [CHOICE 1: "Yes, I'll help!"] ──▶ [Quest Accepted]
         │           (Green, AnswerId=1)
         │
         ├─── [CHOICE 2: "Not right now"] ──▶ [Quest Delayed]
         │           (Yellow, AnswerId=2)
         │
         └─── [CHOICE 3: "No, never!"] ──▶ [Quest Declined]
                     (Red, AnswerId=3)
   ```

3. **Consequence Preview**:
   - Show what actions trigger from each choice
   - Display quest state changes
   - Highlight flags set/cleared

### 3.2 Dialogue Data Structure

**Enhanced DialogNode**:

```python
class DialogChoice:
    """Represents a single player choice in dialogue"""
    
    choice_id: int  # AnswerId in Lua
    text: str  # Player response text
    choice_type: ChoiceType  # ACCEPT, DECLINE, NEUTRAL, INFO
    conditions: List[Condition]  # When this choice is available
    actions: List[Action]  # What happens when chosen
    next_node: Optional[int]  # ID of next dialogue node
    
class DialogNode:
    """Enhanced with choice support"""
    
    # Existing fields
    dialogue_id: int
    speaker: SpeakerType  # NPC, PLAYER
    text: str
    
    # New fields for choices
    is_choice_point: bool  # True if player can choose response
    choices: List[DialogChoice]  # Available player responses
    parent_choice_id: Optional[int]  # Which choice led here
```

### 3.3 Choice Builder UI

**DialogChoiceEditor Widget** (extends existing dialog editor):

```python
class DialogChoiceEditor(QWidget):
    """Visual editor for dialogue choices"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Left panel: Choice list
        self.choice_list = QListWidget()
        
        # Right panel: Choice details
        self.choice_text = QLineEdit()
        self.choice_type = QComboBox()  # Accept, Decline, Neutral, Info
        self.conditions_builder = ConditionsBuilderWidget()
        self.actions_builder = ActionsBuilderWidget()
        
        # Bottom panel: Consequence preview
        self.consequence_preview = QTextEdit()
```

**Features**:
- ✅ Add/Remove choices
- ✅ Drag-drop to reorder
- ✅ Color-coded choice types
- ✅ Condition/action builders
- ✅ Preview generated Lua code

---

## Phase 4: Quest Step Hierarchy

### 4.1 Visual Step Representation

**Quest Flow Diagram**:

```
┌─────────────────────────────────────────────────────────┐
│                   Quest: "The Hunter's Request"          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  STEP 1: Talk to Hunter                                 │
│  ├─ Trigger: Player enters village                      │
│  ├─ Action: Start dialogue                              │
│  └─ Result: Quest activated (QuestId 1000)              │
│        │                                                 │
│        ▼                                                 │
│  STEP 2: Collect 3 Wolf Pelts                           │
│  ├─ Objective: PlayerHasItem{ItemId=2500, Amount=3}     │
│  ├─ Optional: Kill wolves (spawn script)                │
│  └─ Result: Flag "HunterQuestItemsReady" set            │
│        │                                                 │
│        ▼                                                 │
│  STEP 3: Return to Hunter                               │
│  ├─ Trigger: Player talks to Hunter again               │
│  ├─ Condition: HunterQuestItemsReady == true            │
│  └─ Result: Quest completed                             │
│        │                                                 │
│        ▼                                                 │
│  STEP 4: Receive Reward                                 │
│  ├─ Remove: 3 Wolf Pelts                                │
│  ├─ Give: 100 XP, 5 Gold, Healing Potion                │
│  └─ Result: Quest solved (StateSolved)                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Quest Step Editor

**QuestStepHierarchyWidget** (new widget in quest editor):

```python
class QuestStep:
    """Represents a single step in quest progression"""
    
    step_id: int
    step_name: str
    step_type: StepType  # START, OBJECTIVE, CHECK, COMPLETE
    dependencies: List[int]  # Which steps must complete first
    
    # Event definition
    event_type: EventType  # OnOneTimeEvent, OnEvent, OnToggleEvent
    conditions: List[Condition]
    actions: List[Action]
    
    # Visual properties
    position: Tuple[int, int]  # Position in graph
    color: str  # Color code for step type

class QuestStepHierarchyWidget(QWidget):
    """Visual quest flow editor with drag-drop steps"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Canvas for visual graph
        self.canvas = QuestFlowCanvas()
        
        # Toolbox with step templates
        self.step_toolbox = QuestStepToolbox()
        
        # Properties panel
        self.step_properties = QuestStepPropertiesPanel()
```

**Features**:
- ✅ Drag-drop quest steps onto canvas
- ✅ Connect steps with dependency arrows
- ✅ Validate step logic (detect circular dependencies)
- ✅ Color-coded step types
- ✅ Zoom/pan canvas for complex quests
- ✅ Export to event sequence (OnOneTimeEvent blocks)

### 4.3 Step Templates

**Pre-built Templates**:

| Template | Description | Lua Pattern |
|----------|-------------|-------------|
| **Talk to NPC** | Dialogue interaction | `OnBeginDialog` + conditions |
| **Collect Items** | Gather X items | `PlayerHasItem{ItemId, Amount}` |
| **Kill Enemies** | Defeat X enemies | `FigureDead` + counter |
| **Reach Location** | Travel to coordinates | `FigureInRange{X, Y, Range}` |
| **Wait for Time** | Delay before next step | Timer-based event |
| **Escort NPC** | Protect NPC to location | `FigureAlive` + `FigureInRange` |
| **Activate Object** | Use lever/chest/portal | Object interaction flag |

---

## Phase 5: Integration & Testing

### 5.1 Export System

**Lua Script Generation**:

```python
class QuestLuaExporter:
    """Generate production-ready Lua scripts from quest data"""
    
    def export_quest(self, quest_data: QuestCreationData) -> Dict[str, str]:
        """
        Export quest to Lua files
        
        Returns:
            Dict mapping file paths to Lua code content
        """
        
        files = {}
        
        # 1. Platform script (n0.lua)
        files[f"script/{quest_data.target_map}/n0.lua"] = \
            self.generate_platform_script(quest_data)
        
        # 2. Quest giver NPC script
        files[f"script/{quest_data.target_map}/n{quest_data.npc_id}.lua"] = \
            self.generate_npc_script(quest_data)
        
        # 3. Quest rewards entry
        files["script/GdsQuestRewards.lua"] = \
            self.generate_rewards_entry(quest_data)
        
        return files
    
    def generate_platform_script(self, quest_data: QuestCreationData) -> str:
        """Generate n0.lua with quest events"""
        
        lua_code = []
        
        # Header
        lua_code.append("function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)")
        lua_code.append("BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)")
        lua_code.append("")
        lua_code.append(f"-- Quest: {quest_data.quest_name}")
        lua_code.append(f"-- QuestId: {quest_data.quest_id}")
        lua_code.append("")
        
        # Generate events for each quest step
        for step in quest_data.objectives:
            lua_code.append(self.generate_event(step))
        
        # Footer
        lua_code.append("EndDefinition()")
        lua_code.append("end")
        
        return "\n".join(lua_code)
```

### 5.2 Testing Workflow

**In-Game Test Process**:

1. **Pre-Test Validation**:
   - Check quest ID uniqueness
   - Validate item IDs exist
   - Verify NPC IDs don't conflict
   - Check map exists

2. **Export to Test Map**:
   - Generate Lua scripts → `script/P999/`
   - Copy to game directory
   - Backup existing files

3. **Launch Game**:
   - Load test map (P999)
   - Talk to Quest Master NPC (9900)
   - Accept quest from wizard

4. **Test Checklist**:
   - ☐ Quest appears in journal
   - ☐ Objectives are clear
   - ☐ Items can be collected
   - ☐ Dialogues work correctly
   - ☐ Quest completes successfully
   - ☐ Rewards are granted

5. **Debug Tools**:
   - Console flag viewer (show quest states)
   - Item spawner (test collection quests)
   - Teleport commands (test locations)

### 5.3 Iteration Feedback Loop

```
Create Quest → Export → Test → Find Issues → Fix in GUI → Re-export → Re-test
```

**Built-in Debugging**:
- Quest state logger (track StateUnknown → StateActive → StateSolved)
- Dialogue flow tracer (log all dialogue choices taken)
- Event trigger logger (show which conditions passed/failed)

---

## Phase 6: Advanced Features

### 6.1 Quest Templates

**Pre-built Quest Types**:

1. **Fetch Quest**:
   - Template: "Bring me X items"
   - Fill-in: Item ID, quantity, NPC, reward

2. **Kill Quest**:
   - Template: "Defeat X enemies"
   - Fill-in: Enemy type, quantity, location

3. **Escort Quest**:
   - Template: "Protect NPC from A to B"
   - Fill-in: NPC ID, start/end locations, spawn enemies

4. **Discovery Quest**:
   - Template: "Find location X"
   - Fill-in: Coordinates, description

5. **Multi-Stage Quest**:
   - Template: Chain of sub-quests
   - Fill-in: Multiple objectives in sequence

### 6.2 Quest Validation

**Automated Checks**:

```python
class QuestValidator:
    """Validate quest logic before export"""
    
    def validate(self, quest_data: QuestCreationData) -> List[ValidationError]:
        errors = []
        
        # Check for circular dependencies
        if self.has_circular_dependency(quest_data.objectives):
            errors.append("Quest has circular step dependencies")
        
        # Check item IDs exist
        for obj in quest_data.objectives:
            if obj.type == ObjectiveType.COLLECT:
                if not self.item_exists(obj.target_id):
                    errors.append(f"Item ID {obj.target_id} not found")
        
        # Check NPC IDs are valid
        if not self.npc_id_available(quest_data.npc_id):
            errors.append(f"NPC ID {quest_data.npc_id} already in use")
        
        # Check quest ID uniqueness
        if self.quest_id_exists(quest_data.quest_id):
            errors.append(f"Quest ID {quest_data.quest_id} already exists")
        
        return errors
```

### 6.3 Collaborative Features

**Quest Sharing**:
- Export quest to JSON format
- Import quest from JSON
- Share quest templates with community
- Version control integration (Git-friendly format)

**Quest Library**:
- Browse community-created quests
- Rate and review quests
- Download and import with one click

---

## Implementation Timeline

### Week 1: Foundation (Phase 1)
- ☐ Create `QuestCreatorWizard` class
- ☐ Implement wizard pages (Basics, Giver, Objectives, Rewards)
- ☐ Build `QuestCreationData` model
- ☐ Add menu integration to main application

### Week 2: Test Map (Phase 2)
- ☐ Design test map structure
- ☐ Create test NPCs (9900-9904)
- ☐ Create test items (9700-9710)
- ☐ Implement `generate_test_map.py` script
- ☐ Test map file generation

### Week 3: Dialogue System (Phase 3)
- ☐ Enhance `DialogNode` with choice support
- ☐ Build `DialogChoiceEditor` widget
- ☐ Implement branching visualization
- ☐ Add consequence preview
- ☐ Test dialogue export to Lua

### Week 4: Quest Steps (Phase 4)
- ☐ Create `QuestStep` model
- ☐ Build `QuestStepHierarchyWidget`
- ☐ Implement drag-drop canvas
- ☐ Add step templates toolbox
- ☐ Implement dependency validation

### Week 5: Integration (Phase 5)
- ☐ Build `QuestLuaExporter` class
- ☐ Implement script generation for all components
- ☐ Create testing workflow documentation
- ☐ Add validation system
- ☐ Test full create → export → test cycle

### Week 6: Polish & Documentation
- ☐ Add quest templates (Phase 6)
- ☐ Implement quest validation
- ☐ Create user tutorials
- ☐ Write API documentation
- ☐ Create video walkthrough

---

## Technical Requirements

### Dependencies

**Python Packages**:
- PySide6 (Qt GUI framework) - ✅ Already installed
- dataclasses (data models) - ✅ Python standard library
- typing (type hints) - ✅ Python standard library
- json (quest import/export) - ✅ Python standard library

**Game Files Access**:
- Read: `script/GdsQuestRewards.lua` (parse existing quests)
- Read: `script/P*/` (analyze quest patterns)
- Write: `script/P999/` (test map scripts)
- Write: `map/custom/` (test map file)

### File Structure

```
src/TirganachReloaded/cff_editor/
├── widgets/
│   ├── quest_tree_editor.py          # ✅ Existing editor
│   ├── quest_creator_wizard.py       # NEW: Wizard interface
│   ├── quest_step_hierarchy.py       # NEW: Step flow editor
│   ├── dialog_choice_editor.py       # NEW: Choice builder
│   └── quest_validation.py           # NEW: Validation system
├── models/
│   ├── quest_creation_data.py        # NEW: Quest data model
│   ├── quest_step.py                 # NEW: Step model
│   └── dialog_choice.py              # NEW: Choice model
├── exporters/
│   ├── quest_lua_exporter.py         # NEW: Lua generation
│   └── test_map_generator.py         # NEW: Test map creator
└── templates/
    ├── fetch_quest.json               # NEW: Quest templates
    ├── kill_quest.json
    ├── escort_quest.json
    └── discovery_quest.json
```

---

## Success Metrics

### Phase 1 Success
- ✅ Wizard completes all 5 steps
- ✅ Data validation works on each step
- ✅ Quest data can be saved/loaded
- ✅ Preview shows quest structure

### Phase 2 Success
- ✅ Test map loads in game
- ✅ All test NPCs spawn correctly
- ✅ Test items are usable
- ✅ Map is navigable and functional

### Phase 3 Success
- ✅ Dialogue choices display correctly
- ✅ Branching logic works in-game
- ✅ Player can make meaningful choices
- ✅ Choices affect quest progression

### Phase 4 Success
- ✅ Quest steps display in logical order
- ✅ Dependencies are enforced
- ✅ Step validation catches errors
- ✅ Visual flow matches Lua output

### Phase 5 Success
- ✅ Generated Lua scripts are syntactically correct
- ✅ Quest works in-game without errors
- ✅ All quest steps trigger correctly
- ✅ Rewards are granted properly

### Final Success Criteria
- ✅ Non-programmer can create a working quest in under 30 minutes
- ✅ Quest exports to clean, readable Lua code
- ✅ Quest works in-game on first export (no manual fixing)
- ✅ System generates quests matching official SpellForce quality

---

## Risks & Mitigations

### Risk 1: Complex Lua Generation
**Issue**: Generating correct Lua syntax is error-prone  
**Mitigation**: 
- Use template-based generation (fill-in-the-blanks)
- Validate against official quest scripts
- Provide Lua syntax preview before export

### Risk 2: Game Integration Issues
**Issue**: Generated scripts may not work in-game  
**Mitigation**:
- Test with simple quests first
- Use test map for isolated testing
- Provide detailed error logging

### Risk 3: UI Complexity
**Issue**: Too many features may overwhelm users  
**Mitigation**:
- Start with wizard (simple, guided)
- Add advanced features later
- Provide "Basic" vs "Advanced" modes

### Risk 4: Quest ID Conflicts
**Issue**: Quest IDs may collide with existing quests  
**Mitigation**:
- Auto-generate IDs in safe range (9000-9999)
- Validate against existing quest database
- Allow manual override for experts

---

## Future Enhancements

### Post-V1 Features

1. **Visual Scripting**:
   - Node-based quest logic editor
   - Drag-drop conditions and actions
   - Real-time Lua preview

2. **AI-Assisted Quest Writing**:
   - Generate quest descriptions from templates
   - Suggest appropriate rewards
   - Auto-balance difficulty

3. **Quest Analytics**:
   - Track quest completion rates
   - Identify broken quests
   - Suggest improvements

4. **Multi-Quest Campaigns**:
   - Chain multiple quests together
   - Manage quest dependencies across maps
   - Create branching storylines

5. **Localization Support**:
   - Multi-language quest text
   - Translation management
   - Export to localization files

---

## Related Documentation

- [Quest System Guide](../../docs/Guides/SpellForce_Quest_System_Guide.md)
- [Quest Campaign Creation Guide](../../docs/Guides/SpellForce_Quest_Campaign_Creation_Guide.md)
- [Quest Editor Enhancements](QUEST_EDITOR.md)
- [Modding Master Plan](MODDING_PLAN.md)

---

## Current Quest Editor Enhancement Tasks

### High Priority Tasks

1. **Location & NPC Tab Enhancement**
   - Add dropdown menu for Quest giver selection with existing NPCs (ID and name)
   - Research and test if object NPCs (gravestones, etc.) are included in NPC IDs or need separate handling
   - **Task ID**: `quest_npc_giver_dropdown`

2. **Objectives Tab Data Research**
   - Investigate game's objective/requirement data format
   - Determine correct data structure needed for game compatibility
   - Plan UI improvements (dropdown menus, predefined elements) based on findings
   - **Task ID**: `quest_objectives_data_research`

### Medium Priority Tasks

3. **Rewards Tab Item Browser**
   - Create comprehensive item browser showing all obtainable items (weapons, armor, spells, etc.) with names and IDs
   - Research if existing weapon/armor/spell browsers can be reused or if new browser is needed
   - **Task ID**: `quest_rewards_item_browser`

4. **Preview Tab Visual Fix**
   - Remove white background fillings in preview tab for better readability and visual consistency
   - **Task ID**: `quest_preview_visual_fix`

### Low Priority Tasks

5. **Original Quest Loading**
   - Implement ability to load original game quests into editor for editing and analysis
   - Analyze existing quest structure (NPC locations, rewards, requirements, etc.)
   - **Task ID**: `quest_original_loading`

### Dialogue System Enhancement (Based on George from Jungle Example)

**Reference**: `ModdingTools/SpellForceLUASources/script/P213/n10983.lua`

**Key Elements Identified**:
- Player choices with unique `AnswerId` system
- Conditional responses using `IsNpcFlagTrue/False`, `IsGlobalFlagTrue/False`
- Complex branching with `OnAnswer{Id; ...}` blocks
- State management through NPC flags
- Multiple choice options with `OfferAnswer` vs `Answer` distinction

**Planned Dialogue Enhancements**:
- Enhanced choice management system
- Conditional logic builder for dialogue availability
- State flag management interface
- Improved dialogue tree visualization
- Import/export compatibility with LUA dialogue format

---

**Document Version**: 1.1  
**Created**: 2025-10-27  
**Updated**: 2025-11-14  
**Author**: SpellSmut Development Team  
**Status**: 🟢 Active Development - Enhancement Tasks Defined
