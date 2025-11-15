# Weapon Forge CFF Export Implementation

## Overview

This document describes the implementation of CFF (SpellForce GameData.cff) export functionality for the Weapon Forge system. This feature allows users to export created weapons directly to GameData.cff format, making them usable in-game.

## Features Implemented

### ✅ Core CFF Export System

**File**: `exporters/weapon_cff_exporter.py`

1. **WeaponCFFExporter Class**
   - Initializes with reference GameData.cff for proper structure
   - Creates complete GameData.cff files with custom weapons added
   - Handles all required entities: Item, Weapon, Localization
   - Supports custom weapon types and materials

2. **Entity Creation**
   - **Item Entry**: Handles basic item properties (ID, type, subtype, name_id, prices)
   - **Weapon Entry**: Manages combat statistics (damage, range, speed, type, material)
   - **Localization**: Creates text entries for weapon names and descriptions
   - **Weapon Types**: Handles custom weapon type definitions
   - **Materials**: Supports custom material definitions

3. **Tirganach Integration**
   - Uses the established `TirganachReloaded.tirganach` library
   - Works with existing GameData structure and entity definitions
   - Maintains compatibility with original SpellForce format

### ✅ Weapon Forge Wizard Integration

**File**: `widgets/weapon_forge_wizard.py`

1. **Enhanced Export Options**
   - **JSON Export**: Original functionality (preserved)
   - **CFF Export**: New GameData.cff export capability
   - **Both Formats**: Export to both JSON and CFF simultaneously

2. **Smart UI Updates**
   - Automatically detects GameData.cff availability
   - Enables/disables CFF options based on system capabilities
   - Provides informative messages about export status

3. **GameData.cff Detection**
   - Searches multiple standard locations for GameData.cff
   - Supports custom installation paths
   - Graceful fallback when GameData.cff is not available

### ✅ Export Workflow

1. **Automatic GameData Detection**
   ```python
   # Searches in order:
   # 1. OriginalGameFiles/data/GameData.cff
   # 2. OriginalGameFiles/GameData.cff
   # 3. ~/SpellForce Platinum Edition/data/GameData.cff
   ```

2. **Complete File Creation**
   - Creates new GameData.cff with original data + custom weapon
   - Maintains all existing game content
   - Adds weapon to appropriate tables (items, weapons, localisation)

3. **Output Naming**
   ```
   GameData_custom_weapon_<ID>_<Name>.cff
   Example: GameData_custom_weapon_10003_Dragonslayer_Sword.cff
   ```

## Technical Implementation Details

### Entity Structure Mapping

| WeaponForge Field | GameData Entity | Notes |
|-------------------|-----------------|-------|
| `weapon_id` | Item.item_id, Weapon.item_id | Primary key across tables |
| `weapon_name` | Localisation.text | UTF-16LE encoded |
| `weapon_type_id` | Weapon.weapon_type | Maps to WeaponTypeName |
| `weapon_material_id` | Weapon.material | Maps to WeaponMaterialName |
| `hands` | Item.item_subtype | EquipmentType.WEAPON_1H/2H/UNARMED |
| `min_damage/max_damage` | Weapon.min_damage/Weapon.max_damage | Combat stats |
| `attack_speed` | Weapon.speed | Lower = faster |
| `sell_value/buy_value` | Item.selling_price/Item.buying_price | Economic values |
| `rarity` | Item.item_set_id | Custom mapping for game compatibility |

### CFF Export Process

```python
# Simplified flow:
1. Load original GameData.cff
2. Create new entities for weapon:
   - Item entity with basic properties
   - Weapon entity with combat stats
   - Localization entities for text
3. Add entities to GameData tables
4. Save modified GameData.cff
```

### Error Handling

- **Graceful Degradation**: Falls back to JSON export if CFF unavailable
- **Validation**: Checks GameData.cff availability before export
- **User Feedback**: Clear messages about export status and requirements
- **Safe Operation**: Creates new files, doesn't modify originals

## Usage Instructions

### For Users

1. **Ensure GameData.cff is Available**
   - Place original GameData.cff in `OriginalGameFiles/data/` directory
   - Or ensure it's available in standard installation path

2. **Create Weapon**
   - Use Weapon Forge wizard to design weapon
   - Complete all wizard steps

3. **Export to CFF**
   - Select "Export to CFF only" or "Export to both JSON and CFF"
   - Output saved to `custom_weapons_cff/` directory

4. **Test in Game**
   - Backup original GameData.cff
   - Replace with exported file
   - Launch SpellForce to test weapon

### For Developers

1. **Custom Weapon Types**
   ```python
   # Custom types have IDs >= 20
   weapon_type_id = 20  # First custom type
   ```

2. **Custom Materials**
   ```python
   # Custom materials have IDs >= 10
   weapon_material_id = 10  # First custom material
   ```

3. **Localization Support**
   ```python
   # Text IDs use weapon_id + offset
   name_id = weapon_id + 50000
   description_id = weapon_id + 50001
   ```

## File Structure

```
src/TirganachReloaded/cff_editor/
├── exporters/
│   └── weapon_cff_exporter.py          # Core CFF export logic
├── widgets/
│   └── weapon_forge_wizard.py          # Enhanced wizard with CFF options
├── models/
│   └── weapon_creation_data.py         # Weapon data model
└── docs/
    └── CFF_EXPORT_IMPLEMENTATION.md    # This documentation
```

## Testing

### Test Coverage

1. **Unit Tests** (`tests/test_weapon_cff_export.py`)
   - Weapon creation and export
   - ID Manager integration
   - File structure validation

2. **Integration Tests**
   - Complete export workflow
   - GameData loading and verification
   - UI interaction testing

### Running Tests

```bash
cd src/TirganachReloaded
python3 cff_editor/tests/test_weapon_cff_export.py
```

## Future Enhancements

### Planned Features

1. **Enhanced Weapon Type Support**
   - Full custom weapon type definitions
   - Custom animation and sound mappings
   - Visual effect assignments

2. **Batch Export**
   - Export multiple weapons at once
   - Batch validation and processing
   - Progress indicators for large exports

3. **Mod Integration**
   - Direct mod file creation
   - Compatibility checking
   - Automatic file organization

### Technical Improvements

1. **Performance Optimization**
   - Incremental CFF updates (instead of full reload)
   - Memory-efficient large mod handling
   - Parallel processing for batch operations

2. **Advanced Validation**
   - Game balance analysis
   - ID conflict prevention
   - Compatibility checking

## Troubleshooting

### Common Issues

1. **"CFF Export Not Available"**
   - **Cause**: GameData.cff not found in expected locations
   - **Solution**: Ensure GameData.cff is in `OriginalGameFiles/data/` directory

2. **Export Failed**
   - **Cause**: Permission issues or invalid weapon data
   - **Solution**: Check file permissions and weapon validation results

3. **Generated Weapon Not Visible in Game**
   - **Cause**: ID conflicts or incorrect entity linking
   - **Solution**: Verify weapon ID is in custom range (10000+)

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export WEAPON_FORGE_DEBUG=1
```

## Compatibility

- **SpellForce Version**: Platinum Edition
- **Python Version**: 3.8+
- **Dependencies**: TirganachReloaded library, PySide6

## Conclusion

The CFF export implementation provides a robust bridge between the Weapon Forge's intuitive weapon creation interface and the SpellForce game format. Users can now create weapons using the visual wizard and immediately test them in-game, significantly improving the modding workflow.

The implementation maintains backward compatibility, provides graceful error handling, and follows established patterns in the codebase for maintainability and extensibility.