# Quest Viewer Integration Documentation

**Date:** November 25, 2025
**Version:** 1.0
**Status:** ✅ **COMPLETED** - Quest viewing functionality fully integrated

---

## 🎯 **Overview**

The Quest Viewer Integration provides a comprehensive solution for viewing existing quests from the SpellForce CFF data in an enhanced quest editor interface. This bridges the gap between the traditional quest browser and the advanced quest editing capabilities, allowing users to examine, understand, and potentially modify existing quests.

---

## 🏗️ **Architecture**

### **Core Components**

1. **QuestViewerIntegration** (`quest_viewer_integration.py`)
   - Main integration manager between CFF data and enhanced quest editor
   - Processes raw quest data into editor-compatible format
   - Handles read-only and editing mode switching

2. **QuestDataProcessor** (`quest_viewer_integration.py`)
   - Converts CFF quest elements into enhanced quest editor format
   - Extracts quest giver, requirements, objectives, rewards, and dialogues
   - Builds dialogue tree structures for visualization

3. **QuestViewerWidget** (`quest_viewer_integration.py`)
   - Complete UI widget with integrated enhanced quest editor
   - Provides controls for viewing, editing, and exporting quest data
   - Handles mode switching between view and edit states

4. **Main Window Integration** (`main_window.py`)
   - Added quest viewer panel to the main application layout
   - Integrated with existing quest hierarchy tree selection
   - Added menu items and keyboard shortcuts for easy access

### **Data Flow**

```
CFF Data Model → Quest Hierarchy Tree → Element Selection → Quest Viewer Integration → Enhanced Quest Editor
     ↓                    ↓                      ↓                           ↓
Raw Quest Elements → User Selection → Data Processing → Visual Display & Editing
```

---

## 🚀 **Features**

### **1. Comprehensive Quest Viewing**
- **Complete Quest Information**: ID, name, description, type, difficulty, priority, status
- **Quest Giver Details**: Name, location, NPC information
- **Requirements**: Level requirements, item requirements, quest prerequisites
- **Objectives**: Complete quest objectives with status tracking
- **Rewards**: Experience, gold, items, faction reputation, skill points
- **Map Locations**: All quest-related locations with platform codes
- **Dialogues**: Full dialogue tree with nodes, choices, conditions, and actions
- **Variables & Flags**: Quest-specific variables and global flags

### **2. Enhanced Dialogue Visualization**
- **Interactive Dialogue Tree**: Visual representation of dialogue flow
- **Node Types**: NPC, player, response, start, end nodes with distinct icons
- **Conditions & Actions**: Display of dialogue logic and quest triggers
- **Choice Navigation**: Visual paths through dialogue options
- **Search & Navigation**: Jump to specific nodes or dialogue elements

### **3. Mode Switching**
- **Read-Only Mode**: View quests without modification (default)
- **Editing Mode**: Modify quest data (when enabled)
- **Export Capabilities**: Export quest data in various formats
- **Validation**: Real-time validation of quest structure and data

### **4. Integration with Existing System**
- **Sidebar Selection**: Click quests in the hierarchy tree to view them
- **Automatic Loading**: Quest data loads automatically when selected
- **Seamless Switching**: Toggle between quest details and quest viewer
- **Keyboard Shortcuts**: Quick access via Ctrl+Shift+Q

---

## 📋 **User Guide**

### **Accessing the Quest Viewer**

#### **Method 1: View Menu**
1. Open the main CFF Editor application
2. Go to **View → Quest Viewer** (Ctrl+Shift+Q)
3. The quest viewer panel will appear, replacing the element table
4. Select a quest from the category tree sidebar
5. The quest will automatically load into the viewer

#### **Method 2: Tools Menu**
1. Go to **Tools → Quest Viewer** (Ctrl+Q, V)
2. This toggles the quest viewer panel visibility

#### **Method 3: Automatic Integration**
1. Ensure quest viewer is visible (Method 1)
2. Click on any quest in the quest hierarchy tree
3. The quest automatically loads into the enhanced editor

### **Understanding the Interface**

#### **Header Controls**
- **Enable/Disable Editing**: Toggle between view-only and editing modes
- **Export Quest**: Save quest data in various formats
- **Refresh**: Reload quest data from the CFF model

#### **Quest Information Tabs**
1. **📋 Basic Info**: Quest ID, name, description, type, difficulty, priority
2. **🔗 Integration**: Quest dependencies, connections, variables
3. **🎁 Rewards**: Experience, gold, items, reputation rewards
4. **🔧 Variables**: Quest variables, flags, and global state
5. **✅ Validation**: Quest structure and consistency validation

#### **Dialogue Editor Tabs**
1. **💬 Enhanced Dialogue**: Visual dialogue tree editor with node management
2. **📝 Text Mode**: Text-based dialogue overview
3. **🔍 Search & Navigation**: Advanced search and navigation tools

### **Working with Quest Data**

#### **Viewing Mode (Default)**
- All fields are read-only
- Cannot modify quest structure
- Can export and analyze quest data
- Full access to validation and testing tools

#### **Editing Mode**
- Click "Enable Editing" to activate editing mode
- All fields become editable
- Changes are tracked in the editor
- Save functionality becomes available
- **Note**: Changes exist only in the editor session (not saved to CFF)

#### **Exporting Quest Data**
1. Click the "Export Quest" button
2. Choose export format:
   - **Summary**: Human-readable text summary
   - **JSON**: Complete quest data in JSON format
3. Copy to clipboard or save to file

---

## 🔧 **Technical Details**

### **Quest Data Processing**

The `QuestDataProcessor` class converts CFF quest elements into the enhanced quest editor format:

