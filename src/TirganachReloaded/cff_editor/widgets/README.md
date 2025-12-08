# Enhanced Quest Creation System

A comprehensive quest creation suite for SpellForce with visual editing, CFF integration, and validation capabilities.

## Features

### 🎯 Core Components

1. **Enhanced Quest Creation Wizard**
   - Multi-step quest creation process
   - Direct GameData.cff integration
   - Automatic quest ID generation (9000-9999 range)
   - Quest hierarchy management (parent/child relationships)

2. **Visual Dialogue Editor**
   - Drag-and-drop dialogue tree builder
   - Real-time dialogue flow visualization
   - NPC/Player assignment
   - Connection management with arrows
   - Auto-arrange layout options

3. **Reward Builder with Item Browser**
   - CFF item database integration
   - Visual reward configuration
   - Balance checking and validation
   - Quest templates (Starter, Medium, Main, Epic)
   - Item search and filtering

4. **Quest Validator**
   - Comprehensive validation system
   - Quest ID conflict checking
   - Dialogue flow validation
   - Reward balance analysis
   - CFF compatibility checking
   - Lua syntax validation

5. **Data Integration**
   - Direct GameData.cff reading/writing
   - Lua script generation
   - Quest data enhancement
   - Conflict resolution

## File Structure

```
src/TirganachReloaded/cff_editor/widgets/
├── enhanced_quest_creation_wizard.py  # Main wizard controller
├── dialogue_editor.py                  # Visual dialogue tree editor
├── reward_builder.py                  # Reward builder with item browser
├── quest_validator.py                 # Comprehensive validation system
├── launch_enhanced_quest_creator.py  # Main launcher application
└── test_enhanced_quest_system.py    # Basic functionality tests
```

## Installation & Setup

### Prerequisites
```bash
# Install required Python packages
pip install PySide6 loguru
```

### File Organization
Ensure your project structure matches:
```
project_root/
├── src/
│   └── TirganachReloaded/
│       └── cff_editor/widgets/
├── OriginalGameFiles/
│   └── data/GameData.cff
└── ModdedGameFiles/
    └── lua/  (Generated scripts will go here)
```

## Usage

### 1. Launcher Application
```bash
# Run the main launcher
python launch_enhanced_quest_creator.py

# With debug logging
python launch_enhanced_quest_creator.py --debug
```

### 2. Test System
```bash
# Run basic functionality tests
python test_enhanced_quest_system.py
```

### 3. Component Usage
```python
# Import main wizard
from TirganachReloaded.cff_editor.widgets.enhanced_quest_creation_wizard import EnhancedQuestCreationWizard
from TirganachReloaded.cff_editor.data_model import CFFDataModel

# Initialize data model
data_model = CFFDataModel()
data_model.load_file("OriginalGameFiles/data/GameData.cff")

# Create wizard
wizard = EnhancedQuestCreationWizard(data_model, quest_data)
wizard.exec()
```

## Workflow

### 1. Quest Creation Process
1. **Quest Identity** - Set name, description, type
2. **Quest Hierarchy** - Configure parent/child relationships
3. **Location & NPC** - Set map location and quest giver
4. **Objectives** - Define quest objectives and requirements
5. **Dialogues** - Build dialogue trees with visual editor
6. **Rewards** - Configure rewards with balance checking
7. **Summary & Save** - Review and save to GameData.cff

### 2. Dialogue Editor Workflow
- Add NPC/Player dialogue nodes
- Drag to arrange nodes
- Double-click to edit text
- Connect nodes with visual arrows
- Auto-arrange for clean layout
- Real-time preview

### 3. Reward Builder Workflow
- Browse items from CFF database
- Set quest level for balance checking
- Choose template or configure manually
- Add items, XP, gold rewards
- Real-time balance validation
- Visual reward preview

## Quest Data Model

