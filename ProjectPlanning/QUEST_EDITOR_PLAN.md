# Quest Editor Enhancement Plan

## Executive Summary

This document outlines the comprehensive plan for enhancing the SpellForce CFF Editor with a full-featured quest creation and editing system. The enhancement transforms the current read-only quest viewer into an interactive quest creation tool with hierarchical quest trees and branching dialog systems.

## Current Status

### ✅ Completed Tasks (High Priority)

#### 1. Quest Structure Analysis
**Date Completed**: Current Session
**Findings**:
- **Quest Data Model**: Quests use hierarchical relationships via `parent_quest_id` and `sub_quests` relations
- **Data Sources**:
  - Quest metadata: `quests` table (quest_id, parent_quest_id, order_index)
  - Names: `localisation` table via `name_id`
  - Descriptions: `advanced_descriptions` table via `description_id`
- **Current Implementation**: `QuestDetailsWidget` provides read-only view with basic info, keyword-based dialog search, and simple hierarchy display

#### 2. Hierarchical Quest Tree Design
**Date Completed**: Current Session
**Components Created**:
- **QuestNode Data Model**: Serializable quest node with hierarchy support
- **QuestTreeEditorWidget**: Interactive tree widget with full CRUD operations
- **Features**:
  - Drag-drop reordering
  - Context menus for add/edit/delete
  - Visual distinction (main quests vs subquests)
  - Parent-child relationship management
  - Auto-generated quest IDs

#### 3. Dialog Branching System Design
**Date Completed**: Current Session
**Dialog Structure Analysis**:
- **Naming Convention**: Sequential numbered dialogs (character001, character002, etc.)
- **Conversation Flow**: Alternating NPC lines and player choices
- **Player Choices**: Marked with "PC" suffix (ashawe001PC)
- **Branching Logic**: Each player choice can lead to different NPC responses

**Components Created**:
- **DialogNode Data Model**: Conversation tree node with branching support
- **DialogBranchingEditorWidget**: Interactive dialog tree editor
- **Features**:
  - Conversation preview
  - Branch visualization
  - NPC/Player distinction
  - Sequential dialog generation

## Architecture Overview

### Current CFF Editor Integration
- **Data Model**: `CFFDataModel` provides access to all game data tables
- **Widget System**: PySide6-based widgets with signal/slot communication
- **Category System**: Extensible category-based element viewing
- **File Operations**: Load/save CFF files with change tracking

### Quest Editor Components

#### Core Widgets
1. **QuestTreeEditorWidget** (`TirganachReloaded/cff_editor/widgets/quest_tree_editor.py`)
   - Hierarchical quest tree display
   - Interactive editing capabilities
   - Parent-child relationship management

2. **DialogBranchingEditorWidget** (`TirganachReloaded/cff_editor/widgets/dialog_branching_editor.py`)
   - Conversation tree visualization
   - Dialog branching logic
   - NPC/Player response management

3. **Enhanced QuestDetailsWidget** (existing, to be enhanced)
   - Unified quest information display
   - Integration with tree and dialog editors

#### Data Models
1. **QuestNode**: Hierarchical quest representation
2. **DialogNode**: Conversation tree node
3. **QuestHierarchy**: Complete quest structure with relationships

## Implementation Plan

### 🔄 In Progress Tasks (Medium Priority)

#### 4. Create QuestNode and DialogNode Data Models
**Status**: Partially Complete
**Requirements**:
- Full serialization/deserialization support
- Validation logic for quest hierarchies
- Integration with CFF data structures
- Undo/redo support

#### 5. Build Interactive Quest Tree Widget
**Status**: Partially Complete
**Requirements**:
- Drag-drop reparenting
- Bulk operations (copy, paste, duplicate)
- Search and filter capabilities
- Keyboard shortcuts
- Visual feedback for operations

#### 6. Build Dialog Editor Widget
**Status**: Partially Complete
**Requirements**:
- Visual conversation flow
- Conditional branching (quest state, player choices)
- Dialog validation
- Preview mode
- Export/import dialog trees