```python
# Basic quest information
quest_data = {
    'quest_id': quest_element.quest_id,
    'name': localized_name,
    'description': localized_description,
    'quest_type': determined_type,
    'difficulty': determined_difficulty,
    # ... additional fields
}

# Dialogue tree structure
dialogue_data = {
    'nodes': {
        'node_id': {
            'node_type': 'npc',
            'speaker': 'Quest Giver',
            'text': 'Dialogue text',
            'conditions': [...],
            'actions': [...],
            'choices': [...]
        }
    },
    'start_node_id': 'node_id'
}
```

### **Integration Points**

#### **Element Selection Handler**
```python
def on_element_selected(self, category, element_index):
    if category == "quests":
        # Update quest details (existing functionality)
        self.quest_details.on_element_selected(category, element_index)

        # Load quest into enhanced viewer
        if self.quest_viewer_integration and element_index >= 0:
            quests = self.data_model.get_elements("quests")
            if element_index < len(quests):
                quest = quests[element_index]
                quest_id = getattr(quest, 'quest_id', None)
                if quest_id is not None:
                    success = self.quest_viewer_integration.load_quest_for_viewing(quest_id)
```

#### **Mode Management**
```python
def _set_read_only_mode(self, read_only: bool):
    # Disable/enable editing controls
    self.save_quest_btn.setEnabled(not read_only)
    self.validate_btn.setEnabled(not read_only)
    self.test_btn.setEnabled(not read_only)

    # Keep view-only controls enabled
    self.preview_btn.setEnabled(True)
    self.export_lua_btn.setEnabled(True)
```

### **Error Handling**

The system includes comprehensive error handling:
- **Import Errors**: Graceful fallback when components are unavailable
- **Data Processing Errors**: Detailed logging and user feedback
- **UI Integration Errors**: Safe handling of missing widgets or data
- **Validation Errors**: Clear indication of data issues and suggestions

---

## 🎮 **Usage Examples**

### **Example 1: Viewing a Simple Quest**
1. Launch the CFF Editor
2. Go to **View → Quest Viewer**
3. In the category tree, select "quests"
4. Click on "The First Quest"
5. View the complete quest information in the enhanced editor
6. Navigate through dialogue nodes using the visual tree
7. Export the quest as a summary for reference

### **Example 2: Analyzing Quest Structure**
1. Load the quest viewer as above
2. Select a complex quest with multiple objectives
3. Switch to the **Validation** tab
4. Check for any structural issues or warnings
5. Use the **Preview** function to see the dialogue flow
6. Export as JSON for detailed analysis

### **Example 3: Export Quest Data**
1. Load a quest into the viewer
2. Click "Export Quest"
3. Choose "Summary" format for human-readable overview
4. Review the exported quest information
5. Copy to clipboard for documentation or sharing

---

## 🧪 **Testing**

### **Running the Test Script**

```bash
# Navigate to the quest-wizard directory
cd /path/to/quest-wizard

# Run the test script
python test_quest_viewer.py
```

The test script provides:
- **Sample Quest Data**: Three sample quests with varying complexity
- **Integration Testing**: Tests the data processing pipeline
- **UI Testing**: Verifies the quest viewer functionality
- **Error Handling**: Tests error conditions and recovery

### **Manual Testing Checklist**

#### **Basic Functionality**
- [ ] Quest viewer opens correctly from menu
- [ ] Quests load when selected from hierarchy tree
- [ ] All quest information displays correctly
- [ ] Dialogue tree renders properly
- [ ] Mode switching works between view and edit

#### **Data Integration**
- [ ] Quest ID and basic information match CFF data
- [ ] Localized text displays correctly
- [ ] Quest giver information is accurate
- [ ] Requirements and objectives are complete
- [ ] Rewards data is correctly processed

#### **UI Interaction**
- [ ] All tabs load and display content
- [ ] Export functionality works
- [ ] Validation reports are generated
- [ ] Keyboard shortcuts work as expected
- [ ] Error messages display appropriately

---

## 🔄 **Future Enhancements**

### **Potential Improvements**

1. **Direct CFF Integration**
   - Save modified quests back to CFF format
   - Real-time synchronization with CFF data
   - Automatic validation against CFF constraints

2. **Advanced Editing Features**
   - Batch quest editing operations
   - Quest template application
   - Dialogue import/export functionality

3. **Enhanced Visualization**
   - Graphical quest flow diagrams
   - Interactive map integration
   - Timeline-based quest progression

4. **Collaboration Features**
   - Quest sharing and import/export
   - Version control integration
   - Team collaboration tools

### **Integration with Other Components**

The quest viewer is designed to integrate with:
- **NPC Browser**: Link quest givers to NPC database
- **Multi-Language Support**: View quests in different languages
- **Testing Mode**: Test quest logic and dialogue flow
- **External Resources**: Import quest templates and data

---

## 📝 **Conclusion**

The Quest Viewer Integration successfully bridges the gap between existing SpellForce quest data and modern quest editing capabilities. It provides:

- **✅ Complete Quest Visualization**: All quest aspects displayed in an intuitive interface
- **✅ Seamless Integration**: Works directly with existing CFF data and quest hierarchy
- **✅ Advanced Editing Capabilities**: When enabled, full quest modification functionality
- **✅ Export and Analysis**: Multiple export formats for documentation and sharing
- **✅ Robust Architecture**: Clean separation of concerns with comprehensive error handling

The system transforms the traditional quest browser into a powerful quest analysis and editing tool while maintaining compatibility with the existing CFF Editor workflow.

---

**Status:** ✅ **FULLY IMPLEMENTED AND INTEGRATED**