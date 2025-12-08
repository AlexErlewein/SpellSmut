# Weapon Forge Test Script

## Overview

This script provides a comprehensive test environment for the Weapon Forge wizard with all the latest features and improvements.

## Features

### ✅ Latest Weapon Forge Integration
- Complete weapon properties inheritance system
- Professional sound system with audio preview
- Enhanced UI with dark theme styling
- CFF and JSON export options
- Comprehensive validation system

### 🔍 Dependency Checking
- **Pygame Detection**: Checks for audio preview capabilities
- **Tirganach Library**: Verifies CFF export functionality  
- **GameData.cff**: Locates game data files
- **Clear Feedback**: Shows what features are available

### 🧪 Test Modes

#### GUI Mode (Default)
```bash
python test_weapon_forge.py
```
- Full weapon forge wizard interface
- Professional dark theme styling
- Complete testing environment
- Mock parent window with data_model context

#### Non-GUI Mode (Component Testing)
```bash
python test_weapon_forge.py --no-gui
```
- Fast component initialization testing
- No GUI dependencies for automated testing
- Validates all core systems
- Quick verification of dependencies

## Usage Examples

### Basic Testing
```bash
# Run full GUI test
source .venv/bin/activate
cd src
python test_weapon_forge.py

# Run component-only test
python test_weapon_forge.py --no-gui
```

### What Gets Tested

#### ✅ Core Components
- **ID Manager**: Weapon ID allocation and validation
- **Data Model**: Icon loading and mapping system
- **Weapon Forge Wizard**: Complete wizard initialization

#### ✅ Feature Availability
- **Audio System**: Pygame integration for sound preview
- **CFF Export**: Tirganach library for direct game export
- **Icon System**: Data model integration for icon browsing
- **Game Data**: GameData.cff file detection and loading

#### ✅ UI Enhancements
- **Dark Theme**: Professional styling matching weapon forge
- **Error Handling**: Comprehensive error messages and recovery
- **Validation Feedback**: Clear guidance during weapon creation

## Test Output Examples

### Successful Component Test
```
🔧 Weapon Forge Test Runner (Enhanced)
==================================================
🔍 Checking dependencies...
   ✅ Pygame available for audio preview
   ✅ Tirganach library available for CFF export
   ⚠️  GameData.cff not found - some features may be limited

🔧 Running in non-GUI test mode
📁 Testing component initialization...
   ✅ ID Manager: 9982 weapon IDs available
   ✅ Data Model: 4258 icons loaded
   ✅ Weapon Forge: Wizard created successfully
✅ All components initialized successfully!
```

### Successful GUI Test
When you run the GUI mode, you'll get:
- Mock parent window with feature overview
- Full Weapon Forge wizard with all pages
- Complete weapon creation workflow
- Professional dark theme styling
- Real-time validation and feedback

## Integration with Latest Features

### 🎨 Dark Theme Support
The test script applies the same professional dark theme used in the weapon forge:
- `#2d2d2d` backgrounds for better readability
- High contrast white text
- Consistent styling across all widgets

### 🔊 Audio System Testing
If pygame is available, the test will show:
- Audio preview capabilities confirmation
- Volume and pitch control support
- Real-time sound testing features

### 📦 Export System Testing
If tirganach library is available:
- CFF export functionality verification
- Large weapon ID support testing
- Export format validation

### 🗡️ Complete Weapon Creation
The test provides full access to:
- **Mode Selection**: New/Edit/Duplicate with ID management
- **Basic Properties**: All 20 weapon types with smart matching
- **Combat Stats**: Complete damage and speed configuration
- **Requirements**: Attribute requirements and economic values
- **Visual & Audio**: Icon browser and sound selection
- **Review & Export**: Validation and multiple export formats

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'PySide6'"
```bash
# Activate virtual environment first
source .venv/bin/activate
python test_weapon_forge.py
```

#### "QWidget: Must construct a QApplication before a QWidget"
- Use `--no-gui` mode for component testing
- Ensure QApplication is created before GUI mode

#### GameData.cff not found
The test will show expected locations:
- `OriginalGameFiles/data/GameData.cff`
- `OriginalGameFiles/GameData.cff`
- `~/SpellForce Platinum Edition/data/GameData.cff`

### Feature Availability
- **⚠️ Warning**: Feature not available but will work with limitations
- **✅ Success**: Feature fully available for testing
- **❌ Error**: Critical issue preventing testing

## Development Notes

This test script integrates with all the weapon forge improvements from the progress document:

### Phase 1: Weapon Properties Inheritance ✅
- Complete property inheritance across all wizard pages
- Smart weapon type matching for all 20 types
- Material and attribute preservation

### Phase 3: Sound System Enhancement ✅  
- Professional audio preview with pygame
- Tabbed sound selection interface
- Volume and pitch controls

### Phase 4: Export System Fixes ✅
- Large weapon ID support (up to 4.29 billion)
- Comprehensive error handling and validation
- Multiple export formats (CFF + JSON)

### Phase 5: UI Polish & UX ✅
- Professional dark theme styling
- Enhanced error messages and feedback
- Improved validation and user guidance

## Quick Start

1. **Activate Environment**: `source .venv/bin/activate`
2. **Navigate**: `cd src`  
3. **Run Test**: `python test_weapon_forge.py` or `python test_weapon_forge.py --no-gui`
4. **Follow Output**: Check dependency status and test results

The test script provides a complete validation environment for the weapon forge system with all latest improvements and professional UI enhancements.