# Spell Browser & Forge Integration

## Overview
This project now includes a comprehensive spell browser that allows users to browse all original game spells extracted from the GameData.cff file, with detailed level progression information and the ability to start the spell forge from any selected spell.

## Features

### Spell Browser
- Browse all 3,461+ original game spells from CFF extraction
- Search and filter spells by name, school, or type
- View detailed spell information including:
  - Basic properties (name, school, type, range, etc.)
  - Level progression data displayed in collapsible sections
  - Raw spell data for advanced users
- Multiple views: General info, Level progression, Raw data

### Spell Forge Integration
- Start the spell forge directly from the spell browser
- Edit existing spells or duplicate them to create new variants
- Create spells from templates or original game spells

### Multiple Spell Versions
- The browser correctly handles multiple versions of the same spell from the original game
- Each spell variant has a unique ID (original game spells are shifted to 1000+ range to avoid conflicts)
- Users can see different levels or variations of the same spell type

## Usage

### Launching the Spell Browser
```bash
cd src/MulandirsZauberschule
uv run spell_browser_launcher.py
```

### Main Launcher Features
1. **Browse Original Spells**: Opens the spell browser with all available spells
2. **Open Spell Forge**: Opens the spell creation wizard directly

### Spell Browser Features
1. **Search**: Type in the search box to filter spells by name, school, or type
2. **Categories**: Spells are grouped by magic school
3. **Details**: Select any spell to see detailed information in the right panel
4. **Level Progression**: View how spell parameters change across levels
5. **Spell Forge**: Double-click a spell or use "Open in Spell Forge" to edit it

### Spell Forge Features
- Create new spells from scratch
- Edit existing spells
- Duplicate and modify original game spells
- Visual feedback and validation

## Technical Implementation

### Data Loading
- Template spells are loaded from the spell templates system
- Original game spells are loaded from CFF extraction (3,455+ spells)
- All spells are combined and made available in the browser
- Spell IDs are managed to avoid conflicts (templates: 300+, CFF: 1000+)

### Level Progression Display
- Detailed level-by-level statistics for each spell
- Shows damage, mana cost, cooldown, cast time, and other parameters per level
- Collapsible sections make it easy to view progression data

### Multiple Spell Versions
- The original game contains multiple versions of certain spells (e.g., "Fireburst" appears many times with different parameters)
- Each version is preserved and given a unique ID to avoid conflicts
- This represents the actual game data structure accurately

## File Structure
```
src/MulandirsZauberschule/
├── spell_browser.py          # Main spell browser implementation
├── spell_browser_launcher.py # Main launcher for browser and forge
├── spell_forge_wizard.py     # Enhanced spell forge with browser integration
├── populate_spell_templates.py # Functions to load spells from CFF
└── custom_spells/           # Directory containing all spells
    ├── spells.json           # Combined spells file
    └── individual/           # Individual spell files
```

## Benefits
- Access to all original game spells for reference and modification
- Easy creation of new spells based on original game mechanics
- Detailed understanding of spell progression and balance
- Preservation of original game spell data integrity