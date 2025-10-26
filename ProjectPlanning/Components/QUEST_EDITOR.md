# Quest Editor Component

## Overview

The Quest Editor is an interactive system for creating and managing quests. It transforms the existing read-only viewer into a full-featured design tool, enabling hierarchical quest trees and branching dialog systems.

## Current Status: 🔄 IN PROGRESS (Phase 2)

### Completed Milestones
- ✅ **Quest Structure Analysis**: Mapped hierarchical relationships using `parent_quest_id` and `sub_quests`.
- ✅ **Initial Data Model**: Designed `QuestNode` and `DialogNode` classes with serialization support.
- ✅ **UI/UX Design**: Prototyped interactive tree widgets and conversation flow visualizations.
- ✅ **Quest Tree Implementation**: Built interactive quest tree widget with drag-drop functionality.
- ✅ **Dialog Editor Integration**: Implemented dialog editor widget with branching visualization and language filtering.
- ✅ **Data Model Enhancement**: Enhanced `QuestNode` to include `dialog_nodes` property for better quest-dialog association.

### Roadmap
- 🔄 **Phase 1 (Completed)**:
  - ✅ Complete data models with validation logic.
  - ✅ Build interactive quest tree widget with drag-drop functionality.
  - ✅ Implement dialog editor widget with branching visualization.
- 🔄 **Phase 2 (In Progress)**:
  - Implement language filtering for dialog entries to show only the selected language.
  - Develop quest creation wizards and templates.
  - Implement full dialog editing with conditional branching.
  - Add save/load functionality for quest hierarchies.
- 📋 **Phase 3**:
  - Introduce robust validation for quest logic and dependencies.
  - Optimize performance for large quest trees.
  - Conduct comprehensive testing and bug fixing.
- 📋 **Phase 4**:
  - Integrate the editor into the main application.
  - Finalize user documentation and release.

## Key Features

### 1. Visual Quest Tree Editor
- **Hierarchical Management**: Visually organize quests in parent-child relationships.
- **Intuitive Editing**: Add, edit, delete, and reorder quests with drag-drop and context menus.
- **Clear Visualization**: At-a-glance understanding of complex quest chains.

### 2. Branching Dialog Editor
- **Conversation Flow**: Design complex dialogs with a node-based graphical editor.
- **Conditional Logic**: Implement branching narratives based on player choices and game state.
- **Role Distinction**: Clearly separate NPC and player dialog for better readability.

### 3. Smart Creation Tools
- **Templates & Wizards**: Accelerate quest creation with pre-built structures and guided processes.
- **Real-time Validation**: Instantly check for logical errors and dependency conflicts.

## Technical Architecture

### Data Models
- **QuestNode**: Represents a single quest in the hierarchy, managing its properties and relationships.
- **DialogNode**: Represents a point in a conversation, handling branching and speaker roles.
- **QuestHierarchy**: A container for the entire quest structure, managing serialization and validation.

### Key Algorithms
- **Graph Traversal**: Algorithms to validate quest and dialog graphs, detecting loops, dead ends, and orphaned nodes.
- **Topological Sort**: To ensure correct quest order and dependency resolution.

### Widget Components
- **QuestTreeEditorWidget**: The main interactive widget for editing the quest hierarchy.
- **DialogBranchingEditorWidget**: The graphical editor for conversation trees.
- **EnhancedQuestDetailsWidget**: A unified panel for displaying and editing quest information.

### Integration Points
- **Main Window**: A dedicated "Quest Editor" tab for easy access.
- **CFFDataModel**: Extended to include methods for reading and writing quest-specific data.
- **File Operations**: Save and load quest changes to and from CFF files.

## Data Structure Analysis

### Quest Relationships
- **Parent-Child**: Linked via `parent_quest_id` and `sub_quests` fields.
- **Ordering**: `order_index` determines the sequence of quests within a hierarchy.
- **Localization**: Names and descriptions are sourced from the `localisation` and `advanced_descriptions` tables.

### Dialog Structure
- **Flow Control**: Dialog sequences are managed through a naming convention (e.g., `character001`, `character002`).
- **Player Choices**: Player responses are identified by a "PC" suffix (e.g., `ashawe001PC`), enabling branching.

## Success Metrics

- **Functionality**: All quest creation, editing, and deletion operations are fully functional and stable.
- **Usability**: The UI is intuitive and allows for the creation of complex quest hierarchies with at least 5 levels of nesting.
- **Data Integrity**: Saving and loading quest hierarchies preserves all data and relationships without corruption.
- **Performance**: The UI remains responsive (<100ms latency) when handling quest trees with over 500 nodes.
- **Validation**: The system correctly identifies and reports at least 95% of common quest logic errors (e.g., broken links, circular dependencies).

## Files Consolidated From
- `Internal/QUEST_EDITOR_PLAN.md` (summarized from 370-line detailed plan)