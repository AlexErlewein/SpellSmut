# NPC Browser Integration Guide

**Status**: ✅ IMPLEMENTED  
**Date**: November 16, 2025  
**Component**: `npc_browser_dialog.py`

## Overview

The NPC Browser is a searchable, filterable dialog for selecting NPCs in the Quest Editor. It provides a user-friendly interface for choosing quest givers, dialogue speakers, and involved NPCs from the game's NPC database.

## Features

### Core Functionality
- ✅ Load NPCs from GameData.cff
- ✅ Searchable by name, ID, faction, and map
- ✅ Filter by race, faction, and map/region
- ✅ Single and multi-selection modes
- ✅ Live preview pane with NPC details
- ✅ Keyboard navigation
- ✅ Background thread loading (non-blocking UI)
- ✅ Indexed fast searching

### Data Sources
- NPC Names table (`gd.npc_names`)
- Creatures table (`gd.creatures`)
- Creature Stats table (`gd.creature_stats`)
- Localisation table for NPC names

## Usage

### Basic Usage

```python
from TirganachReloaded.cff_editor.widgets.npc_browser_dialog import (
    NPCBrowserDialog, SelectionMode, choose_quest_giver, choose_involved_npcs
)

# Quick helper - Choose a quest giver
npc = choose_quest_giver(parent=self)
if npc:
    print(f"Selected: {npc.name} (ID: {npc.npc_id})")

# Quick helper - Choose multiple involved NPCs
npcs = choose_involved_npcs(parent=self)
for npc in npcs:
    print(f"Involved NPC: {npc.name}")
```

### Advanced Usage

```python
# Single selection mode (for quest giver)
dialog = NPCBrowserDialog(mode=SelectionMode.SINGLE, parent=self)
if dialog.exec():
    npc = dialog.get_selected_npc()
    if npc:
        quest_giver_id = npc.npc_id
        quest_giver_name = npc.name
        # Use in quest editor...

# Multi-selection mode (for involved NPCs)
dialog = NPCBrowserDialog(mode=SelectionMode.MULTI, parent=self)
if dialog.exec():
    npcs = dialog.get_selected_npcs()
    npc_ids = dialog.get_selected_npc_ids()
    # Use in quest metadata...
```

## Integration Points

### 1. Quest Editor - Quest Giver Selection

In `unified_quest_editor.py`:

```python
def _create_properties_tab(self):
    """Add NPC chooser to properties tab"""
    
    # Quest Giver section
    giver_layout = QHBoxLayout()
    self.quest_giver_id = QSpinBox()
    giver_layout.addWidget(QLabel("Quest Giver ID:"))
    giver_layout.addWidget(self.quest_giver_id)
    
    # Add browse button
    browse_btn = QPushButton("Browse NPCs...")
    browse_btn.clicked.connect(self._browse_quest_giver)
    giver_layout.addWidget(browse_btn)
    
    # Display selected NPC name
    self.quest_giver_name = QLabel("(Not selected)")
    giver_layout.addWidget(self.quest_giver_name)

def _browse_quest_giver(self):
    """Open NPC browser for quest giver"""
    from npc_browser_dialog import choose_quest_giver
    
    npc = choose_quest_giver(parent=self)
    if npc:
        self.quest_giver_id.setValue(npc.npc_id)
        self.quest_giver_name.setText(npc.name)
```

### 2. Dialogue Editor - Speaker Selection

In `simple_dialogue_builder.py`:

```python
def _create_speaker_selector(self):
    """Add speaker selector to dialogue step editor"""
    
    layout = QHBoxLayout()
    
    # NPC ID input
    self.speaker_npc_id = QSpinBox()
    self.speaker_npc_id.setRange(0, 99999)
    layout.addWidget(QLabel("Speaker NPC:"))
    layout.addWidget(self.speaker_npc_id)
    
    # Browse button
    browse_btn = QPushButton("Browse...")
    browse_btn.clicked.connect(self._browse_speaker)
    layout.addWidget(browse_btn)
    
    # Display name
    self.speaker_name = QLabel("")
    layout.addWidget(self.speaker_name)
    
    return layout

def _browse_speaker(self):
    """Browse for dialogue speaker"""
    from npc_browser_dialog import NPCBrowserDialog, SelectionMode
    
    dialog = NPCBrowserDialog(mode=SelectionMode.SINGLE, parent=self)
    if dialog.exec():
        npc = dialog.get_selected_npc()
        if npc:
            self.speaker_npc_id.setValue(npc.npc_id)
            self.speaker_name.setText(f"({npc.name})")
            
            # Update current dialogue step
            if self.current_step:
                self.current_step.speaker = npc.name
                self.current_step.speaker_npc_id = npc.npc_id
```

### 3. Quest Metadata - Involved NPCs

