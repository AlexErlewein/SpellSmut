# Universal Savefile System Plan
## 💾 The ModSave Framework

## Overview

The **Universal Savefile System** provides standardized file formats for saving and loading work-in-progress content across all modding tools. This system allows creators to save their progress without committing to game files, enabling iterative development and sharing of work-in-progress assets.

**Status**: ✅ Planning Complete  
**Priority**: High  
**Dependencies**: All creator tools

---

## Key Features

### 1. Custom File Extensions
- `.quest` for quest files
- `.spell` for spell files
- `.weapon` for weapon files  
- `.armor` for armor files
- `.npc` for NPC files
- `.building` for building files (when implemented)

### 2. Format Specifications
- Underlying format: JSON with optional YAML support
- Human-readable for easy editing
- Version tracking for compatibility
- Built-in validation schemas

### 3. Cross-Tool Compatibility
- Works with all creator tools (Quest, Spell, Weapon, Armor, NPC)
- Allows loading content created in one tool into another
- Enables work-in-progress sharing between modders

### 4. Project Integration
- Save/load directly within each creation tool
- Option to export for sharing
- Import functionality for building on others' work

---

## File Format Specifications

### Common Structure (.modsave Format)
```json
{
  "metadata": {
    "version": "1.0",
    "creator_tool": "Weapon Forge",
    "created_date": "2025-10-27T14:30:00Z",
    "last_modified": "2025-10-27T15:45:00Z",
    "compatible_versions": ["1.0", "1.1"]
  },
  "data": {
    // Content-specific data goes here
  },
  "validation": {
    "checksum": "abc123...",
    "status": "valid"
  }
}
```

### Specific Format Examples

#### Weapon Save (.weapon)
```json
{
  "metadata": { ... },
  "data": {
    "id": 10001,
    "name": "Flaming Sword",
    "slot": "RightHand",
    "damage_min": 15,
    "damage_max": 25,
    "speed": 1.2,
    "material": "Steel",
    "elemental_effect": {
      "type": "Fire",
      "damage": 5,
      "duration": 3
    },
    "requirements": {
      "strength": 12,
      "skill": "Swords"
    },
    "visual": {
      "icon": "icon_001",
      "model": "sword_01.mdl"
    }
  },
  "validation": { ... }
}
```

#### Spell Save (.spell)
```json
{
  "metadata": { ... },
  "data": {
    "id": 305,
    "name": "Fireball",
    "school": "Fire",
    "levels": [
      {
        "level": 1,
        "damage": 20,
        "mana_cost": 15,
        "cooldown": 2.5,
        "range": 30,
        "duration": 0
      },
      {
        "level": 2,
        "damage": 35,
        "mana_cost": 25,
        "cooldown": 2.5,
        "range": 35,
        "duration": 0
      }
      // ... up to level 15
    ],
    "requirements": {
      "intelligence": 10,
      "wisdom": 8
    },
    "visual": {
      "icon": "spell_fireball_01",
      "cast_effect": "fire_explosion_01",
      "target_effect": "fire_impact_01"
    }
  },
  "validation": { ... }
}
```

#### Quest Save (.quest)
```json
{
  "metadata": { ... },
  "data": {
    "id": 9001,
    "name": "The Lost Artifact",
    "difficulty": "Medium",
    "steps": [
      {
        "step_id": 1,
        "description": "Talk to NPC in town",
        "conditions": [
          {"type": "dialogue", "npc_id": 40001}
        ],
        "rewards": [
          {"type": "exp", "amount": 100},
          {"type": "item", "item_id": 30001}
        ]
      }
    ],
    "prerequisites": [
      {"quest_id": 9000, "status": "completed"}
    ]
  },
  "validation": { ... }
}
```

---

## Integration Points

### 1. Save Functionality
- Available in each tool's main menu as "Save Project" and "Export"
- "Save Project" keeps work internal to tool
- "Export" creates shareable .{type} file
- Auto-save feature (configurable interval)

### 2. Load Functionality
- "Open Project" and "Import" options
- Browse and search capabilities
- Preview functionality before loading
- Version compatibility check

### 3. Validation System
- Schema validation for structure
- ID conflict checking against ID Manager
- Game compatibility verification
- Error reporting for invalid files

### 4. Sharing & Collaboration
- Import other modders' work as base for new content
- Version tracking for collaborative projects
- Metadata attribution for original creators

---

## Technical Implementation

### File Structure
```
ProjectSaveSystem/
├── core/
│   ├── save_manager.py
│   ├── format_validator.py
│   └── version_checker.py
├── formats/
│   ├── weapon_format.py
│   ├── spell_format.py
│   ├── quest_format.py
│   ├── armor_format.py
│   ├── npc_format.py
│   └── building_format.py
└── utils/
    ├── file_dialogs.py
    └── checksum_utils.py
```

### API Interface
```python
class SaveManager:
    def save_content(self, content_data, file_path, content_type):
        """Save content to specified file path"""
    
    def load_content(self, file_path):
        """Load content from file path"""
    
    def validate_content(self, content_data, content_type):
        """Validate content against schema"""
    
    def check_compatibility(self, file_path):
        """Check file version compatibility"""
```

---

## Implementation Timeline

**Week 1**: Core save manager and common format structure  
**Week 2**: Individual format implementations (.spell, .weapon, .quest)  
**Week 3**: Integration with creator tools  
**Week 4**: Validation and error handling  
**Week 5**: Sharing and import/export functionality  
**Week 6**: Testing and documentation

---

## Success Criteria

- ✅ All creator tools support .{type} save/load
- ✅ Cross-tool compatibility works
- ✅ Files can be shared between modders
- ✅ Version compatibility maintained
- ✅ Validation system prevents corrupt saves
- ✅ Auto-save functionality works reliably

---

## Related Documents

- [Quest Creator](QUEST_CREATION_PLAN.md) - Integration point
- [Spell Creator](SPELL_CREATION_PLAN.md) - Integration point  
- [Weapon Creator](WEAPON_CREATION_PLAN.md) - Integration point
- [Armor Creator](ARMOR_CREATOR_PLAN.md) - Integration point
- [NPC Creator](NPC_CREATOR_PLAN.md) - Integration point

---

**Document Version**: 1.0  
**Created**: 2025-10-27  
**Status**: ✅ Planning Complete - Ready for Implementation