#### 7. Add Quest Creation Wizard
**Status**: Pending
**Requirements**:
- New quest templates
- Guided quest creation process
- Validation and error checking
- Integration with existing quests

#### 8. Add Subquest Creation and Linking
**Status**: Pending
**Requirements**:
- Automatic parent-child linking
- Dependency management
- Quest chain validation
- Circular reference prevention

### 📋 Planned Tasks (Low Priority)

#### 9. Add Save/Load Quest Hierarchies
**Status**: Pending
**Requirements**:
- Export quest trees to JSON
- Import from JSON templates
- Integration with CFF save operations
- Backup and versioning

#### 10. Add Validation for Quest Logic
**Status**: Pending
**Requirements**:
- Quest dependency validation
- Dialog flow consistency checks
- Localization completeness
- Game logic integration testing

## Technical Specifications

### Quest Data Structure
```python
class QuestNode:
    quest_id: Optional[int]          # Primary key, auto-generated for new quests
    name: str                        # Display name from localisation
    description: str                 # Quest description
    parent_id: Optional[int]         # Parent quest ID
    order_index: int                 # Sort order within hierarchy
    is_new: bool                     # Flag for newly created quests
    children: List[QuestNode]        # Subquests
    original_data: Dict              # Original CFF data for change tracking
```

### Dialog Data Structure
```python
class DialogNode:
    dialogue_name: str               # e.g., "ashawe001"
    text: str                        # Dialog text
    speaker: str                     # "NPC" or "Player"
    is_player_choice: bool           # True for player responses
    parent_choice: Optional[str]     # Which choice leads here
    children: List[DialogNode]       # Follow-up dialogs
    order_index: int                 # Sequence order
```

### File Structure
```
TirganachReloaded/cff_editor/widgets/
├── quest_tree_editor.py           # Hierarchical quest editor
├── dialog_branching_editor.py     # Dialog tree editor
└── quest_details.py               # Enhanced quest details (existing)

TirganachReloaded/cff_editor/
├── data_model.py                  # Enhanced with quest operations
└── main_window.py                 # Integration points

ProjectPlanning/
└── QUEST_EDITOR_PLAN.md           # This file
```

## Integration Points

### Main Window Integration
- Add "Quest Editor" tab to main window
- Integrate with existing category selection system
- Provide toolbar access to quest operations

### Data Model Integration
- Extend `CFFDataModel` with quest-specific methods
- Add quest hierarchy loading/saving
- Integrate with localisation table updates

### File Operations
- Save quest changes to CFF file
- Export quest templates
- Import quest hierarchies
- Backup existing data

## User Experience Design

