# Quest Editor Component

## Overview
Interactive quest creation and editing system with hierarchical quest trees and branching dialog systems, transforming the current read-only quest viewer into a full-featured quest design tool.

## Current Status: 🔄 IN PROGRESS (Phase 1)

### ✅ Completed (Phase 1)
- **Quest Structure Analysis**: Hierarchical relationships via parent_quest_id and sub_quests
- **Data Model Design**: QuestNode and DialogNode classes with serialization support
- **Quest Tree Editor**: Interactive tree widget with drag-drop reordering and CRUD operations
- **Dialog Branching System**: Conversation tree visualization with branching logic

### 🔄 In Progress
- Complete data models and validation logic
- Build interactive quest tree widget
- Implement dialog editor widget
- Add quest creation wizards

### 📋 Planned (Phase 2-4)
- Quest creation wizards and templates
- Full dialog editing with conditional branching
- Save/load quest hierarchies
- Validation for quest logic and dependencies

## Key Features Planned

### Quest Tree Editor
- **Hierarchical Display**: Parent-child quest relationships
- **Interactive Editing**: Add, edit, delete, reorder quests
- **Drag-Drop Support**: Visual reparenting and reordering
- **Context Menus**: Right-click operations for all quest actions

### Dialog Branching Editor
- **Conversation Trees**: Visual dialog flow representation
- **Branching Logic**: Multiple response options and outcomes
- **NPC/Player Distinction**: Clear visual separation of speakers
- **Validation**: Dialog flow consistency checking

### Quest Creation Tools
- **Templates**: Pre-built quest structures for common patterns
- **Wizards**: Guided quest creation process
- **Validation**: Real-time checking of quest logic and dependencies

## Technical Architecture

### Data Models
- **QuestNode**: Hierarchical quest representation with serialization
- **DialogNode**: Conversation tree node with branching support
- **QuestHierarchy**: Complete quest structure with relationships

### Widget Components
- **QuestTreeEditorWidget**: Interactive hierarchical quest editor
- **DialogBranchingEditorWidget**: Conversation tree editor
- **Enhanced QuestDetailsWidget**: Unified quest information display

### Integration Points
- **Main Window**: Dedicated "Quest Editor" tab
- **Data Model**: Extended CFFDataModel with quest-specific methods
- **File Operations**: Save quest changes to CFF files

## Data Structure Analysis

### Quest Relationships
- **Parent-Child**: Via `parent_quest_id` and `sub_quests` fields
- **Ordering**: `order_index` for sort order within hierarchy
- **Localization**: Names from `localisation` table, descriptions from `advanced_descriptions`

### Dialog Structure
- **Naming Convention**: Sequential dialogs (character001, character002, etc.)
- **Conversation Flow**: Alternating NPC lines and player choices
- **Player Choices**: Marked with "PC" suffix (ashawe001PC)
- **Branching**: Each choice can lead to different NPC responses

## Implementation Plan

### Phase 1: Core Implementation (Current)
- ✅ Quest structure analysis
- ✅ Basic tree editor design
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
- Final release

## Dependencies
- **PySide6**: GUI framework for tree and dialog editors
- **Tirganach**: CFF data access for quest tables
- **Python 3.8+**: Base runtime requirements

## Success Metrics
- **Quest Creation**: All quest creation operations work correctly
- **Dialog Branching**: Complex conversation trees display properly
- **Save/Load**: Quest hierarchies preserve data integrity
- **Integration**: Seamless integration with main editor
- **Performance**: UI remains responsive with large quest trees

## Files Consolidated From
- `Internal/QUEST_EDITOR_PLAN.md` (summarized from 370-line detailed plan)