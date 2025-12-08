# Graufurter Bürger Büro - NPC Creation Suite

**Graufurter Bürger Büro** (Graufurt Citizen's Office) is a standalone NPC browser and creation tool for SpellForce modding. It provides a comprehensive interface for creating, editing, and managing custom NPCs.

---

## 🎯 Features

### NPC Creation Wizard
- **Multi-step wizard** for easy NPC creation
- **Identity**: Name, title, description, type, class, level, faction
- **Base Stats**: Strength, stamina, agility, dexterity, intelligence, wisdom, charisma
- **Combat Stats**: Health, mana, damage, armor, resistances
- **Appearance**: Head model, race, gender, voice type
- **Equipment**: Weapon slots, armor slots, accessories
- **Behavior**: Movement patterns, spawn conditions, AI settings
- **Review & Export**: Preview and export to CFF format

### NPC Browser
- **Search & Filter**: Find NPCs by name, type, or class
- **Detailed View**: Inspect all NPC properties
- **Edit Existing**: Modify NPCs from game files
- **Duplicate**: Clone NPCs as templates
- **Delete Custom**: Remove custom NPCs

### Data Management
- **JSON Storage**: Custom NPCs saved to `npcs/custom_npcs.json`
- **CFF Export**: Export NPCs to GameData.cff binary format
- **CFF Import**: Load NPCs from custom CFF files
- **ID Management**: Automatic allocation of NPC IDs (40000-49999 range)

---

## 🚀 Usage

### Running the Application

```bash
# From the GraufurterBuergerBuero directory
python run_graufurter_buerger_buero.py

# Or directly
python graufurter_buerger_buero.py

# With debug logging
python graufurter_buerger_buero.py --debug

# Rebuild game data cache
python graufurter_buerger_buero.py --rebuild-cache
```

---

## 📁 File Structure

```
GraufurterBuergerBuero/
├── graufurter_buerger_buero.py    # Main application
├── run_graufurter_buerger_buero.py # Launcher script
├── npc_creator_wizard.py          # NPC creation wizard
├── enhanced_npc_browser.py        # NPC browser dialog
├── npc_creation_data.py           # NPC data models
├── npc_cff_exporter.py           # CFF export functionality
├── npc_loader.py                 # JSON persistence layer
├── id_manager.py                 # ID allocation system
├── npcs/                         # NPC data storage
│   └── custom_npcs.json         # Custom NPC database
└── README.md                     # This file
```

---

## 🎨 Interface Overview

### Main Window
- **Header**: Language selector, search field, action buttons
- **Left Panel**: NPC tree with categories (by type)
- **Right Panel**: Detailed NPC information
- **Status Bar**: Current file and operation status

### NPC Tree Categories
- **Hostile**: Enemy NPCs
- **Friendly**: Ally NPCs
- **Neutral**: Non-combat NPCs
- **Merchant**: Vendor NPCs
- **Quest**: Quest-related NPCs

---

## 🔧 Dependencies

### Required Modules
- `PySide6` - GUI framework
- `TirganachReloaded.cff_editor.logging_config` - Logging utilities
- `TirganachReloaded.tirganach.types` - Game data types

### Shared Components
- **IDManager**: Automatic ID allocation (40000-49999 for NPCs)
- **Language**: Multi-language support (German, English, French, Spanish, Italian)
- **GameData**: Access to game CFF files

---

## 📝 NPC Data Model

### Basic Identity
- **Name**: Display name
- **Title**: Optional title
- **Description**: Lore description
- **Type**: hostile, friendly, neutral, merchant, quest
- **Class**: warrior, mage, ranger, etc.
- **Level**: 1-200
- **Faction**: Alignment/group

### Base Stats (7 attributes)
- Strength
- Stamina
- Agility
- Dexterity
- Intelligence
- Wisdom
- Charisma

### Combat Stats (11 stats + resistances)
- Health, Mana
- Min/Max Damage
- Armor, Magic Resistance
- Attack Speed, Move Speed
- Critical Chance, Dodge Chance
- Elemental Resistances

### Equipment (7 slots)
- Main Hand, Off Hand
- Head, Chest, Legs, Feet
- Accessory

### Appearance
- Head Model ID
- Race
- Gender
- Voice Type

### Behavior
- Movement Pattern
- Spawn Conditions
- AI Settings
- Quest Rewards

---

## 💾 Data Persistence

### JSON Format
Custom NPCs are stored in `npcs/custom_npcs.json`:

```json
{
  "40000": {
    "name": "Custom Guard",
    "npc_type": "friendly",
    "character_class": "warrior",
    "level": 10,
    "stats": { ... },
    "combat_stats": { ... },
    "equipment": { ... },
    "appearance": { ... },
    "behavior": { ... }
  }
}
```

### CFF Export
NPCs are exported to GameData.cff with categories:
- **3001**: General NPC data
- **3002**: Stats
- **3003**: Combat stats
- **3004**: Equipment
- **3005**: Behavior
- **2016**: Text entries (names, descriptions)

---

## 🎓 Usage Guide

### Creating a New NPC

1. **Click "Create NPC"** button
2. **Select Creation Mode**:
   - Create New: Start from scratch
   - Edit Existing: Modify a game NPC
   - Duplicate: Clone an existing NPC
3. **Identity Page**: Enter name, type, class, level
4. **Base Stats Page**: Set attribute values
5. **Combat Stats Page**: Configure combat properties
6. **Appearance/Voice Page**: Select visual/audio
7. **Equipment Page**: Assign items to slots
8. **Behavior Page**: Configure AI and spawn
9. **Review Page**: Preview and export

### Browsing NPCs

1. **Click "Browse NPCs"** button
2. **Search**: Use search field to filter
3. **Select**: Click NPC to view details
4. **Actions**:
   - Edit: Modify NPC properties
   - Duplicate: Clone as template
   - Delete: Remove custom NPC
   - Create New: Launch wizard

### Loading Custom CFF

1. **Click "Load CFF File"** button
2. **Select**: Choose a .cff file
3. **Browse**: View NPCs from file
4. **Export**: Save modifications

---

## 🔍 ID Ranges

- **Game NPCs**: 1-39999
- **Custom NPCs**: 40000-49999
- **Reserved**: 50000+

The ID Manager automatically allocates IDs in the custom range and prevents conflicts.

---

## 🐛 Troubleshooting

### NPCs Not Loading
- Check `npcs/custom_npcs.json` exists
- Verify JSON syntax is valid
- Check file permissions

### Export Failures
- Ensure output directory is writable
- Verify all required fields are filled
- Check ID is in valid range

### Missing Dependencies
```bash
# Install required packages
uv pip install PySide6
```

---

## 📚 Related Tools

- **Orthancs Schmiede** (`src/OrthancsSchmiede/`) - Weapon & Armor Suite
- **Mulandirs Zauberschule** (`src/MulandirsZauberschule/`) - Spell Editor
- **Darius Almanach** (`src/DariusAlmanach/`) - Dialogue Viewer
- **TirganachReloaded** (`src/TirganachReloaded/`) - Main CFF Editor

---

## 🏗️ Architecture

Graufurter Bürger Büro is a **standalone application** that:
1. Uses shared components from TirganachReloaded
2. Maintains its own NPC database
3. Exports to standard CFF format
4. Integrates with the ID Manager system

---

## 📖 Development Notes

### Standalone Design
- Follows Orthancs Schmiede pattern
- Self-contained with necessary dependencies
- Shared ID management with other tools
- Consistent UI/UX across suite

### Future Enhancements
- [ ] Icon/portrait display
- [ ] Visual appearance preview
- [ ] Equipment preview
- [ ] Dialogue integration
- [ ] Quest assignment
- [ ] Spawn location map
- [ ] AI behavior editor
- [ ] Loot table editor

---

## 👥 Credits

**Author**: TirganachReloaded Modding Tools  
**Project**: SpellSmut (SpellForce Modding Utilities)  
**Version**: 1.0  
**Date**: 2025

---

## 📄 License

Part of the SpellSmut project. See main project LICENSE for details.