```python
def _create_involved_npcs_section(self):
    """Section for selecting involved NPCs"""
    
    group = QGroupBox("Involved NPCs")
    layout = QVBoxLayout(group)
    
    # List of involved NPCs
    self.involved_npcs_list = QListWidget()
    layout.addWidget(self.involved_npcs_list)
    
    # Buttons
    btn_layout = QHBoxLayout()
    
    add_btn = QPushButton("Add NPCs...")
    add_btn.clicked.connect(self._add_involved_npcs)
    btn_layout.addWidget(add_btn)
    
    remove_btn = QPushButton("Remove Selected")
    remove_btn.clicked.connect(self._remove_involved_npc)
    btn_layout.addWidget(remove_btn)
    
    layout.addLayout(btn_layout)
    
    return group

def _add_involved_npcs(self):
    """Add involved NPCs via browser"""
    from npc_browser_dialog import choose_involved_npcs
    
    npcs = choose_involved_npcs(parent=self)
    for npc in npcs:
        item = QListWidgetItem(f"{npc.name} (ID: {npc.npc_id})")
        item.setData(Qt.UserRole, npc.npc_id)
        self.involved_npcs_list.addItem(item)
```

## NPC Data Structure

```python
@dataclass
class NPCData:
    """NPC data returned by browser"""
    npc_id: int
    name: str
    race: str = "Unknown"
    faction: str = "Unknown"
    level: int = 1
    stats_id: int = 0
    map_hint: str = ""  # Optional map/region info
    creature_type: str = "NPC"
```

## API Reference

### NPCBrowserDialog

```python
class NPCBrowserDialog(QDialog):
    """Main NPC browser dialog"""
    
    def __init__(self, mode: SelectionMode = SelectionMode.SINGLE, parent=None)
    
    # Public methods
    def get_selected_npc(self) -> Optional[NPCData]
    def get_selected_npcs(self) -> List[NPCData]
    def get_selected_npc_id(self) -> Optional[int]
    def get_selected_npc_ids(self) -> List[int]
    def get_selected_npc_name(self) -> Optional[str]
```

### Convenience Functions

```python
def choose_quest_giver(parent=None) -> Optional[NPCData]:
    """Quick helper to choose a quest giver NPC"""
    
def choose_involved_npcs(parent=None) -> List[NPCData]:
    """Quick helper to choose multiple involved NPCs"""
```

### SelectionMode Enum

```python
class SelectionMode(Enum):
    SINGLE = "single"  # For quest giver, speaker
    MULTI = "multi"    # For involved NPCs
```

## Testing

### Manual Testing

```bash
# Run standalone test
cd /Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard
python3 -m src.TirganachReloaded.cff_editor.widgets.npc_browser_dialog
```

### Integration Testing

1. Open Quest Editor
2. Navigate to Properties tab
3. Click "Browse NPCs..." button
4. Search/filter for NPC
5. Double-click or select and click "Select"
6. Verify NPC ID and name populate correctly

## Performance

- **Loading**: Background thread prevents UI blocking
- **Search**: Indexed searching for fast lookups
- **Filtering**: Real-time filtering with debouncing
- **Memory**: Loads all NPCs into memory (~1000-5000 NPCs typical)

## Error Handling

- **GameData.cff not found**: Shows warning dialog with path
- **No GameData module**: Gracefully disables browser
- **Empty NPC table**: Shows placeholder message
- **Load failure**: Logs error and shows empty table

## Future Enhancements

### Planned Features
- [ ] Portrait/icon display for NPCs
- [ ] Recent selections history
- [ ] Favorites/bookmarks
- [ ] Export selected NPCs to CSV
- [ ] Integration with map viewer (show NPC location)
- [ ] Custom NPC creation from browser
- [ ] Bulk NPC editing

### Nice-to-Have
- [ ] NPC relationship graph
- [ ] Dialogue preview for NPC
- [ ] Quest involvement tracking (which quests use this NPC)
- [ ] Localization support for multiple languages

## Known Limitations

1. **Map hints**: Currently not populated (requires additional data parsing)
2. **Faction**: Defaults to "Unknown" (requires game logic understanding)
3. **Portraits**: Not yet implemented (requires icon system integration)
4. **Object NPCs**: Gravestones, levers, etc. may not be included (needs research)

## Related Files

- **Implementation**: `src/TirganachReloaded/cff_editor/widgets/npc_browser_dialog.py`
- **Spec**: `ProjectPlanning/Components/QuestSystem/NPC_CHOOSER_BROWSER_SPEC.md`
- **Quest Editor**: `src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py`
- **Dialogue Builder**: `src/TirganachReloaded/cff_editor/widgets/simple_dialogue_builder.py`

## Changelog

### v1.0.0 - November 16, 2025
- ✅ Initial implementation
- ✅ Single and multi-select modes
- ✅ Search and filtering
- ✅ Background loading
- ✅ Preview pane
- ✅ Keyboard navigation
- ✅ GameData.cff integration

---

**Author**: SpellSmut Development Team  
**Status**: ✅ Ready for Integration