### EnhancedQuestData Structure
```python
@dataclass
class EnhancedQuestData:
    # Basic CFF data
    quest_id: int
    name: str
    description: str
    parent_id: int = 0
    order_index: int = 0
    
    # Enhanced data
    map_locations: List[MapLocation]
    dialogues: List[Dialogue]
    rewards: Optional[QuestReward]
    file_references: List[FileReference]
    relationships: List[QuestRelationship]
    
    # Metadata
    has_extended_dialogues: bool = False
    lua_files_count: int = 0
    total_lua_references: int = 0
```

### Validation Categories
- **General**: Quest ID, name, description validation
- **Dialogue**: Text length, speaker validation, flow checking
- **Rewards**: Balance checking, item validation
- **CFF**: Format compatibility, character encoding
- **Lua**: Syntax checking, reserved word validation

## Templates

### Quest Templates
- **Starter Quest**: 50 XP, 5G, 25S, 50C, 1-2 items
- **Medium Quest**: 200 XP, 20G, 50S, 2-3 items
- **Main Quest**: 1000 XP, 100G, 3-4 items
- **Epic Quest**: 5000 XP, 500G, 5+ items

### Balance System
- XP value: 1 XP = 1 value point
- Money value: 1 Gold = 100 value points
- Item value: Based on CFF item value field
- Recommended level: Total value ÷ 500

## Output Files

### Generated Files
1. **GameData.cff** (Updated)
   - New quest entries
   - Localization string IDs
   - Quest relationships

2. **Lua Scripts** (ModdedGameFiles/lua/)
   - `quest_{quest_id}.lua`
   - Complete state machine
   - Quest begin/end events
   - Reward integration

3. **Quest Cache** (Data/cache/)
   - Enhanced quest data
   - Dialogue trees
   - Validation results

## Error Handling

### Validation Levels
- **Error**: Critical issues preventing save
- **Warning**: Recommended fixes, but can proceed
- **Info**: Suggestions and optimizations

### Common Issues
1. **Quest ID Conflicts**: Use auto-generated IDs in 9000-9999 range
2. **Dialogue Flow**: Ensure NPC/Player alternation
3. **Reward Balance**: Check balance warnings and adjust
4. **CFF Compatibility**: Avoid special characters in names

## Integration Points

### With Darius Almanach
- Export quests from Almanach to creator
- Import created quests to Almanach for review
- Shared quest data format

### With Mod Tools
- Export quests as mod packages
- Dependency management
- Version control integration

### With Game
- Direct CFF file modification
- Lua script generation
- Quest chain management

## Development

### Adding New Features
1. Extend EnhancedQuestData model
2. Add validation rules to QuestValidator
3. Update UI components as needed
4. Add tests for new functionality

### Testing
```bash
# Run component tests
python test_enhanced_quest_system.py

# Test with GUI
python launch_enhanced_quest_creator.py --debug
```

## Troubleshooting

### Common Issues
1. **CFF File Not Found**: Ensure OriginalGameFiles/data/GameData.cff exists
2. **Import Errors**: Check Python path and package installation
3. **Validation Failures**: Review error messages and adjust quest data
4. **Save Failures**: Check file permissions and disk space

### Debug Mode
```bash
python launch_enhanced_quest_creator.py --debug
```
This enables detailed logging and error reporting.

## Future Enhancements

### Planned Features
1. **Advanced Dialogue Conditions**
   - Complex logic support
   - Variable integration
   - Flag-based triggers

2. **Quest Chain Builder**
   - Visual chain editor
   - Auto-dependency management
   - Progress tracking

3. **Mod Packaging System**
   - Export as installable mods
   - Dependency resolution
   - Version management

4. **Integration Testing**
   - Quest simulation
   - Game testing integration
   - Automated validation

## Contributing

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Add comprehensive docstrings
- Include unit tests for new features

### Submitting Changes
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request with description

## License

This enhanced quest creation system is part of the TirganachReloaded project and follows the same licensing terms.

---

**Ready to create amazing quests! 🎮✨**