### Quest Editor Interface
```
┌─────────────────────────────────────────────────────────────┐
│ Quest Editor - [CFF File Name]                              │
├─────────────────┬───────────────────────────────────────────┤
│                 │ Toolbar: Add Main Quest | Save | Load     │
│ Quest Hierarchy │                                           │
│ Tree            │ ┌─ Quest Tree ──────────────────────────┐ │
│                 │ │ • Main Quest 1 (ID: 1)                │ │
│ • Main Quest 1  │ │   └─ Subquest 1.1 (ID: 2)             │ │
│   └─ Subquest   │ │   └─ Subquest 1.2 (ID: 3)             │ │
│ • Main Quest 2  │ │ • Main Quest 2 (ID: 4)                │ │
│ • Main Quest 3  │ │   └─ Subquest 2.1 (ID: 5)             │ │
│                 │ └───────────────────────────────────────┘ │
├─────────────────┼───────────────────────────────────────────┤
│ Quest Details   │ ┌─ Quest Properties ────────────────────┐ │
│                 │ │ ID: 1                                 │ │
│ • Basic Info    │ │ Name: Stardust                       │ │
│ • Dialogs       │ │ Description: [Text]                  │ │
│ • Hierarchy     │ │ Parent: None                         │ │
│                 │ └───────────────────────────────────────┘ │
├─────────────────┴───────────────────────────────────────────┤
│ Dialog Branching Editor                                    │
│ ┌─ Dialog Tree ──────────────────┬─ Properties ──────────┐ │
│ │ • NPC: Hello adventurer!       │ │ Speaker: NPC        │ │
│ │   └─ Player: What do you need? │ │ Text: [Edit]        │ │
│ │     └─ NPC: I need your help...│ │                     │ │
│ │   └─ Player: I'm busy right now│ └─────────────────────┘ │
│ │     └─ NPC: Very well...       │                         │
│ └────────────────────────────────┴─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Workflow
1. **Load CFF File**: Open existing game data
2. **Browse Quests**: Use tree view to navigate quest hierarchy
3. **Edit Quest**: Modify properties, add subquests
4. **Edit Dialogs**: Create/modify conversation trees
5. **Save Changes**: Apply modifications to CFF file

## Validation and Testing

### Quest Validation Rules
- No circular parent-child relationships
- Valid quest IDs (unique, sequential)
- Required fields (name, description)
- Proper localisation table references

### Dialog Validation Rules
- Valid dialogue names (alphanumeric + numbers)
- Proper NPC/Player alternation
- No orphaned dialog branches
- Consistent conversation flow

### Testing Scenarios
- Create new quest hierarchy
- Modify existing quests
- Add branching dialogs
- Save/load operations
- Integration with main editor

## Future Enhancements

### Advanced Features
- **Quest Dependencies**: Prerequisites and unlock conditions
- **Quest Rewards**: Item/experience/gold rewards
- **Quest Objectives**: Multiple completion criteria
- **Quest States**: Active, completed, failed states
- **Dialog Conditions**: Context-aware responses

### Performance Optimizations
- Lazy loading for large quest hierarchies
- Caching for frequently accessed data
- Background validation
- Memory management for large dialog trees

### Modding Support
- Export quest templates
- Import community-created quests
- Quest sharing format
- Compatibility checking

## Dependencies and Requirements

### Software Dependencies
- PySide6 (Qt6 bindings)
- Existing Tirganach library
- Python 3.8+

### Data Dependencies
- Access to `quests` table
- Access to `localisation` table
- Access to `advanced_descriptions` table
- Write access to CFF files

### Hardware Requirements
- Sufficient RAM for large quest hierarchies
- Display resolution for complex dialog trees
- Standard development environment

## Risk Assessment

### Technical Risks
- **Data Corruption**: Invalid quest modifications could break CFF files
- **Performance**: Large quest hierarchies may impact UI responsiveness
- **Compatibility**: Changes must maintain backward compatibility

### Mitigation Strategies
- Comprehensive validation before saving
- Backup original data before modifications
- Incremental saving with rollback capability
- Extensive testing with existing CFF files

## Success Metrics

### Functional Metrics
- All quest creation operations work correctly
- Dialog branching displays properly
- Save/load operations preserve data integrity
- Integration with main editor is seamless

### User Experience Metrics
- Intuitive interface for quest creation
- Efficient workflow for complex quest hierarchies
- Clear visual feedback for all operations
- Comprehensive error messages and validation

### Performance Metrics
- UI remains responsive with large quest trees
- Save operations complete within reasonable time
- Memory usage remains within acceptable limits

## Timeline and Milestones

### Phase 1: Core Implementation (Current)
- ✅ Quest structure analysis
- ✅ Basic tree editor
- ✅ Dialog branching design
- 🔄 Complete data models and widgets

### Phase 2: Advanced Features
- Quest creation wizards
- Full dialog editing
- Save/load functionality
- Validation systems

### Phase 3: Polish and Testing
- UI/UX improvements
- Performance optimization
- Comprehensive testing
- Documentation

### Phase 4: Integration and Release
- Main editor integration
- User documentation
- Modding community feedback
- Final release

## Conclusion

This quest editor enhancement represents a significant upgrade to the SpellForce modding toolkit, providing modders with powerful tools for creating complex, branching quest systems. The hierarchical quest tree and dialog branching capabilities will enable rich, interactive storytelling experiences in SpellForce mods.

The modular design ensures maintainability and extensibility, allowing for future enhancements while maintaining compatibility with the existing CFF editor architecture.

---

**Document Version**: 1.0
**Last Updated**: Current Session
**Next Review**: After Phase 1 completion