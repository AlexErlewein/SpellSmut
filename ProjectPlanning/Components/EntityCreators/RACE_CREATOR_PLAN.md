# Race Creation System Plan
## 👁️ The Race Creator (Completed!)

## Overview

The **Race Creation System** allows users to create entirely new playable races for SpellForce Platinum Edition with comprehensive unit and building definitions. The system includes features for designing custom units, buildings, and managing all aspects of a new race through an intuitive wizard interface.

**Status**: ✅ COMPLETE  
**Priority**: High  
**Dependencies**: ID Management System

## Key Features

### 1. 7-Phase Wizard Interface
- **Mode Selection**: Create new race, edit existing, or use template
- **Basic Properties**: Race name, type, visual theme, and description
- **Stats & Scaling**: Equipment scaling (100-180%) and shadow size (0.8-2.0)
- **Units Creation**: Design 7+ required unit types (worker, fighter, ranged, mage, siege, titan, swarm)
- **Buildings Creation**: Design 8+ required building types (HQ, resource, barracks, etc.)
- **Audio Visual Assets**: Link 3D models, textures, and sound assets
- **Review & Export**: Validate and export race configuration

### 2. Comprehensive Unit Design
**Base Stats**:
- Strength, Dexterity, Intelligence
- Physical and Magic Resistance
- Walk/Run Speed

**Combat Stats**:
- Health and Mana with regeneration rates
- Armor and damage values (min/max)
- Damage types (Normal, Piercing, Fire, Ice, Earth, Air)

**Appearance**:
- 3D mesh and texture assignments
- Shadow size and scale factors
- Animation library integration

### 3. Building Configuration
- **Required Types**: HQ, Resource depot, Barracks, Mage tower, Siege workshop, Titan forge, Swarm nest, Defense structures
- **Properties**: HP, build time, resource costs, visual assets
- **Production Links**: Connect buildings to the units they can produce

### 4. Integrated Validation System
- **Requirements Check**: Verify minimum required units and buildings
- **Balance Score**: Calculate race balance metrics
- **Data Validation**: Check stat ranges and ID conflicts
- **Asset Verification**: Confirm linked asset paths exist

### 5. ID Management Integration
- **Race ID Assignment**: Uses range 7-99 (7+ recommended since 1-6 are official races)
- **Unit ID Management**: Auto-assigns IDs starting from 5000+ to avoid conflicts
- **Building ID Management**: Auto-assigns IDs starting from 6000+ to avoid conflicts
- **Conflict Prevention**: Ensures unique IDs across all content types

## Implementation Details

### Data Model
- **RaceCreationData**: Complete race definition with all required components
- **UnitData**: Individual unit definitions with stats, appearance, and combat properties
- **BuildingData**: Building definitions with construction costs and properties

### Architecture
- **7-Phase QWizard Interface**: Guided creation process with tabbed unit design
- **Modular Page Design**: Each phase implemented as separate QWizardPage
- **Validation Pipeline**: Comprehensive validation before export
- **Export System**: Generates game-ready race configuration

## File Structure

```
src/TirganachReloaded/cff_editor/
├── widgets/race_creator_wizard.py    # Main wizard implementation
├── widgets/race_validation.py        # Validation system
├── models/race_creation_data.py      # Data model classes
```

## Menu Integration

The Race Creator is accessible from the main application:
- **Menu Location**: Tools → Race Creator
- **Status Tip**: "Create and edit custom races"
- **Implementation**: Integrated into MainWindow.show_race_creator()

## Known Limitations

1. **Asset Creation**: Does not create 3D models, textures, or sound files - only manages the configuration
2. **Advanced Scripting**: Does not generate complex Lua scripts for special race abilities
3. **Animation Libraries**: Requires manual creation of animation files for new races

## Future Enhancements

1. **Template System**: Pre-built race templates based on different archetypes
2. **Advanced Abilities**: Spell and ability creation for racial powers
3. **Asset Generation**: Integration with 3D asset generation tools
4. **Balance Calculator**: More sophisticated race balance metrics

## Dependencies

- **ID Management System**: For unique race ID allocation
- **PySide6**: For GUI implementation
- **GameData.cff Structure**: Understanding of race, unit, and building data structures

## Testing Status

✅ **Fully Implemented and Tested**
- UI navigation works correctly
- Data validation functions properly
- ID management integration verified
- Menu integration confirmed